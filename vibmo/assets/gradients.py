"""
Curated high-vibe gradient presets and gradient generation utilities.
"""

from __future__ import annotations
import math
from typing import Any, Dict, List, Optional, Tuple, Union
from vibmo.core.color import Color, ColorStop, LinearGradient, RadialGradient, colors


# Curated high-vibe gradient stops presets
GRADIENT_PRESETS: Dict[str, List[Tuple[float, str]]] = {
    "sunset": [
        (0.0, "#ff5e62"),
        (1.0, "#ff9966"),
    ],
    "aurora": [
        (0.0, "#00c6ff"),
        (0.5, "#0072ff"),
        (1.0, "#10b981"),
    ],
    "cyberpunk": [
        (0.0, "#f72585"),
        (0.5, "#7209b7"),
        (1.0, "#4cc9f0"),
    ],
    "cosmic": [
        (0.0, "#11002c"),
        (0.5, "#3b0764"),
        (1.0, "#06b6d4"),
    ],
    "emerald": [
        (0.0, "#059669"),
        (1.0, "#10b981"),
    ],
    "neon": [
        (0.0, "#00f5d4"),
        (0.5, "#7b2cbf"),
        (1.0, "#f72585"),
    ],
    "velvet": [
        (0.0, "#4a0e4e"),
        (1.0, "#0d0221"),
    ],
    "cotton_candy": [
        (0.0, "#ffafbd"),
        (1.0, "#ffc3a0"),
    ],
    "obsidian": [
        (0.0, "#1e293b"),
        (1.0, "#020617"),
    ],
    "solar_flare": [
        (0.0, "#f59e0b"),
        (0.5, "#ef4444"),
        (1.0, "#7c3aed"),
    ],
}


class Gradients:
    """
    Factory for curated high-vibe gradient backgrounds and fills.
    """

    @classmethod
    def get(cls, name: str, angle: float = 45.0) -> LinearGradient:
        """Get a curated preset gradient by name."""
        stops_def = GRADIENT_PRESETS.get(name.lower().replace("-", "_"), GRADIENT_PRESETS["cyberpunk"])
        rad = math.radians(angle)
        sx = 0.5 - math.cos(rad) * 0.5
        sy = 0.5 - math.sin(rad) * 0.5
        ex = 0.5 + math.cos(rad) * 0.5
        ey = 0.5 + math.sin(rad) * 0.5
        return LinearGradient(start=(sx, sy), end=(ex, ey), stops=stops_def)

    @classmethod
    def linear(
        cls,
        colors_list: Sequence[Union[Color, str]],
        angle: float = 45.0,
    ) -> LinearGradient:
        """Create a custom multi-stop linear gradient along an angle."""
        n = len(colors_list)
        if n == 0:
            return cls.get("cyberpunk")
        stops = []
        for i, c in enumerate(colors_list):
            offset = float(i) / max(1, n - 1)
            stops.append((offset, c))
        
        rad = math.radians(angle)
        sx = 0.5 - math.cos(rad) * 0.5
        sy = 0.5 - math.sin(rad) * 0.5
        ex = 0.5 + math.cos(rad) * 0.5
        ey = 0.5 + math.sin(rad) * 0.5
        return LinearGradient(start=(sx, sy), end=(ex, ey), stops=stops)

    @classmethod
    def radial(
        cls,
        colors_list: Sequence[Union[Color, str]],
        center: Tuple[float, float] = (0.5, 0.5),
        radius: float = 0.5,
    ) -> RadialGradient:
        """Create a custom multi-stop radial gradient."""
        n = len(colors_list)
        stops = []
        for i, c in enumerate(colors_list):
            offset = float(i) / max(1, n - 1)
            stops.append((offset, c))
        return RadialGradient(center=center, radius=radius, stops=stops)


# Presets
Gradients.SUNSET = Gradients.get("sunset")
Gradients.AURORA = Gradients.get("aurora")
Gradients.CYBERPUNK = Gradients.get("cyberpunk")
Gradients.COSMIC = Gradients.get("cosmic")
Gradients.EMERALD = Gradients.get("emerald")
Gradients.NEON = Gradients.get("neon")
Gradients.VELVET = Gradients.get("velvet")
Gradients.COTTON_CANDY = Gradients.get("cotton_candy")
Gradients.OBSIDIAN = Gradients.get("obsidian")
Gradients.SOLAR_FLARE = Gradients.get("solar_flare")
