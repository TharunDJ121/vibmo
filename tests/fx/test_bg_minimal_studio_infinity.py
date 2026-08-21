import math
import pytest
import cairo
import numpy as np

from vibmo.fx.backgrounds.bg_minimal_studio_infinity import (
    AppleStudioInfinityCyc,
    SoftStageSpotlightBackdrop,
    FrostedGlassHorizon
)
from vibmo.core.color import colors


def test_apple_studio_cyc():
    cyc = AppleStudioInfinityCyc(
        base_color=colors.WHITE,
        bg_color=colors.GRAY,
        floor_color=colors.BLACK,
        width=100.0,
        height=100.0
    )

    # We use a real ImageSurface to verify cairo drawing without needing UI
    surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, 100, 100)
    ctx = cairo.Context(surface)

    cyc.draw(ctx, 0.0)

    # Check pixels to ensure top/bottom parts are drawing
    # Top should have base/bg color
    # Bottom should have floor color
    data = surface.get_data()
    arr = np.ndarray(shape=(100, 100, 4), dtype=np.uint8, buffer=data)

    # Check near top (y=10)
    # The radial gradient center is at x=50, y=0, radius=80
    # At y=10, x=50, it should be close to base_color (white)
    b, g, r, a = arr[10, 50]
    assert r > 200 and g > 200 and b > 200, "Top part of softbox gradient should be light"

    # Check near bottom (y=90)
    # The linear gradient goes from y=70 to y=100, bg->floor
    # At y=90, it should be closer to floor_color (black)
    b2, g2, r2, a2 = arr[90, 50]
    assert r2 < 100 and g2 < 100 and b2 < 100, "Bottom floor shadow gradient should be dark"


def test_soft_stage_spotlight():
    spot = SoftStageSpotlightBackdrop(
        spot_color=colors.WHITE,
        bg_color=colors.BLACK,
        width=100.0,
        height=100.0,
        breath_speed=1.0,
        breath_amplitude=0.5
    )

    surface1 = cairo.ImageSurface(cairo.FORMAT_ARGB32, 100, 100)
    ctx1 = cairo.Context(surface1)

    surface2 = cairo.ImageSurface(cairo.FORMAT_ARGB32, 100, 100)
    ctx2 = cairo.Context(surface2)

    # Base radius calculation in code: min(w,h) * 0.4 = 40.0
    # Radius = 40.0 * (1 + breath)
    # breath = sin(t * pi * b_speed) * b_amp

    # t=0, breath=0, radius=40.0
    spot.draw(ctx1, 0.0)
    data1 = surface1.get_data()
    arr1 = np.ndarray(shape=(100, 100, 4), dtype=np.uint8, buffer=data1)

    # t=0.5, breath=sin(0.5*pi) * 0.5 = 0.5, radius=40.0 * 1.5 = 60.0
    spot.draw(ctx2, 0.5)
    data2 = surface2.get_data()
    arr2 = np.ndarray(shape=(100, 100, 4), dtype=np.uint8, buffer=data2)

    # Check center (x=50, y=50). It should be the spot color (white) in both.
    assert arr1[50, 50][2] > 200 # Red channel > 200 (White)
    assert arr2[50, 50][2] > 200

    # Check edge (x=95, y=50).
    # At t=0, x=95 is distance 45 from center. Since radius is 40.0, it should be black (spot end)
    # Matrix scaling makes x-axis 1.5x larger, so radius in x is actually 40.0 * 1.5 = 60.0.
    # Wait, translating to 50,50 then scale 1.5,1.0 makes x radius = 60.0.
    # So at x=95 (dist 45), it is within the spot (60.0). Let's check further out.

    # Let's check y=95 (dist 45 from center). Y radius is 40.0. So at y=95, it should be bg color (black)
    assert arr1[95, 50][2] < 50, "Outside spot radius should be dark"

    # At t=0.5, Y radius is 60.0. So at y=95 (dist 45), it should be lighter than at t=0
    assert arr2[95, 50][2] > arr1[95, 50][2], "Spot should breathe and expand at t=0.5"


def test_frosted_glass_horizon():
    glass = FrostedGlassHorizon(
        top_color=colors.WHITE,
        bottom_color=colors.BLACK,
        width=100.0,
        height=100.0,
        horizon_y=50.0,
        blur_height=20.0
    )

    surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, 100, 100)
    ctx = cairo.Context(surface)

    glass.draw(ctx, 0.0)

    data = surface.get_data()
    arr = np.ndarray(shape=(100, 100, 4), dtype=np.uint8, buffer=data)

    # Check far top (y=10) -> Should be top_color (white)
    b_t, g_t, r_t, a_t = arr[10, 50]
    assert r_t > 200, "Top should be white"

    # Check far bottom (y=90) -> Should be bottom_color (black)
    b_b, g_b, r_b, a_b = arr[90, 50]
    assert r_b < 50, "Bottom should be black"

    # Check blur line top edge (y=42). Gradient starts at 40 (hy - bh/2).
    # It transitions to bottom color.
    # It should not be pure white or pure black.
    b_m, g_m, r_m, a_m = arr[42, 50]
    assert 50 < r_m < 250, f"Blur edge should be gradient, got R={r_m}"
