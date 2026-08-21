import pytest
import cairo
from vibmo.product.hardware.hw_automotive_cockpit_suite import (
    TeslaCenterTouchscreen,
    CarPlayDashboardPill,
    DigitalGaugeClusterHud,
)

def test_tesla_center_touchscreen():
    touchscreen = TeslaCenterTouchscreen(width=1200, height=750)
    assert touchscreen.width_val == 1200
    assert touchscreen.height_val == 750
    assert len(touchscreen.children) == 1

    # Test local bounds
    bounds = touchscreen.local_bounds()
    assert bounds == (0.0, 0.0, 1200.0, 750.0)

    # Test draw
    surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, 1200, 750)
    ctx = cairo.Context(surface)
    touchscreen.draw(ctx)

def test_car_play_dashboard_pill():
    pill = CarPlayDashboardPill(width=1400, height=400)
    assert pill.width_val == 1400
    assert pill.height_val == 400
    assert len(pill.children) == 1

    # Test local bounds
    bounds = pill.local_bounds()
    assert bounds == (0.0, 0.0, 1400.0, 400.0)

    # Test draw
    surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, 1400, 400)
    ctx = cairo.Context(surface)
    pill.draw(ctx)

def test_digital_gauge_cluster_hud():
    hud = DigitalGaugeClusterHud(width=1000, height=500, speed=50.0, battery_percentage=80.0)
    assert hud.width_val == 1000
    assert hud.height_val == 500
    assert hud.speed.get(0) == 50.0
    assert hud.battery.get(0) == 80.0

    # Test local bounds
    bounds = hud.local_bounds()
    assert bounds == (0.0, 0.0, 1000.0, 500.0)

    # Test draw
    surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, 1000, 500)
    ctx = cairo.Context(surface)
    hud.draw(ctx)

    # Test animation
    action = hud.set_speed(100.0, duration=1.0)
    assert action is not None
