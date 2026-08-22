import math
from typing import Any, List, Dict, Optional, Union, Sequence
import cairo

from vibmo.scene.node import Node
from vibmo.core.color import Color, colors
from vibmo.core.signal import Signal
from vibmo.core.vector import Vector2D
from vibmo.typography.text import Text

class ProportionalRadiusWedge(Node):
    """Translucent colored wedge sectors layered by time/season."""
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

        resolved_color = Color.from_any(color) if isinstance(color, (str, Color)) else color
        # Ensure it is somewhat translucent if layered by time/season as requested, or we can leave it to the user.
        # But we can just use the color directly.
        self.color = Signal(resolved_color, f"{self.name}.color")

    def draw(self, ctx: Any, time: float = 0.0) -> None:
        val = self.value.get()
        if val <= 0:
            super().draw(ctx, time)
            return

        # Radius is proportional to the square root of the metric area
        # A = pi * r^2 * (theta / 2pi) -> r is proportional to sqrt(val)
        ratio = val / self.max_value
        if ratio < 0:
            ratio = 0
        r = self.max_radius * math.sqrt(ratio)

        start = self.start_angle.get()
        end = self.end_angle.get()

        ctx.save()
        c = self.color.get()
        ctx.set_source_rgba(*c.to_cairo())

        ctx.move_to(0, 0)
        ctx.arc(0, 0, r, start, end)
        ctx.close_path()
        ctx.fill()

        # Optional: draw outline? Not explicitly required, maybe simple fill is fine.
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
        c = self.color.get()
        ctx.set_source_rgba(*c.to_cairo())
        ctx.set_line_width(self.line_width)

        for i in range(1, self.rings + 1):
            # Equal area concentric rings or equal value concentric rings?
            # Usually Florence Nightingale uses equal value steps, so r = sqrt(val)
            val = (i / self.rings) * self.max_value
            r = self.max_radius * math.sqrt(val / self.max_value)

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

        # Add Text children for each category
        n_categories = len(self.categories)
        if n_categories > 0:
            angle_step = 2 * math.pi / n_categories
            for i, cat in enumerate(self.categories):
                # The label is placed at the center of the wedge
                mid_angle = i * angle_step + angle_step / 2.0

                # Position it slightly outside the max_radius
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
        c = self.color.get()
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
        data: Dict[str, Sequence[float]],
        categories: Sequence[str],
        max_radius: float = 200.0,
        series_colors: Optional[Sequence[Union[Color, str]]] = None,
        rings: int = 5,
        **kwargs: Any
    ):
        super().__init__(**kwargs)
        self.data = data
        self.categories = list(categories)
        self.max_radius = max_radius

        n_categories = len(self.categories)

        # Find maximum value to scale radii
        max_val = 0.0
        for series, values in self.data.items():
            max_val = max(max_val, max(values))

        if max_val == 0:
            max_val = 1.0  # avoid division by zero

        # Add Concentric Rings
        self.add(ConcentricRadiusRings(
            max_value=max_val,
            max_radius=self.max_radius,
            rings=rings,
            color=colors.SLATE_700,
            line_width=1.0,
        ))

        # Add Angular Axis
        self.add(AngularCategoryAxis(
            categories=self.categories,
            max_radius=self.max_radius,
            color=colors.SLATE_700,
            line_width=1.0,
            text_color=colors.SLATE_400,
            font_size=14.0
        ))

        # Add Wedges for each series and each category
        # Nightingale charts often overlap series, largest values back to smallest,
        # or have translucent colors. We'll use alpha on the colors.

        default_colors = [colors.ROSE_500, colors.BLUE_500, colors.EMERALD_500, colors.AMBER_500, colors.PURPLE_500]
        if series_colors is None:
            series_colors = default_colors

        if n_categories > 0:
            angle_step = 2 * math.pi / n_categories

            # For each series
            for s_idx, (series_name, values) in enumerate(self.data.items()):
                s_color = series_colors[s_idx % len(series_colors)]
                resolved_c = Color.from_any(s_color)
                # Ensure it's translucent
                if resolved_c.a == 1.0:
                    translucent_c = Color(resolved_c.r, resolved_c.g, resolved_c.b, 0.7)
                else:
                    translucent_c = resolved_c

                for i, val in enumerate(values):
                    if i >= n_categories:
                        break
                    start_angle = i * angle_step
                    end_angle = (i + 1) * angle_step

                    self.add(ProportionalRadiusWedge(
                        value=val,
                        max_value=max_val,
                        max_radius=self.max_radius,
                        start_angle=start_angle,
                        end_angle=end_angle,
                        color=translucent_c,
                    ))
