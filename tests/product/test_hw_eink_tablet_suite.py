import pytest
import math
import numpy as np

from vibmo.product.hardware.hw_eink_tablet_suite import (
    PaperEInkReaderFrame,
    StylusPenMockup,
    TextureMatteScreenBezel,
)
from vibmo.core.vector import Vector2D
from vibmo.core.color import Color

# Mock Context to verify Cairo drawing calls
class MockCairoContext:
    def __init__(self):
        self.calls = []

    def save(self):
        self.calls.append(("save",))

    def restore(self):
        self.calls.append(("restore",))

    def set_source_rgba(self, r, g, b, a):
        self.calls.append(("set_source_rgba", r, g, b, a))

    def new_path(self):
        self.calls.append(("new_path",))

    def arc(self, xc, yc, radius, angle1, angle2):
        self.calls.append(("arc", xc, yc, radius, angle1, angle2))

    def close_path(self):
        self.calls.append(("close_path",))

    def fill(self):
        self.calls.append(("fill",))

    def move_to(self, x, y):
        self.calls.append(("move_to", x, y))

    def line_to(self, x, y):
        self.calls.append(("line_to", x, y))

    def set_line_width(self, width):
        self.calls.append(("set_line_width", width))

    def stroke(self):
        self.calls.append(("stroke",))

    def rectangle(self, x, y, width, height):
        self.calls.append(("rectangle", x, y, width, height))

def test_paper_eink_reader_frame_bounds():
    frame = PaperEInkReaderFrame(width=800, height=1200)
    bounds = frame.local_bounds()
    assert bounds == (0.0, 0.0, 800.0, 1200.0)

def test_stylus_pen_mockup_bounds():
    stylus = StylusPenMockup(length=150, radius=5)
    bounds = stylus.local_bounds()
    assert bounds == (0.0, 0.0, 10.0, 150.0)

def test_texture_matte_screen_bezel_bounds():
    matte = TextureMatteScreenBezel(width=600, height=800)
    bounds = matte.local_bounds()
    assert bounds == (0.0, 0.0, 600.0, 800.0)

def test_paper_eink_reader_frame_drawing():
    frame = PaperEInkReaderFrame(width=600, height=800)
    ctx = MockCairoContext()
    frame.draw(ctx, time=0.0)

    call_names = [call[0] for call in ctx.calls]
    assert "save" in call_names
    assert "set_source_rgba" in call_names
    assert "new_path" in call_names
    assert "arc" in call_names
    assert "close_path" in call_names
    assert "fill" in call_names
    assert "move_to" in call_names
    assert "line_to" in call_names
    assert "stroke" in call_names
    assert "restore" in call_names

def test_stylus_pen_mockup_drawing():
    stylus = StylusPenMockup(length=140, radius=4)
    ctx = MockCairoContext()
    stylus.draw(ctx, time=0.0)

    call_names = [call[0] for call in ctx.calls]
    assert "save" in call_names
    assert "set_source_rgba" in call_names
    assert "new_path" in call_names
    assert "arc" in call_names
    assert "line_to" in call_names
    assert "close_path" in call_names
    assert "fill" in call_names
    assert "move_to" in call_names
    assert "set_line_width" in call_names
    assert "stroke" in call_names
    assert "restore" in call_names

def test_texture_matte_screen_bezel_drawing_idle():
    matte = TextureMatteScreenBezel(width=400, height=600)
    ctx = MockCairoContext()
    # At time 0.0, refresh_progress is 0.0
    matte.draw(ctx, time=0.0)

    call_names = [call[0] for call in ctx.calls]
    assert "save" in call_names
    assert "set_source_rgba" in call_names
    assert "rectangle" in call_names
    assert "fill" in call_names
    assert "restore" in call_names

def test_texture_matte_screen_bezel_drawing_refreshing():
    matte = TextureMatteScreenBezel(width=400, height=600)
    # Set refresh progress to trigger artifact drawing
    matte.refresh_progress.set(0.1) # Black flash phase
    ctx = MockCairoContext()
    matte.draw(ctx, time=0.0)

    rgba_calls = [call for call in ctx.calls if call[0] == "set_source_rgba"]
    # Check if dark flash color was set (r=0.1, g=0.1, b=0.1)
    found_black_flash = False
    for call in rgba_calls:
        if call[1] == 0.1 and call[2] == 0.1 and call[3] == 0.1:
            found_black_flash = True
            break
    assert found_black_flash

    # Reset ctx and test white flash phase
    ctx = MockCairoContext()
    matte.refresh_progress.set(0.4)
    matte.draw(ctx, time=0.0)
    rgba_calls = [call for call in ctx.calls if call[0] == "set_source_rgba"]
    found_white_flash = False
    for call in rgba_calls:
        if call[1] == 0.95 and call[2] == 0.95 and call[3] == 0.95:
            found_white_flash = True
            break
    assert found_white_flash

    # Reset ctx and test ghosting phase
    ctx = MockCairoContext()
    matte.refresh_progress.set(0.8)
    matte.draw(ctx, time=0.0)
    rgba_calls = [call for call in ctx.calls if call[0] == "set_source_rgba"]
    found_ghosting = False
    for call in rgba_calls:
        if call[1] == 0.0 and call[2] == 0.0 and call[3] == 0.0:
            found_ghosting = True
            break
    assert found_ghosting
