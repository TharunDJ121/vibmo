from typing import Any, List, Optional, Tuple, Union, Dict
from vibmo.scene.node import Node
from vibmo.core.color import Color, colors
from vibmo.core.signal import Signal

class FrequencyBarChart(Node):
    def __init__(
        self,
        data: List[Tuple[str, float]],
        width: float = 800.0,
        height: float = 400.0,
        bar_color: Union[Color, str] = colors.BLUE,
        **kwargs
    ) -> None:
        super().__init__(**kwargs)
        self.data = sorted(data, key=lambda x: x[1], reverse=True)
        self.width = Signal(float(width), f"{self.name}.width")
        self.height = Signal(float(height), f"{self.name}.height")
        self.bar_color = Signal(Color.from_any(bar_color), f"{self.name}.bar_color")

    def draw(self, ctx: Any, time: float = 0.0) -> None:
        if not self.data:
            return

        w = self.width(time)
        h = self.height(time)
        bar_color = self.bar_color(time)

        max_val = max(x[1] for x in self.data)
        if max_val <= 0:
            return

        num_bars = len(self.data)
        bar_width = (w / num_bars) * 0.8
        gap = (w / num_bars) * 0.2

        ctx.save()
        ctx.set_source_rgba(*bar_color.to_cairo())

        for i, (label, val) in enumerate(self.data):
            x = i * (w / num_bars) + gap / 2
            bar_height = (val / max_val) * h
            y = h - bar_height

            ctx.rectangle(x, y, bar_width, bar_height)
            ctx.fill()

        ctx.restore()

class Cumulative8020Curve(Node):
    def __init__(
        self,
        cumulative_data: List[float],
        width: float = 800.0,
        height: float = 400.0,
        line_color: Union[Color, str] = colors.ORANGE,
        **kwargs
    ) -> None:
        super().__init__(**kwargs)
        self.cumulative_data = cumulative_data
        self.width = Signal(float(width), f"{self.name}.width")
        self.height = Signal(float(height), f"{self.name}.height")
        self.line_color = Signal(Color.from_any(line_color), f"{self.name}.line_color")

    def draw(self, ctx: Any, time: float = 0.0) -> None:
        if not self.cumulative_data:
            return

        w = self.width(time)
        h = self.height(time)
        line_color = self.line_color(time)

        num_points = len(self.cumulative_data)

        ctx.save()
        ctx.set_source_rgba(*line_color.to_cairo())
        ctx.set_line_width(3.0)

        points = []
        for i, val in enumerate(self.cumulative_data):
            x = i * (w / num_points) + (w / num_points) / 2
            y = h - (val * h)
            points.append((x, y))

        if points:
            ctx.move_to(*points[0])
            for i in range(1, len(points)):
                x0, y0 = points[i-1]
                x1, y1 = points[i]

                # Smooth cubic bezier
                # Control points horizontally offset
                cx0 = x0 + (x1 - x0) / 2
                cy0 = y0
                cx1 = x0 + (x1 - x0) / 2
                cy1 = y1

                ctx.curve_to(cx0, cy0, cx1, cy1, x1, y1)

        ctx.stroke()
        ctx.restore()

class CriticalThresholdLine(Node):
    def __init__(
        self,
        threshold: float = 0.8,
        width: float = 800.0,
        height: float = 400.0,
        line_color: Union[Color, str] = colors.RED,
        **kwargs
    ) -> None:
        super().__init__(**kwargs)
        self.threshold = Signal(float(threshold), f"{self.name}.threshold")
        self.width = Signal(float(width), f"{self.name}.width")
        self.height = Signal(float(height), f"{self.name}.height")
        self.line_color = Signal(Color.from_any(line_color), f"{self.name}.line_color")

    def draw(self, ctx: Any, time: float = 0.0) -> None:
        w = self.width(time)
        h = self.height(time)
        threshold = self.threshold(time)
        line_color = self.line_color(time)

        y = h - (threshold * h)

        ctx.save()
        # Glow effect: multiple layered strokes
        for width, alpha in [(12.0, 0.1), (6.0, 0.3), (2.0, 1.0)]:
            color = line_color.with_alpha(alpha)
            ctx.set_source_rgba(*color.to_cairo())
            ctx.set_line_width(width)
            ctx.set_dash([10.0, 5.0], 0)

            ctx.move_to(0, y)
            ctx.line_to(w, y)
            ctx.stroke()
        ctx.restore()

class ParetoAnalysisChart(Node):
    def __init__(
        self,
        data: List[Tuple[str, float]],
        width: float = 800.0,
        height: float = 400.0,
        bar_color: Union[Color, str] = colors.BLUE,
        line_color: Union[Color, str] = colors.ORANGE,
        threshold_color: Union[Color, str] = colors.RED,
        **kwargs
    ) -> None:
        super().__init__(**kwargs)

        # Sort data descending
        self.sorted_data = sorted(data, key=lambda x: x[1], reverse=True)

        # Compute cumulative percentage
        total = sum(x[1] for x in self.sorted_data)
        self.cumulative_data = []
        current_sum = 0.0
        for _, val in self.sorted_data:
            current_sum += val
            self.cumulative_data.append(current_sum / total if total > 0 else 0.0)

        self.bar_chart = FrequencyBarChart(
            data=self.sorted_data,
            width=width,
            height=height,
            bar_color=bar_color,
            name=f"{self.name}.bar_chart"
        )
        self.add(self.bar_chart)

        self.curve = Cumulative8020Curve(
            cumulative_data=self.cumulative_data,
            width=width,
            height=height,
            line_color=line_color,
            name=f"{self.name}.curve"
        )
        self.add(self.curve)

        self.threshold_line = CriticalThresholdLine(
            threshold=0.8,
            width=width,
            height=height,
            line_color=threshold_color,
            name=f"{self.name}.threshold_line"
        )
        self.add(self.threshold_line)

    def draw(self, ctx: Any, time: float = 0.0) -> None:
        # Drawing of children is handled by Node traversal
        # We need to call super to let children draw
        super().draw(ctx, time)
