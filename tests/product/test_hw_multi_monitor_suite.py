import math
import pytest
from vibmo.product.hardware.hw_multi_monitor_suite import (
    DualDeveloperMonitors,
    VerticalSidecarDisplay,
    TripleCurvedSimulatorDeck,
)
from vibmo.scene.node import Node

class MockContext:
    def __init__(self):
        self.calls = []

    def save(self):
        self.calls.append("save")

    def restore(self):
        self.calls.append("restore")

    def set_source_rgba(self, r, g, b, a):
        self.calls.append(("set_source_rgba", r, g, b, a))

    def rectangle(self, x, y, w, h):
        self.calls.append(("rectangle", x, y, w, h))

    def fill_preserve(self):
        self.calls.append("fill_preserve")

    def set_line_width(self, w):
        self.calls.append(("set_line_width", w))

    def stroke(self):
        self.calls.append("stroke")


def test_dual_developer_monitors():
    suite = DualDeveloperMonitors(screen_width=600, screen_height=340, inward_angle=0.5, gap=20)

    assert suite.left_screen is not None
    assert suite.right_screen is not None
    assert suite.center_screen is None

    # Check content nesting
    n1 = Node()
    n2 = Node()
    suite.left_screen.add_content(n1)
    suite.right_screen.add_content(n2)

    assert n1 in suite.left_screen.content.children
    assert n2 in suite.right_screen.content.children

    # Coordinates check
    assert suite.left_screen.rotate_y.get(0.0) == 0.5
    assert suite.right_screen.rotate_y.get(0.0) == -0.5

    assert suite.left_screen.position.get(0.0).x == -10
    assert suite.right_screen.position.get(0.0).x == 10

    # Draw test
    ctx = MockContext()
    suite.left_screen.draw(ctx)
    assert "save" in ctx.calls
    assert ("rectangle", 0, 0, 600, 340) in ctx.calls


def test_vertical_sidecar_display():
    suite = VerticalSidecarDisplay(primary_width=600, primary_height=340, sidecar_width=340, sidecar_height=600, gap=30)

    assert suite.center_screen is not None
    assert suite.left_screen is not None
    assert getattr(suite, "right_screen", None) is None

    # Coordinates check
    assert suite.center_screen.position.get(0.0).x == 0
    assert suite.center_screen.position.get(0.0).y == 0
    # -(600/2 + 30 + 340/2) = -(300 + 30 + 170) = -500
    assert suite.left_screen.position.get(0.0).x == -500

    # Content nesting
    n1 = Node()
    suite.center_screen.add_content(n1)
    assert n1 in suite.center_screen.content.children


def test_triple_curved_simulator_deck():
    suite = TripleCurvedSimulatorDeck(screen_width=600, screen_height=340, wrap_angle=0.6, gap=10)

    assert suite.left_screen is not None
    assert suite.center_screen is not None
    assert suite.right_screen is not None

    # Coordinates check
    assert suite.center_screen.position.get(0.0).x == 0
    # -(600/2 + 10) = -310
    assert suite.left_screen.position.get(0.0).x == -310
    assert suite.right_screen.position.get(0.0).x == 310

    assert suite.left_screen.rotate_y.get(0.0) == 0.6
    assert suite.right_screen.rotate_y.get(0.0) == -0.6
