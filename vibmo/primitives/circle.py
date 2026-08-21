"""
Circle and Ellipse vector primitives.
"""

from __future__ import annotations
import math
from typing import Any, Optional, Tuple, Union
from vibmo.core.color import Color, LinearGradient, RadialGradient, colors
from vibmo.core.signal import Signal
from vibmo.scene.node import Node


class Circle(Node):
    """Circular vector primitive centered at (0, 0) by default."""

    def __init__(
        self,
        radius: float = 50.0,
        fill: Optional[Union[Color, LinearGradient, RadialGradient, str]] = colors.WHITE,
        stroke: Optional[Union[Color, str]] = None,
        stroke_width: float = 1.0,
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)
        self.radius = Signal(float(radius), f"{self.name}.radius")
        
        resolved_fill = Color.from_any(fill) if isinstance(fill, (str, Color)) else fill
        self.fill = Signal(resolved_fill, f"{self.name}.fill")
        
        resolved_stroke = Color.from_any(stroke) if isinstance(stroke, (str, Color)) else stroke
        self.stroke = Signal(resolved_stroke, f"{self.name}.stroke")
        self.stroke_width = Signal(float(stroke_width), f"{self.name}.stroke_width")

    def local_bounds(self, time: float = 0.0) -> Tuple[float, float, float, float]:
        r = max(0.0, self.radius.get(time))
        return (-r, -r, 2.0 * r, 2.0 * r)

    def draw(self, ctx: Any, time: float = 0.0) -> None:
        r = max(0.0, self.radius.get(time))
        if r <= 0:
            return

        ctx.new_path()
        ctx.arc(0, 0, r, 0, 2.0 * math.pi)

        # Fill
        fill_val = self.fill.get(time)
        if fill_val is not None:
            ctx.save()
            if isinstance(fill_val, Color):
                ctx.set_source_rgba(fill_val.r, fill_val.g, fill_val.b, fill_val.a)
            if self.stroke.get(time) is not None:
                ctx.fill_preserve()
            else:
                ctx.fill()
            ctx.restore()

        # Stroke
        stroke_val = self.stroke.get(time)
        sw = self.stroke_width.get(time)
        if stroke_val is not None and sw > 0:
            ctx.save()
            if isinstance(stroke_val, Color):
                ctx.set_source_rgba(stroke_val.r, stroke_val.g, stroke_val.b, stroke_val.a)
            ctx.set_line_width(sw)
            ctx.stroke()
            ctx.restore()


class Ellipse(Node):
    """Ellipse vector primitive."""

    def __init__(
        self,
        radius_x: float = 60.0,
        radius_y: float = 40.0,
        fill: Optional[Union[Color, str]] = colors.WHITE,
        stroke: Optional[Union[Color, str]] = None,
        stroke_width: float = 1.0,
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)
        self.radius_x = Signal(float(radius_x), f"{self.name}.radius_x")
        self.radius_y = Signal(float(radius_y), f"{self.name}.radius_y")
        
        resolved_fill = Color.from_any(fill) if isinstance(fill, (str, Color)) else fill
        self.fill = Signal(resolved_fill, f"{self.name}.fill")
        
        resolved_stroke = Color.from_any(stroke) if isinstance(stroke, (str, Color)) else stroke
        self.stroke = Signal(resolved_stroke, f"{self.name}.stroke")
        self.stroke_width = Signal(float(stroke_width), f"{self.name}.stroke_width")

    def local_bounds(self, time: float = 0.0) -> Tuple[float, float, float, float]:
        rx = max(0.0, self.radius_x.get(time))
        ry = max(0.0, self.radius_y.get(time))
        return (-rx, -ry, 2.0 * rx, 2.0 * ry)

    def draw(self, ctx: Any, time: float = 0.0) -> None:
        rx = max(0.0, self.radius_x.get(time))
        ry = max(0.0, self.radius_y.get(time))
        if rx <= 0 or ry <= 0:
            return

        ctx.save()
        ctx.scale(rx, ry)
        ctx.new_path()
        ctx.arc(0, 0, 1.0, 0, 2.0 * math.pi)

        fill_val = self.fill.get(time)
        if fill_val is not None:
            if isinstance(fill_val, Color):
                ctx.set_source_rgba(fill_val.r, fill_val.g, fill_val.b, fill_val.a)
            if self.stroke.get(time) is not None:
                ctx.fill_preserve()
            else:
                ctx.fill()

        stroke_val = self.stroke.get(time)
        sw = self.stroke_width.get(time)
        if stroke_val is not None and sw > 0:
            ctx.restore()
            ctx.save()
            # Draw unscaled stroke
            ctx.scale(rx, ry)
            ctx.new_path()
            ctx.arc(0, 0, 1.0, 0, 2.0 * math.pi)
            if isinstance(stroke_val, Color):
                ctx.set_source_rgba(stroke_val.r, stroke_val.g, stroke_val.b, stroke_val.a)
            ctx.set_line_width(sw / max(rx, ry))
            ctx.stroke()
        ctx.restore()
