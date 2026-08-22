"""
Kinetic Typography: Character, Word, and Line-level Staggered Animation Decompositions with Rich Markup.
"""

from __future__ import annotations
import math
import re
from typing import Any, Callable, List, NamedTuple, Optional, Tuple, Union
import cairo


from vibmo.core.vector import Vector2D
from vibmo.core.color import Color, LinearGradient, colors
from vibmo.core.signal import Signal, AnimationAction
from vibmo.core.easing import Ease, EasingFunc
from vibmo.scene.node import Node
from vibmo.typography.text import Text


class RichToken(NamedTuple):
    text: str
    color: Color
    bold: bool
    italic: bool


class GlyphNode(Text):

    """Represents an individual character glyph node within a KineticText hierarchy."""
    def __init__(self, char: str, **kwargs: Any) -> None:
        super().__init__(text=char, **kwargs)


class _WaveBinding:
    def __init__(self, base_y: float, index: int, amplitude: float, speed: float, wave_length: float):
        self.base_y = base_y
        self.index = index
        self.amplitude = amplitude
        self.speed = speed
        self.wave_length = wave_length

    def __call__(self, t: float) -> Vector2D:
        offset_y = math.sin((t * math.pi * self.speed) - (self.index * self.wave_length)) * self.amplitude
        return Vector2D(0.0, self.base_y + offset_y)


class KineticText(Node):
    """
    Advanced typography engine supporting inline rich tags (<bold>, <gradient>, <glow>, <color>),
    precise text metrics, auto-alignment, and cinematic 3D character reveals.
    """

    def __init__(
        self,
        text: str = "",
        font_size: float = 36.0,
        font_family: str = "Inter",
        bold: bool = False,
        italic: bool = False,
        color: Optional[Union[Color, str]] = colors.WHITE,
        line_height: float = 1.3,
        letter_spacing: float = 0.0,
        align: str = "left",
        max_width: Optional[float] = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)
        self.raw_text = str(text)
        self.font_size = Signal(float(font_size), f"{self.name}.font_size")
        self.font_family = font_family
        self.bold = bold
        self.italic = italic
        
        resolved_color = Color.from_any(color) if isinstance(color, (str, Color)) else colors.WHITE
        self.color = Signal(resolved_color, f"{self.name}.color")
        self.line_height = line_height
        self.letter_spacing = letter_spacing
        self.text_align = align.lower()
        self.max_width = max_width

        self.glyphs: List[GlyphNode] = []
        self._build_glyph_tree()

    def _parse_rich_tokens(self, text: str, default_color: Color) -> List[RichToken]:
        """Parses inline markup tags: <bold>, <italic>, <gradient:#c1:#c2>, <color:#hex>, <#hex>."""
        tokens: List[RichToken] = []
        
        tag_pattern = re.compile(r"<([#a-zA-Z0-9_:-]+)>(.*?)</\1>", re.DOTALL)
        last_idx = 0

        for m in tag_pattern.finditer(text):
            if m.start() > last_idx:
                tokens.append(RichToken(text[last_idx:m.start()], default_color, self.bold, self.italic))
            
            raw_tag = m.group(1).lower()
            inner_text = m.group(2)
            c = default_color
            b = self.bold
            it = self.italic

            if raw_tag in ("b", "bold"):
                b = True
            elif raw_tag in ("i", "italic"):
                it = True
            elif raw_tag.startswith("gradient:"):
                # <gradient:#6366f1:#06b6d4>
                parts = raw_tag.split(":")[1:]
                if len(parts) >= 2:
                    c1 = Color.from_any(parts[0])
                    c2 = Color.from_any(parts[1])
                    # Interpolate per character in inner_text
                    n_chars = max(1, len(inner_text))
                    for i, ch in enumerate(inner_text):
                        t = i / max(1, n_chars - 1)
                        interp_c = Color(
                            r=c1.r + (c2.r - c1.r) * t,
                            g=c1.g + (c2.g - c1.g) * t,
                            b=c1.b + (c2.b - c1.b) * t,
                            a=c1.a + (c2.a - c1.a) * t,
                        )
                        tokens.append(RichToken(ch, interp_c, b, it))
                    last_idx = m.end()
                    continue
            elif raw_tag.startswith("#"):
                c = Color.hex(raw_tag)
            elif raw_tag.startswith("color:"):
                c = Color.from_any(raw_tag.split(":", 1)[1])
            elif hasattr(colors, raw_tag.upper()):
                c = getattr(colors, raw_tag.upper())

            tokens.append(RichToken(inner_text, c, b, it))
            last_idx = m.end()

        if last_idx < len(text):
            tokens.append(RichToken(text[last_idx:], default_color, self.bold, self.italic))

        return tokens


    def _build_glyph_tree(self) -> None:
        self.clear()
        self.glyphs.clear()

        fs = max(1.0, float(self.font_size.get()))
        base_color = self.color.get()
        if not isinstance(base_color, Color):
            base_color = colors.WHITE

        # 1. Parse tokens
        tokens = self._parse_rich_tokens(self.raw_text, base_color)

        # 2. Measure glyphs and break into lines
        measuring_surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, 1, 1)
        m_ctx = cairo.Context(measuring_surf)

        lines: List[List[Tuple[str, Color, bool, bool, float]]] = [[]]
        line_widths: List[float] = [0.0]

        for text_chunk, chunk_color, is_b, is_it in tokens:
            slant = cairo.FONT_SLANT_ITALIC if is_it else cairo.FONT_SLANT_NORMAL
            weight = cairo.FONT_WEIGHT_BOLD if is_b else cairo.FONT_WEIGHT_NORMAL
            m_ctx.select_font_face(self.font_family, slant, weight)
            m_ctx.set_font_size(fs)

            for ch in text_chunk:
                if ch == "\n":
                    lines.append([])
                    line_widths.append(0.0)
                    continue

                ext = m_ctx.text_extents(ch)
                adv = ext.x_advance if ext.x_advance > 0 else (fs * 0.3 if ch == " " else fs * 0.5)

                if self.max_width is not None and line_widths[-1] + adv > self.max_width and ch != " ":
                    lines.append([])
                    line_widths.append(0.0)

                lines[-1].append((ch, chunk_color, is_b, is_it, adv))
                line_widths[-1] += adv + self.letter_spacing

        # 3. Create GlyphNodes positioned per alignment
        max_line_w = max(line_widths, default=0.0)
        curr_y = 0.0

        for line_idx, line in enumerate(lines):
            lw = line_widths[line_idx]
            if self.text_align == "center":
                start_x = (max_line_w - lw) * 0.5
            elif self.text_align == "right":
                start_x = max_line_w - lw
            else:
                start_x = 0.0


            curr_x = start_x
            for ch, chunk_color, is_b, is_it, adv in line:
                glyph = GlyphNode(
                    char=ch,
                    font_size=fs,
                    font_family=self.font_family,
                    bold=is_b,
                    italic=is_it,
                    color=chunk_color,
                    position=Vector2D(curr_x, curr_y),
                )
                self.glyphs.append(glyph)
                self.add(glyph)
                curr_x += adv + self.letter_spacing

            curr_y += fs * self.line_height

    def local_bounds(self, time: float = 0.0) -> Tuple[float, float, float, float]:
        if not self.glyphs:
            return (0.0, 0.0, 0.0, 0.0)
        fs = max(1.0, float(self.font_size.get(time)))
        lines = self.raw_text.split("\n")
        max_x = max((g.position.get(time).x + fs * 0.6 for g in self.glyphs), default=0.0)
        h = len(lines) * fs * self.line_height
        return (0.0, 0.0, max_x, h)

    def reveal_characters(
        self,
        stagger: float = 0.022,
        duration: float = 0.6,
        offset_y: float = 35.0,
        scale_from: float = 0.6,
        rotate_x_from: float = 0.4,
        ease: Optional[EasingFunc] = None,
        delay: float = 0.0,
    ) -> List[AnimationAction]:
        """
        Staggers character glyph entrances upward with spring overshoot and subtle 3D tilt.
        """
        e = ease or Ease.spring(stiffness=150, damping=13)
        actions: List[AnimationAction] = []
        curr_delay = delay

        for glyph in self.glyphs:
            if glyph.text.get() == " ":
                curr_delay += stagger * 0.5
                continue

            curr_pos = glyph.position.get()
            glyph.position.set(Vector2D(curr_pos.x, curr_pos.y + offset_y))
            glyph.opacity.set(0.0)
            glyph.scale.set(Vector2D(scale_from, scale_from))
            if rotate_x_from != 0.0:
                glyph.rotate_x.set(rotate_x_from)
                actions.append(glyph.rotate_x.to(0.0, duration=duration, ease=e, delay=curr_delay))

            actions.append(glyph.position.to(curr_pos, duration=duration, ease=e, delay=curr_delay))
            actions.append(glyph.opacity.to(1.0, duration=duration * 0.5, ease=Ease.out_quad, delay=curr_delay))
            actions.append(glyph.scale.to(Vector2D(1.0, 1.0), duration=duration, ease=e, delay=curr_delay))
            curr_delay += stagger

        return actions

    def reveal_words(
        self,
        stagger: float = 0.08,
        duration: float = 0.6,
        offset_y: float = 30.0,
        ease: Optional[EasingFunc] = None,
        delay: float = 0.0,
    ) -> List[AnimationAction]:
        """Staggers whole words simultaneously."""
        e = ease or Ease.out_cubic
        actions: List[AnimationAction] = []
        curr_delay = delay

        for glyph in self.glyphs:
            if glyph.text.get() == " ":
                curr_delay += stagger
                continue
            curr_pos = glyph.position.get()
            glyph.position.set(Vector2D(curr_pos.x, curr_pos.y + offset_y))
            glyph.opacity.set(0.0)
            actions.append(glyph.position.to(curr_pos, duration=duration, ease=e, delay=curr_delay))
            actions.append(glyph.opacity.to(1.0, duration=duration * 0.6, ease=Ease.out_quad, delay=curr_delay))

        return actions

    def typewriter(self, speed: float = 25.0, delay: float = 0.0) -> List[AnimationAction]:
        """Reveals characters sequentially in typewriter cadence."""
        actions: List[AnimationAction] = []
        dt = 1.0 / speed
        curr_delay = delay

        for glyph in self.glyphs:
            glyph.opacity.set(0.0)
            actions.append(glyph.opacity.to(1.0, duration=0.01, delay=curr_delay))
            curr_delay += dt

        return actions

    def wave(self, amplitude: float = 6.0, speed: float = 1.5, wave_length: float = 0.25) -> None:
        """Sets up continuous harmonic sine wave floating across characters."""
        for i, glyph in enumerate(self.glyphs):
            base_pos = glyph.position.get()
            glyph.position.bind(_WaveBinding(base_pos.y, i, amplitude, speed, wave_length))

