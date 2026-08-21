"""
Mathematical Formula rendering, LaTeX parsing, and Equation term animation.
Outperforms traditional math animation engines with instant vector rasterization and beautiful defaults.
"""

from __future__ import annotations
import math
import re
from typing import Any, List, Optional, Tuple, Union
import cairo
from vibmo.core.vector import Vector2D
from vibmo.core.color import Color, colors
from vibmo.core.signal import Signal, AnimationAction
from vibmo.core.easing import Ease, EasingFunc
from vibmo.scene.node import Node
from vibmo.typography.text import Text


# Unicode math symbol mapping for fast instant rendering without requiring external LaTeX binary
LATEX_SYMBOL_MAP = {
    r"\alpha": "α", r"\beta": "β", r"\gamma": "γ", r"\delta": "δ",
    r"\epsilon": "ε", r"\zeta": "ζ", r"\eta": "η", r"\theta": "θ",
    r"\iota": "ι", r"\kappa": "κ", r"\lambda": "λ", r"\mu": "μ",
    r"\nu": "ν", r"\xi": "ξ", r"\pi": "π", r"\rho": "ρ",
    r"\sigma": "σ", r"\tau": "τ", r"\upsilon": "υ", r"\phi": "φ",
    r"\chi": "χ", r"\psi": "ψ", r"\omega": "ω",
    r"\Gamma": "Γ", r"\Delta": "Δ", r"\Theta": "Θ", r"\Lambda": "Λ",
    r"\Xi": "Ξ", r"\Pi": "Π", r"\Sigma": "Σ", r"\Upsilon": "Υ",
    r"\Phi": "Φ", r"\Psi": "Ψ", r"\Omega": "Ω",
    r"\times": "×", r"\div": "÷", r"\pm": "±", r"\mp": "∓",
    r"\cdot": "·", r"\infty": "∞", r"\partial": "∂", r"\nabla": "∇",
    r"\sum": "∑", r"\prod": "∏", r"\int": "∫", r"\oint": "∮",
    r"\approx": "≈", r"\neq": "≠", r"\leq": "≤", r"\geq": "≥",
    r"\equiv": "≡", r"\in": "∈", r"\notin": "∉", r"\subset": "⊂",
    r"\cup": "∪", r"\cap": "∩", r"\forall": "∀", r"\exists": "∃",
    r"\sqrt": "√", r"\to": "→", r"\leftarrow": "←", r"\Rightarrow": "⇒",
}

SUPERSCRIPTS = {
    "0": "⁰", "1": "¹", "2": "²", "3": "³", "4": "⁴",
    "5": "⁵", "6": "⁶", "7": "⁷", "8": "⁸", "9": "⁹",
    "+": "⁺", "-": "⁻", "=": "⁼", "(": "⁽", ")": "⁾",
    "n": "ⁿ", "i": "ⁱ", "x": "ˣ", "y": "ʸ",
}

SUBSCRIPTS = {
    "0": "₀", "1": "₁", "2": "₂", "3": "₃", "4": "₄",
    "5": "₅", "6": "₆", "7": "₇", "8": "₈", "9": "₉",
    "+": "₊", "-": "₋", "=": "₌", "(": "₍", ")": "₎",
    "a": "ₐ", "e": "ₑ", "h": "ₕ", "i": "ᵢ", "j": "ⱼ",
    "k": "ₖ", "l": "ₗ", "m": "ₘ", "n": "ₙ", "o": "ₒ",
    "p": "ₚ", "r": "ᵣ", "s": "ₛ", "t": "ₜ", "u": "ᵤ", "v": "ᵥ", "x": "ₓ",
}


def _clean_latex_to_unicode(latex_str: str) -> str:
    """Converts common LaTeX notation into clean high-res Unicode typography."""
    out = latex_str.strip().strip("$")

    # Square roots: \sqrt{x} -> √(x)
    out = re.sub(r"\\sqrt\{([^}]+)\}", r"√(\1)", out)

    # Fractions: \frac{a}{b} -> (a / b)
    out = re.sub(r"\\frac\{([^}]+)\}\{([^}]+)\}", r"(\1 / \2)", out)

    # Replace symbols
    for tex, uni in LATEX_SYMBOL_MAP.items():
        out = out.replace(tex, uni)

    # Superscripts: x^{2} or x^2
    def _sub_sup(m):
        raw = m.group(1) or m.group(2)
        return "".join(SUPERSCRIPTS.get(c, c) for c in raw)

    out = re.sub(r"\^\{([^}]+)\}|\^([0-9a-zA-Z+-])", _sub_sup, out)

    # Subscripts: x_{0} or x_0
    def _sub_sub(m):
        raw = m.group(1) or m.group(2)
        return "".join(SUBSCRIPTS.get(c, c) for c in raw)

    out = re.sub(r"_\{([^}]+)\}|_([0-9a-zA-Z+-])", _sub_sub, out)

    # Clean remaining curly braces
    out = out.replace("{", "").replace("}", "")

    return out


class MathFormula(Node):
    """
    High-performance Mathematical Formula renderer.
    Renders formulas instantly without requiring a LaTeX binary install,
    with beautiful glowing mathematical styling and term animations.
    """

    def __init__(
        self,
        latex: str = "",
        font_size: float = 48.0,
        font_family: str = "Cambria Math",
        color: Optional[Union[Color, str]] = colors.WHITE,
        glow: bool = True,
        glow_color: Optional[Union[Color, str]] = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)
        self.latex = latex
        self.unicode_text = _clean_latex_to_unicode(latex)
        self.font_size = Signal(float(font_size), f"{self.name}.font_size")
        self.font_family = font_family
        
        resolved_color = Color.from_any(color) if isinstance(color, (str, Color)) else color
        self.color = Signal(resolved_color, f"{self.name}.color")
        self.glow = glow
        self.glow_color = Color.from_any(glow_color) if glow_color else resolved_color.with_alpha(0.3)

    def local_bounds(self, time: float = 0.0) -> Tuple[float, float, float, float]:
        fs = self.font_size.get(time)
        w = len(self.unicode_text) * fs * 0.55
        h = fs * 1.3
        return (0.0, 0.0, w, h)

    def draw(self, ctx: Any, time: float = 0.0) -> None:
        if not self.unicode_text:
            return

        fs = max(1.0, self.font_size.get(time))
        c = self.color.get(time)
        if c is None:
            return

        ctx.save()

        # Fallback fonts for math
        ctx.select_font_face(self.font_family, cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)
        ctx.set_font_size(fs)

        y_baseline = fs * 0.95

        # Draw subtle glow pass
        if self.glow and self.glow_color:
            ctx.save()
            ctx.set_source_rgba(self.glow_color.r, self.glow_color.g, self.glow_color.b, self.glow_color.a * 0.5)
            for ox, oy in [(-2, 0), (2, 0), (0, -2), (0, 2)]:
                ctx.move_to(ox, y_baseline + oy)
                ctx.show_text(self.unicode_text)
            ctx.restore()

        # Main text draw
        ctx.set_source_rgba(c.r, c.g, c.b, c.a)
        ctx.move_to(0, y_baseline)
        ctx.show_text(self.unicode_text)

        ctx.restore()

    def transform_to(
        self,
        new_latex: str,
        duration: float = 0.8,
        ease: Optional[EasingFunc] = None,
    ) -> List[AnimationAction]:
        """Smoothly morphs and crossfades to a new equation."""
        e = ease or Ease.out_cubic
        curr_op = self.opacity.get()
        curr_scale = self.scale.get()

        def _swap_content():
            self.latex = new_latex
            self.unicode_text = _clean_latex_to_unicode(new_latex)

        return [
            self.opacity.to(0.0, duration=duration * 0.4, ease=Ease.in_quad),
            self.scale.to(Vector2D(curr_scale.x * 0.9, curr_scale.y * 0.9), duration=duration * 0.4),
            self.opacity.to(curr_op, duration=duration * 0.6, ease=e, delay=duration * 0.4),
            self.scale.to(curr_scale, duration=duration * 0.6, ease=Ease.spring(stiffness=140, damping=12), delay=duration * 0.4),
        ]
