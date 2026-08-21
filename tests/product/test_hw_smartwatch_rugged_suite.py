import pytest
import math
import cairo
from vibmo.product.hardware.hw_smartwatch_rugged_suite import (
    TitaniumRuggedWatch,
    MinimalistSquareWatch,
    ClassicRoundSmartwatchFace
)
from vibmo.scene.node import Node

class MockContext:
    def __init__(self):
        self.operations = []
        self.clips = 0
        self.translates = []

    def save(self):
        self.operations.append("save")

    def restore(self):
        self.operations.append("restore")

    def set_source_rgba(self, r, g, b, a):
        self.operations.append(("set_source_rgba", r, g, b, a))

    def move_to(self, x, y):
        self.operations.append(("move_to", x, y))

    def line_to(self, x, y):
        self.operations.append(("line_to", x, y))

    def arc(self, x, y, radius, angle1, angle2):
        self.operations.append(("arc", x, y, radius, angle1, angle2))

    def fill(self):
        self.operations.append("fill")

    def fill_preserve(self):
        self.operations.append("fill_preserve")

    def stroke(self):
        self.operations.append("stroke")

    def set_line_width(self, width):
        self.operations.append(("set_line_width", width))

    def close_path(self):
        self.operations.append("close_path")

    def clip(self):
        self.operations.append("clip")
        self.clips += 1

    def translate(self, x, y):
        self.operations.append(("translate", x, y))
        self.translates.append((x, y))

    def new_path(self):
        self.operations.append("new_path")

    def new_sub_path(self):
        self.operations.append("new_sub_path")

    def rectangle(self, x, y, w, h):
        self.operations.append(("rectangle", x, y, w, h))

class MockNode(Node):
    def draw(self, ctx, time=0.0):
        ctx.operations.append("mock_node_drawn")

def test_titanium_rugged_watch_bounds():
    watch = TitaniumRuggedWatch(width=300, height=380)
    bounds = watch.local_bounds()
    assert bounds == (0.0, 0.0, 300.0, 380.0)

def test_minimalist_square_watch_bounds():
    watch = MinimalistSquareWatch(width=280, height=340)
    bounds = watch.local_bounds()
    assert bounds == (0.0, 0.0, 280.0, 340.0)

def test_classic_round_smartwatch_face_bounds():
    watch = ClassicRoundSmartwatchFace(radius=160)
    bounds = watch.local_bounds()
    assert bounds == (0.0, 0.0, 320.0, 320.0)

def test_titanium_rugged_watch_clipping():
    watch = TitaniumRuggedWatch(width=300, height=380, corner_radius=40)
    mock_node = MockNode()
    watch.add_screen_content(mock_node)

    ctx = MockContext()
    watch.draw(ctx)

    assert ctx.clips == 1
    # Check that mock node inside screen container was drawn
    found_mock = False
    for op in ctx.operations:
        if op == "mock_node_drawn":
            found_mock = True
    assert found_mock

    # Assert translation to bezel padding
    assert ctx.translates[-1] == (20.0, 20.0)

def test_minimalist_square_watch_clipping():
    watch = MinimalistSquareWatch(width=280, height=340, corner_radius=45)
    mock_node = MockNode()
    watch.add_screen_content(mock_node)

    ctx = MockContext()
    watch.draw(ctx)

    assert ctx.clips == 1
    # Check that mock node inside screen container was drawn
    found_mock = False
    for op in ctx.operations:
        if op == "mock_node_drawn":
            found_mock = True
    assert found_mock

    # Assert translation to bezel padding
    assert ctx.translates[-1] == (15.0, 15.0)

def test_classic_round_smartwatch_clipping():
    watch = ClassicRoundSmartwatchFace(radius=160)
    mock_node = MockNode()
    watch.add_screen_content(mock_node)

    ctx = MockContext()
    watch.draw(ctx)

    assert ctx.clips == 1
    # Check that mock node inside screen container was drawn
    found_mock = False
    for op in ctx.operations:
        if op == "mock_node_drawn":
            found_mock = True
    assert found_mock

    # Assert translation to bezel padding
    assert ctx.translates[-1] == (25.0, 25.0)
