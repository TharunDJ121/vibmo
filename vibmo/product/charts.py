"""
Production-grade Glowing Area Charts and Metric Sparklines for SaaS Analytics Demos.
"""

from __future__ import annotations
import math
from typing import Any, List, Optional, Sequence, Tuple, Union
import cairo

from vibmo.core.vector import Vector2D
from vibmo.core.color import Color, LinearGradient, colors
from vibmo.core.signal import Signal, AnimationAction
from vibmo.core.easing import Ease, EasingFunc
from vibmo.scene.node import Node
from vibmo.spatial.shadows import DropShadow


class AreaChart(Node):
    """
    Silicon-Valley style Glowing Area Chart with cubic spline curves,
    luminous vertical gradient fills, animated line tracing, and live dot tracers.
    """

    def __init__(
        self,
        data: Sequence[float] = (20, 35, 28, 55, 42, 78, 65, 95, 88, 120),
        width: float = 600.0,
        height: float = 240.0,
        color: Optional[Union[Color, str]] = colors.EMERALD,
        line_width: float = 3.5,
        fill_opacity: float = 0.25,
        show_grid: bool = True,
        show_dots: bool = True,
        glow: bool = True,
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)
        self.data = [float(v) for v in data] if data else [0.0, 10.0]
        self.width_val = float(width)
        self.height_val = float(height)
        self.chart_color = Color.from_any(color) if color else colors.EMERALD
        self.line_width = float(line_width)
        self.fill_opacity = float(fill_opacity)
        self.show_grid = show_grid
        self.show_dots = show_dots
        self.glow = glow

        # Animatable signals
        self.trace_progress = Signal(1.0, f"{self.name}.trace_progress")
        self.dot_pulse = Signal(1.0, f"{self.name}.dot_pulse")

        if self.glow:
            self.shadow = DropShadow.glow(color=self.chart_color, blur=20.0, intensity=0.5)
        else:
            self.shadow = None

    def trace(
        self,
        duration: float = 1.6,
        delay: float = 0.0,
        ease: Optional[EasingFunc] = None,
    ) -> AnimationAction:
        """Animates the chart line being drawn from left to right."""
        self.trace_progress.set(0.0)
        e = ease or Ease.out_cubic
        return self.trace_progress.to(1.0, duration=duration, ease=e, delay=delay)

    def local_bounds(self, time: float = 0.0) -> Tuple[float, float, float, float]:
        return (0.0, 0.0, self.width_val, self.height_val)

    def _compute_points(self) -> List[Tuple[float, float]]:
        """Maps raw data values into canvas pixel coordinates."""
        n = len(self.data)
        if n < 2:
            return [(0.0, self.height_val * 0.5), (self.width_val, self.height_val * 0.5)]

        min_val = min(self.data)
        max_val = max(self.data)
        val_range = max(1e-4, max_val - min_val)

        # Padding inside chart
        pad_top = 20.0
        pad_bot = 20.0
        usable_h = self.height_val - pad_top - pad_bot
        dx = self.width_val / (n - 1)

        pts = []
        for i, val in enumerate(self.data):
            x = i * dx
            # Invert Y (0 at top)
            norm_y = (val - min_val) / val_range
            y = self.height_val - pad_bot - (norm_y * usable_h)
            pts.append((x, y))

        return pts

    def _build_spline_path(self, ctx: Any, pts: List[Tuple[float, float]], max_x: float) -> None:
        """Builds a smooth Catmull-Rom / cubic bezier curve through points up to max_x."""
        if not pts:
            return

        ctx.move_to(pts[0][0], pts[0][1])
        if len(pts) == 2:
            ctx.line_to(min(max_x, pts[1][0]), pts[1][1])
            return

        for i in range(len(pts) - 1):
            p0 = pts[i - 1] if i > 0 else pts[i]
            p1 = pts[i]
            p2 = pts[i + 1]
            p3 = pts[i + 2] if i + 2 < len(pts) else p2

            if p1[0] > max_x:
                break

            # Cubic control points
            cp1x = p1[0] + (p2[0] - p0[0]) / 6.0
            cp1y = p1[1] + (p2[1] - p0[1]) / 6.0
            cp2x = p2[0] - (p3[0] - p1[0]) / 6.0
            cp2y = p2[1] - (p3[1] - p1[1]) / 6.0

            if p2[0] <= max_x:
                ctx.curve_to(cp1x, cp1y, cp2x, cp2y, p2[0], p2[1])
            else:
                # Partial segment
                t = max(0.0, min(1.0, (max_x - p1[0]) / max(1e-4, p2[0] - p1[0])))
                end_x = p1[0] + (p2[0] - p1[0]) * t
                end_y = p1[1] + (p2[1] - p1[1]) * t
                ctx.line_to(end_x, end_y)
                break

    def draw(self, ctx: Any, time: float = 0.0) -> None:
        w = self.width_val
        h = self.height_val
        pts = self._compute_points()
        if not pts:
            return

        progress = max(0.0, min(1.0, float(self.trace_progress.get(time))))
        if progress <= 0.001:
            return

        max_trace_x = progress * w

        ctx.save()

        # 1. Subtle horizontal gridlines
        if self.show_grid:
            ctx.save()
            ctx.set_source_rgba(1.0, 1.0, 1.0, 0.05)
            ctx.set_line_width(1.0)
            ctx.set_dash([4.0, 6.0])
            for k in range(1, 4):
                gy = h * (k / 4.0)
                ctx.move_to(0, gy)
                ctx.line_to(w, gy)
                ctx.stroke()
            ctx.restore()

        # 2. Glowing Gradient Area Fill
        ctx.save()
        ctx.new_path()
        self._build_spline_path(ctx, pts, max_trace_x)
        
        # Close path down to bottom baseline
        last_pt_x = max_trace_x
        ctx.line_to(last_pt_x, h)
        ctx.line_to(0.0, h)
        ctx.close_path()

        # Vertical linear gradient fading to transparent
        grad = cairo.LinearGradient(0, 0, 0, h)
        c = self.chart_color
        grad.add_color_stop_rgba(0.0, c.r, c.g, c.b, self.fill_opacity)
        grad.add_color_stop_rgba(0.6, c.r, c.g, c.b, self.fill_opacity * 0.3)
        grad.add_color_stop_rgba(1.0, c.r, c.g, c.b, 0.0)

        ctx.set_source(grad)
        ctx.fill()
        ctx.restore()

        # 3. Outer Neon Glow Line (underneath)
        if self.glow:
            ctx.save()
            ctx.new_path()
            self._build_spline_path(ctx, pts, max_trace_x)
            ctx.set_source_rgba(c.r, c.g, c.b, 0.3)
            ctx.set_line_width(self.line_width * 2.5)
            ctx.stroke()
            ctx.restore()

        # 4. Main Crisp Line Stroke
        ctx.save()
        ctx.new_path()
        self._build_spline_path(ctx, pts, max_trace_x)
        ctx.set_source_rgba(c.r, c.g, c.b, c.a)
        ctx.set_line_width(self.line_width)
        ctx.set_line_cap(cairo.LINE_CAP_ROUND)
        ctx.set_line_join(cairo.LINE_JOIN_ROUND)
        ctx.stroke()
        ctx.restore()

        # 5. Pulsating Leading Tracer Dot
        if self.show_dots and progress > 0.05:
            # Find active leading point
            lead_idx = min(len(pts) - 1, int(progress * (len(pts) - 1)))
            lead_x, lead_y = pts[lead_idx]

            # Glowing outer ripple
            pulse_rad = 8.0 + math.sin(time * 6.0) * 2.5
            ctx.set_source_rgba(c.r, c.g, c.b, 0.25)
            ctx.arc(lead_x, lead_y, pulse_rad * 1.6, 0, math.pi * 2)
            ctx.fill()

            # White center dot
            ctx.set_source_rgba(1.0, 1.0, 1.0, 1.0)
            ctx.arc(lead_x, lead_y, 4.5, 0, math.pi * 2)
            ctx.fill()

            # Colored halo rim
            ctx.set_source_rgba(c.r, c.g, c.b, 1.0)
            ctx.set_line_width(2.0)
            ctx.arc(lead_x, lead_y, 4.5, 0, math.pi * 2)
            ctx.stroke()

        ctx.restore()


class Sparkline(AreaChart):
    """Compact inline KPI sparkline without gridlines."""
    def __init__(
        self,
        data: Sequence[float] = (10, 15, 12, 22, 18, 30),
        width: float = 140.0,
        height: float = 48.0,
        color: Optional[Union[Color, str]] = colors.EMERALD,
        **kwargs: Any,
    ) -> None:
        super().__init__(
            data=data,
            width=width,
            height=height,
            color=color,
            line_width=2.5,
            fill_opacity=0.2,
            show_grid=False,
            show_dots=False,
            **kwargs,
        )


# =========================================================================
# NEW PHASE 4 DATA VISUALIZATION COMPONENTS
# =========================================================================

class BarChart(Node):
    """
    Animated Vertical/Horizontal Bar Chart with staggered spring entrance,
    rounded bar capsules, and value labels.
    """

    def __init__(
        self,
        data: Sequence[Union[float, Tuple[str, float]]] = (("Mon", 45), ("Tue", 72), ("Wed", 60), ("Thu", 95), ("Fri", 84), ("Sat", 110)),
        width: float = 540.0,
        height: float = 240.0,
        color: Optional[Union[Color, str]] = colors.INDIGO,
        corner_radius: float = 6.0,
        show_values: bool = True,
        gap: float = 16.0,
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)
        self.width_val = float(width)
        self.height_val = float(height)
        self.bar_color = Color.from_any(color) if color else colors.INDIGO
        self.corner_radius = float(corner_radius)
        self.show_values = show_values
        self.gap = float(gap)

        self.labels: List[str] = []
        self.values: List[float] = []

        for item in data:
            if isinstance(item, (tuple, list)):
                self.labels.append(str(item[0]))
                self.values.append(float(item[1]))
            else:
                self.labels.append("")
                self.values.append(float(item))

        self.max_val = max(self.values) if self.values and max(self.values) > 0 else 100.0
        self.growth_signals = [Signal(1.0, f"{self.name}.bar_{i}") for i in range(len(self.values))]

    def grow_bars(
        self,
        duration: float = 1.0,
        stagger: float = 0.08,
        ease: Optional[EasingFunc] = None,
        delay: float = 0.0,
    ) -> Any:
        """Animates bars growing up from 0 with staggered spring physics."""
        from vibmo.timeline.scheduler import ParallelGroup
        spring_ease = ease or Ease.spring(stiffness=160, damping=14)
        actions = []
        for i, sig in enumerate(self.growth_signals):
            sig.set(0.0)
            actions.append(sig.to(1.0, duration=duration, ease=spring_ease, delay=delay + i * stagger))
        return ParallelGroup(actions)

    def local_bounds(self, time: float = 0.0) -> Tuple[float, float, float, float]:
        return (0.0, 0.0, self.width_val, self.height_val)

    def draw(self, ctx: Any, time: float = 0.0) -> None:
        n = len(self.values)
        if n == 0:
            return

        w, h = self.width_val, self.height_val
        bottom_pad = 28.0
        chart_h = h - bottom_pad
        total_gap = self.gap * (n - 1)
        bar_w = max(4.0, (w - total_gap) / n)
        c = self.bar_color

        for i, val in enumerate(self.values):
            prog = max(0.0, min(2.0, float(self.growth_signals[i].get(time))))
            bar_h = max(2.0, (val / self.max_val) * chart_h * prog)
            x = i * (bar_w + self.gap)
            y = chart_h - bar_h

            # Draw bar capsule
            ctx.save()
            r = min(self.corner_radius, bar_w * 0.5, bar_h * 0.5)
            ctx.new_sub_path()
            ctx.arc(x + bar_w - r, y + r, r, -math.pi / 2, 0)
            ctx.arc(x + bar_w - r, y + bar_h - r, r, 0, math.pi / 2)
            ctx.arc(x + r, y + bar_h - r, r, math.pi / 2, math.pi)
            ctx.arc(x + r, y + r, r, math.pi, 3 * math.pi / 2)
            ctx.close_path()

            # Vertical bar gradient
            pat = cairo.LinearGradient(x, y, x, y + bar_h)
            pat.add_color_stop_rgba(0.0, c.r, c.g, c.b, 0.95)
            pat.add_color_stop_rgba(1.0, c.r * 0.6, c.g * 0.6, c.b * 0.6, 0.75)
            ctx.set_source(pat)
            ctx.fill()
            ctx.restore()

            # Label below bar
            if i < len(self.labels) and self.labels[i]:
                ctx.set_source_rgba(0.6, 0.65, 0.75, 0.8)
                ctx.select_font_face("Inter", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)
                ctx.set_font_size(12.0)
                ext = ctx.text_extents(self.labels[i])
                ctx.move_to(x + (bar_w - ext.width) * 0.5, h - 6.0)
                ctx.show_text(self.labels[i])


class PieChart(Node):
    """
    Animated Circular Pie & Donut Chart with radial sweep reveal and slice explode verbs.
    """

    def __init__(
        self,
        data: Sequence[Union[float, Tuple[str, float]]] = (("Search", 45), ("Direct", 30), ("Social", 15), ("Referral", 10)),
        radius: float = 110.0,
        donut_ratio: float = 0.0,
        slice_colors: Optional[Sequence[Union[Color, str]]] = None,
        center_text: Optional[str] = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)
        self.radius_val = float(radius)
        self.donut_ratio = float(donut_ratio)
        self.center_text = center_text

        default_palette = [
            colors.INDIGO,
            colors.CYAN,
            colors.EMERALD,
            colors.AMBER,
            colors.ROSE,
            colors.VIOLET,
        ]
        self.colors = [Color.from_any(c) for c in slice_colors] if slice_colors else default_palette

        self.labels: List[str] = []
        self.values: List[float] = []
        for item in data:
            if isinstance(item, (tuple, list)):
                self.labels.append(str(item[0]))
                self.values.append(float(item[1]))
            else:
                self.labels.append("")
                self.values.append(float(item))

        self.total = sum(self.values) if self.values and sum(self.values) > 0 else 1.0
        self.sweep_progress = Signal(1.0, f"{self.name}.sweep")
        self.slice_offsets = [Signal(0.0, f"{self.name}.offset_{i}") for i in range(len(self.values))]

    def reveal(
        self,
        duration: float = 1.4,
        ease: Optional[EasingFunc] = None,
        delay: float = 0.0,
    ) -> AnimationAction:
        """Animates 360 degree radial sweep entrance."""
        self.sweep_progress.set(0.0)
        return self.sweep_progress.to(1.0, duration=duration, ease=ease or Ease.out_expo, delay=delay)

    def explode_slice(
        self,
        slice_idx: int,
        offset: float = 14.0,
        duration: float = 0.6,
        ease: Optional[EasingFunc] = None,
    ) -> AnimationAction:
        """Pulls a specific pie slice outwards for highlight emphasis."""
        if 0 <= slice_idx < len(self.slice_offsets):
            return self.slice_offsets[slice_idx].to(float(offset), duration=duration, ease=ease or Ease.spring(180, 12))
        return self.sweep_progress.to(1.0, duration=0.1)

    def local_bounds(self, time: float = 0.0) -> Tuple[float, float, float, float]:
        d = self.radius_val * 2.0 + 30.0
        return (0.0, 0.0, d, d)

    def draw(self, ctx: Any, time: float = 0.0) -> None:
        n = len(self.values)
        if n == 0:
            return

        cx = self.radius_val + 15.0
        cy = self.radius_val + 15.0
        r_outer = self.radius_val
        r_inner = r_outer * self.donut_ratio
        sweep = max(0.0, min(1.0, float(self.sweep_progress.get(time))))

        start_angle = -math.pi * 0.5
        for i, val in enumerate(self.values):
            slice_angle = (val / self.total) * (math.pi * 2.0)
            cur_slice_angle = slice_angle * sweep
            end_angle = start_angle + cur_slice_angle

            # Slice radial explode translation
            off = float(self.slice_offsets[i].get(time))
            mid_angle = start_angle + cur_slice_angle * 0.5
            sx = math.cos(mid_angle) * off
            sy = math.sin(mid_angle) * off

            c = self.colors[i % len(self.colors)]

            ctx.save()
            ctx.translate(cx + sx, cy + sy)

            ctx.new_path()
            ctx.arc(0, 0, r_outer, start_angle, end_angle)
            if r_inner > 0.0:
                ctx.arc_negative(0, 0, r_inner, end_angle, start_angle)
            else:
                ctx.line_to(0, 0)
            ctx.close_path()

            ctx.set_source_rgba(c.r, c.g, c.b, 0.92)
            ctx.fill_preserve()
            ctx.set_source_rgba(0.04, 0.07, 0.12, 0.8)
            ctx.set_line_width(2.0)
            ctx.stroke()

            ctx.restore()
            start_angle += slice_angle * sweep

        # Center Donut Metric Label
        if self.donut_ratio > 0.3 and self.center_text:
            ctx.set_source_rgba(1.0, 1.0, 1.0, 0.95)
            ctx.select_font_face("Inter", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
            ctx.set_font_size(16.0)
            ext = ctx.text_extents(self.center_text)
            ctx.move_to(cx - ext.width * 0.5, cy + ext.height * 0.35)
            ctx.show_text(self.center_text)


class DonutChart(PieChart):
    """Frosted Glass Donut Chart with center KPI metric badge."""
    def __init__(
        self,
        data: Sequence[Union[float, Tuple[str, float]]] = (("Active", 68), ("Pending", 22), ("Churn", 10)),
        radius: float = 110.0,
        donut_ratio: float = 0.65,
        center_text: str = "100%",
        **kwargs: Any,
    ) -> None:
        super().__init__(
            data=data,
            radius=radius,
            donut_ratio=donut_ratio,
            center_text=center_text,
            **kwargs,
        )


class GaugeChart(Node):
    """
    Speedometer / Circular KPI Dial with animated arc indicator and glowing needle.
    """

    def __init__(
        self,
        value: float = 78.0,
        min_val: float = 0.0,
        max_val: float = 100.0,
        radius: float = 90.0,
        unit: str = "%",
        color: Optional[Union[Color, str]] = colors.CYAN,
        thickness: float = 14.0,
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)
        self.min_val = float(min_val)
        self.max_val = float(max_val)
        self.radius_val = float(radius)
        self.unit = str(unit)
        self.color = Color.from_any(color) if color else colors.CYAN
        self.thickness = float(thickness)

        self.current_value = Signal(float(value), f"{self.name}.value")

    def animate_to(
        self,
        target_val: float,
        duration: float = 1.2,
        ease: Optional[EasingFunc] = None,
        delay: float = 0.0,
    ) -> AnimationAction:
        """Animates gauge needle and arc to a new target value."""
        return self.current_value.to(float(target_val), duration=duration, ease=ease or Ease.out_expo, delay=delay)

    def local_bounds(self, time: float = 0.0) -> Tuple[float, float, float, float]:
        d = self.radius_val * 2.0 + 20.0
        return (0.0, 0.0, d, d)

    def draw(self, ctx: Any, time: float = 0.0) -> None:
        cx = self.radius_val + 10.0
        cy = self.radius_val + 10.0
        r = self.radius_val
        val = float(self.current_value.get(time))
        frac = max(0.0, min(1.0, (val - self.min_val) / max(1e-4, self.max_val - self.min_val)))

        start_angle = math.pi * 0.75
        end_angle = math.pi * 2.25
        total_sweep = end_angle - start_angle
        active_end = start_angle + total_sweep * frac

        # 1. Background Arc Track
        ctx.save()
        ctx.set_source_rgba(0.15, 0.2, 0.3, 0.5)
        ctx.set_line_width(self.thickness)
        ctx.set_line_cap(cairo.LINE_CAP_ROUND)
        ctx.arc(cx, cy, r, start_angle, end_angle)
        ctx.stroke()

        # 2. Glowing Active Value Arc
        c = self.color
        ctx.set_source_rgba(c.r, c.g, c.b, 0.95)
        ctx.set_line_width(self.thickness)
        ctx.set_line_cap(cairo.LINE_CAP_ROUND)
        if frac > 0.01:
            ctx.arc(cx, cy, r, start_angle, active_end)
            ctx.stroke()

        # 3. Center Value Typography
        ctx.set_source_rgba(1.0, 1.0, 1.0, 1.0)
        ctx.select_font_face("Inter", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
        ctx.set_font_size(24.0)
        text_val = f"{int(val)}{self.unit}"
        ext = ctx.text_extents(text_val)
        ctx.move_to(cx - ext.width * 0.5, cy + ext.height * 0.35)
        ctx.show_text(text_val)
        ctx.restore()

