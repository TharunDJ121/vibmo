"""
Advanced Glowing Charts Suite (LineChart, ScatterChart, RadarChart, FunnelChart, Heatmap, CandlestickChart)
for executive dashboards and financial/data motion graphics.
"""

from __future__ import annotations
import math
from typing import Any, Dict, List, Optional, Sequence, Tuple, Union
import cairo
import numpy as np

from vibmo.core.vector import Vector2D
from vibmo.core.color import Color, LinearGradient, colors
from vibmo.core.signal import Signal, AnimationAction
from vibmo.core.easing import Ease, EasingFunc
from vibmo.scene.node import Node
from vibmo.spatial.shadows import DropShadow


class LineChart(Node):
    """
    Multi-series glowing line chart with spline interpolation, animated line tracing, and markers.
    """

    def __init__(
        self,
        series: Optional[Dict[str, Sequence[float]]] = None,
        width: float = 640.0,
        height: float = 280.0,
        series_colors: Optional[Dict[str, Union[Color, str]]] = None,
        line_width: float = 3.0,
        show_grid: bool = True,
        show_dots: bool = True,
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)
        self.series = series or {"Revenue": [10, 25, 18, 42, 60, 55, 85, 95], "Target": [20, 30, 40, 50, 60, 70, 80, 90]}
        self.width_val = float(width)
        self.height_val = float(height)
        self.line_width = float(line_width)
        self.show_grid = show_grid
        self.show_dots = show_dots

        # Color mapping
        default_palette = [colors.EMERALD, colors.INDIGO, colors.CYAN, colors.AMBER, colors.ROSE]
        self.colors_map: Dict[str, Color] = {}
        for idx, name in enumerate(self.series.keys()):
            if series_colors and name in series_colors:
                self.colors_map[name] = Color.from_any(series_colors[name])
            else:
                self.colors_map[name] = default_palette[idx % len(default_palette)]

        self.trace_progress = Signal(1.0, f"{self.name}.trace_progress")

    def trace(self, duration: float = 1.6, delay: float = 0.0, ease: Optional[EasingFunc] = None) -> AnimationAction:
        self.trace_progress.set(0.0)
        return self.trace_progress.to(1.0, duration=duration, ease=ease or Ease.out_cubic, delay=delay)

    def local_bounds(self, time: float = 0.0) -> Tuple[float, float, float, float]:
        return (0.0, 0.0, self.width_val, self.height_val)

    def draw(self, ctx: Any, time: float = 0.0) -> None:
        w = self.width_val
        h = self.height_val
        pad_x = 40.0
        pad_y = 30.0
        plot_w = w - pad_x * 2
        plot_h = h - pad_y * 2

        ctx.save()
        # 1. Background Gridlines
        if self.show_grid:
            ctx.set_source_rgba(1.0, 1.0, 1.0, 0.06)
            ctx.set_line_width(1.0)
            for row in range(5):
                gy = pad_y + (plot_h / 4.0) * row
                ctx.move_to(pad_x, gy)
                ctx.line_to(pad_x + plot_w, gy)
                ctx.stroke()

        # Find min/max across all series
        all_vals = [v for s in self.series.values() for v in s]
        min_v = min(all_vals) if all_vals else 0.0
        max_v = max(all_vals) if all_vals else 100.0
        v_span = max(1e-4, max_v - min_v)

        p = float(self.trace_progress.get(time))

        # 2. Draw each series
        for name, vals in self.series.items():
            if len(vals) < 2:
                continue
            c = self.colors_map[name]
            n = len(vals)
            dx = plot_w / (n - 1)

            points = []
            for i, val in enumerate(vals):
                norm_y = (val - min_v) / v_span
                px = pad_x + i * dx
                py = pad_y + plot_h - norm_y * plot_h
                points.append((px, py))

            # Truncate points along progress
            max_idx = int(p * (n - 1))
            frac = (p * (n - 1)) - max_idx

            ctx.save()
            ctx.set_source_rgba(c.r, c.g, c.b, c.a)
            ctx.set_line_width(self.line_width)
            ctx.set_line_cap(cairo.LINE_CAP_ROUND)
            ctx.set_line_join(cairo.LINE_JOIN_ROUND)

            ctx.new_path()
            ctx.move_to(points[0][0], points[0][1])
            for i in range(1, max_idx + 1):
                ctx.line_to(points[i][0], points[i][1])
            if max_idx < n - 1 and frac > 0.01:
                cur_x = points[max_idx][0] + (points[max_idx + 1][0] - points[max_idx][0]) * frac
                cur_y = points[max_idx][1] + (points[max_idx + 1][1] - points[max_idx][1]) * frac
                ctx.line_to(cur_x, cur_y)
            ctx.stroke()

            # Dots
            if self.show_dots:
                for i in range(max_idx + 1):
                    ctx.set_source_rgba(c.r, c.g, c.b, 1.0)
                    ctx.arc(points[i][0], points[i][1], 4.0, 0, math.pi * 2)
                    ctx.fill()
                    ctx.set_source_rgba(1.0, 1.0, 1.0, 0.9)
                    ctx.arc(points[i][0], points[i][1], 2.0, 0, math.pi * 2)
                    ctx.fill()
            ctx.restore()

        ctx.restore()


class ScatterChart(Node):
    """
    2D Scatter plot with variable bubble radius, glowing points, and animated entrance.
    """

    def __init__(
        self,
        points: Optional[Sequence[Tuple[float, float, float]]] = None,  # (x, y, radius)
        width: float = 580.0,
        height: float = 320.0,
        color: Union[Color, str] = colors.CYAN,
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)
        self.points = points or [(15, 20, 8), (35, 65, 14), (50, 45, 10), (70, 85, 18), (85, 60, 12), (90, 92, 22)]
        self.width_val = float(width)
        self.height_val = float(height)
        self.color = Color.from_any(color)
        self.reveal_progress = Signal(1.0, f"{self.name}.reveal_progress")

    def pop_in(self, duration: float = 1.2, delay: float = 0.0) -> AnimationAction:
        self.reveal_progress.set(0.0)
        return self.reveal_progress.to(1.0, duration=duration, ease=Ease.out_back, delay=delay)

    def local_bounds(self, time: float = 0.0) -> Tuple[float, float, float, float]:
        return (0.0, 0.0, self.width_val, self.height_val)

    def draw(self, ctx: Any, time: float = 0.0) -> None:
        w = self.width_val
        h = self.height_val
        pad = 32.0
        plot_w = w - pad * 2
        plot_h = h - pad * 2
        p = float(self.reveal_progress.get(time))

        ctx.save()
        # Grid
        ctx.set_source_rgba(1.0, 1.0, 1.0, 0.08)
        ctx.rectangle(pad, pad, plot_w, plot_h)
        ctx.stroke()

        c = self.color
        for pt in self.points:
            norm_x, norm_y, r = pt[0] / 100.0, pt[1] / 100.0, pt[2]
            px = pad + norm_x * plot_w
            py = pad + plot_h - norm_y * plot_h
            cur_r = r * p

            if cur_r > 0.5:
                # Glowing bubble
                ctx.set_source_rgba(c.r, c.g, c.b, 0.35)
                ctx.arc(px, py, cur_r * 1.5, 0, math.pi * 2)
                ctx.fill()
                # Solid core
                ctx.set_source_rgba(c.r, c.g, c.b, 0.9)
                ctx.arc(px, py, cur_r, 0, math.pi * 2)
                ctx.fill()
        ctx.restore()


class RadarChart(Node):
    """
    Spider / Radar polygon chart with radial axes and animated polygon area unfolding.
    """

    def __init__(
        self,
        categories: Sequence[str] = ("Speed", "Reliability", "Security", "Scale", "UX", "Cost"),
        values: Sequence[float] = (85, 90, 75, 95, 80, 70),  # 0 to 100
        radius: float = 140.0,
        color: Union[Color, str] = colors.INDIGO,
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)
        self.categories = list(categories)
        self.values = [float(v) for v in values]
        self.radius = float(radius)
        self.color = Color.from_any(color)
        self.unfold_progress = Signal(1.0, f"{self.name}.unfold_progress")

    def unfold(self, duration: float = 1.4, delay: float = 0.0) -> AnimationAction:
        self.unfold_progress.set(0.0)
        return self.unfold_progress.to(1.0, duration=duration, ease=Ease.out_elastic, delay=delay)

    def local_bounds(self, time: float = 0.0) -> Tuple[float, float, float, float]:
        r = self.radius + 40.0
        return (-r, -r, r * 2, r * 2)

    def draw(self, ctx: Any, time: float = 0.0) -> None:
        n = len(self.categories)
        if n < 3:
            return
        r = self.radius
        p = float(self.unfold_progress.get(time))
        angle_step = (math.pi * 2) / n

        ctx.save()
        # 1. Concentric Web Rings
        ctx.set_source_rgba(1.0, 1.0, 1.0, 0.1)
        ctx.set_line_width(1.0)
        for ring_frac in (0.25, 0.5, 0.75, 1.0):
            ctx.new_path()
            for i in range(n):
                a = i * angle_step - math.pi * 0.5
                vx = math.cos(a) * r * ring_frac
                vy = math.sin(a) * r * ring_frac
                if i == 0:
                    ctx.move_to(vx, vy)
                else:
                    ctx.line_to(vx, vy)
            ctx.close_path()
            ctx.stroke()

        # 2. Radial Spoke Axes
        for i in range(n):
            a = i * angle_step - math.pi * 0.5
            ctx.move_to(0, 0)
            ctx.line_to(math.cos(a) * r, math.sin(a) * r)
            ctx.stroke()

        # 3. Polygon Data Area
        c = self.color
        ctx.new_path()
        for i in range(n):
            val_norm = (self.values[i % len(self.values)] / 100.0) * p
            a = i * angle_step - math.pi * 0.5
            vx = math.cos(a) * r * val_norm
            vy = math.sin(a) * r * val_norm
            if i == 0:
                ctx.move_to(vx, vy)
            else:
                ctx.line_to(vx, vy)
        ctx.close_path()
        ctx.set_source_rgba(c.r, c.g, c.b, 0.35)
        ctx.fill_preserve()
        ctx.set_source_rgba(c.r, c.g, c.b, 0.95)
        ctx.set_line_width(2.5)
        ctx.stroke()

        ctx.restore()


class FunnelChart(Node):
    """
    Conversion Funnel chart showing stage drop-off and conversion rates.
    """

    def __init__(
        self,
        stages: Sequence[Tuple[str, float]] = (("Visitors", 10000), ("Signups", 4200), ("Active", 2100), ("Paid", 850)),
        width: float = 540.0,
        height: float = 280.0,
        color: Union[Color, str] = colors.EMERALD,
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)
        self.stages = list(stages)
        self.width_val = float(width)
        self.height_val = float(height)
        self.color = Color.from_any(color)
        self.fill_progress = Signal(1.0, f"{self.name}.fill_progress")

    def animate_stages(self, duration: float = 1.5, delay: float = 0.0) -> AnimationAction:
        self.fill_progress.set(0.0)
        return self.fill_progress.to(1.0, duration=duration, ease=Ease.out_expo, delay=delay)

    def local_bounds(self, time: float = 0.0) -> Tuple[float, float, float, float]:
        return (0.0, 0.0, self.width_val, self.height_val)

    def draw(self, ctx: Any, time: float = 0.0) -> None:
        n = len(self.stages)
        if n == 0:
            return
        w = self.width_val
        h = self.height_val
        p = float(self.fill_progress.get(time))
        stage_h = h / n
        gap = 6.0
        max_val = max(s[1] for s in self.stages)

        ctx.save()
        c = self.color

        for i, (label, val) in enumerate(self.stages):
            frac = (val / max_val) * p
            cur_w = max(60.0, w * frac)
            x0 = (w - cur_w) * 0.5
            y0 = i * stage_h + gap * 0.5
            cur_h = stage_h - gap

            # Stage bar
            ctx.set_source_rgba(c.r, c.g, c.b, 0.25 + (i / n) * 0.5)
            self._rounded_rect(ctx, x0, y0, cur_w, cur_h, 8.0)
            ctx.fill_preserve()
            ctx.set_source_rgba(1.0, 1.0, 1.0, 0.2)
            ctx.set_line_width(1.0)
            ctx.stroke()

            # Label text
            ctx.set_source_rgba(1.0, 1.0, 1.0, 0.9)
            ctx.select_font_face("Segoe UI", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
            ctx.set_font_size(13.0)
            txt = f"{label}: {int(val):,}"
            ext = ctx.text_extents(txt)
            ctx.move_to(w * 0.5 - ext.width * 0.5, y0 + cur_h * 0.5 + ext.height * 0.5 - 2.0)
            ctx.show_text(txt)

        ctx.restore()

    def _rounded_rect(self, ctx: Any, x: float, y: float, w: float, h: float, r: float) -> None:
        r = min(r, w * 0.5, h * 0.5)
        ctx.new_path()
        ctx.arc(x + w - r, y + r, r, -math.pi * 0.5, 0)
        ctx.arc(x + w - r, y + h - r, r, 0, math.pi * 0.5)
        ctx.arc(x + r, y + h - r, r, math.pi * 0.5, math.pi)
        ctx.arc(x + r, y + r, r, math.pi, math.pi * 1.5)
        ctx.close_path()


class Heatmap(Node):
    """
    2D Matrix Heatmap with animated cell intensities and color transitions.
    """

    def __init__(
        self,
        matrix: Optional[Sequence[Sequence[float]]] = None,
        width: float = 480.0,
        height: float = 240.0,
        color: Union[Color, str] = colors.EMERALD,
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)
        self.matrix = matrix or [[10, 30, 70, 90], [20, 50, 80, 100], [5, 25, 45, 60], [15, 40, 85, 95]]
        self.width_val = float(width)
        self.height_val = float(height)
        self.color = Color.from_any(color)
        self.reveal_progress = Signal(1.0, f"{self.name}.reveal_progress")

    def local_bounds(self, time: float = 0.0) -> Tuple[float, float, float, float]:
        return (0.0, 0.0, self.width_val, self.height_val)

    def draw(self, ctx: Any, time: float = 0.0) -> None:
        rows = len(self.matrix)
        cols = len(self.matrix[0]) if rows > 0 else 0
        if rows == 0 or cols == 0:
            return

        w, h = self.width_val, self.height_val
        cell_w = w / cols
        cell_h = h / rows
        gap = 4.0
        c = self.color
        p = float(self.reveal_progress.get(time))

        ctx.save()
        for r in range(rows):
            for col in range(cols):
                val = (self.matrix[r][col] / 100.0) * p
                alpha = np.clip(val, 0.05, 0.95)
                x = col * cell_w + gap * 0.5
                y = r * cell_h + gap * 0.5
                cw = cell_w - gap
                ch = cell_h - gap

                ctx.set_source_rgba(c.r, c.g, c.b, alpha)
                self._rounded_rect(ctx, x, y, cw, ch, 4.0)
                ctx.fill()
        ctx.restore()

    def _rounded_rect(self, ctx: Any, x: float, y: float, w: float, h: float, r: float) -> None:
        r = min(r, w * 0.5, h * 0.5)
        ctx.new_path()
        ctx.arc(x + w - r, y + r, r, -math.pi * 0.5, 0)
        ctx.arc(x + w - r, y + h - r, r, 0, math.pi * 0.5)
        ctx.arc(x + r, y + h - r, r, math.pi * 0.5, math.pi)
        ctx.arc(x + r, y + r, r, math.pi, math.pi * 1.5)
        ctx.close_path()


class CandlestickChart(Node):
    """
    Financial Stock / Crypto Candlestick chart with high/low wicks and open/close bodies.
    """

    def __init__(
        self,
        candles: Optional[Sequence[Tuple[float, float, float, float]]] = None,  # (open, high, low, close)
        width: float = 600.0,
        height: float = 280.0,
        bull_color: Union[Color, str] = colors.EMERALD,
        bear_color: Union[Color, str] = colors.ROSE,
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)
        self.candles = candles or [
            (100, 115, 95, 110),
            (110, 125, 108, 122),
            (122, 124, 112, 115),
            (115, 130, 114, 128),
            (128, 142, 126, 140),
            (140, 145, 132, 135),
            (135, 155, 134, 150),
        ]
        self.width_val = float(width)
        self.height_val = float(height)
        self.bull_color = Color.from_any(bull_color)
        self.bear_color = Color.from_any(bear_color)
        self.trace_progress = Signal(1.0, f"{self.name}.trace_progress")

    def local_bounds(self, time: float = 0.0) -> Tuple[float, float, float, float]:
        return (0.0, 0.0, self.width_val, self.height_val)

    def draw(self, ctx: Any, time: float = 0.0) -> None:
        n = len(self.candles)
        if n == 0:
            return
        w, h = self.width_val, self.height_val
        pad_x, pad_y = 30.0, 24.0
        plot_w = w - pad_x * 2
        plot_h = h - pad_y * 2

        all_lows = [c[2] for c in self.candles]
        all_highs = [c[1] for c in self.candles]
        min_v = min(all_lows)
        max_v = max(all_highs)
        span = max(1e-4, max_v - min_v)

        slot_w = plot_w / n
        candle_w = max(6.0, slot_w * 0.6)
        p = float(self.trace_progress.get(time))
        active_count = int(p * n)

        ctx.save()
        for i in range(active_count):
            o, hi, lo, c = self.candles[i]
            is_bull = c >= o
            color = self.bull_color if is_bull else self.bear_color

            cx = pad_x + i * slot_w + slot_w * 0.5
            y_hi = pad_y + plot_h - ((hi - min_v) / span) * plot_h
            y_lo = pad_y + plot_h - ((lo - min_v) / span) * plot_h
            y_open = pad_y + plot_h - ((o - min_v) / span) * plot_h
            y_close = pad_y + plot_h - ((c - min_v) / span) * plot_h

            top_y = min(y_open, y_close)
            bot_y = max(y_open, y_close)
            body_h = max(3.0, bot_y - top_y)

            # Wick line
            ctx.set_source_rgba(color.r, color.g, color.b, 0.8)
            ctx.set_line_width(1.5)
            ctx.move_to(cx, y_hi)
            ctx.line_to(cx, y_lo)
            ctx.stroke()

            # Candle Body
            ctx.set_source_rgba(color.r, color.g, color.b, 0.9)
            ctx.rectangle(cx - candle_w * 0.5, top_y, candle_w, body_h)
            ctx.fill()

        ctx.restore()
