import math
import pytest
from unittest.mock import Mock, call

from vibmo.core.color import colors
from vibmo.product.ai.ui_telemetry_dial_suite import (
    CircularCpuGaugeDial,
    RamMemoryMeterBar,
    NetworkPingLatencyLine,
    UptimePercentageBadge
)

class MockContext:
    def __init__(self):
        self.calls = []
        self.paths = []
        self._current_path = []

    def save(self): self.calls.append(("save",))
    def restore(self): self.calls.append(("restore",))
    
    def arc(self, xc, yc, radius, angle1, angle2):
        self.calls.append(("arc", xc, yc, radius, angle1, angle2))
        self._current_path.append(("arc", xc, yc, radius, angle1, angle2))
        
    def set_source_rgba(self, r, g, b, a): self.calls.append(("set_source_rgba", r, g, b, a))
    def set_line_width(self, w): self.calls.append(("set_line_width", w))
    def set_line_cap(self, c): self.calls.append(("set_line_cap", c))
    def stroke(self): self.calls.append(("stroke",))
    def fill(self): self.calls.append(("fill",))
    def rectangle(self, x, y, w, h): self.calls.append(("rectangle", x, y, w, h))
    def move_to(self, x, y): self.calls.append(("move_to", x, y))
    def line_to(self, x, y): self.calls.append(("line_to", x, y))
    def set_dash(self, dashes, offset): self.calls.append(("set_dash", dashes, offset))
    
    def new_path(self): self.calls.append(("new_path",))
    def close_path(self): self.calls.append(("close_path",))
    def fill_preserve(self): self.calls.append(("fill_preserve",))
    
    def select_font_face(self, family, slant, weight): self.calls.append(("select_font_face", family, slant, weight))
    def set_font_size(self, size): self.calls.append(("set_font_size", size))
    def text_extents(self, text):
        mock_extents = Mock()
        mock_extents.width = 100
        mock_extents.height = 10
        mock_extents.x_bearing = 0
        mock_extents.y_bearing = -10
        self.calls.append(("text_extents", text))
        return mock_extents
    def show_text(self, text): self.calls.append(("show_text", text))
    
    def new_sub_path(self): self.calls.append(("new_sub_path",))
    def clip(self): self.calls.append(("clip",))


def test_circular_cpu_gauge_dial():
    dial = CircularCpuGaugeDial(radius=100.0, load=0.25, stroke_width=10.0)
    ctx = MockContext()
    dial.draw(ctx, time=0.0)
    
    # Assert arc calls
    # 1. Background arc
    # 2. Foreground arc
    arc_calls = [c for c in ctx.calls if c[0] == "arc"]
    assert len(arc_calls) == 2
    
    # Check background arc
    bg_arc = arc_calls[0]
    assert bg_arc[1:4] == (0, 0, 100.0)
    assert bg_arc[4:] == (0, 2 * math.pi)
    
    # Check foreground arc with load=0.25
    fg_arc = arc_calls[1]
    assert fg_arc[1:4] == (0, 0, 100.0)
    start_angle = -math.pi / 2
    end_angle = start_angle + (0.25 * 2 * math.pi)
    assert fg_arc[4] == start_angle
    assert fg_arc[5] == end_angle

    # Color for 0.25 load should be between GREEN and AMBER
    # 0.25 -> progress 0.5
    rgba_calls = [c for c in ctx.calls if c[0] == "set_source_rgba"]
    assert len(rgba_calls) == 2
    bg_color = rgba_calls[0]
    fg_color = rgba_calls[1]
    
    expected_fg_color = colors.GREEN.lerp(colors.AMBER, 0.5).to_tuple_rgba()
    assert fg_color[1:] == expected_fg_color

def test_ram_memory_meter_bar():
    meter = RamMemoryMeterBar(width=100.0, height=20.0, segments=5, usage=0.6)
    ctx = MockContext()
    meter.draw(ctx, time=0.0)
    
    rect_calls = [c for c in ctx.calls if c[0] == "rectangle"]
    assert len(rect_calls) == 5
    
    # usage=0.6, segments=5 -> active_segments = round(0.6 * 5) = 3
    rgba_calls = [c for c in ctx.calls if c[0] == "set_source_rgba"]
    
    assert len(rgba_calls) == 5
    # First 3 segments active (INDIGO)
    for i in range(3):
        assert rgba_calls[i][1:] == colors.INDIGO.to_tuple_rgba()
    # Remaining 2 segments inactive (SLATE_800)
    for i in range(3, 5):
        assert rgba_calls[i][1:] == colors.SLATE_800.to_tuple_rgba()

def test_network_ping_latency_line():
    line = NetworkPingLatencyLine(width=200.0, height=100.0, history_size=10)
    # Clear and set mock history
    line.latencies = [10, 20, 30, 40, 50]
    ctx = MockContext()
    line.draw(ctx, time=0.0)
    
    move_to_calls = [c for c in ctx.calls if c[0] == "move_to"]
    line_to_calls = [c for c in ctx.calls if c[0] == "line_to"]
    
    assert len(move_to_calls) >= 2 # 1 for chart start, 1 for p99 start
    assert len(line_to_calls) >= 4 # 4 segments for 5 points, +1 for p99 line
    
def test_uptime_percentage_badge():
    badge = UptimePercentageBadge()
    ctx = MockContext()
    badge.draw(ctx, time=0.0)
    
    arc_calls = [c for c in ctx.calls if c[0] == "arc"]
    assert len(arc_calls) == 4 # 4 corners
    
    show_text_calls = [c for c in ctx.calls if c[0] == "show_text"]
    assert len(show_text_calls) == 1
    assert show_text_calls[0][1] == "99.999% SLA Uptime"
    
