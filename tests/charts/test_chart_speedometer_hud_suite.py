import math
import cairo
import pytest

from vibmo.charts.chart_speedometer_hud_suite import (
    SpeedometerNeedleGauge,
    RedlineRpmArc,
    DigitalSpeedNumberTicker,
    TurboBoostBar
)

class MockContext:
    def __init__(self):
        self.calls = []

    def set_line_width(self, width):
        self.calls.append(("set_line_width", width))

    def set_source_rgba(self, r, g, b, a):
        self.calls.append(("set_source_rgba", r, g, b, a))

    def arc(self, xc, yc, radius, angle1, angle2):
        self.calls.append(("arc", xc, yc, radius, angle1, angle2))

    def stroke(self):
        self.calls.append(("stroke",))

    def move_to(self, x, y):
        self.calls.append(("move_to", x, y))

    def line_to(self, x, y):
        self.calls.append(("line_to", x, y))

    def save(self):
        self.calls.append(("save",))

    def restore(self):
        self.calls.append(("restore",))

    def clip(self):
        self.calls.append(("clip",))

    def rectangle(self, x, y, width, height):
        self.calls.append(("rectangle", x, y, width, height))

    def show_text(self, text):
        self.calls.append(("show_text", text))

    def select_font_face(self, family, slant, weight):
        self.calls.append(("select_font_face", family, slant, weight))

    def set_font_size(self, size):
        self.calls.append(("set_font_size", size))

def test_speedometer_needle_gauge_angles():
    gauge = SpeedometerNeedleGauge(min_val=0, max_val=100)
    assert math.isclose(gauge._val_to_angle(0), math.pi * 0.75)
    assert math.isclose(gauge._val_to_angle(50), math.pi * 1.5)
    assert math.isclose(gauge._val_to_angle(100), math.pi * 2.25)
    assert math.isclose(gauge._val_to_angle(-10), math.pi * 0.75)
    assert math.isclose(gauge._val_to_angle(110), math.pi * 2.25)

def test_speedometer_needle_gauge_draw():
    gauge = SpeedometerNeedleGauge(min_val=0, max_val=100)
    gauge.display_value.set(50)
    ctx = MockContext()
    gauge.draw(ctx)
    assert any(call[0] == "arc" for call in ctx.calls)
    assert any(call[0] == "line_to" for call in ctx.calls)
    assert any(call[0] == "stroke" for call in ctx.calls)

def test_redline_rpm_arc_pulse_intensity():
    arc = RedlineRpmArc(redline_start=80, redline_end=100)
    arc.value.set(70)
    ctx = MockContext()
    arc.draw(ctx, time=0.0)
    rgba_calls = [c for c in ctx.calls if c[0] == "set_source_rgba"]
    assert rgba_calls[0][4] == 1.0  # Full opacity when below redline

    arc.value.set(90)
    ctx2 = MockContext()
    arc.draw(ctx2, time=0.0) # sin(0) = 0 -> intensity = 0.5
    rgba_calls = [c for c in ctx2.calls if c[0] == "set_source_rgba"]
    assert rgba_calls[0][4] == 0.5

def test_digital_speed_ticker():
    ticker = DigitalSpeedNumberTicker()
    ticker.display_value.set(123)
    ctx = MockContext()
    ticker.draw(ctx)
    text_calls = [c[1] for c in ctx.calls if c[0] == "show_text"]

    # It should show current and next digit for each place.
    # 123 -> digits: 1, 2, 3
    # Fractional part is 0, so next digit isn't strictly visible but is drawn.
    # Text calls for hundreds (1.23): '1', '2'
    # Text calls for tens (12.3): '2', '3'
    # Text calls for units (123.0): '3', '4'
    assert '1' in text_calls
    assert '2' in text_calls
    assert '3' in text_calls

    assert any(c[0] == "clip" for c in ctx.calls)
    assert any(c[0] == "rectangle" for c in ctx.calls)

def test_turbo_boost_bar():
    bar = TurboBoostBar(min_val=-1, max_val=2)
    bar.display_value.set(0.5)

    # -1 is 0.8*pi, 2 is 1.2*pi, range is 3
    # 0.5 is exactly half-way, so angle should be 1.0*pi
    assert math.isclose(bar._val_to_angle(0.5), math.pi)

    ctx = MockContext()
    bar.draw(ctx)
    arcs = [c for c in ctx.calls if c[0] == "arc"]
    assert len(arcs) >= 2 # Background arc and fill arc
    assert any(c[0] == "line_to" for c in ctx.calls)

def test_value_damping():
    # Test that sweep_to, roll_to, fill_to return AnimationAction with proper values
    gauge = SpeedometerNeedleGauge()
    action = gauge.sweep_to(80, duration=2.0)
    assert action.target_value == 80
    assert action.duration == 2.0
    assert gauge.value.get() == 80 # Immediate logical update

    ticker = DigitalSpeedNumberTicker()
    action2 = ticker.roll_to(450)
    assert action2.target_value == 450
    assert ticker.value.get() == 450

    bar = TurboBoostBar()
    action3 = bar.fill_to(1.5)
    assert action3.target_value == 1.5
    assert bar.value.get() == 1.5

def test_actual_cairo_context():
    surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, 200, 200)
    ctx = cairo.Context(surface)

    # Just draw them all to ensure no cairo errors
    gauge = SpeedometerNeedleGauge(min_val=0, max_val=100)
    gauge.draw(ctx)

    arc = RedlineRpmArc()
    arc.draw(ctx)

    ticker = DigitalSpeedNumberTicker()
    ticker.draw(ctx)

    bar = TurboBoostBar()
    bar.draw(ctx)
