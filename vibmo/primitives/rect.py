"""
Rectangles, Rounded Rectangles, Borders, Shadows, and Gradients.
"""

from __future__ import annotations
import math
from typing import Any, Dict, Optional, Sequence, Tuple, Union
from vibmo.core.vector import Vector2D
from vibmo.core.color import Color, LinearGradient, RadialGradient, colors
from vibmo.core.signal import Signal
from vibmo.scene.node import Node


class Rect(Node):
    """A rectangular vector node supporting rounded corners, gradient fills, and drop shadows."""

    def __init__(
        self,
        width: float = 100.0,
        height: float = 100.0,
        corner_radius: Union[float, Sequence[float]] = 0.0,
        fill: Optional[Union[Color, LinearGradient, RadialGradient, str]] = colors.WHITE,
        stroke: Optional[Union[Color, str]] = None,
        stroke_width: float = 1.0,
        shadow: Optional[Dict[str, Any]] = None,
        glow: Optional[Dict[str, Any]] = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)
        self.width = Signal(float(width), f"{self.name}.width")
        self.height = Signal(float(height), f"{self.name}.height")
        self.corner_radius = Signal(corner_radius, f"{self.name}.corner_radius")
        
        # Color & Style signals
        resolved_fill = Color.from_any(fill) if isinstance(fill, (str, Color)) else fill
        self.fill = Signal(resolved_fill, f"{self.name}.fill")
        
        resolved_stroke = Color.from_any(stroke) if isinstance(stroke, (str, Color)) else stroke
        self.stroke = Signal(resolved_stroke, f"{self.name}.stroke")
        self.stroke_width = Signal(float(stroke_width), f"{self.name}.stroke_width")

        self.shadow = shadow
        self.glow = glow

    def local_bounds(self, time: float = 0.0) -> Tuple[float, float, float, float]:
        w = max(0.0, self.width.get(time))
        h = max(0.0, self.height.get(time))
        return (0.0, 0.0, w, h)

    def _build_path(self, ctx: Any, time: float = 0.0) -> None:
        w = max(0.0, self.width.get(time))
        h = max(0.0, self.height.get(time))
        if w <= 0 or h <= 0:
            return

        cr = self.corner_radius.get(time)
        if isinstance(cr, (int, float)):
            r_tl = r_tr = r_br = r_bl = max(0.0, min(min(w, h) * 0.5, float(cr)))
        elif isinstance(cr, (tuple, list)) and len(cr) == 4:
            r_tl, r_tr, r_br, r_bl = cr
        else:
            r_tl = r_tr = r_br = r_bl = 0.0

        ctx.new_path()
        if r_tl == 0 and r_tr == 0 and r_br == 0 and r_bl == 0:
            ctx.rectangle(0, 0, w, h)
        else:
            # Rounded rectangle path
            deg = math.pi / 180.0
            ctx.new_sub_path()
            ctx.arc(w - r_tr, r_tr, r_tr, -90 * deg, 0 * deg)
            ctx.arc(w - r_br, h - r_br, r_br, 0 * deg, 90 * deg)
            ctx.arc(r_bl, h - r_bl, r_bl, 90 * deg, 180 * deg)
            ctx.arc(r_tl, r_tl, r_tl, 180 * deg, 270 * deg)
            ctx.close_path()

    def draw(self, ctx: Any, time: float = 0.0) -> None:
        self._build_path(ctx, time)
        
        w = max(0.0, self.width.get(time))
        h = max(0.0, self.height.get(time))

        # Handle Fill
        fill_val = self.fill.get(time)
        if fill_val is not None:
            ctx.save()
            if isinstance(fill_val, Color):
                ctx.set_source_rgba(fill_val.r, fill_val.g, fill_val.b, fill_val.a)
            elif isinstance(fill_val, LinearGradient):
                import cairo
                pat = cairo.LinearGradient(
                    fill_val.start[0] * w, fill_val.start[1] * h,
                    fill_val.end[0] * w, fill_val.end[1] * h
                )
                for stop in fill_val.stops:
                    pat.add_color_stop_rgba(stop.offset, stop.color.r, stop.color.g, stop.color.b, stop.color.a)
                ctx.set_source(pat)
            elif isinstance(fill_val, RadialGradient):
                import cairo
                cx = fill_val.center[0] * w
                cy = fill_val.center[1] * h
                r = fill_val.radius * max(w, h)
                pat = cairo.RadialGradient(cx, cy, 0, cx, cy, r)
                for stop in fill_val.stops:
                    pat.add_color_stop_rgba(stop.offset, stop.color.r, stop.color.g, stop.color.b, stop.color.a)
                ctx.set_source(pat)
            
            if self.stroke.get(time) is not None:
                ctx.fill_preserve()
            else:
                ctx.fill()
            ctx.restore()

        # Handle Stroke
        stroke_val = self.stroke.get(time)
        sw = self.stroke_width.get(time)
        if stroke_val is not None and sw > 0:
            ctx.save()
            if isinstance(stroke_val, Color):
                ctx.set_source_rgba(stroke_val.r, stroke_val.g, stroke_val.b, stroke_val.a)
            elif isinstance(stroke_val, LinearGradient):
                import cairo
                pat = cairo.LinearGradient(
                    stroke_val.start[0] * w, stroke_val.start[1] * h,
                    stroke_val.end[0] * w, stroke_val.end[1] * h
                )
                for stop in stroke_val.stops:
                    pat.add_color_stop_rgba(stop.offset, stop.color.r, stop.color.g, stop.color.b, stop.color.a)
                ctx.set_source(pat)
            elif isinstance(stroke_val, RadialGradient):
                import cairo
                cx = stroke_val.center[0] * w
                cy = stroke_val.center[1] * h
                r = stroke_val.radius * max(w, h)
                pat = cairo.RadialGradient(cx, cy, 0, cx, cy, r)
                for stop in stroke_val.stops:
                    pat.add_color_stop_rgba(stop.offset, stop.color.r, stop.color.g, stop.color.b, stop.color.a)
                ctx.set_source(pat)
            ctx.set_line_width(sw)
            ctx.stroke()
            ctx.restore()


class RoundedRect(Rect):
    """Alias for Rect with a non-zero default corner radius."""
    def __init__(self, corner_radius: float = 16.0, **kwargs: Any) -> None:
        super().__init__(corner_radius=corner_radius, **kwargs)
