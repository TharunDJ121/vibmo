import pytest
import cairo
from vibmo.product.ai.ui_telemetry_dial_suite import (
    CircularCpuGaugeDial,
    RamMemoryMeterBar,
    NetworkPingLatencyLine,
    UptimePercentageBadge,
    TelemetryDialHUD,
    RadialGaugeDial,
)

def test_circular_cpu_gauge_dial():
    dial = CircularCpuGaugeDial(label="CPU", value=68.5)
    surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, 200, 200)
    ctx = cairo.Context(surface)
    dial.draw(ctx, time=0.0)
    assert dial.value.get() == 68.5

def test_ram_memory_meter_bar():
    bar = RamMemoryMeterBar(used_gb=12.4, total_gb=16.0)
    surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, 300, 40)
    ctx = cairo.Context(surface)
    bar.draw(ctx, time=0.0)
    assert bar.used_gb.get() == 12.4

def test_network_ping_latency_line():
    line = NetworkPingLatencyLine(history=[12, 14, 18, 15, 13, 11])
    surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, 300, 100)
    ctx = cairo.Context(surface)
    line.draw(ctx, time=0.0)
    assert len(line.history) == 6

def test_uptime_percentage_badge():
    badge = UptimePercentageBadge(uptime_pct=99.99)
    surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, 160, 40)
    ctx = cairo.Context(surface)
    badge.draw(ctx, time=0.0)
    assert badge.uptime_pct == 99.99
