from typing import Any, Dict, List, Optional, Sequence, Tuple, Union
import math

from vibmo.scene.node import Node
from vibmo.core.signal import Signal, AnimationAction
from vibmo.core.color import Color, colors
from vibmo.core.easing import Ease, EasingFunc
from vibmo.timeline.scheduler import ParallelGroup
from vibmo.typography.text import Text


class ProportionalRadiusWedge(Node):
    """Radial wedge whose area is strictly proportional to metric value."""
    def __init__(
        self,
        value: float,
        max_value: float,
        max_radius: float,
        start_angle: float,
        end_angle: float,
        color: Union[Color, str] = colors.ROSE_500,
        **kwargs: Any
    ):
        super().__init__(**kwargs)
        self.value = Signal(float(value), f"{self.name}.value")
        self.max_value = max_value
        self.max_radius = max_radius
        self.start_angle = Signal(float(start_angle), f"{self.name}.start_angle")
        self.end_angle = Signal(float(end_angle), f"{self.name}.end_angle")
        self.bloom_progress = Signal(1.0, f"{self.name}.bloom_progress")

        resolved_color = Color.from_any(color) if isinstance(color, (str, Color)) else color
        self.color = Signal(resolved_color, f"{self.name}.color")

    def draw(self, ctx: Any, time: float = 0.0) -> None:
        val = self.value.get(time)
        prog = max(0.0, min(1.0, float(self.bloom_progress.get(time))))
        if val <= 0 or prog <= 0.001:
            super().draw(ctx, time)
            return

        ratio = val / self.max_value if self.max_value > 0 else 0.0
        if ratio < 0:
            ratio = 0
        r = self.max_radius * math.sqrt(ratio) * prog

        start = self.start_angle.get(time)
        end = self.end_angle.get(time)

        ctx.save()
        c = self.color.get(time)
        ctx.set_source_rgba(*c.to_cairo())

        ctx.move_to(0, 0)
        ctx.arc(0, 0, r, start, end)
        ctx.close_path()
        ctx.fill()

        ctx.restore()
        super().draw(ctx, time)


class ConcentricRadiusRings(Node):
    """Background guide rings indicating scale thresholds."""
    def __init__(
        self,
        max_value: float,
        max_radius: float,
        rings: int = 5,
        color: Union[Color, str] = colors.SLATE_700,
        line_width: float = 1.0,
        **kwargs: Any
    ):
        super().__init__(**kwargs)
        self.max_value = max_value
        self.max_radius = max_radius
        self.rings = rings
        self.line_width = line_width
        self.color = Signal(Color.from_any(color) if isinstance(color, (str, Color)) else color, f"{self.name}.color")

    def draw(self, ctx: Any, time: float = 0.0) -> None:
        ctx.save()
        c = self.color.get(time)
        ctx.set_source_rgba(*c.to_cairo())
        ctx.set_line_width(self.line_width)

        for i in range(1, self.rings + 1):
            val = (i / self.rings) * self.max_value
            r = self.max_radius * math.sqrt(val / self.max_value) if self.max_value > 0 else 0.0

            ctx.new_path()
            ctx.arc(0, 0, r, 0, 2 * math.pi)
            ctx.stroke()

        ctx.restore()
        super().draw(ctx, time)


class AngularCategoryAxis(Node):
    """360-degree radial spoke grid labeled by months or categories."""
    def __init__(
        self,
        categories: Sequence[str],
        max_radius: float,
        color: Union[Color, str] = colors.SLATE_700,
        line_width: float = 1.0,
        text_color: Union[Color, str] = colors.WHITE,
        font_size: float = 12.0,
        **kwargs: Any
    ):
        super().__init__(**kwargs)
        self.categories = list(categories)
        self.max_radius = max_radius
        self.line_width = line_width
        self.color = Signal(Color.from_any(color) if isinstance(color, (str, Color)) else color, f"{self.name}.color")
        self.text_color = Color.from_any(text_color)
        self.font_size = font_size

        n_categories = len(self.categories)
        if n_categories > 0:
            angle_step = 2 * math.pi / n_categories
            for i, cat in enumerate(self.categories):
                mid_angle = i * angle_step + angle_step / 2.0
                label_radius = self.max_radius * 1.15

                x = label_radius * math.cos(mid_angle)
                y = label_radius * math.sin(mid_angle)

                t = Text(
                    text=cat,
                    font_size=self.font_size,
                    color=self.text_color,
                    align="center",
                    position=(x, y)
                )
                self.add(t)

    def draw(self, ctx: Any, time: float = 0.0) -> None:
        ctx.save()
        c = self.color.get(time)
        ctx.set_source_rgba(*c.to_cairo())
        ctx.set_line_width(self.line_width)

        n_categories = len(self.categories)
        if n_categories > 0:
            angle_step = 2 * math.pi / n_categories
            for i in range(n_categories):
                angle = i * angle_step
                ctx.move_to(0, 0)
                x = self.max_radius * math.cos(angle)
                y = self.max_radius * math.sin(angle)
                ctx.line_to(x, y)
                ctx.stroke()

        ctx.restore()
        super().draw(ctx, time)


class PolarRoseAreaChart(Node):
    """Cyclic radial chart where sectors have equal angles and radius proportional to square root of metric area."""
    def __init__(
        self,
        data: Optional[Dict[str, Sequence[float]]] = None,
        categories: Optional[Sequence[str]] = None,
        sectors: Optional[Union[List[Dict[str, Any]], List[float]]] = None,
        max_radius: float = 200.0,
        series_colors: Optional[Sequence[Union[Color, str]]] = None,
        rings: int = 5,
        **kwargs: Any
    ):
        super().__init__(**kwargs)

        parsed_data = data or {}
        parsed_cats = list(categories) if categories is not None else []

        if sectors is not None:
            if isinstance(sectors, list) and sectors:
                if isinstance(sectors[0], dict):
                    parsed_cats = [s.get("category", s.get("label", f"Cat {i+1}")) for i, s in enumerate(sectors)]
                    parsed_data = {"Series 1": [float(s.get("value", 0.0)) for s in sectors]}
                else:
                    parsed_cats = [f"Sec {i+1}" for i in range(len(sectors))]
                    parsed_data = {"Series 1": [float(v) for v in sectors]}

        self.data = parsed_data
        self.categories = parsed_cats
        self.max_radius = max_radius
        self.wedges: List[ProportionalRadiusWedge] = []

        n_categories = len(self.categories)

        max_val = 0.0
        for series, values in self.data.items():
            max_val = max(max_val, max(values)) if values else max_val

        if max_val == 0:
            max_val = 1.0

        self.add(ConcentricRadiusRings(
            max_value=max_val,
            max_radius=self.max_radius,
            rings=rings,
            color=colors.SLATE_700,
            line_width=1.0,
        ))

        self.add(AngularCategoryAxis(
            categories=self.categories,
            max_radius=self.max_radius,
            color=colors.SLATE_700,
            line_width=1.0,
            text_color=colors.SLATE_400,
            font_size=14.0
        ))

        default_colors = [colors.ROSE_500, colors.BLUE_500, colors.EMERALD_500, colors.AMBER_500, colors.PURPLE_500]
        if series_colors is None:
            series_colors = default_colors

        if n_categories > 0:
            angle_step = 2 * math.pi / n_categories

            for s_idx, (series_name, values) in enumerate(self.data.items()):
                s_color = series_colors[s_idx % len(series_colors)]
                resolved_c = Color.from_any(s_color)
                if resolved_c.a == 1.0:
                    translucent_c = Color(resolved_c.r, resolved_c.g, resolved_c.b, 0.7)
                else:
                    translucent_c = resolved_c

                for i, val in enumerate(values):
                    if i >= n_categories:
                        break
                    start_angle = i * angle_step
                    end_angle = (i + 1) * angle_step

                    wedge = ProportionalRadiusWedge(
                        value=val,
                        max_value=max_val,
                        max_radius=self.max_radius,
                        start_angle=start_angle,
                        end_angle=end_angle,
                        color=translucent_c,
                    )
                    self.add(wedge)
                    self.wedges.append(wedge)

    def bloom_wedges(
        self,
        duration: float = 1.5,
        delay: float = 0.0,
        stagger: float = 0.05,
        ease: Optional[EasingFunc] = None
    ) -> ParallelGroup:
        """Animates cyclic rose wedges blooming outward proportionally."""
        e = ease or Ease.out_back
        actions = []
        for i, wedge in enumerate(self.wedges):
            wedge.bloom_progress.set(0.0)
            actions.append(wedge.bloom_progress.to(1.0, duration=duration, delay=delay + i * stagger, ease=e))
        return ParallelGroup(actions)


PolarRoseCoxcombChart = PolarRoseAreaChart
RoseWedgeNode = ProportionalRadiusWedge
