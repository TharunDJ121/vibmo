"""
Telemetry HUD & Real-time Metrics UI Suite for Vibmo / Motio.
Components:
- TelemetryDialHUD
- RadialGaugeDial (CircularCpuGaugeDial)
- RamMemoryMeterBar
- NetworkPingLatencyLine
- UptimePercentageBadge
"""

from __future__ import annotations
import math
from typing import Any, Dict, List, Optional, Sequence, Tuple, Union
import cairo

from vibmo.core.color import Color, colors
from vibmo.core.vector import Vector2D
from vibmo.core.signal import Signal, AnimationAction
from vibmo.core.easing import Ease, EasingFunc
from vibmo.scene.node import Node
from vibmo.spatial.shadows import DropShadow


class RadialGaugeDial(Node):
    """Radial gauge dial with colored arc sweep and center percentage readout."""

    def __init__(
        self,
        label: str = "CPU Load",
        value: float = 45.0,
        radius: float = 55.0,
        stroke_width: float = 9.0,
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)
        self.label = label
        self.radius = float(radius)
        self.stroke_width = float(stroke_width)
        self.value = Signal(float(value), f"{self.name}.value")

    def _get_color_for_val(self, val_pct: float) -> Tuple[float, float, float, float]:
        v = max(0.0, min(100.0, val_pct)) / 100.0
        if v < 0.6:
            return (0.1, 0.85, 0.45, 0.95) # Green
        elif v < 0.85:
            return (0.95, 0.7, 0.15, 0.95) # Amber
        return (0.95, 0.25, 0.35, 0.95) # Red

    def draw(self, ctx: Any, time: float = 0.0) -> None:
        val = self.value.get(time)
        val_clamped = max(0.0, min(100.0, val))
        r = self.radius
        sw = self.stroke_width

        ctx.save()
        # Track background
        ctx.arc(0, 0, r, -math.pi * 0.75, math.pi * 0.75)
        ctx.set_source_rgba(0.12, 0.16, 0.24, 0.8)
        ctx.set_line_width(sw)
        ctx.set_line_cap(1) # Round
        ctx.stroke()

        # Value Arc
        sweep_angle = -math.pi * 0.75 + (val_clamped / 100.0) * (math.pi * 1.5)
        ctx.arc(0, 0, r, -math.pi * 0.75, sweep_angle)
        ctx.set_source_rgba(*self._get_color_for_val(val_clamped))
        ctx.set_line_width(sw)
        ctx.set_line_cap(1)
        ctx.stroke()

        # Center readout
        ctx.select_font_face("Inter", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
        ctx.set_font_size(18.0)
        ctx.set_source_rgba(0.95, 0.98, 1.0, 0.95)
        text = f"{int(val_clamped)}%"
        ext = ctx.text_extents(text)
        ctx.move_to(-ext.width * 0.5, 4.0)
        ctx.show_text(text)

        # Label below
        ctx.select_font_face("Inter", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)
        ctx.set_font_size(11.0)
        ctx.set_source_rgba(0.6, 0.7, 0.8, 0.8)
        lbl_ext = ctx.text_extents(self.label)
        ctx.move_to(-lbl_ext.width * 0.5, r + 18.0)
        ctx.show_text(self.label)

        ctx.restore()


CircularCpuGaugeDial = RadialGaugeDial


class RamMemoryMeterBar(Node):
    """Segmented horizontal RAM memory usage meter bar."""

    def __init__(
        self,
        label: str = "RAM Allocation",
        used_gb: float = 16.4,
        total_gb: float = 32.0,
        width: float = 240.0,
        height: float = 40.0,
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)
        self.label = label
        self.total_gb = float(total_gb)
        self.width_val = float(width)
        self.height_val = float(height)
        self.used_gb = Signal(float(used_gb), f"{self.name}.used_gb")

    def draw(self, ctx: Any, time: float = 0.0) -> None:
        w, h = self.width_val, self.height_val
        used = max(0.0, min(self.total_gb, self.used_gb.get(time)))
        fraction = used / max(0.1, self.total_gb)

        ctx.save()
        # Label and readout
        ctx.select_font_face("Inter", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)
        ctx.set_font_size(11.0)
        ctx.set_source_rgba(0.7, 0.8, 0.9, 0.9)
        ctx.move_to(0.0, 12.0)
        ctx.show_text(self.label)

        val_text = f"{used:.1f} / {self.total_gb:.0f} GB"
        ext = ctx.text_extents(val_text)
        ctx.move_to(w - ext.width, 12.0)
        ctx.set_source_rgba(0.2, 0.85, 1.0, 0.95)
        ctx.show_text(val_text)

        # Bar track
        bar_y = 20.0
        bar_h = 10.0
        r = 4.0
        ctx.new_path()
        ctx.arc(w - r, bar_y + r, r, -math.pi * 0.5, math.pi * 0.5)
        ctx.arc(r, bar_y + r, r, math.pi * 0.5, math.pi * 1.5)
        ctx.close_path()
        ctx.set_source_rgba(0.12, 0.16, 0.24, 0.8)
        ctx.fill()

        # Fill
        fill_w = max(r * 2.0, w * fraction)
        ctx.new_path()
        ctx.arc(fill_w - r, bar_y + r, r, -math.pi * 0.5, math.pi * 0.5)
        ctx.arc(r, bar_y + r, r, math.pi * 0.5, math.pi * 1.5)
        ctx.close_path()
        ctx.set_source_rgba(0.2, 0.7, 1.0, 0.95)
        ctx.fill()

        ctx.restore()


class NetworkPingLatencyLine(Node):
    """Real-time latency sparkline graph with live ms ping readout."""

    def __init__(self, latency: float = 24.0, width: float = 240.0, height: float = 65.0, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.width_val = float(width)
        self.height_val = float(height)
        self.latency = Signal(float(latency), f"{self.name}.latency")

    def draw(self, ctx: Any, time: float = 0.0) -> None:
        w, h = self.width_val, self.height_val
        lat = self.latency.get(time)

        ctx.save()
        # Title
        ctx.select_font_face("Inter", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)
        ctx.set_font_size(11.0)
        ctx.set_source_rgba(0.7, 0.8, 0.9, 0.9)
        ctx.move_to(0.0, 12.0)
        ctx.show_text("Network Latency")

        val_text = f"{int(lat)} ms"
        ext = ctx.text_extents(val_text)
        ctx.move_to(w - ext.width, 12.0)
        ctx.set_source_rgba(0.1, 0.85, 0.5, 0.95)
        ctx.show_text(val_text)

        # Sparkline
        points = [22.0, 24.0, 28.0, 21.0, 25.0, 23.0, lat]
        step = w / (len(points) - 1)
        ctx.set_source_rgba(0.1, 0.85, 0.5, 0.8)
        ctx.set_line_width(1.5)

        for i, p in enumerate(points):
            y = h - 8.0 - (p / 60.0) * (h - 26.0)
            if i == 0:
                ctx.move_to(0, y)
            else:
                ctx.line_to(i * step, y)
        ctx.stroke()

        ctx.restore()


class UptimePercentageBadge(Node):
    """Badge displaying SLA uptime percentage (`99.99% Uptime`)."""

    def __init__(self, uptime: float = 99.98, width: float = 140.0, height: float = 28.0, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.uptime = Signal(float(uptime), f"{self.name}.uptime")
        self.width_val = float(width)
        self.height_val = float(height)

    def draw(self, ctx: Any, time: float = 0.0) -> None:
        w, h = self.width_val, self.height_val
        val = self.uptime.get(time)

        ctx.save()
        r = 6.0
        ctx.new_path()
        ctx.arc(w - r, r, r, -math.pi * 0.5, 0)
        ctx.arc(w - r, h - r, r, 0, math.pi * 0.5)
        ctx.arc(r, h - r, r, math.pi * 0.5, math.pi)
        ctx.arc(r, r, r, math.pi, math.pi * 1.5)
        ctx.close_path()

        ctx.set_source_rgba(0.04, 0.16, 0.1, 0.85)
        ctx.fill_preserve()
        ctx.set_source_rgba(0.1, 0.8, 0.45, 0.7)
        ctx.set_line_width(1.0)
        ctx.stroke()

        ctx.select_font_face("Inter", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
        ctx.set_font_size(11.0)
        ctx.set_source_rgba(0.2, 0.95, 0.55, 0.95)
        text = f"● {val:.2f}% Uptime"
        ext = ctx.text_extents(text)
        ctx.move_to((w - ext.width) * 0.5, h * 0.5 + ext.height * 0.35)
        ctx.show_text(text)
        ctx.restore()


class TelemetryDialHUD(Node):
    """
    Telemetry HUD Suite.
    Renders real-time cluster telemetry dials, memory bars, network ping sparklines,
    and SLA uptime badges with signal reactivity.
    """

    def __init__(
        self,
        cpu: float = 45.0,
        ram: float = 16.4,
        latency: float = 24.0,
        uptime: float = 99.98,
        width: float = 750.0,
        height: float = 400.0,
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)
        self.width_val = float(width)
        self.height_val = float(height)
        self.shadow = DropShadow(color=Color(0.0, 0.0, 0.0, 0.5), blur=32.0, offset=(0.0, 16.0))

        # Dials
        self.cpu_dial = RadialGaugeDial(label="CPU Cluster Load", value=cpu, radius=60.0)
        self.cpu_dial.position.set(Vector2D(130.0, 150.0))

        self.gpu_dial = RadialGaugeDial(label="GPU VRAM Compute", value=68.0, radius=60.0)
        self.gpu_dial.position.set(Vector2D(310.0, 150.0))

        # RAM bar
        self.ram_bar = RamMemoryMeterBar(label="Host RAM Usage", used_gb=ram, total_gb=32.0, width=220.0)
        self.ram_bar.position.set(Vector2D(480.0, 95.0))

        # Latency sparkline
        self.latency_line = NetworkPingLatencyLine(latency=latency, width=220.0, height=60.0)
        self.latency_line.position.set(Vector2D(480.0, 160.0))

        # Uptime Badge
        self.uptime_badge = UptimePercentageBadge(uptime=uptime)
        self.uptime_badge.position.set(Vector2D(self.width_val - 170.0, 24.0))

        self.add(self.cpu_dial, self.gpu_dial, self.ram_bar, self.latency_line, self.uptime_badge)

    def set_metric(
        self,
        metric: Optional[str] = None,
        value: Optional[float] = None,
        name: Optional[str] = None,
        val: Optional[float] = None,
        duration: float = 1.0,
        ease: EasingFunc = Ease.out_quad,
    ) -> AnimationAction:
        """
        Fluent generator animation verb to smoothly update a telemetry metric.
        """
        m_name = (name or metric or "CPU").lower()
        v_num = float(val if val is not None else (value if value is not None else 88.5))
        if "cpu" in m_name:
            return self.cpu_dial.value.to(v_num, duration=duration, ease=ease)
        elif "gpu" in m_name or "vram" in m_name:
            return self.gpu_dial.value.to(v_num, duration=duration, ease=ease)
        elif "ram" in m_name or "memory" in m_name:
            return self.ram_bar.used_gb.to(v_num, duration=duration, ease=ease)
        elif "lat" in m_name or "ping" in m_name:
            return self.latency_line.latency.to(v_num, duration=duration, ease=ease)
        elif "up" in m_name:
            return self.uptime_badge.uptime.to(v_num, duration=duration, ease=ease)
        return self.cpu_dial.value.to(v_num, duration=duration, ease=ease)

    def local_bounds(self, time: float = 0.0) -> Tuple[float, float, float, float]:
        return (0.0, 0.0, self.width_val, self.height_val)

    def draw(self, ctx: Any, time: float = 0.0) -> None:
        w, h = self.width_val, self.height_val
        ctx.save()

        # Canvas card
        r = 16.0
        ctx.new_path()
        ctx.arc(w - r, r, r, -math.pi * 0.5, 0)
        ctx.arc(w - r, h - r, r, 0, math.pi * 0.5)
        ctx.arc(r, h - r, r, math.pi * 0.5, math.pi)
        ctx.arc(r, r, r, math.pi, math.pi * 1.5)
        ctx.close_path()

        ctx.set_source_rgba(0.04, 0.06, 0.1, 0.95)
        ctx.fill_preserve()
        ctx.set_source_rgba(0.18, 0.25, 0.38, 0.8)
        ctx.set_line_width(1.5)
        ctx.stroke()

        # Title
        ctx.select_font_face("Inter", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
        ctx.set_font_size(15.0)
        ctx.set_source_rgba(0.95, 0.98, 1.0, 0.95)
        ctx.move_to(24.0, 42.0)
        ctx.show_text("Live Cluster Telemetry & Node HUD")

        # Divider
        ctx.set_source_rgba(0.2, 0.25, 0.35, 0.4)
        ctx.set_line_width(1.0)
        ctx.move_to(20.0, 64.0)
        ctx.line_to(w - 20.0, 64.0)
        ctx.stroke()

        super().draw(ctx, time)
        ctx.restore()
