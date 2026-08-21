"""
Coordinate Systems, Function Plotting, Vector Drawing, and Mathematical Graphs.
"""

from __future__ import annotations
import math
from typing import Any, Callable, List, Optional, Sequence, Tuple, Union
import cairo
from vibmo.core.vector import Vector2D
from vibmo.core.color import Color, colors
from vibmo.core.signal import Signal, AnimationAction
from vibmo.core.easing import Ease, EasingFunc
from vibmo.scene.node import Node
from vibmo.primitives.path import Path
from vibmo.primitives.circle import Circle
from vibmo.primitives.polygon import Line
from vibmo.typography.text import Text


class Axes(Node):
    """
    Cartesian 2D coordinate system for mathematical function graphing and vector field animations.
    """

    def __init__(
        self,
        x_range: Tuple[float, float] = (-5.0, 5.0),
        y_range: Tuple[float, float] = (-3.0, 3.0),
        width: float = 900.0,
        height: float = 550.0,
        grid: bool = True,
        grid_step: float = 1.0,
        axis_color: Optional[Union[Color, str]] = colors.SLATE_400,
        grid_color: Optional[Union[Color, str]] = None,
        stroke_width: float = 2.0,
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)
        self.x_min, self.x_max = x_range
        self.y_min, self.y_max = y_range
        self.width = float(width)
        self.height = float(height)
        self.grid = grid
        self.grid_step = grid_step
        
        self.axis_color = Color.from_any(axis_color) if axis_color else colors.SLATE_400
        self.grid_color = Color.from_any(grid_color) if grid_color else Color.WHITE.with_alpha(0.06)
        self.stroke_width = float(stroke_width)

    def c2p(self, x: float, y: float) -> Vector2D:
        """Converts math coordinates (x, y) to pixel coordinates (px, py)."""
        norm_x = (x - self.x_min) / (self.x_max - self.x_min)
        norm_y = (y - self.y_min) / (self.y_max - self.y_min)
        # Flip Y so positive math Y is upward on screen
        px = norm_x * self.width
        py = (1.0 - norm_y) * self.height
        return Vector2D(px, py)

    def p2c(self, px: float, py: float) -> Tuple[float, float]:
        """Converts pixel coordinates to math coordinates."""
        norm_x = px / self.width
        norm_y = 1.0 - (py / self.height)
        x = self.x_min + norm_x * (self.x_max - self.x_min)
        y = self.y_min + norm_y * (self.y_max - self.y_min)
        return (x, y)

    def local_bounds(self, time: float = 0.0) -> Tuple[float, float, float, float]:
        return (0.0, 0.0, self.width, self.height)

    def draw(self, ctx: Any, time: float = 0.0) -> None:
        ctx.save()

        # 1. Draw Grid Lines
        if self.grid:
            ctx.set_source_rgba(self.grid_color.r, self.grid_color.g, self.grid_color.b, self.grid_color.a)
            ctx.set_line_width(1.0)

            # Vertical grid lines
            curr_x = math.ceil(self.x_min / self.grid_step) * self.grid_step
            while curr_x <= self.x_max:
                p_top = self.c2p(curr_x, self.y_max)
                p_bot = self.c2p(curr_x, self.y_min)
                ctx.move_to(p_top.x, p_top.y)
                ctx.line_to(p_bot.x, p_bot.y)
                curr_x += self.grid_step

            # Horizontal grid lines
            curr_y = math.ceil(self.y_min / self.grid_step) * self.grid_step
            while curr_y <= self.y_max:
                p_left = self.c2p(self.x_min, curr_y)
                p_right = self.c2p(self.x_max, curr_y)
                ctx.move_to(p_left.x, p_left.y)
                ctx.line_to(p_right.x, p_right.y)
                curr_y += self.grid_step

            ctx.stroke()

        # 2. Draw Main X and Y Axes
        ctx.set_source_rgba(self.axis_color.r, self.axis_color.g, self.axis_color.b, self.axis_color.a)
        ctx.set_line_width(self.stroke_width)

        # X Axis (y=0)
        p_x0 = self.c2p(self.x_min, 0.0)
        p_x1 = self.c2p(self.x_max, 0.0)
        ctx.move_to(p_x0.x, p_x0.y)
        ctx.line_to(p_x1.x, p_x1.y)

        # Y Axis (x=0)
        p_y0 = self.c2p(0.0, self.y_min)
        p_y1 = self.c2p(0.0, self.y_max)
        ctx.move_to(p_y0.x, p_y0.y)
        ctx.line_to(p_y1.x, p_y1.y)

        ctx.stroke()
        ctx.restore()

    def plot(
        self,
        func: Callable[[float], float],
        color: Optional[Union[Color, str]] = colors.CYAN,
        stroke_width: float = 3.0,
        samples: int = 300,
        x_min: Optional[float] = None,
        x_max: Optional[float] = None,
        **kwargs: Any,
    ) -> Path:
        """Plots a mathematical function y = f(x) onto the axes returning an animatable Path."""
        sw = kwargs.get("line_width", stroke_width)
        start_x = x_min if x_min is not None else self.x_min
        end_x = x_max if x_max is not None else self.x_max

        xs = [start_x + i * (end_x - start_x) / (samples - 1) for i in range(samples)]
        pts: List[Vector2D] = []
        for x in xs:
            try:
                y = func(x)
                pts.append(self.c2p(x, y))
            except Exception:
                continue

        if not pts:
            return Path()

        # Build SVG path d string
        d_parts = [f"M {pts[0].x:.2f} {pts[0].y:.2f}"]
        for p in pts[1:]:
            d_parts.append(f"L {p.x:.2f} {p.y:.2f}")

        path_node = Path(
            d=" ".join(d_parts),
            fill=None,
            stroke=color,
            stroke_width=stroke_width,
            trim_end=1.0,
        )
        self.add(path_node)
        return path_node

    def draw_vector(
        self,
        target: Tuple[float, float],
        start: Tuple[float, float] = (0.0, 0.0),
        color: Optional[Union[Color, str]] = colors.AMBER,
        stroke_width: float = 3.0,
        label: str = "",
    ) -> Line:
        """Draws an animated vector with an arrow head."""
        p0 = self.c2p(start[0], start[1])
        p1 = self.c2p(target[0], target[1])
        line = Line(start=p0, end=p1, stroke=color, stroke_width=stroke_width)
        self.add(line)

        if label:
            lbl = Text(label, font_size=18.0, color=color, position=(p1.x + 10, p1.y - 10))
            self.add(lbl)

        return line
