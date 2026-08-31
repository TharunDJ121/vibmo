import math
from typing import Any, List, Optional, Tuple, Union

from vibmo.scene.node import Node
from vibmo.core.signal import Signal, AnimationAction
from vibmo.core.color import Color, colors
from vibmo.core.vector import Vector2D
from vibmo.core.easing import Ease, EasingFunc
from vibmo.timeline.scheduler import ParallelGroup
from vibmo.layout.container import FlexContainer
from vibmo.typography.text import Text
from vibmo.primitives.rect import Rect

def compute_streamgraph_stack(data: List[List[float]], method: str = "wiggle") -> Tuple[List[List[float]], List[List[float]]]:
    """
    Computes bottom and top baselines for a stacked streamgraph.

    Args:
        data: A 2D list where data[i][j] is the value of layer i at time point j.
        method: "zero", "silhouette", or "wiggle" (Lee-Byron).

    Returns:
        (bottoms, tops) - two 2D lists of the same shape as data.
    """
    if not data or not data[0]:
        return [], []

    num_layers = len(data)
    num_points = len(data[0])
    bottoms = [[0.0] * num_points for _ in range(num_layers)]
    tops = [[0.0] * num_points for _ in range(num_layers)]

    g0 = [0.0] * num_points
    if method == "silhouette":
        for j in range(num_points):
            g0[j] = -0.5 * sum(data[i][j] for i in range(num_layers))
    elif method == "wiggle":
        g0[0] = -0.5 * sum(data[i][0] for i in range(num_layers))
        for j in range(1, num_points):
            total_y = sum(data[i][j] for i in range(num_layers))
            if total_y == 0:
                g0[j] = g0[j-1]
                continue
            derivative_sum = 0.0
            for i in range(num_layers):
                dy_i = data[i][j] - data[i][j-1]
                sum_dy_k = sum(data[k][j] - data[k][j-1] for k in range(i))
                derivative_sum += data[i][j] * (sum_dy_k + 0.5 * dy_i)
            g0_prime = -derivative_sum / total_y
            g0[j] = g0[j-1] + g0_prime

    for j in range(num_points):
        current_y = g0[j]
        for i in range(num_layers):
            bottoms[i][j] = current_y
            current_y += data[i][j]
            tops[i][j] = current_y

    return bottoms, tops

def compute_cubic_spline_controls(points: List[Tuple[float, float]], tension: float = 0.3) -> List[Tuple[float, float, float, float, float, float]]:
    """
    Computes control points for a cubic spline through points.
    Uses Cardinal Spline (tension parameter).
    Returns list of (c1x, c1y, c2x, c2y, p2x, p2y) for each segment.
    """
    segments = []
    if len(points) < 2:
        return segments

    for i in range(len(points) - 1):
        p0 = points[max(0, i - 1)]
        p1 = points[i]
        p2 = points[i + 1]
        p3 = points[min(len(points) - 1, i + 2)]

        # Tangents
        t1x = (p2[0] - p0[0]) * tension
        t1y = (p2[1] - p0[1]) * tension
        t2x = (p3[0] - p1[0]) * tension
        t2y = (p3[1] - p1[1]) * tension

        c1x = p1[0] + t1x / 3.0
        c1y = p1[1] + t1y / 3.0
        c2x = p2[0] - t2x / 3.0
        c2y = p2[1] - t2y / 3.0

        segments.append((c1x, c1y, c2x, c2y, p2[0], p2[1]))

    return segments

class OrganicWaveBand(Node):
    """
    Individual smooth categorical color stream ribbon with cubic spline interpolation.
    """
    def __init__(self,
                 bottom_points: Optional[List[Tuple[float, float]]] = None,
                 top_points: Optional[List[Tuple[float, float]]] = None,
                 color: Union[Color, str] = colors.CYAN,
                 tension: float = 0.3,
                 **kwargs: Any):
        super().__init__(**kwargs)
        self.bottom_points = bottom_points or []
        self.top_points = top_points or []
        self.tension = tension
        self.fill_color = Signal(Color.from_any(color) if isinstance(color, (str, Color)) else color, f"{self.name}.fill_color")

    def draw(self, ctx: Any, time: float = 0.0) -> None:
        if len(self.bottom_points) < 2 or len(self.top_points) < 2:
            return

        c = self.fill_color.get(time)
        if c is None:
            return

        ctx.save()
        ctx.set_source_rgba(c.r, c.g, c.b, c.a)

        # Start at first top point
        ctx.new_path()
        ctx.move_to(self.top_points[0][0], self.top_points[0][1])

        # Spline across top (left to right)
        top_spline = compute_cubic_spline_controls(self.top_points, self.tension)
        for seg in top_spline:
            ctx.curve_to(seg[0], seg[1], seg[2], seg[3], seg[4], seg[5])

        # Draw line down to last bottom point
        ctx.line_to(self.bottom_points[-1][0], self.bottom_points[-1][1])

        # Spline across bottom (right to left)
        reversed_bottom = list(reversed(self.bottom_points))
        bottom_spline = compute_cubic_spline_controls(reversed_bottom, self.tension)
        for seg in bottom_spline:
            ctx.curve_to(seg[0], seg[1], seg[2], seg[3], seg[4], seg[5])

        ctx.close_path()
        ctx.fill()
        ctx.restore()

class FlowingStreamgraphArea(Node):
    """
    Stacked area graph with silhouette centered around a flowing organic baseline.
    """
    def __init__(self,
                 data: Optional[List[List[float]]] = None,
                 series: Optional[List[List[float]]] = None,
                 colors_list: Optional[List[Union[Color, str]]] = None,
                 method: str = "wiggle",
                 width: float = 800.0,
                 height: float = 400.0,
                 tension: float = 0.3,
                 **kwargs: Any):
        super().__init__(**kwargs)
        self.data = series if series is not None else (data or [])
        self.method = method
        self.chart_width = Signal(float(width), f"{self.name}.width")
        self.chart_height = Signal(float(height), f"{self.name}.height")
        self.tension = tension
        self.wave_phase = Signal(0.0, f"{self.name}.wave_phase")

        if not colors_list:
            colors_list = [colors.BLUE, colors.CYAN, colors.TEAL, colors.EMERALD]

        self.colors_list = [Color.from_any(c) for c in colors_list]
        self.bands = []

        self._build_chart()

    def _build_chart(self):
        if not self.data or not self.data[0]:
            return

        bottoms, tops = compute_streamgraph_stack(self.data, self.method)
        num_points = len(self.data[0])
        num_layers = len(self.data)

        min_y = float('inf')
        max_y = float('-inf')
        for i in range(num_layers):
            min_y = min(min_y, min(bottoms[i]))
            max_y = max(max_y, max(tops[i]))

        value_range = max_y - min_y if max_y > min_y else 1.0

        cw = self.chart_width.get(0.0)
        ch = self.chart_height.get(0.0)

        step_x = cw / max(1, (num_points - 1))

        self.clear()
        self.bands = []
        for i in range(num_layers):
            bot_pts = []
            top_pts = []
            for j in range(num_points):
                x = j * step_x
                by = ch - ((bottoms[i][j] - min_y) / value_range) * ch
                ty = ch - ((tops[i][j] - min_y) / value_range) * ch
                bot_pts.append((x, by))
                top_pts.append((x, ty))

            color = self.colors_list[i % len(self.colors_list)]
            band = OrganicWaveBand(bottom_points=bot_pts, top_points=top_pts, color=color, tension=self.tension)
            self.add(band)
            self.bands.append(band)

    def undulate_stream(
        self,
        duration: float = 2.0,
        delay: float = 0.0,
        amplitude: float = 1.0,
        ease: Optional[EasingFunc] = None
    ) -> AnimationAction:
        """Animates organic time-series stream layers undulating with smooth wave phase progression."""
        e = ease or Ease.in_out_sine
        self.wave_phase.set(0.0)
        return self.wave_phase.to(math.pi * 2 * amplitude, duration=duration, delay=delay, ease=e)


class TimeAxisScrubber(Node):
    """
    Vertical cursor line scrubbing across timestamps with data breakdown card.
    """
    def __init__(self,
                 x: float = 0.0,
                 height: float = 400.0,
                 label: str = "Time",
                 **kwargs: Any):
        super().__init__(**kwargs)
        self.scrub_x = Signal(float(x), f"{self.name}.scrub_x")
        self.line_height = Signal(float(height), f"{self.name}.height")
        self.label = Signal(str(label), f"{self.name}.label")
        self.color = Signal(colors.WHITE, f"{self.name}.color")

        self.card = FlexContainer(
            direction="column",
            gap=4,
            padding=8,
            corner_radius=8,
            fill=colors.SLATE_800.with_alpha(0.8),
            stroke=colors.SLATE_700
        )
        self.card.position.set(Vector2D(10, 10))
        self.add(self.card)
        self.text_node = Text(text=self.label.get(0.0), font_size=14, color=colors.WHITE)
        self.card.add(self.text_node)

    def draw(self, ctx: Any, time: float = 0.0) -> None:
        sx = self.scrub_x.get(time)
        lh = self.line_height.get(time)
        c = self.color.get(time)
        lbl = self.label.get(time)

        if self.text_node.text.get(time) != lbl:
            self.text_node.text.set(lbl)

        ctx.save()
        ctx.set_source_rgba(c.r, c.g, c.b, c.a)
        ctx.set_line_width(2.0)

        ctx.new_path()
        ctx.move_to(sx, 0)
        ctx.line_to(sx, lh)
        ctx.stroke()
        ctx.restore()

        self.card.position.set(Vector2D(sx + 10, 10))
        super().draw(ctx, time)

class StreamgraphLegend(FlexContainer):
    """
    Floating pills showing category names and total volumes.
    """
    def __init__(self, categories: List[Tuple[str, Union[Color, str], float]], **kwargs: Any):
        super().__init__(
            direction="row",
            gap=12,
            padding=16,
            corner_radius=24,
            fill=colors.SLATE_900.with_alpha(0.85),
            stroke=colors.SLATE_800,
            **kwargs
        )
        for name, color, total in categories:
            color_obj = Color.from_any(color) if isinstance(color, (str, Color)) else color
            pill = FlexContainer(direction="row", gap=8, padding=6, corner_radius=12)

            dot = Rect(width=12, height=12, corner_radius=6, fill=color_obj)
            label_text = f"{name} {total:g}"
            text_node = Text(text=label_text, font_size=14, color=colors.SLATE_200)

            pill.add(dot, text_node)
            self.add(pill)


OrganicWaveStreamgraph = FlowingStreamgraphArea
StackedWaveRibbon = OrganicWaveBand
