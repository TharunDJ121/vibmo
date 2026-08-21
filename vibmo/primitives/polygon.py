"""
Polygons, Stars, Lines, and Arrows.
"""

from __future__ import annotations
import math
from typing import Any, List, Optional, Sequence, Tuple, Union
from vibmo.core.vector import Vector2D
from vibmo.core.color import Color, colors
from vibmo.core.signal import Signal
from vibmo.scene.node import Node


class Polygon(Node):
    """Arbitrary 2D polygon defined by vertices."""

    def __init__(
        self,
        points: Sequence[Union[Vector2D, Sequence[float]]],
        fill: Optional[Union[Color, str]] = colors.WHITE,
        stroke: Optional[Union[Color, str]] = None,
        stroke_width: float = 1.0,
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)
        self.points = [Vector2D.from_any(p) for p in points]
        resolved_fill = Color.from_any(fill) if isinstance(fill, (str, Color)) else fill
        self.fill = Signal(resolved_fill, f"{self.name}.fill")
        resolved_stroke = Color.from_any(stroke) if isinstance(stroke, (str, Color)) else stroke
        self.stroke = Signal(resolved_stroke, f"{self.name}.stroke")
        self.stroke_width = Signal(float(stroke_width), f"{self.name}.stroke_width")

    def local_bounds(self, time: float = 0.0) -> Tuple[float, float, float, float]:
        if not self.points:
            return (0.0, 0.0, 0.0, 0.0)
        xs = [p.x for p in self.points]
        ys = [p.y for p in self.points]
        min_x, max_x = min(xs), max(xs)
        min_y, max_y = min(ys), max(ys)
        return (min_x, min_y, max_x - min_x, max_y - min_y)

    def draw(self, ctx: Any, time: float = 0.0) -> None:
        if len(self.points) < 2:
            return

        ctx.new_path()
        ctx.move_to(self.points[0].x, self.points[0].y)
        for p in self.points[1:]:
            ctx.line_to(p.x, p.y)
        ctx.close_path()

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

        stroke_val = self.stroke.get(time)
        sw = self.stroke_width.get(time)
        if stroke_val is not None and sw > 0:
            ctx.save()
            if isinstance(stroke_val, Color):
                ctx.set_source_rgba(stroke_val.r, stroke_val.g, stroke_val.b, stroke_val.a)
            ctx.set_line_width(sw)
            ctx.stroke()
            ctx.restore()


class Star(Polygon):
    """N-pointed star vector shape."""

    def __init__(
        self,
        points: int = 5,
        outer_radius: float = 50.0,
        inner_radius: float = 25.0,
        fill: Optional[Union[Color, str]] = colors.AMBER,
        stroke: Optional[Union[Color, str]] = None,
        stroke_width: float = 1.0,
        **kwargs: Any,
    ) -> None:
        verts: List[Vector2D] = []
        step = math.pi / points
        angle = -math.pi * 0.5
        for i in range(points * 2):
            r = outer_radius if (i % 2 == 0) else inner_radius
            verts.append(Vector2D(r * math.cos(angle), r * math.sin(angle)))
            angle += step
        super().__init__(points=verts, fill=fill, stroke=stroke, stroke_width=stroke_width, **kwargs)


class Line(Node):
    """A straight line segment between start and end."""

    def __init__(
        self,
        start: Union[Vector2D, Sequence[float]] = (0.0, 0.0),
        end: Union[Vector2D, Sequence[float]] = (100.0, 0.0),
        stroke: Optional[Union[Color, str]] = colors.WHITE,
        stroke_width: float = 2.0,
        cap: str = "round",
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)
        self.start = Signal(Vector2D.from_any(start), f"{self.name}.start")
        self.end = Signal(Vector2D.from_any(end), f"{self.name}.end")
        resolved_stroke = Color.from_any(stroke) if isinstance(stroke, (str, Color)) else stroke
        self.stroke = Signal(resolved_stroke, f"{self.name}.stroke")
        self.stroke_width = Signal(float(stroke_width), f"{self.name}.stroke_width")
        self.cap = cap

    def local_bounds(self, time: float = 0.0) -> Tuple[float, float, float, float]:
        p1 = self.start.get(time)
        p2 = self.end.get(time)
        min_x, max_x = min(p1.x, p2.x), max(p1.x, p2.x)
        min_y, max_y = min(p1.y, p2.y), max(p1.y, p2.y)
        sw = self.stroke_width.get(time)
        return (min_x - sw, min_y - sw, (max_x - min_x) + sw * 2, (max_y - min_y) + sw * 2)

    def draw(self, ctx: Any, time: float = 0.0) -> None:
        p1 = self.start.get(time)
        p2 = self.end.get(time)
        stroke_val = self.stroke.get(time)
        sw = self.stroke_width.get(time)
        if stroke_val is None or sw <= 0:
            return

        import cairo
        ctx.save()
        ctx.new_path()
        ctx.move_to(p1.x, p1.y)
        ctx.line_to(p2.x, p2.y)
        ctx.set_source_rgba(stroke_val.r, stroke_val.g, stroke_val.b, stroke_val.a)
        ctx.set_line_width(sw)
        if self.cap == "round":
            ctx.set_line_cap(cairo.LINE_CAP_ROUND)
        elif self.cap == "square":
            ctx.set_line_cap(cairo.LINE_CAP_SQUARE)
        else:
            ctx.set_line_cap(cairo.LINE_CAP_BUTT)
        ctx.stroke()
        ctx.restore()
