"""
Curated Aesthetic Design Themes for rapid Vibe Coding.
"""

from __future__ import annotations
from dataclasses import dataclass
from vibmo.core.color import Color, colors


@dataclass
class Theme:
    name: str
    background: Color
    card_bg: Color
    card_stroke: Color
    text_primary: Color
    text_secondary: Color
    accent: Color
    accent_secondary: Color
    font_heading: str
    font_body: str
    corner_radius: float


class Themes:
    """Pre-styled aesthetic themes."""

    MODERN_DARK = Theme(
        name="ModernDark",
        background=Color.hex("#090D16"),
        card_bg=Color.hex("#1E293B").with_alpha(0.6),
        card_stroke=Color.WHITE.with_alpha(0.12),
        text_primary=Color.WHITE,
        text_secondary=Color.hex("#94A3B8"),
        accent=Color.hex("#6366F1"),
        accent_secondary=Color.hex("#EC4899"),
        font_heading="Inter",
        font_body="Inter",
        corner_radius=20.0,
    )

    APPLE_MINIMAL = Theme(
        name="AppleMinimal",
        background=Color.hex("#F5F5F7"),
        card_bg=Color.WHITE,
        card_stroke=Color.hex("#E5E5EA"),
        text_primary=Color.hex("#1D1D1F"),
        text_secondary=Color.hex("#86868B"),
        accent=Color.hex("#0071E3"),
        accent_secondary=Color.hex("#34C759"),
        font_heading="SF Pro Display",
        font_body="SF Pro Text",
        corner_radius=22.0,
    )

    NEON_CYBER = Theme(
        name="NeonCyber",
        background=Color.hex("#05050A"),
        card_bg=Color.hex("#0D1117").with_alpha(0.8),
        card_stroke=Color.hex("#00F0FF").with_alpha(0.3),
        text_primary=Color.hex("#F0F6FC"),
        text_secondary=Color.hex("#8B949E"),
        accent=Color.hex("#00F0FF"),
        accent_secondary=Color.hex("#FF0055"),
        font_heading="JetBrains Mono",
        font_body="JetBrains Mono",
        corner_radius=12.0,
    )

    WARM_EDITORIAL = Theme(
        name="WarmEditorial",
        background=Color.hex("#FAF7F2"),
        card_bg=Color.hex("#FFFFFF"),
        card_stroke=Color.hex("#E6DFD5"),
        text_primary=Color.hex("#2C2420"),
        text_secondary=Color.hex("#786C65"),
        accent=Color.hex("#D9532F"),
        accent_secondary=Color.hex("#3B6E8C"),
        font_heading="Playfair Display",
        font_body="Georgia",
        corner_radius=8.0,
    )
