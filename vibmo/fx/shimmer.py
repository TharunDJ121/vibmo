"""
Shimmer & Specular Light Reflection engine.
Provides continuous or one-shot radiant diagonal specular sweeps across UI cards, buttons, badges, and text.
"""

from __future__ import annotations
import math
from typing import Any, Optional, Tuple, Union
import cairo

from vibmo.core.color import Color, colors
from vibmo.core.signal import Signal, AnimationAction
from vibmo.core.easing import Ease, EasingFunc
from vibmo.scene.node import Node


class Shimmer(Node):
    """
    Glossy diagonal specular sheen sweep over a rectangular or rounded-rect region.
    """

    def __init__(
        self,
        width: float = 400.0,
        height: float = 120.0,
        corner_radius: float = 24.0,
        speed: float = 1.0,
        intensity: float = 0.40,
        sheen_width: float = 120.0,
        color: Union[Color, str] = colors.WHITE,
        angle_rad: float = 0.45,
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)
        self.w = float(width)
        self.h = float(height)
        self.corner_radius = float(corner_radius)
        self.speed = float(speed)
        self.intensity = float(intensity)
        self.sheen_width = float(sheen_width)
        self.color = Color.from_any(color)
        self.angle_rad = float(angle_rad)

    def local_bounds(self, time: float = 0.0) -> Tuple[float, float, float, float]:
        return (0.0, 0.0, self.w, self.h)

    def draw(self, ctx: Any, time: float = 0.0) -> None:
        w, h, r = self.w, self.h, self.corner_radius
        ctx.save()

        # Clip to rounded bounding box
        self._rounded_rect(ctx, 0, 0, w, h, r)
        ctx.clip()

        # Calculate sweep progress (cycles smoothly across width)
        total_span = w + h * math.tan(self.angle_rad) + self.sheen_width * 2
        progress = (time * self.speed) % 2.2  # 2.2s repeat period with pause
        sweep_x = -self.sheen_width + progress * (total_span / 1.4)

        # Diagonal linear gradient
        dx = math.cos(self.angle_rad) * self.sheen_width
        dy = math.sin(self.angle_rad) * self.sheen_width
        pat = cairo.LinearGradient(sweep_x - dx, 0, sweep_x + dx, h)

        c = self.color
        pat.add_color_stop_rgba(0.0, c.r, c.g, c.b, 0.0)
        pat.add_color_stop_rgba(0.5, c.r, c.g, c.b, self.intensity)
        pat.add_color_stop_rgba(1.0, c.r, c.g, c.b, 0.0)

        ctx.rectangle(0, 0, w, h)
        ctx.set_source(pat)
        ctx.fill()

        ctx.restore()

    def _rounded_rect(self, ctx: Any, x: float, y: float, w: float, h: float, r: float) -> None:
        ctx.new_path()
        ctx.arc(x + w - r, y + r, r, -math.pi * 0.5, 0)
        ctx.arc(x + w - r, y + h - r, r, 0, math.pi * 0.5)
        ctx.arc(x + r, y + h - r, r, math.pi * 0.5, math.pi)
        ctx.arc(x + r, y + r, r, math.pi, math.pi * 1.5)
        ctx.close_path()
