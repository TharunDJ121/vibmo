"""
Unit tests for Smart Home Hub & IoT Device Mockup suite.
"""

import pytest
import cairo

from vibmo.product.hardware.hw_smart_home_hub_suite import (
    FabricAcousticSmartHub,
    RoundThermostatDial,
    WallMountSecurityKeypad
)
from vibmo.scene.node import Node

class MockContext:
    def __init__(self):
        self.operations = []
        self.paths = []

    def save(self):
        self.operations.append("save")

    def restore(self):
        self.operations.append("restore")

    def translate(self, tx, ty):
        self.operations.append(f"translate({tx}, {ty})")

    def set_source_rgba(self, r, g, b, a):
        self.operations.append(f"set_source_rgba({r}, {g}, {b}, {a})")

    def set_source(self, pat):
        self.operations.append("set_source")

    def set_line_width(self, w):
        self.operations.append(f"set_line_width({w})")

    def move_to(self, x, y):
        self.paths.append(f"move_to({x}, {y})")

    def line_to(self, x, y):
        self.paths.append(f"line_to({x}, {y})")

    def curve_to(self, x1, y1, x2, y2, x3, y3):
        self.paths.append(f"curve_to({x1}, {y1}, {x2}, {y2}, {x3}, {y3})")

    def arc(self, x, y, r, a1, a2):
        self.paths.append(f"arc({x}, {y}, {r}, {a1}, {a2})")

    def rectangle(self, x, y, w, h):
        self.paths.append(f"rectangle({x}, {y}, {w}, {h})")

    def close_path(self):
        self.paths.append("close_path")

    def fill(self):
        self.operations.append("fill")

    def fill_preserve(self):
        self.operations.append("fill_preserve")

    def stroke(self):
        self.operations.append("stroke")

def test_fabric_acoustic_smart_hub():
    hub = FabricAcousticSmartHub(width=800, height=600)

    # Test screen slots
    content = Node(name="test_content")
    hub.add_screen_content(content)
    assert len(hub.screen_content.children) == 1
    assert hub.screen_content.children[0].name == "test_content"

    # Test drawing
    ctx = MockContext()
    hub.draw(ctx)

    assert "save" in ctx.operations
    assert "restore" in ctx.operations
    assert "fill" in ctx.operations or "fill_preserve" in ctx.operations
    # Fabric base and screen both create paths
    assert len(ctx.paths) > 0

def test_round_thermostat_dial():
    dial = RoundThermostatDial(radius=150, temperature=72.0)

    # Test screen slots
    content = Node(name="test_content")
    dial.add_screen_content(content)
    assert len(dial.screen_content.children) == 1
    assert dial.screen_content.children[0].name == "test_content"

    # Test drawing
    ctx = MockContext()
    dial.draw(ctx)

    assert "save" in ctx.operations
    assert "restore" in ctx.operations
    assert "fill" in ctx.operations or "fill_preserve" in ctx.operations
    assert len(ctx.paths) > 0
    # Should draw multiple arcs (outer ring, screen, reflection)
    arc_count = sum(1 for p in ctx.paths if p.startswith("arc("))
    assert arc_count >= 3

def test_wall_mount_security_keypad():
    keypad = WallMountSecurityKeypad(width=300, height=400)

    # Test drawing
    ctx = MockContext()
    keypad.draw(ctx)

    assert "save" in ctx.operations
    assert "restore" in ctx.operations
    assert "fill" in ctx.operations or "fill_preserve" in ctx.operations
    assert len(ctx.paths) > 0

    # Should draw a status LED (arc)
    has_arc = any(p.startswith("arc(") for p in ctx.paths)
    assert has_arc

    # Should draw a screen (rectangle)
    has_rect = any(p.startswith("rectangle(") for p in ctx.paths)
    assert has_rect
