"""
Arbitrary SVG Path rendering, length calculation, and Trim Path stroke animations.
"""

from __future__ import annotations
import math
from typing import Any, List, Optional, Tuple, Union
import svgelements
from vibmo.core.vector import Vector2D
from vibmo.core.color import Color, colors
from vibmo.core.signal import Signal
from vibmo.scene.node import Node


class Path(Node):
    """
    Renders SVG Path strings (M, L, C, S, Q, A, Z) with trim path animation support.
    """

    def __init__(
        self,
        d: str = "",
        fill: Optional[Union[Color, str]] = None,
        stroke: Optional[Union[Color, str]] = colors.WHITE,
        stroke_width: float = 2.0,
        trim_start: float = 0.0,
        trim_end: float = 1.0,
        trim_offset: float = 0.0,
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)
        self.d = d
        self._svg_path = svgelements.Path(d) if d else svgelements.Path()
        
        resolved_fill = Color.from_any(fill) if isinstance(fill, (str, Color)) else fill
        self.fill = Signal(resolved_fill, f"{self.name}.fill")
        resolved_stroke = Color.from_any(stroke) if isinstance(stroke, (str, Color)) else stroke
        self.stroke = Signal(resolved_stroke, f"{self.name}.stroke")
        self.stroke_width = Signal(float(stroke_width), f"{self.name}.stroke_width")

        self.trim_start = Signal(float(trim_start), f"{self.name}.trim_start")
        self.trim_end = Signal(float(trim_end), f"{self.name}.trim_end")
        self.trim_offset = Signal(float(trim_offset), f"{self.name}.trim_offset")

    @classmethod
    def from_svg_d(cls, d: str, **kwargs: Any) -> Path:
        return cls(d=d, **kwargs)

    @property
    def total_length(self) -> float:
        try:
            return float(self._svg_path.length())
        except Exception:
            return 100.0

    def local_bounds(self, time: float = 0.0) -> Tuple[float, float, float, float]:
        try:
            bbox = self._svg_path.bbox()
            if bbox:
                return (bbox[0], bbox[1], bbox[2] - bbox[0], bbox[3] - bbox[1])
        except Exception:
            pass
        return (0.0, 0.0, 100.0, 100.0)

    def draw(self, ctx: Any, time: float = 0.0) -> None:
        if not self.d:
            return

        ctx.new_path()
        for seg in self._svg_path:
            if isinstance(seg, svgelements.Move):
                ctx.move_to(seg.end.x, seg.end.y)
            elif isinstance(seg, svgelements.Line):
                ctx.line_to(seg.end.x, seg.end.y)
            elif isinstance(seg, svgelements.CubicBezier):
                ctx.curve_to(seg.control1.x, seg.control1.y, seg.control2.x, seg.control2.y, seg.end.x, seg.end.y)
            elif isinstance(seg, svgelements.QuadraticBezier):
                # Convert quad to cubic
                p0 = seg.start
                p1 = seg.control
                p2 = seg.end
                c1x = p0.x + 2.0 / 3.0 * (p1.x - p0.x)
                c1y = p0.y + 2.0 / 3.0 * (p1.y - p0.y)
                c2x = p2.x + 2.0 / 3.0 * (p1.x - p2.x)
                c2y = p2.y + 2.0 / 3.0 * (p1.y - p2.y)
                ctx.curve_to(c1x, c1y, c2x, c2y, p2.x, p2.y)
            elif isinstance(seg, svgelements.Close):
                ctx.close_path()

        # Handle Fill
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

        # Handle Stroke & Trim Path
        stroke_val = self.stroke.get(time)
        sw = self.stroke_width.get(time)
        if stroke_val is not None and sw > 0:
            ctx.save()
            if isinstance(stroke_val, Color):
                ctx.set_source_rgba(stroke_val.r, stroke_val.g, stroke_val.b, stroke_val.a)
            ctx.set_line_width(sw)

            t_start = max(0.0, min(1.0, self.trim_start.get(time)))
            t_end = max(0.0, min(1.0, self.trim_end.get(time)))
            t_offset = self.trim_offset.get(time)

            if t_start > 0.0 or t_end < 1.0 or t_offset != 0.0:
                length = max(1.0, self.total_length)
                dash_len = max(0.0, (t_end - t_start) * length)
                gap_len = max(0.0, length - dash_len)
                offset = (t_start + t_offset) * length
                ctx.set_dash([dash_len, gap_len], -offset)

            ctx.stroke()
            ctx.restore()
