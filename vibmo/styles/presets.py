"""
Aesthetic Style Presets and Vibe Design System for Vibmo.
Provides instant 1-line production aesthetics: Linear Dark, Apple Keynote, Cyberpunk, Fintech, Vaporwave, etc.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Callable, List, Optional, Union
from vibmo.core.color import Color, colors


@dataclass
class StylePreset:
    """Design System theme defining lighting, color harmonies, materials, and typography."""
    name: str
    background: Color
    accent: Color
    secondary_accent: Color
    text_primary: Color
    text_muted: Color
    card_fill: Color
    card_stroke: Color
    card_corner_radius: float = 20.0
    font_family: str = "Inter"
    post_fx: List[Any] = field(default_factory=list)
    glow_color: Optional[Color] = None
    vignette_intensity: float = 0.25
    grain_amount: float = 0.02


class Styles:
    """Curated collection of world-class motion design aesthetics."""

    LINEAR_DARK = StylePreset(
        name="Linear Dark",
        background=Color.hex("#030712"),
        accent=Color.hex("#6366f1"),
        secondary_accent=Color.hex("#38bdf8"),
        text_primary=Color.hex("#f8fafc"),
        text_muted=Color.hex("#94a3b8"),
        card_fill=Color.rgba(15, 23, 42, 0.65),
        card_stroke=Color.rgba(99, 102, 241, 0.25),
        card_corner_radius=20.0,
        font_family="Inter",
        glow_color=Color.rgba(99, 102, 241, 0.3),
        vignette_intensity=0.25,
        grain_amount=0.015,
    )

    APPLE_KEYNOTE = StylePreset(
        name="Apple Keynote",
        background=Color.hex("#000000"),
        accent=Color.hex("#0071e3"),
        secondary_accent=Color.hex("#2997ff"),
        text_primary=Color.hex("#f5f5f7"),
        text_muted=Color.hex("#86868b"),
        card_fill=Color.rgba(255, 255, 255, 0.08),
        card_stroke=Color.rgba(255, 255, 255, 0.18),
        card_corner_radius=28.0,
        font_family="SF Pro Display",
        glow_color=Color.rgba(41, 151, 255, 0.2),
        vignette_intensity=0.2,
        grain_amount=0.01,
    )

    CYBERPUNK = StylePreset(
        name="Cyberpunk Neon",
        background=Color.hex("#05050d"),
        accent=Color.hex("#00f0ff"),
        secondary_accent=Color.hex("#ff003c"),
        text_primary=Color.hex("#fcee0a"),
        text_muted=Color.hex("#71717a"),
        card_fill=Color.rgba(10, 10, 25, 0.85),
        card_stroke=Color.rgba(0, 240, 255, 0.45),
        card_corner_radius=12.0,
        font_family="Space Grotesk",
        glow_color=Color.rgba(0, 240, 255, 0.5),
        vignette_intensity=0.35,
        grain_amount=0.035,
    )

    FINTECH_EMERALD = StylePreset(
        name="Fintech Emerald",
        background=Color.hex("#021a12"),
        accent=Color.hex("#10b981"),
        secondary_accent=Color.hex("#34d399"),
        text_primary=Color.hex("#ecfdf5"),
        text_muted=Color.hex("#6ee7b7"),
        card_fill=Color.rgba(4, 47, 34, 0.7),
        card_stroke=Color.rgba(16, 185, 129, 0.35),
        card_corner_radius=22.0,
        font_family="Plus Jakarta Sans",
        glow_color=Color.rgba(16, 185, 129, 0.35),
        vignette_intensity=0.22,
        grain_amount=0.015,
    )

    RETRO_VAPORWAVE = StylePreset(
        name="Retro Vaporwave",
        background=Color.hex("#1a0933"),
        accent=Color.hex("#ff71ce"),
        secondary_accent=Color.hex("#01cdfe"),
        text_primary=Color.hex("#fffb96"),
        text_muted=Color.hex("#b967ff"),
        card_fill=Color.rgba(45, 15, 75, 0.75),
        card_stroke=Color.rgba(255, 113, 206, 0.4),
        card_corner_radius=16.0,
        font_family="VT323",
        glow_color=Color.rgba(255, 113, 206, 0.4),
        vignette_intensity=0.3,
        grain_amount=0.04,
    )

    MINIMALIST_LIGHT = StylePreset(
        name="Minimalist Light",
        background=Color.hex("#f8fafc"),
        accent=Color.hex("#0f172a"),
        secondary_accent=Color.hex("#334155"),
        text_primary=Color.hex("#0f172a"),
        text_muted=Color.hex("#64748b"),
        card_fill=Color.rgba(255, 255, 255, 0.95),
        card_stroke=Color.rgba(15, 23, 42, 0.1),
        card_corner_radius=18.0,
        font_family="Inter",
        glow_color=None,
        vignette_intensity=0.0,
        grain_amount=0.0,
    )
