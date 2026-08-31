"""
Dark Starfield Stage & Horizon Glow for Vibmo.
Inspired by video-production-skills dark-saas-magic-video (Presenton style).
Provides a pure black spatial stage with twinkling star dust particles and a bottom purple horizon glow.
"""

from __future__ import annotations
import math
import random
from typing import List, Optional, Tuple, Dict, Any, Union
import cairo
import numpy as np

from vibmo.core.color import Color, colors
from vibmo.core.signal import Signal
from vibmo.scene.node import Node


class DarkStarfieldStage(Node):
    """
    Presenton-style Dark Spatial Stage:
    Deep space black background with subtle drifting star particles and a smooth bottom purple horizon glow.
    """

    def __init__(
        self,
        particle_count: int = 65,
        horizon_color: Union[Color, str] = "#7c3aed",
        horizon_intensity: float = 0.45,
        horizon_y: float = 1080.0,
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)
        self.particle_count = particle_count
        self.horizon_color = Color.from_any(horizon_color)
        self.horizon_intensity = Signal(horizon_intensity, f"{self.id}.intensity")
        self.horizon_y = horizon_y

        # Deterministic star distribution
        rng = random.Random(42)
        self.stars = [
            (rng.uniform(0, 1920), rng.uniform(0, 1080), rng.uniform(0.8, 2.2), rng.uniform(0.1, 0.8), rng.uniform(0.5, 2.5))
            for _ in range(particle_count)
        ]

    def draw(self, ctx: cairo.Context, time: float = 0.0) -> None:
        inte = self.horizon_intensity.evaluate_at(time)

        ctx.save()

        # 1. Base Pitch Black Canvas
        ctx.set_source_rgb(0.02, 0.02, 0.04)
        ctx.paint()

        # 2. Bottom Purple / Violet Horizon Ambient Glow
        if inte > 0.001:
            pat = cairo.RadialGradient(960.0, self.horizon_y + 100.0, 50.0, 960.0, self.horizon_y + 100.0, 750.0)
            pat.add_color_stop_rgba(
                0.0,
                self.horizon_color.r,
                self.horizon_color.g,
                self.horizon_color.b,
                0.45 * inte,
            )
            pat.add_color_stop_rgba(
                0.45,
                self.horizon_color.r * 0.4,
                self.horizon_color.g * 0.4,
                self.horizon_color.b * 0.4,
                0.15 * inte,
            )
            pat.add_color_stop_rgba(1.0, 0.0, 0.0, 0.0, 0.0)

            ctx.save()
            ctx.translate(960.0, self.horizon_y + 100.0)
            ctx.scale(1.0, 0.4)
            ctx.translate(-960.0, -(self.horizon_y + 100.0))
            ctx.set_source(pat)
            ctx.paint()
            ctx.restore()

        # 3. Drifting & Twinkling Star Dust Particles
        for x0, y0, radius, base_alpha, speed in self.stars:
            twinkle = 0.5 + 0.5 * math.sin(time * speed * 2.0 + x0)
            cur_alpha = min(1.0, base_alpha * (0.6 + 0.4 * twinkle))
            cur_y = (y0 - time * speed * 8.0) % 1080.0

            ctx.set_source_rgba(0.9, 0.95, 1.0, cur_alpha)
            ctx.arc(x0, cur_y, radius, 0, 2 * math.pi)
            ctx.fill()

        ctx.restore()
