import pytest
import math
from vibmo.product.hardware.hw_pos_retail_suite import (
    NfcHandheldPosTerminal,
    CountertopRegisterScreen,
    ThermalReceiptSlot,
    TapPaymentSensor
)
from vibmo.core.color import Color

class MockContext:
    def __init__(self):
        self.paths = []
        self.fills = 0
        self.strokes = 0
        self.rects = []
        self.arcs = []
        self.rgba = None
        self.line_width = 1.0

    def set_source_rgba(self, r, g, b, a):
        self.rgba = (r, g, b, a)

    def set_line_width(self, w):
        self.line_width = w

    def new_path(self):
        self.paths.append("new")

    def move_to(self, x, y):
        self.paths.append(("move", x, y))

    def line_to(self, x, y):
        self.paths.append(("line", x, y))

    def arc(self, x, y, radius, angle1, angle2):
        self.arcs.append((x, y, radius, angle1, angle2))

    def close_path(self):
        self.paths.append("close")

    def fill(self):
        self.fills += 1

    def stroke(self):
        self.strokes += 1

    def rectangle(self, x, y, w, h):
        self.rects.append((x, y, w, h))

def test_nfc_handheld_pos_terminal():
    node = NfcHandheldPosTerminal(width=100, height=200)
    assert node.local_bounds(0.0) == (-50.0, -100.0, 100.0, 200.0)

    ctx = MockContext()
    node.draw(ctx, 0.0)

    assert ctx.fills == 2 # base and screen
    assert len(ctx.arcs) == 4 # rounded corners for base
    assert len(ctx.rects) == 1 # screen

    # Test approval animation
    anim = node.approve_payment(duration=1.0)
    node.payment_approved.set(1.0) # simulate end of animation
    assert node.payment_approved.get(1.0) == 1.0

def test_countertop_register_screen():
    node = CountertopRegisterScreen(width=300, height=200, stand_height=100)
    assert node.local_bounds(0.0) == (-150.0, -300.0, 300.0, 300.0)

    ctx = MockContext()
    node.draw(ctx, 0.0)

    assert ctx.fills == 3 # base, main screen body, screen
    assert len(ctx.rects) == 1
    assert len(ctx.arcs) == 4

def test_thermal_receipt_slot():
    node = ThermalReceiptSlot(slot_width=150, receipt_length=200)
    assert node.local_bounds(0.0) == (-75.0, 0, 150.0, 210.0)

    ctx = MockContext()
    node.draw(ctx, 0.0)

    assert ctx.fills == 1 # only slot when progress is 0
    assert len(ctx.rects) == 1

    # Print receipt
    anim = node.print_receipt()
    node.print_progress.set(1.0)

    ctx2 = MockContext()
    node.draw(ctx2, 0.0)

    assert ctx2.fills > 1
    assert len(ctx2.rects) > 1

def test_tap_payment_sensor():
    node = TapPaymentSensor(radius=40)
    assert node.local_bounds(0.0) == (-40.0, -40.0, 80.0, 80.0)

    ctx = MockContext()
    node.draw(ctx, 0.0)

    assert ctx.fills == 5 # 1 bg + 4 LEDs
    assert ctx.strokes == 3 # 3 wave arcs
    assert len(ctx.arcs) == 8 # 1 bg, 3 waves, 4 leds

    # Pulse animation
    anim = node.pulse_led()
    node.pulse.set(1.0)
    assert node.pulse.get(1.0) == 1.0

    # Approve animation
    anim2 = node.approve()
    node.approved.set(1.0)
    assert node.approved.get(1.0) == 1.0
