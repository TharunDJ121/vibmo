import pytest
import cairo
import math
import numpy as np
from unittest.mock import MagicMock
from vibmo.typography.kinetic.typo_odometer_tumbler_suite import (
    VerticalRollingGlyphs,
    MechanicalSeparatorCommas,
    TumblerBezelSlot,
    OdometerTumblerCounter
)

def test_vertical_rolling_glyphs_draw():
    # Setup cairo context
    surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, 200, 200)
    ctx = cairo.Context(surface)
    ctx.translate(100, 100)

    # Test drawing a glyph
    glyph = VerticalRollingGlyphs(font_size=20, radius=50)
    glyph.value.set(2.5) # rolling between 2 and 3
    glyph.draw(ctx, 0.0)

    # Verify we actually drew something (buffer shouldn't be all zero)
    buf = surface.get_data()
    assert any(b != 0 for b in buf), "Surface should not be empty after drawing text"

def test_mechanical_separator_commas_draw():
    surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, 50, 50)
    ctx = cairo.Context(surface)
    ctx.translate(25, 25)

    sep = MechanicalSeparatorCommas(text=",", font_size=20)
    sep.draw(ctx, 0.0)

    buf = surface.get_data()
    assert any(b != 0 for b in buf), "Surface should not be empty after drawing separator"

def test_tumbler_bezel_slot_draw():
    surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, 100, 100)
    ctx = cairo.Context(surface)
    ctx.translate(50, 50)

    bezel = TumblerBezelSlot(width=50, height=50)
    bezel.draw(ctx, 0.0)

    buf = surface.get_data()
    assert any(b != 0 for b in buf), "Surface should not be empty after drawing bezel"

def test_odometer_tumbler_math_and_draw():
    # Using the rasterizer to properly test drawing inside the scene graph
    # which sets up transforms appropriately
    from vibmo.render.rasterizer import Rasterizer

    odo = OdometerTumblerCounter(num_digits=4, decimals=1, digit_spacing=20)
    odo.value.set(123.8) # 4 digits, 1 decimal point -> total 4 digits, but decimals=1 means 3 int, 1 frac

    r = Rasterizer(400, 400)
    odo.position.set((200, 200))

    frame = r.render_frame([odo], time=0.0)

    digits = odo.digits
    assert len(digits) == 4

    # Check values set to internal digit signals
    # least significant is index 3 (because it's appended last)
    # the drawing logic iterates over reversed(self.digits)
    # meaning index 3 (the rightmost decimal) represents divisor 1
    # index 2 represents divisor 10, etc.

    assert math.isclose(digits[3].value.get(), 1238.0)
    assert math.isclose(digits[2].value.get(), 123.0)
    assert math.isclose(digits[1].value.get(), 12.0)
    assert math.isclose(digits[0].value.get(), 1.0)

    assert np.max(frame) > 0, "Rendered frame should not be empty after drawing odometer"

def test_odometer_tumbler_roll_to():
    odo = OdometerTumblerCounter()
    odo.roll_to(543.21, duration=1.0)
    # The signal should be scheduled
    # Since we are not running a timeline, value is still 0
    assert odo.value.get() == 0.0
