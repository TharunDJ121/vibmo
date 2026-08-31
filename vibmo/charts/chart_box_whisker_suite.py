"""
Statistical Box-and-Whisker Plot suite.
"""

from __future__ import annotations
import math
from typing import Any, List, Optional, Sequence, Tuple, Union
import cairo
import numpy as np

from vibmo.core.vector import Vector2D
from vibmo.core.color import Color, colors
from vibmo.core.signal import Signal, AnimationAction
from vibmo.core.easing import Ease, EasingFunc
from vibmo.timeline.scheduler import ParallelGroup
from vibmo.scene.node import Node


def calculate_box_stats(data: Sequence[float]) -> dict:
    """Calculates statistics for a box plot."""
    d = np.array(data, dtype=float)
    if len(d) == 0:
        return {
            "q1": 0.0, "median": 0.0, "q3": 0.0,
            "iqr": 0.0, "min_whisker": 0.0, "max_whisker": 0.0,
            "outliers": []
        }

    q1 = np.percentile(d, 25)
    median = np.percentile(d, 50)
    q3 = np.percentile(d, 75)
    iqr = q3 - q1

    lower_bound = q1 - 1.5 * iqr
    upper_bound = q3 + 1.5 * iqr

    # Whiskers extend to the lowest/highest data points within the 1.5 * IQR bounds
    non_outliers = d[(d >= lower_bound) & (d <= upper_bound)]
    if len(non_outliers) > 0:
        min_whisker = np.min(non_outliers)
        max_whisker = np.max(non_outliers)
    else:
        min_whisker = q1
        max_whisker = q3

    outliers = d[(d < lower_bound) | (d > upper_bound)].tolist()

    return {
        "q1": q1,
        "median": median,
        "q3": q3,
        "iqr": iqr,
        "min_whisker": min_whisker,
        "max_whisker": max_whisker,
        "outliers": outliers
    }

class AnimatedOutlierPings(Node):
    def __init__(
        self,
        outliers: Sequence[float],
        scale_y: float = 1.0,
        offset_y: float = 0.0,
        x_pos: float = 0.0,
        color: Union[Color, str] = colors.RED,
        **kwargs: Any
    ) -> None:
        super().__init__(**kwargs)
        self.outliers = outliers
        self.scale_y = scale_y
        self.offset_y = offset_y
        self.x_pos = x_pos
        self.dot_color = Color.from_any(color) if color else colors.RED
        self.ping_progress = Signal(1.0, f"{self.name}.ping_progress")

    def draw(self, ctx: Any, time: float = 0.0) -> None:
        if not self.outliers:
            return

        progress = max(0.0, min(1.0, float(self.ping_progress.get(time))))
        if progress <= 0.001:
            return

        ctx.save()
        r, g, b, a = self.dot_color.to_cairo()

        for val in self.outliers:
            y_pos = self.offset_y - val * self.scale_y

            # Glow
            ctx.save()
            ctx.set_source_rgba(r, g, b, a * 0.3 * (1.0 - progress))
            ctx.arc(self.x_pos, y_pos, 8.0 * progress, 0, math.pi * 2)
            ctx.fill()
            ctx.restore()

            # Core
            ctx.save()
            ctx.set_source_rgba(r, g, b, a)
            ctx.arc(self.x_pos, y_pos, 3.0, 0, math.pi * 2)
            ctx.fill()
            ctx.restore()

        ctx.restore()

class WhiskersErrorBars(Node):
    def __init__(
        self,
        min_whisker: float,
        max_whisker: float,
        q1: float,
        q3: float,
        scale_y: float = 1.0,
        offset_y: float = 0.0,
        x_pos: float = 0.0,
        width: float = 20.0,
        color: Union[Color, str] = colors.GRAY,
        **kwargs: Any
    ) -> None:
        super().__init__(**kwargs)
        self.min_whisker = min_whisker
        self.max_whisker = max_whisker
        self.q1 = q1
        self.q3 = q3
        self.scale_y = scale_y
        self.offset_y = offset_y
        self.x_pos = x_pos
        self.width_val = width
        self.line_color = Color.from_any(color) if color else colors.GRAY
        self.reveal = Signal(1.0, f"{self.name}.reveal")

    def draw(self, ctx: Any, time: float = 0.0) -> None:
        progress = max(0.0, min(1.0, float(self.reveal.get(time))))
        if progress <= 0.001:
            return

        ctx.save()
        ctx.set_source_rgba(*self.line_color.to_cairo())
        ctx.set_line_width(2.0)

        half_w = (self.width_val / 2.0) * progress

        # Lower whisker
        min_y = self.offset_y - self.min_whisker * self.scale_y
        q1_y = self.offset_y - self.q1 * self.scale_y

        ctx.move_to(self.x_pos, q1_y)
        ctx.line_to(self.x_pos, q1_y + (min_y - q1_y) * progress)
        ctx.stroke()

        ctx.move_to(self.x_pos - half_w, min_y)
        ctx.line_to(self.x_pos + half_w, min_y)
        ctx.stroke()

        # Upper whisker
        max_y = self.offset_y - self.max_whisker * self.scale_y
        q3_y = self.offset_y - self.q3 * self.scale_y

        ctx.move_to(self.x_pos, q3_y)
        ctx.line_to(self.x_pos, q3_y + (max_y - q3_y) * progress)
        ctx.stroke()

        ctx.move_to(self.x_pos - half_w, max_y)
        ctx.line_to(self.x_pos + half_w, max_y)
        ctx.stroke()

        ctx.restore()

class InterquartileBox(Node):
    def __init__(
        self,
        q1: float,
        median: float,
        q3: float,
        scale_y: float = 1.0,
        offset_y: float = 0.0,
        x_pos: float = 0.0,
        width: float = 40.0,
        color: Union[Color, str] = colors.BLUE,
        **kwargs: Any
    ) -> None:
        super().__init__(**kwargs)
        self.q1 = q1
        self.median = median
        self.q3 = q3
        self.scale_y = scale_y
        self.offset_y = offset_y
        self.x_pos = x_pos
        self.width_val = width
        self.box_color = Color.from_any(color) if color else colors.BLUE
        self.reveal = Signal(1.0, f"{self.name}.reveal")

    def draw(self, ctx: Any, time: float = 0.0) -> None:
        progress = max(0.0, min(1.0, float(self.reveal.get(time))))
        if progress <= 0.001:
            return

        ctx.save()
        r, g, b, a = self.box_color.to_cairo()

        q1_y = self.offset_y - self.q1 * self.scale_y
        q3_y = self.offset_y - self.q3 * self.scale_y
        median_y = self.offset_y - self.median * self.scale_y

        box_h = abs(q3_y - q1_y)
        box_y = min(q1_y, q3_y)

        current_h = box_h * progress
        current_y = median_y - (median_y - box_y) * progress

        half_w = (self.width_val / 2.0) * progress

        # Box Fill
        ctx.set_source_rgba(r, g, b, a * 0.5)
        ctx.rectangle(self.x_pos - half_w, current_y, half_w * 2, current_h)
        ctx.fill_preserve()

        # Box Stroke
        ctx.set_source_rgba(r, g, b, a)
        ctx.set_line_width(2.0)
        ctx.stroke()

        # Median Line
        ctx.set_source_rgba(1.0, 1.0, 1.0, a) # White prominent line
        ctx.set_line_width(3.0)
        ctx.move_to(self.x_pos - half_w, median_y)
        ctx.line_to(self.x_pos + half_w, median_y)
        ctx.stroke()

        ctx.restore()

class StatisticalBoxPlot(Node):
    """Multi-category box plot comparing medians, interquartile ranges (IQR), and extremes."""
    def __init__(
        self,
        datasets: Sequence[Sequence[float]],
        width: float = 600.0,
        height: float = 400.0,
        colors_list: Optional[Sequence[Union[Color, str]]] = None,
        y_min: Optional[float] = None,
        y_max: Optional[float] = None,
        **kwargs: Any
    ) -> None:
        super().__init__(**kwargs)
        self.datasets = datasets
        self.width_val = width
        self.height_val = height

        default_colors = [colors.BLUE, colors.EMERALD, colors.PURPLE, colors.AMBER, colors.ROSE]
        self.colors_list = [Color.from_any(c) for c in (colors_list or default_colors)]

        self.stats = [calculate_box_stats(d) for d in datasets]

        all_vals = []
        for d in datasets:
            all_vals.extend(d)

        if len(all_vals) > 0:
            v_min = min(all_vals)
            v_max = max(all_vals)
            v_range = v_max - v_min
            margin = v_range * 0.1 if v_range > 0 else abs(v_max) * 0.1
            if margin == 0:
                margin = 1.0
            self.y_min = y_min if y_min is not None else v_min - margin
            self.y_max = y_max if y_max is not None else v_max + margin
        else:
            self.y_min = y_min if y_min is not None else 0.0
            self.y_max = y_max if y_max is not None else 1.0

        self.whiskers: List[WhiskersErrorBars] = []
        self.boxes: List[InterquartileBox] = []
        self.pings: List[AnimatedOutlierPings] = []

        n = len(self.datasets)
        if n == 0:
            return

        x_gap = self.width_val / (n + 1)

        val_range = max(1e-6, self.y_max - self.y_min)
        self.scale_y = self.height_val / val_range
        self.offset_y = self.height_val + self.y_min * self.scale_y

        for i, stat in enumerate(self.stats):
            x_pos = x_gap * (i + 1)
            c = self.colors_list[i % len(self.colors_list)]

            whisker = WhiskersErrorBars(
                min_whisker=stat["min_whisker"],
                max_whisker=stat["max_whisker"],
                q1=stat["q1"],
                q3=stat["q3"],
                scale_y=self.scale_y,
                offset_y=self.offset_y,
                x_pos=x_pos,
                color=c
            )

            box = InterquartileBox(
                q1=stat["q1"],
                median=stat["median"],
                q3=stat["q3"],
                scale_y=self.scale_y,
                offset_y=self.offset_y,
                x_pos=x_pos,
                color=c
            )

            pings = AnimatedOutlierPings(
                outliers=stat["outliers"],
                scale_y=self.scale_y,
                offset_y=self.offset_y,
                x_pos=x_pos,
                color=colors.RED
            )

            self.add(whisker)
            self.add(box)
            self.add(pings)

            self.whiskers.append(whisker)
            self.boxes.append(box)
            self.pings.append(pings)

    def extend_whiskers(
        self,
        duration: float = 1.2,
        delay: float = 0.0,
        stagger: float = 0.05,
        ease: Optional[EasingFunc] = None
    ) -> ParallelGroup:
        """Animates statistical quartile boxes and whiskers extending smoothly."""
        e = ease or Ease.out_expo
        actions = []
        for i, (whisker, box, ping) in enumerate(zip(self.whiskers, self.boxes, self.pings)):
            whisker.reveal.set(0.0)
            box.reveal.set(0.0)
            ping.ping_progress.set(0.0)
            actions.append(box.reveal.to(1.0, duration=duration, delay=delay + i * stagger, ease=e))
            actions.append(whisker.reveal.to(1.0, duration=duration, delay=delay + i * stagger + 0.05, ease=e))
            actions.append(ping.ping_progress.to(1.0, duration=duration * 0.8, delay=delay + i * stagger + 0.1, ease=Ease.out_cubic))
        return ParallelGroup(actions)

    def draw(self, ctx: Any, time: float = 0.0) -> None:
        super().draw(ctx, time)


BoxAndWhiskerPlot = StatisticalBoxPlot
OutlierDotNode = AnimatedOutlierPings
