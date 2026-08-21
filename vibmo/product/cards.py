"""
SaaS Stat Cards, KPI Metric Displays, and Feature Highlights.
"""

from __future__ import annotations
import math
from typing import Any, List, Optional, Sequence, Tuple, Union
import cairo

from vibmo.core.vector import Vector2D
from vibmo.core.color import Color, colors
from vibmo.core.signal import Signal, AnimationAction
from vibmo.core.easing import Ease, EasingFunc
from vibmo.scene.node import Node
from vibmo.layout.container import FlexContainer
from vibmo.components.glass import GlassCard
from vibmo.components.counter import MetricCounter
from vibmo.typography.kinetic import KineticText
from vibmo.importers.icons import Icon
from vibmo.product.charts import Sparkline
from vibmo.product.social import Badge


class StatCard(GlassCard):
    """
    SaaS Dashboard KPI Stat Card with metric counter, trend percentage badge, and inline sparkline.
    """

    def __init__(
        self,
        title: str = "Monthly Recurring Revenue",
        value: float = 148500.0,
        prefix: str = "$",
        suffix: str = "",
        trend: str = "+24.5%",
        trend_positive: bool = True,
        sparkline_data: Sequence[float] = (30, 45, 40, 65, 55, 90, 85, 120),
        width: float = 320.0,
        color: Optional[Union[Color, str]] = colors.EMERALD,
        position: Union[Vector2D, Sequence[float]] = (0.0, 0.0),
        **kwargs: Any,
    ) -> None:
        super().__init__(
            direction="column",
            gap=12.0,
            padding=24.0,
            corner_radius=20.0,
            position=position,
            **kwargs,
        )
        self.width_val = float(width)
        theme_color = Color.from_any(color) if color else colors.EMERALD

        # 1. Title + Trend Header Row
        header = FlexContainer(direction="row", gap=12.0, padding=0.0, fill=Color.TRANSPARENT, stroke=Color.TRANSPARENT)
        title_node = KineticText(title, font_size=13.0, color=Color.hex("#94a3b8"), bold=True)
        trend_badge = Badge(text=trend, color=colors.EMERALD if trend_positive else colors.ROSE)
        header.add(title_node, trend_badge)

        # 2. Main Metric Counter
        self.counter = MetricCounter(
            start_val=0,
            end_val=value,
            prefix=prefix,
            suffix=suffix,
            font_size=38.0,
            bold=True,
            color=colors.WHITE,
        )

        # 3. Mini Sparkline
        self.sparkline = Sparkline(data=sparkline_data, width=self.width_val - 48.0, height=40.0, color=theme_color)

        self.add(header, self.counter, self.sparkline)

    def count_up(self, duration: float = 1.6, delay: float = 0.0) -> AnimationAction:
        """Counts the KPI counter and traces sparkline simultaneously."""
        from vibmo.timeline.scheduler import ParallelGroup
        return ParallelGroup([
            self.counter.count_to(duration=duration, delay=delay),
            self.sparkline.trace(duration=duration, delay=delay),
        ])
