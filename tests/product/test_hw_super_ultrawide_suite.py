import pytest
from unittest.mock import MagicMock
import cairo

from vibmo.product.hardware.hw_super_ultrawide_suite import (
    Curved49InchUltrawide,
    MonitorArmPivotingBase,
    GamerBackGlowRgbLed
)
from vibmo.scene.node import Node
from vibmo.core.color import Color

def test_ultrawide_dimensions():
    # 32:9 ratio test
    height = 360.0
    monitor = Curved49InchUltrawide(height=height)

    assert monitor.height_val == 360.0
    assert monitor.width_val == 360.0 * (32.0 / 9.0)
    assert monitor.width_val == 1280.0

def test_ultrawide_add_screen_content():
    monitor = Curved49InchUltrawide(height=360.0)
    dummy_node = Node(name="dummy")
    monitor.add_screen_content(dummy_node)

    assert dummy_node in monitor.screen.children

def test_ultrawide_layout_slots():
    monitor = Curved49InchUltrawide(height=360.0)
    assert monitor.col_1 is not None
    assert monitor.col_2 is not None
    assert monitor.col_3 is not None

    # We can add them as content
    monitor.add_screen_content(monitor.col_1, monitor.col_2, monitor.col_3)
    assert monitor.col_1 in monitor.screen.children
    assert monitor.col_2 in monitor.screen.children
    assert monitor.col_3 in monitor.screen.children

def test_cairo_rendering():
    # Verify cairo drawing runs without errors
    monitor = Curved49InchUltrawide(height=360.0)
    arm = MonitorArmPivotingBase()
    glow = GamerBackGlowRgbLed()

    surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, 1280, 720)
    ctx = cairo.Context(surface)

    monitor.draw(ctx, 0.0)
    arm.draw(ctx, 0.0)
    glow.draw(ctx, 0.0)

    # We don't verify exact pixels, but ensure no exceptions were raised
    # and basic rendering methods were called via mock context if needed

    mock_ctx = MagicMock()
    monitor.draw(mock_ctx, 0.0)
    assert mock_ctx.arc.called
    assert mock_ctx.curve_to.called
    assert mock_ctx.fill_preserve.called

    mock_ctx.reset_mock()
    arm.draw(mock_ctx, 0.0)
    assert mock_ctx.rectangle.called
    assert mock_ctx.arc.called

    mock_ctx.reset_mock()
    glow.draw(mock_ctx, 0.0)
    assert mock_ctx.rectangle.called
    assert mock_ctx.fill.called
