import math
from typing import Any
from vibmo.scene.node import Node
from vibmo.core.signal import Signal
from vibmo.core.color import Color, colors
from vibmo.core.vector import Vector2D
from vibmo.layout.container import FlexContainer


class CircularCpuGaugeDial(Node):
    """Radial gauge dial displaying live CPU load percentage with color transition."""

    def __init__(self, radius: float = 50.0, load: float = 0.0, stroke_width: float = 8.0, **kwargs):
        super().__init__(**kwargs)
        self.radius = radius
        self.load = Signal(load)
        self.stroke_width = stroke_width

    def _get_color_for_load(self, load_val: float) -> Color:
        # Green -> Amber -> Red transition
        load_val = max(0.0, min(1.0, load_val))
        if load_val < 0.5:
            # Green to Amber
            progress = load_val * 2.0
            return colors.GREEN.lerp(colors.AMBER, progress)
        else:
            # Amber to Red
            progress = (load_val - 0.5) * 2.0
            return colors.AMBER.lerp(colors.RED, progress)

    def draw(self, ctx: Any, time: float = 0.0) -> None:
        load_val = self.load.get(time)
        color = self._get_color_for_load(load_val)

        ctx.save()

        # Draw background track
        ctx.arc(0, 0, self.radius, 0, 2 * math.pi)
        ctx.set_source_rgba(*colors.SLATE_800.to_tuple_rgba())
        ctx.set_line_width(self.stroke_width)
        ctx.stroke()

        # Draw foreground load arc (-90 degrees to start at top)
        start_angle = -math.pi / 2
        end_angle = start_angle + (load_val * 2 * math.pi)

        ctx.arc(0, 0, self.radius, start_angle, end_angle)
        ctx.set_source_rgba(*color.to_tuple_rgba())
        ctx.set_line_width(self.stroke_width)
        ctx.set_line_cap(1) # ROUND
        ctx.stroke()

        ctx.restore()
        super().draw(ctx, time)


class RamMemoryMeterBar(Node):
    """Segmented horizontal RAM memory usage bar."""

    def __init__(self, width: float = 200.0, height: float = 20.0, segments: int = 10, usage: float = 0.0, **kwargs):
        super().__init__(**kwargs)
        self.meter_width = width
        self.meter_height = height
        self.segments = segments
        self.usage = Signal(usage)
        self.gap = 2.0

    def draw(self, ctx: Any, time: float = 0.0) -> None:
        usage_val = self.usage.get(time)
        usage_val = max(0.0, min(1.0, usage_val))

        ctx.save()

        segment_width = (self.meter_width - (self.segments - 1) * self.gap) / self.segments
        active_segments = int(round(usage_val * self.segments))

        current_x = -self.meter_width / 2.0
        start_y = -self.meter_height / 2.0

        for i in range(self.segments):
            ctx.rectangle(current_x, start_y, segment_width, self.meter_height)

            if i < active_segments:
                ctx.set_source_rgba(*colors.INDIGO.to_tuple_rgba())
            else:
                ctx.set_source_rgba(*colors.SLATE_800.to_tuple_rgba())

            ctx.fill()
            current_x += segment_width + self.gap

        ctx.restore()
        super().draw(ctx, time)


class NetworkPingLatencyLine(Node):
    """Animated real-time latency line chart with ping spikes and 99th percentile marker."""

    def __init__(self, width: float = 300.0, height: float = 100.0, history_size: int = 50, **kwargs):
        super().__init__(**kwargs)
        self.chart_width = width
        self.chart_height = height
        self.history_size = history_size
        self.latencies = [20.0 + (i % 5) * 5.0 for i in range(history_size)] # Initial mock history

    def add_latency(self, latency: float):
        self.latencies.append(latency)
        if len(self.latencies) > self.history_size:
            self.latencies.pop(0)

    def draw(self, ctx: Any, time: float = 0.0) -> None:
        ctx.save()

        # Background
        start_x = -self.chart_width / 2.0
        start_y = -self.chart_height / 2.0
        ctx.rectangle(start_x, start_y, self.chart_width, self.chart_height)
        ctx.set_source_rgba(*colors.SLATE_900.to_tuple_rgba())
        ctx.fill()

        if not self.latencies:
            ctx.restore()
            super().draw(ctx, time)
            return

        # Line chart
        max_latency = max(100.0, max(self.latencies)) # minimum max scale is 100ms

        x_step = self.chart_width / max(1, len(self.latencies) - 1)

        ctx.move_to(start_x, start_y + self.chart_height - (self.latencies[0] / max_latency) * self.chart_height)

        for i, latency in enumerate(self.latencies[1:]):
            x = start_x + (i + 1) * x_step
            y = start_y + self.chart_height - (latency / max_latency) * self.chart_height
            ctx.line_to(x, y)

        ctx.set_source_rgba(*colors.CYAN.to_tuple_rgba())
        ctx.set_line_width(2.0)
        ctx.stroke()

        # 99th percentile marker
        sorted_latencies = sorted(self.latencies)
        p99_idx = int(0.99 * len(sorted_latencies))
        if p99_idx < len(sorted_latencies):
            p99_val = sorted_latencies[p99_idx]
            p99_y = start_y + self.chart_height - (p99_val / max_latency) * self.chart_height

            ctx.move_to(start_x, p99_y)
            ctx.line_to(start_x + self.chart_width, p99_y)
            ctx.set_source_rgba(*colors.RED.with_alpha(0.5).to_tuple_rgba())
            ctx.set_line_width(1.0)
            ctx.set_dash([4, 4], 0)
            ctx.stroke()
            ctx.set_dash([], 0) # reset dash

        ctx.restore()
        super().draw(ctx, time)

class UptimePercentageBadge(Node):
    """Emerald pill displaying '99.999% SLA Uptime'."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Using FlexContainer internally or just rendering custom
        self.pill_width = 160.0
        self.pill_height = 36.0
        self.corner_radius = 18.0

    def draw(self, ctx: Any, time: float = 0.0) -> None:
        ctx.save()

        start_x = -self.pill_width / 2.0
        start_y = -self.pill_height / 2.0

        # Pill Background (Emerald)
        # Simple rounded rect
        ctx.new_path()
        ctx.arc(start_x + self.corner_radius, start_y + self.corner_radius, self.corner_radius, math.pi, 1.5 * math.pi)
        ctx.arc(start_x + self.pill_width - self.corner_radius, start_y + self.corner_radius, self.corner_radius, 1.5 * math.pi, 2 * math.pi)
        ctx.arc(start_x + self.pill_width - self.corner_radius, start_y + self.pill_height - self.corner_radius, self.corner_radius, 0, 0.5 * math.pi)
        ctx.arc(start_x + self.corner_radius, start_y + self.pill_height - self.corner_radius, self.corner_radius, 0.5 * math.pi, math.pi)
        ctx.close_path()

        ctx.set_source_rgba(*colors.EMERALD.with_alpha(0.15).to_tuple_rgba())
        ctx.fill_preserve()

        ctx.set_source_rgba(*colors.EMERALD.to_tuple_rgba())
        ctx.set_line_width(1.5)
        ctx.stroke()

        # Draw text "99.999% SLA Uptime"
        # We would normally use KineticText, but we can do a simple cairo text draw for badge
        ctx.set_source_rgba(*colors.EMERALD.to_tuple_rgba())
        ctx.select_font_face("sans-serif", 0, 1) # normal, bold
        ctx.set_font_size(14)

        text = "99.999% SLA Uptime"
        extents = ctx.text_extents(text)
        text_x = start_x + (self.pill_width - extents.width) / 2.0 - extents.x_bearing
        text_y = start_y + (self.pill_height - extents.height) / 2.0 - extents.y_bearing

        ctx.move_to(text_x, text_y)
        ctx.show_text(text)

        ctx.restore()
        super().draw(ctx, time)
