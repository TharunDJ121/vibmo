import pytest
import math
import cairo

from vibmo.product.hardware.hw_smart_tv_display_suite import (
    OledSmartTvFrame,
    CurvedCinemaDisplay,
    WallMountedDisplayShadow,
    FloatingTvStand
)
from vibmo.scene.node import Node

class MockContext:
    def __init__(self):
        self.operations = []
        self.saves = 0
        self.restores = 0

    def save(self):
        self.saves += 1
        self.operations.append("save")

    def restore(self):
        self.restores += 1
        self.operations.append("restore")

    def set_source_rgba(self, r, g, b, a):
        self.operations.append(("set_source_rgba", r, g, b, a))

    def rectangle(self, x, y, w, h):
        self.operations.append(("rectangle", x, y, w, h))

    def fill(self):
        self.operations.append("fill")

    def arc(self, xc, yc, radius, angle1, angle2):
        self.operations.append(("arc", xc, yc, radius, angle1, angle2))

    def move_to(self, x, y):
        self.operations.append(("move_to", x, y))

    def curve_to(self, x1, y1, x2, y2, x3, y3):
        self.operations.append(("curve_to", x1, y1, x2, y2, x3, y3))

    def line_to(self, x, y):
        self.operations.append(("line_to", x, y))

    def set_source(self, source):
        self.operations.append(("set_source", source))

    def paint(self):
        self.operations.append("paint")

    def clip(self):
        self.operations.append("clip")

    def new_path(self):
        self.operations.append("new_path")

    def close_path(self):
        self.operations.append("close_path")

    def fill_preserve(self):
        self.operations.append("fill_preserve")

    def set_line_width(self, width):
        self.operations.append(("set_line_width", width))

    def stroke(self):
        self.operations.append("stroke")

    def paint_with_alpha(self, alpha):
        self.operations.append(("paint_with_alpha", alpha))


def test_oled_smart_tv_frame():
    tv = OledSmartTvFrame(width=1280.0, bezel_width=6.0, bottom_lip_height=24.0)

    # Check 16:9 aspect ratio scaling
    expected_height = 1280.0 * (9.0 / 16.0)
    assert tv.height_val == expected_height

    # Check screen dimensions based on bezel calculations
    inner_w = 1280.0 - (6.0 * 2)
    inner_h = expected_height - 6.0 - 24.0

    assert tv.screen.width.get() == inner_w
    assert tv.screen.height.get() == inner_h
    assert tv.screen.position.get() == (6.0, 6.0)

    # Check add_screen_content
    node1 = Node()
    node2 = Node()
    tv.add_screen_content(node1, node2)
    assert node1 in tv.screen.children
    assert node2 in tv.screen.children

    # Check Cairo drawing
    ctx = MockContext()
    tv.draw(ctx)
    assert ctx.saves == 1
    assert ctx.restores == 1
    assert ("rectangle", 0, 0, 1280.0, expected_height) in ctx.operations

def test_curved_cinema_display():
    display = CurvedCinemaDisplay(width=1440.0, height=600.0, bezel_width=12.0, curve_depth=30.0)

    # Check inner screen dimensions
    inner_w = 1440.0 - 24.0
    inner_h = 600.0 - 24.0
    assert display.screen.width.get() == inner_w
    assert display.screen.height.get() == inner_h

    # Check add_screen_content
    node = Node()
    display.add_screen_content(node)
    assert node in display.screen.children

    # Check Cairo drawing
    ctx = MockContext()
    display.draw(ctx)
    assert ctx.saves == 1
    assert ctx.restores == 1
    assert ("move_to", 0, 0) in ctx.operations
    assert ("curve_to", 1440.0 * 0.33, 30.0, 1440.0 * 0.66, 30.0, 1440.0, 0) in ctx.operations

def test_floating_tv_stand():
    stand = FloatingTvStand(width=300.0, height=80.0)
    assert stand.width_val == 300.0
    assert stand.height_val == 80.0

    ctx = MockContext()
    stand.draw(ctx)
    assert ctx.saves == 1
    assert ctx.restores == 1

    # Test rectangle coordinates for vertical pedestal
    ped_w = 80.0
    ped_h = 80.0 - 10.0
    ped_x = (300.0 - 80.0) * 0.5
    assert ("rectangle", ped_x, 0, ped_w, ped_h) in ctx.operations

def test_wall_mounted_display_shadow():
    shadow_node = WallMountedDisplayShadow(width=800.0, height=600.0, elevation=30.0)
    assert shadow_node.width_val == 800.0
    assert shadow_node.height_val == 600.0

    # We use Cairo image surface to run through actual draw since DropShadow
    # uses advanced rendering techniques internally that might break MockContext
    surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, 800, 600)
    ctx = cairo.Context(surface)
    shadow_node.draw(ctx)
    # If this completes without error, basic rendering logic holds up.
