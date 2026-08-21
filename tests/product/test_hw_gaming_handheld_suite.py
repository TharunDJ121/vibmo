import pytest
from unittest.mock import MagicMock, call

from vibmo.core.color import Color
from vibmo.product.hardware.hw_gaming_handheld_suite import (
    HandheldBase,
    SteamDeckHandheldChassis,
    SwitchJoyConFrame,
    RetroGameBoyEnclosure,
)
from vibmo.primitives.rect import Rect

def test_steam_deck_handheld_chassis():
    deck = SteamDeckHandheldChassis()

    assert deck.width_val == 800.0
    assert deck.height_val == 360.0
    assert deck.screen_w == 520.0
    assert deck.screen_h == 320.0

    # Check that screen dimensions are correct and positioned in the center
    assert deck.screen.width.get() == 520.0
    assert deck.screen.height.get() == 320.0
    assert deck.screen.position.get().x == (800.0 - 520.0) / 2
    assert deck.screen.position.get().y == (360.0 - 320.0) / 2

    # Check add_screen_content functionality
    rect = Rect(10, 10, fill=Color.hex("#fff"))
    deck.add_screen_content(rect)
    assert rect in deck.screen.children

    # Draw method coverage
    ctx = MagicMock()
    # Mock drawing helper functions to trace coordinates
    deck._draw_thumbstick = MagicMock()
    deck._draw_dpad = MagicMock()
    deck._draw_abxy = MagicMock()

    deck.draw(ctx, 0.0)
    assert ctx.fill.called

    # Verify button coordinates are correct on the steam deck
    deck._draw_thumbstick.assert_any_call(ctx, 70, 80, 25, Color.hex("#333"), Color.hex("#222"))
    deck._draw_thumbstick.assert_any_call(ctx, 800.0 - 70, 180, 25, Color.hex("#333"), Color.hex("#222"))
    deck._draw_dpad.assert_any_call(ctx, 70, 180, 45, Color.hex("#444"))
    deck._draw_abxy.assert_any_call(ctx, 800.0 - 70, 80, 20, 8, Color.hex("#444"))

def test_switch_joycon_frame():
    switch = SwitchJoyConFrame()

    # The center body is 560x320 and joycons are 90x320
    assert switch.center_w == 560.0
    assert switch.center_h == 320.0
    assert switch.joycon_w == 90.0
    assert switch.width_val == 90.0 * 2 + 560.0
    assert switch.height_val == 320.0

    # Check screen dimensions
    assert switch.screen_w == 560.0 - 40.0
    assert switch.screen_h == 320.0 - 40.0

    assert switch.screen.width.get() == switch.screen_w
    assert switch.screen.height.get() == switch.screen_h
    assert switch.screen.position.get().x == 90.0 + 20.0
    assert switch.screen.position.get().y == 20.0

    rect = Rect(10, 10)
    switch.add_screen_content(rect)
    assert rect in switch.screen.children

    ctx = MagicMock()
    switch._draw_thumbstick = MagicMock()
    switch._draw_dpad = MagicMock()
    switch._draw_abxy = MagicMock()

    switch.draw(ctx, 0.0)
    assert ctx.fill.called

    # Verify controls coordinates
    switch._draw_thumbstick.assert_any_call(ctx, 90.0 / 2, 80, 20, Color.hex("#333"), Color.hex("#222"))
    switch._draw_abxy.assert_any_call(ctx, 90.0 / 2, 170, 15, 6, Color.hex("#333"))
    switch._draw_abxy.assert_any_call(ctx, switch.width_val - 90.0 / 2, 80, 15, 6, Color.hex("#333"))
    switch._draw_thumbstick.assert_any_call(ctx, switch.width_val - 90.0 / 2, 170, 20, Color.hex("#333"), Color.hex("#222"))

def test_retro_gameboy_enclosure():
    gameboy = RetroGameBoyEnclosure()

    assert gameboy.width_val == 300.0
    assert gameboy.height_val == 500.0
    assert gameboy.screen_w == 200.0
    assert gameboy.screen_h == 180.0

    assert gameboy.screen.position.get().x == (300.0 - 200.0) / 2
    assert gameboy.screen.position.get().y == 50.0

    rect = Rect(10, 10)
    gameboy.add_screen_content(rect)
    assert rect in gameboy.screen.children

    ctx = MagicMock()
    gameboy._draw_dpad = MagicMock()

    gameboy.draw(ctx, 0.0)
    assert ctx.fill.called

    # Verify d-pad coordinates
    gameboy._draw_dpad.assert_any_call(ctx, 80, 350, 60, Color.hex("#111"))

    # The A/B buttons draw directly onto ctx, we can verify ctx.arc calls
    ctx.arc.assert_has_calls([
        call(220, 370, 15, 0, 3.141592653589793 * 2),
        call(260, 340, 15, 0, 3.141592653589793 * 2)
    ], any_order=True)
