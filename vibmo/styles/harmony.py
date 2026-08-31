"""
Color Harmony, Contrast & Design Token Intelligence for Vibmo.

Provides:
  1. WCAG 2.1 Contrast Ratio calculations (AA / AAA compliance for video text).
  2. Color wheel generators: Complementary, Triadic, Analogous, Tetradic.
  3. Responsive typographic scale calculators (Major Third, Golden Ratio, Perfect Fourth).
"""

from __future__ import annotations

import colorsys
import math
from dataclasses import dataclass
from typing import Sequence


@dataclass
class ContrastEvaluation:
    ratio: float
    is_wcag_aa: bool       # >= 4.5:1 (normal text) or >= 3.0:1 (large text / UI components)
    is_wcag_aaa: bool      # >= 7.0:1 (normal text) or >= 4.5:1 (large text)
    rating: str            # "Fail", "AA Large", "AA", "AAA"


class ColorHarmonizer:
    """Design token math and accessibility validator."""

    @staticmethod
    def hex_to_rgb(hex_str: str) -> tuple[float, float, float]:
        """Convert #RRGGBB to (r, g, b) normalized 0.0-1.0."""
        h = hex_str.lstrip("#")
        if len(h) == 3:
            h = "".join(c * 2 for c in h)
        h = h[:6]
        r = int(h[0:2], 16) / 255.0
        g = int(h[2:4], 16) / 255.0
        b = int(h[4:6], 16) / 255.0
        return r, g, b

    @staticmethod
    def rgb_to_hex(r: float, g: float, b: float) -> str:
        """Convert (r, g, b) 0.0-1.0 to #RRGGBB."""
        ir = max(0, min(255, int(round(r * 255))))
        ig = max(0, min(255, int(round(g * 255))))
        ib = max(0, min(255, int(round(b * 255))))
        return f"#{ir:02x}{ig:02x}{ib:02x}"

    @classmethod
    def get_relative_luminance(cls, hex_color: str) -> float:
        """Calculate WCAG relative luminance."""
        r, g, b = cls.hex_to_rgb(hex_color)

        def adjust(c: float) -> float:
            return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4

        return 0.2126 * adjust(r) + 0.7152 * adjust(g) + 0.0722 * adjust(b)

    @classmethod
    def evaluate_contrast(cls, fg_hex: str, bg_hex: str) -> ContrastEvaluation:
        """Calculate WCAG 2.1 contrast ratio between foreground and background."""
        l1 = cls.get_relative_luminance(fg_hex)
        l2 = cls.get_relative_luminance(bg_hex)
        lighter = max(l1, l2)
        darker = min(l1, l2)
        ratio = (lighter + 0.05) / (darker + 0.05)

        is_aa = ratio >= 4.5
        is_aaa = ratio >= 7.0

        if is_aaa:
            rating = "AAA"
        elif is_aa:
            rating = "AA"
        elif ratio >= 3.0:
            rating = "AA Large / UI Components"
        else:
            rating = "Fail"

        return ContrastEvaluation(
            ratio=round(ratio, 2),
            is_wcag_aa=is_aa or ratio >= 3.0,
            is_wcag_aaa=is_aaa,
            rating=rating,
        )

    @classmethod
    def generate_complementary(cls, base_hex: str) -> str:
        r, g, b = cls.hex_to_rgb(base_hex)
        h, l, s = colorsys.rgb_to_hls(r, g, b)
        comp_h = (h + 0.5) % 1.0
        cr, cg, cb = colorsys.hls_to_rgb(comp_h, l, s)
        return cls.rgb_to_hex(cr, cg, cb)

    @classmethod
    def generate_triadic(cls, base_hex: str) -> tuple[str, str, str]:
        r, g, b = cls.hex_to_rgb(base_hex)
        h, l, s = colorsys.rgb_to_hls(r, g, b)
        h1 = (h + 1.0 / 3.0) % 1.0
        h2 = (h + 2.0 / 3.0) % 1.0
        r1, g1, b1 = colorsys.hls_to_rgb(h1, l, s)
        r2, g2, b2 = colorsys.hls_to_rgb(h2, l, s)
        return base_hex, cls.rgb_to_hex(r1, g1, b1), cls.rgb_to_hex(r2, g2, b2)

    @classmethod
    def generate_analogous(cls, base_hex: str, angle: float = 30.0) -> tuple[str, str, str]:
        r, g, b = cls.hex_to_rgb(base_hex)
        h, l, s = colorsys.rgb_to_hls(r, g, b)
        delta = angle / 360.0
        h1 = (h - delta) % 1.0
        h2 = (h + delta) % 1.0
        r1, g1, b1 = colorsys.hls_to_rgb(h1, l, s)
        r2, g2, b2 = colorsys.hls_to_rgb(h2, l, s)
        return cls.rgb_to_hex(r1, g1, b1), base_hex, cls.rgb_to_hex(r2, g2, b2)


class TypographicScale:
    """Generates modular typography scales for motion graphics layout hierarchy."""

    RATIOS = {
        "minor_second": 1.067,
        "major_second": 1.125,
        "minor_third": 1.200,
        "major_third": 1.250,
        "perfect_fourth": 1.333,
        "augmented_fourth": 1.414,
        "perfect_fifth": 1.500,
        "golden_ratio": 1.618,
    }

    @classmethod
    def generate_scale(
        cls,
        base_size: float = 16.0,
        ratio: str = "perfect_fourth",
        steps_up: int = 5,
        steps_down: int = 2,
    ) -> dict[str, float]:
        r = cls.RATIOS.get(ratio, 1.333)
        scale: dict[str, float] = {}

        # Down steps (e.g. caption, micro)
        for i in range(steps_down, 0, -1):
            scale[f"step_-{i}"] = round(base_size / (r ** i), 1)

        scale["base"] = base_size

        # Up steps (e.g. h5, h4, h3, h2, h1, display)
        names = ["h5", "h4", "h3", "h2", "h1", "display", "hero"]
        for i in range(1, steps_up + 1):
            key = names[i - 1] if i - 1 < len(names) else f"step_+{i}"
            scale[key] = round(base_size * (r ** i), 1)

        return scale
