from typing import Any, List, Optional, Tuple, Union, Dict
from vibmo.scene.node import Node
from vibmo.core.color import Color, colors
from vibmo.core.signal import Signal, AnimationAction
from vibmo.core.easing import Ease, EasingFunc
from vibmo.timeline.scheduler import ParallelGroup

class FrequencyBarChart(Node):
    def __init__(
        self,
        data: List[Tuple[str, float]],
        width: float = 800.0,
        height: float = 400.0,
        bar_color: Union[Color, str] = colors.BLUE,
        **kwargs: Any
    ) -> None:
        super().__init__(**kwargs)
        self.data = sorted(data, key=lambda x: x[1], reverse=True)
        self.width = Signal(float(width), f"{self.name}.width")
        self.height = Signal(float(height), f"{self.name}.height")
        self.bar_color = Signal(Color.from_any(bar_color), f"{self.name}.bar_color")
        self.bar_scale = Signal(1.0, f"{self.name}.bar_scale")

    def draw(self, ctx: Any, time: float = 0.0) -> None:
        if not self.data:
            return

        w = self.width.get(time)
        h = self.height.get(time)
        bar_color = self.bar_color.get(time)
        scale = max(0.0, min(1.0, float(self.bar_scale.get(time))))

        if scale <= 0.001:
            return

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
            bar_height = (val / max_val) * h * scale
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
        **kwargs: Any
    ) -> None:
        super().__init__(**kwargs)
        self.cumulative_data = cumulative_data
        self.width = Signal(float(width), f"{self.name}.width")
        self.height = Signal(float(height), f"{self.name}.height")
        self.line_color = Signal(Color.from_any(line_color), f"{self.name}.line_color")
        self.progress = Signal(1.0, f"{self.name}.progress")

    def draw(self, ctx: Any, time: float = 0.0) -> None:
        if not self.cumulative_data:
            return

        w = self.width.get(time)
        h = self.height.get(time)
        line_color = self.line_color.get(time)
        prog = max(0.0, min(1.0, float(self.progress.get(time))))

        if prog <= 0.001:
            return

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
            # Draw curve up to prog
            visible_count = max(1, int(len(points) * prog))
            sub_points = points[:visible_count]

            ctx.move_to(*sub_points[0])
            for i in range(1, len(sub_points)):
                x0, y0 = sub_points[i-1]
                x1, y1 = sub_points[i]

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
        **kwargs: Any
    ) -> None:
        super().__init__(**kwargs)
        self.threshold = Signal(float(threshold), f"{self.name}.threshold")
        self.width = Signal(float(width), f"{self.name}.width")
        self.height = Signal(float(height), f"{self.name}.height")
        self.line_color = Signal(Color.from_any(line_color), f"{self.name}.line_color")
        self.reveal = Signal(1.0, f"{self.name}.reveal")

    def draw(self, ctx: Any, time: float = 0.0) -> None:
        rev = max(0.0, min(1.0, float(self.reveal.get(time))))
        if rev <= 0.001:
            return

        w = self.width.get(time) * rev
        h = self.height.get(time)
        threshold = self.threshold.get(time)
        line_color = self.line_color.get(time)

        y = h - (threshold * h)

        ctx.save()
        for width_val, alpha in [(12.0, 0.1), (6.0, 0.3), (2.0, 1.0)]:
            color = line_color.with_alpha(alpha)
            ctx.set_source_rgba(*color.to_cairo())
            ctx.set_line_width(width_val)
            ctx.set_dash([10.0, 5.0], 0)

            ctx.move_to(0, y)
            ctx.line_to(w, y)
            ctx.stroke()
        ctx.restore()

class ParetoAnalysisChart(Node):
    """Dual-axis 80/20 frequency analysis chart with cumulative distribution curve and cutoff threshold."""

    def __init__(
        self,
        data: Optional[Union[List[Tuple[str, float]], Dict[str, float], List[Dict[str, Any]]]] = None,
        categories: Optional[Union[List[Tuple[str, float]], Dict[str, float], List[Dict[str, Any]]]] = None,
        width: float = 800.0,
        height: float = 400.0,
        bar_color: Union[Color, str] = colors.BLUE,
        line_color: Union[Color, str] = colors.ORANGE,
        threshold_color: Union[Color, str] = colors.RED,
        **kwargs: Any
    ) -> None:
        super().__init__(**kwargs)

        raw = categories if categories is not None else (data or [])
        parsed_data: List[Tuple[str, float]] = []

        if isinstance(raw, dict):
            for k, v in raw.items():
                parsed_data.append((str(k), float(v)))
        elif isinstance(raw, list):
            for item in raw:
                if isinstance(item, tuple) and len(item) == 2:
                    parsed_data.append((str(item[0]), float(item[1])))
                elif isinstance(item, dict):
                    name = item.get("category", item.get("label", item.get("name", "Item")))
                    val = float(item.get("value", item.get("count", item.get("frequency", 0.0))))
                    parsed_data.append((str(name), val))
                else:
                    parsed_data.append((str(item), 1.0))

        self.sorted_data = sorted(parsed_data, key=lambda x: x[1], reverse=True)

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

    def draw_80_20_cutoff(
        self,
        duration: float = 1.5,
        delay: float = 0.0,
        ease: Optional[EasingFunc] = None
    ) -> ParallelGroup:
        """Animates cumulative percentage curve sweep and 80/20 critical threshold line."""
        e = ease or Ease.out_expo
        self.curve.progress.set(0.0)
        self.threshold_line.reveal.set(0.0)
        return ParallelGroup([
            self.curve.progress.to(1.0, duration=duration, delay=delay, ease=e),
            self.threshold_line.reveal.to(1.0, duration=duration * 0.8, delay=delay + duration * 0.3, ease=Ease.out_cubic),
        ])

    def draw(self, ctx: Any, time: float = 0.0) -> None:
        super().draw(ctx, time)


CumulativeCurve = Cumulative8020Curve
