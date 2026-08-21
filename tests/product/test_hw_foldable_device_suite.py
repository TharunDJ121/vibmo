import pytest
import cairo
import numpy as np

from vibmo.product.hardware.hw_foldable_device_suite import (
    FoldableBookPhone,
    ClamshellFlipPhone,
    DualScreenBookDevice,
    HingeCreaseIndicator
)
from vibmo.scene.node import Node


def get_mock_context() -> cairo.Context:
    surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, 1000, 1000)
    return cairo.Context(surface)


def test_foldable_book_phone_init_and_bounds():
    phone = FoldableBookPhone(width=600, height=400, bezel_width=10, corner_radius=20)
    assert phone.local_bounds() == (0.0, 0.0, 600.0, 400.0)
    assert phone.screen.width.get() == 580.0
    assert phone.screen.height.get() == 380.0


def test_foldable_book_phone_add_content():
    phone = FoldableBookPhone()
    child = Node()
    phone.add_screen_content(child)
    assert child in phone.screen.children


def test_foldable_book_phone_draw():
    phone = FoldableBookPhone()
    ctx = get_mock_context()
    phone.draw(ctx, 0.0)
    # Just verify no crash during draw


def test_clamshell_flip_phone_init_and_bounds():
    phone = ClamshellFlipPhone(width=400, height=800, bezel_width=10)
    assert phone.local_bounds() == (0.0, 0.0, 400.0, 800.0)
    assert phone.screen_top.width.get() == 380.0
    assert phone.screen_top.height.get() == 390.0
    assert phone.screen_bottom.width.get() == 380.0
    assert phone.screen_bottom.height.get() == 390.0


def test_clamshell_flip_phone_add_content():
    phone = ClamshellFlipPhone()
    child = Node()
    phone.add_screen_content(child)
    assert child in phone.screen_top.children


def test_clamshell_flip_phone_draw():
    phone = ClamshellFlipPhone()
    ctx = get_mock_context()
    phone.draw(ctx, 0.0)
    # Just verify no crash during draw


def test_dual_screen_book_device_init_and_bounds():
    device = DualScreenBookDevice(width=816, height=600, bezel_width=10)
    assert device.local_bounds() == (0.0, 0.0, 816.0, 600.0)

    # 816 - 16 (hinge) = 800. Panel w = 400. Inner w = 400 - 20 = 380
    assert device.screen_left.width.get() == 380.0
    assert device.screen_right.width.get() == 380.0


def test_dual_screen_book_device_add_content():
    device = DualScreenBookDevice()
    child = Node()
    device.add_screen_content(child)
    assert child in device.screen_left.children


def test_dual_screen_book_device_draw():
    device = DualScreenBookDevice()
    ctx = get_mock_context()
    device.draw(ctx, 0.0)
    # Just verify no crash during draw


def test_hinge_crease_indicator_init_and_bounds():
    indicator_v = HingeCreaseIndicator(length=400, direction="vertical")
    assert indicator_v.local_bounds() == (-20.0, 0.0, 40.0, 400.0)

    indicator_h = HingeCreaseIndicator(length=300, direction="horizontal")
    assert indicator_h.local_bounds() == (0.0, -20.0, 300.0, 40.0)


def test_hinge_crease_indicator_draw():
    indicator = HingeCreaseIndicator()
    ctx = get_mock_context()
    indicator.progress.set(0.5)
    indicator.draw(ctx, 0.0)
    # Just verify no crash during draw
