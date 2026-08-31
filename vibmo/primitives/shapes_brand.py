"""
Brand and Tech Icon Primitives: Anthropic Claude Asterisk, Open AI, Apple, etc.
"""

from __future__ import annotations
import math
from typing import Any, Optional, Tuple, Union
import cairo

from vibmo.core.color import Color, colors
from vibmo.core.vector import Vector2D
from vibmo.scene.node import Node


class AnthropicAsterisk(Node):
    """
    Procedural Anthropic terracotta radiating star/asterisk mark.
    Draws 12 rounded pill-shaped spokes radiating symmetrically from the center.
    """

    def __init__(
        self,
        radius: float = 36.0,
        spokes: int = 12,
        spoke_width: float = 6.0,
        inner_radius: float = 8.0,
        color: Optional[Union[Color, str]] = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)
        self.radius_val = float(radius)
        self.spokes = int(spokes)
        self.spoke_width = float(spoke_width)
        self.inner_radius = float(inner_radius)
        # Canonical Anthropic Terracotta color: #d97757 / #cc6b49
        self.color = Color.from_any(color) if color else Color.from_hex("#d97757")

    def local_bounds(self, time: float = 0.0) -> Tuple[float, float, float, float]:
        r = self.radius_val
        return (-r, -r, r * 2, r * 2)

    def draw(self, ctx: Any, time: float = 0.0) -> None:
        ctx.save()
        ctx.set_source_rgba(self.color.r, self.color.g, self.color.b, self.color.a)
        
        r_outer = self.radius_val
        r_inner = self.inner_radius
        w = self.spoke_width
        half_w = w * 0.5

        for i in range(self.spokes):
            angle = (i * 2.0 * math.pi) / self.spokes
            ctx.save()
            ctx.rotate(angle)
            
            # Draw rounded spoke from inner radius to outer radius
            # Rectangle with rounded caps:
            y_start = r_inner
            y_end = r_outer
            spoke_len = y_end - y_start
            
            # Capsule path along +Y axis
            ctx.new_path()
            ctx.arc(0, y_end - half_w, half_w, 0, math.pi)
            ctx.line_to(-half_w, y_start + half_w)
            ctx.arc(0, y_start + half_w, half_w, math.pi, math.pi * 2)
            ctx.line_to(half_w, y_end - half_w)
            ctx.close_path()
            ctx.fill()
            
            ctx.restore()

        ctx.restore()


AnthropicLogo = AnthropicAsterisk
