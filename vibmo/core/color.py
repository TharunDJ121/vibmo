"""
Color space conversions (RGB, HSL, OKLab), alpha compositing, gradients, and palettes.
"""

from __future__ import annotations
import math
import colorsys
from typing import Tuple, Union, Sequence, List, Optional
from dataclasses import dataclass


def _srgb_to_linear(c: float) -> float:
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


def _linear_to_srgb(c: float) -> float:
    return 12.92 * c if c <= 0.0031308 else 1.055 * (c ** (1.0 / 2.4)) - 0.055


def _rgb_to_oklab(r: float, g: float, b: float) -> Tuple[float, float, float]:
    """Converts sRGB [0..1] to OKLab (L, a, b) color space."""
    lr = _srgb_to_linear(r)
    lg = _srgb_to_linear(g)
    lb = _srgb_to_linear(b)

    l = 0.4122214708 * lr + 0.5363325363 * lg + 0.0514459929 * lb
    m = 0.2119034982 * lr + 0.6806995451 * lg + 0.1073969566 * lb
    s = 0.0883024619 * lr + 0.2817188376 * lg + 0.6299787005 * lb

    l_ = l ** (1.0 / 3.0) if l > 0 else 0.0
    m_ = m ** (1.0 / 3.0) if m > 0 else 0.0
    s_ = s ** (1.0 / 3.0) if s > 0 else 0.0

    L = 0.2104542553 * l_ + 0.7936177850 * m_ - 0.0040720468 * s_
    a = 1.9779984951 * l_ - 2.4285922050 * m_ + 0.4505937099 * s_
    b_ = 0.0259040371 * l_ + 0.7827717662 * m_ - 0.8086757660 * s_
    return (L, a, b_)


def _oklab_to_rgb(L: float, a: float, b: float) -> Tuple[float, float, float]:
    """Converts OKLab (L, a, b) to sRGB [0..1]."""
    l_ = L + 0.3963377774 * a + 0.2158037573 * b
    m_ = L - 0.1055613458 * a - 0.0638541728 * b
    s_ = L - 0.0894841775 * a - 1.2914855480 * b

    l = l_ ** 3 if l_ > 0 else 0.0
    m = m_ ** 3 if m_ > 0 else 0.0
    s = s_ ** 3 if s_ > 0 else 0.0

    lr = +4.0767416621 * l - 3.3077115913 * m + 0.2309699292 * s
    lg = -1.2684380046 * l + 2.6097574011 * m - 0.3413193965 * s
    lb = -0.0041960863 * l - 0.7034186147 * m + 1.7076147010 * s

    r = _linear_to_srgb(max(0.0, min(1.0, lr)))
    g = _linear_to_srgb(max(0.0, min(1.0, lg)))
    b_out = _linear_to_srgb(max(0.0, min(1.0, lb)))
    return (r, g, b_out)


class Color:
    """Represents an RGBA color with float channels in range [0.0, 1.0]."""

    __slots__ = ("r", "g", "b", "a")

    def __init__(self, r: float, g: float, b: float, a: float = 1.0) -> None:
        self.r = max(0.0, min(1.0, float(r)))
        self.g = max(0.0, min(1.0, float(g)))
        self.b = max(0.0, min(1.0, float(b)))
        self.a = max(0.0, min(1.0, float(a)))

    @classmethod
    def rgb(cls, r: float, g: float, b: float, a: float = 1.0) -> Color:
        return cls(r, g, b, a)

    @classmethod
    def rgb255(cls, r: int, g: int, b: int, a: float = 1.0) -> Color:
        return cls(r / 255.0, g / 255.0, b / 255.0, a)

    rgba = rgb255


    @classmethod
    def hex(cls, hex_str: str) -> Color:
        s = hex_str.strip().lstrip("#")
        if len(s) == 3:  # #RGB
            r = int(s[0] * 2, 16) / 255.0
            g = int(s[1] * 2, 16) / 255.0
            b = int(s[2] * 2, 16) / 255.0
            return cls(r, g, b, 1.0)
        elif len(s) == 4:  # #RGBA
            r = int(s[0] * 2, 16) / 255.0
            g = int(s[1] * 2, 16) / 255.0
            b = int(s[2] * 2, 16) / 255.0
            a = int(s[3] * 2, 16) / 255.0
            return cls(r, g, b, a)
        elif len(s) == 6:  # #RRGGBB
            r = int(s[0:2], 16) / 255.0
            g = int(s[2:4], 16) / 255.0
            b = int(s[4:6], 16) / 255.0
            return cls(r, g, b, 1.0)
        elif len(s) == 8:  # #RRGGBBAA
            r = int(s[0:2], 16) / 255.0
            g = int(s[2:4], 16) / 255.0
            b = int(s[4:6], 16) / 255.0
            a = int(s[6:8], 16) / 255.0
            return cls(r, g, b, a)
        raise ValueError(f"Invalid hex color string: '{hex_str}'")

    from_hex = hex

    @classmethod
    def hsl(cls, h: float, s: float, l: float, a: float = 1.0) -> Color:
        """h in [0..360], s in [0..1], l in [0..1], a in [0..1]."""
        r, g, b = colorsys.hls_to_rgb(h / 360.0, l, s)
        return cls(r, g, b, a)

    @classmethod
    def from_any(cls, val: Union[Color, str, Sequence[float], Tuple]) -> Color:
        if isinstance(val, Color):
            return cls(val.r, val.g, val.b, val.a)
        if isinstance(val, (tuple, list)):
            if len(val) == 3:
                return cls(val[0], val[1], val[2], 1.0)
            elif len(val) >= 4:
                return cls(val[0], val[1], val[2], val[3])
        if isinstance(val, str):
            s = val.strip().lower()
            if s.startswith("#"):
                try:
                    return cls.hex(s)
                except Exception:
                    return cls(0.39, 0.40, 0.95, 1.0)  # Safe indigo fallback
            
            # Common CSS & High-Vibe Named Color Lookup
            named_palette = {
                "transparent": (0.0, 0.0, 0.0, 0.0),
                "black": (0.0, 0.0, 0.0, 1.0),
                "white": (1.0, 1.0, 1.0, 1.0),
                "cyan": (0.02, 0.71, 0.83, 1.0),
                "emerald": (0.06, 0.73, 0.51, 1.0),
                "indigo": (0.39, 0.40, 0.95, 1.0),
                "purple": (0.66, 0.33, 0.98, 1.0),
                "rose": (0.96, 0.25, 0.37, 1.0),
                "pink": (0.93, 0.28, 0.60, 1.0),
                "amber": (0.96, 0.62, 0.04, 1.0),
                "red": (0.94, 0.27, 0.27, 1.0),
                "green": (0.13, 0.77, 0.37, 1.0),
                "blue": (0.23, 0.51, 0.96, 1.0),
                "slate": (0.40, 0.47, 0.58, 1.0),
                "dark_navy": (0.04, 0.05, 0.09, 1.0),
                # Agent Hallucination Aliases
                "neon_green": (0.13, 0.95, 0.45, 1.0),
                "hacker_green": (0.13, 0.95, 0.45, 1.0),
                "neon_cyan": (0.0, 0.92, 1.0, 1.0),
                "glow_cyan": (0.0, 0.92, 1.0, 1.0),
                "neon_purple": (0.75, 0.35, 1.0, 1.0),
            }
            
            if s in named_palette:
                rgba = named_palette[s]
                return cls(*rgba)

            # Tokenize by delimiters (e.g., "dark-slate-900", "electric_green")
            import re
            tokens = [t for t in re.split(r'[-_\s]+', s) if t]
            for token in tokens:
                if token in named_palette:
                    return cls(*named_palette[token])

            # Longest key match to prevent short prefixes matching substrings
            for k in sorted(named_palette.keys(), key=len, reverse=True):
                if k in s:
                    return cls(*named_palette[k])

            # Safe universal fallback
            return cls(0.39, 0.40, 0.95, 1.0)  # Indigo fallback
            
        raise ValueError(f"Cannot convert {val} of type {type(val)} to Color")


    def with_alpha(self, alpha: float) -> Color:
        return Color(self.r, self.g, self.b, max(0.0, min(1.0, float(alpha))))

    def fade(self, factor: float) -> Color:
        return Color(self.r, self.g, self.b, self.a * max(0.0, min(1.0, float(factor))))

    def lighten(self, amount: float) -> Color:
        h, l, s = colorsys.rgb_to_hls(self.r, self.g, self.b)
        new_l = max(0.0, min(1.0, l + amount))
        r, g, b = colorsys.hls_to_rgb(h, new_l, s)
        return Color(r, g, b, self.a)

    def darken(self, amount: float) -> Color:
        return self.lighten(-amount)

    def lerp(self, other: Color, t: float, space: str = "oklab") -> Color:
        t = max(0.0, min(1.0, float(t)))
        alpha = self.a + (other.a - self.a) * t

        if space.lower() == "oklab":
            l1, a1, b1 = _rgb_to_oklab(self.r, self.g, self.b)
            l2, a2, b2 = _rgb_to_oklab(other.r, other.g, other.b)
            l = l1 + (l2 - l1) * t
            a = a1 + (a2 - a1) * t
            b = b1 + (b2 - b1) * t
            r, g, b_out = _oklab_to_rgb(l, a, b)
            return Color(r, g, b_out, alpha)
        elif space.lower() == "rgb":
            return Color(
                self.r + (other.r - self.r) * t,
                self.g + (other.g - self.g) * t,
                self.b + (other.b - self.b) * t,
                alpha,
            )
        elif space.lower() == "hsl":
            h1, l1, s1 = colorsys.rgb_to_hls(self.r, self.g, self.b)
            h2, l2, s2 = colorsys.rgb_to_hls(other.r, other.g, other.b)
            # shortest hue distance
            dh = (h2 - h1 + 0.5) % 1.0 - 0.5
            h = (h1 + dh * t) % 1.0
            l = l1 + (l2 - l1) * t
            s = s1 + (s2 - s1) * t
            r, g, b = colorsys.hls_to_rgb(h, l, s)
            return Color(r, g, b, alpha)
        else:
            raise ValueError(f"Unknown color interpolation space: {space}")

    def to_tuple_rgba(self) -> Tuple[float, float, float, float]:
        return (self.r, self.g, self.b, self.a)

    def to_cairo(self) -> Tuple[float, float, float, float]:
        return (self.r, self.g, self.b, self.a)

    def to_rgb255(self) -> Tuple[int, int, int]:
        return (round(self.r * 255), round(self.g * 255), round(self.b * 255))

    def to_rgba255(self) -> Tuple[int, int, int, int]:
        return (round(self.r * 255), round(self.g * 255), round(self.b * 255), round(self.a * 255))

    def to_hex(self, include_alpha: bool = False) -> str:
        r, g, b, a = self.to_rgba255()
        if include_alpha or a < 255:
            return f"#{r:02x}{g:02x}{b:02x}{a:02x}"
        return f"#{r:02x}{g:02x}{b:02x}"

    def to_css(self) -> str:
        if self.a >= 1.0:
            return self.to_hex()
        return f"rgba({round(self.r * 255)}, {round(self.g * 255)}, {round(self.b * 255)}, {self.a:.3f})"

    def __repr__(self) -> str:
        return f"Color({self.to_hex(include_alpha=self.a < 1.0)})"

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Color):
            return False
        return (
            math.isclose(self.r, other.r, abs_tol=1e-4)
            and math.isclose(self.g, other.g, abs_tol=1e-4)
            and math.isclose(self.b, other.b, abs_tol=1e-4)
            and math.isclose(self.a, other.a, abs_tol=1e-4)
        )

# Direct class constants for effortless scripting
Color.WHITE = Color(1.0, 1.0, 1.0, 1.0)
Color.BLACK = Color(0.0, 0.0, 0.0, 1.0)
Color.TRANSPARENT = Color(0.0, 0.0, 0.0, 0.0)


@dataclass
class ColorStop:
    offset: float
    color: Color

    def __init__(self, offset: float, color: Union[Color, str]) -> None:
        self.offset = max(0.0, min(1.0, float(offset)))
        self.color = Color.from_any(color)


class LinearGradient:
    """Linear gradient defined by start point, end point, and color stops."""

    def __init__(
        self,
        start: Tuple[float, float] = (0.0, 0.0),
        end: Tuple[float, float] = (1.0, 1.0),
        stops: Optional[List[Union[ColorStop, Tuple[float, Union[Color, str]]]]] = None,
    ) -> None:
        self.start = start
        self.end = end
        self.stops: List[ColorStop] = []
        if stops:
            for s in stops:
                if isinstance(s, ColorStop):
                    self.stops.append(s)
                elif isinstance(s, (tuple, list)) and len(s) == 2:
                    self.stops.append(ColorStop(s[0], s[1]))


class RadialGradient:
    """Radial gradient defined by center, inner/outer radius, and color stops."""

    def __init__(
        self,
        center: Tuple[float, float] = (0.5, 0.5),
        radius: float = 0.5,
        stops: Optional[List[Union[ColorStop, Tuple[float, Union[Color, str]]]]] = None,
    ) -> None:
        self.center = center
        self.radius = radius
        self.stops: List[ColorStop] = []
        if stops:
            for s in stops:
                if isinstance(s, ColorStop):
                    self.stops.append(s)
                elif isinstance(s, (tuple, list)) and len(s) == 2:
                    self.stops.append(ColorStop(s[0], s[1]))


# Color Palette Presets
class colors:
    TRANSPARENT = Color(0, 0, 0, 0)
    WHITE = Color(1.0, 1.0, 1.0, 1.0)
    BLACK = Color(0.0, 0.0, 0.0, 1.0)

    # Modern Design Palette
    SLATE_950 = Color.hex("#020617")
    SLATE_900 = Color.hex("#0f172a")
    SLATE_800 = Color.hex("#1e293b")
    SLATE_700 = Color.hex("#334155")
    SLATE_400 = Color.hex("#94a3b8")
    SLATE_200 = Color.hex("#e2e8f0")
    SLATE_50 = Color.hex("#f8fafc")

    INDIGO_500 = Color.hex("#6366f1")
    INDIGO_600 = Color.hex("#4f46e5")
    INDIGO_400 = Color.hex("#818cf8")

    VIOLET_500 = Color.hex("#8b5cf6")
    PURPLE_500 = Color.hex("#a855f7")
    FUCHSIA_500 = Color.hex("#d946ef")
    PINK_500 = Color.hex("#ec4899")
    ROSE_500 = Color.hex("#f43f5e")
    RED_500 = Color.hex("#ef4444")
    ORANGE_500 = Color.hex("#f97316")
    AMBER_500 = Color.hex("#f59e0b")
    YELLOW_500 = Color.hex("#eab308")
    LIME_500 = Color.hex("#84cc16")
    GREEN_500 = Color.hex("#22c55e")
    EMERALD_500 = Color.hex("#10b981")
    TEAL_500 = Color.hex("#14b8a6")
    CYAN_500 = Color.hex("#06b6d4")
    SKY_500 = Color.hex("#0ea5e9")
    BLUE_500 = Color.hex("#3b82f6")

    # Short aliases
    RED = RED_500
    GREEN = GREEN_500
    BLUE = BLUE_500
    INDIGO = INDIGO_500
    VIOLET = VIOLET_500
    PINK = PINK_500
    ROSE = ROSE_500
    AMBER = AMBER_500
    EMERALD = EMERALD_500
    CYAN = CYAN_500
    PURPLE = PURPLE_500
    ORANGE = ORANGE_500
    YELLOW = YELLOW_500
    LIME = LIME_500
    TEAL = TEAL_500
    SKY = SKY_500
    GRAY = SLATE_400
    DARK_NAVY = SLATE_950
    NAVY = SLATE_950

    hex = Color.hex
    rgb = Color.rgb
    hsl = Color.hsl
