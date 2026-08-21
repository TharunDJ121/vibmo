import pytest
from unittest.mock import MagicMock
import cairo
import re

from vibmo.product.hardware.hw_cctv_surveillance_suite import (
    CctvQuadCameraGrid,
    PtzCameraTargetingHud,
    BodyCamRecOverlay
)

def test_cctv_quad_camera_grid_dimensions():
    grid = CctvQuadCameraGrid(width=1000, height=800)
    assert grid.local_bounds() == (0.0, 0.0, 1000.0, 800.0)
    assert grid.width == 1000
    assert grid.height == 800

def test_cctv_quad_camera_grid_draw():
    grid = CctvQuadCameraGrid(width=100, height=100)
    ctx_mock = MagicMock()
    grid.draw(ctx_mock, time=0.0)

    assert ctx_mock.save.called
    assert ctx_mock.restore.called
    assert ctx_mock.set_source_rgba.called
    assert ctx_mock.stroke.called

    # Check that a timestamp in format YYYY-MM-DD HH:MM:SS was drawn
    calls = [args[0][0] for args in ctx_mock.show_text.call_args_list if args and args[0]]
    timestamp_regex = re.compile(r'\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}')
    assert any(timestamp_regex.match(text) for text in calls), "Timestamp not correctly formatted"

def test_ptz_camera_targeting_hud_dimensions():
    hud = PtzCameraTargetingHud(width=800, height=600, target_x=10, target_y=20, target_w=30, target_h=40)
    assert hud.local_bounds() == (0.0, 0.0, 800.0, 600.0)
    assert hud.target_x == 10
    assert hud.target_y == 20
    assert hud.target_w == 30
    assert hud.target_h == 40

def test_ptz_camera_targeting_hud_draw():
    hud = PtzCameraTargetingHud(width=800, height=600)
    ctx_mock = MagicMock()
    hud.draw(ctx_mock, time=0.0)

    assert ctx_mock.save.called
    assert ctx_mock.restore.called
    assert ctx_mock.set_source_rgba.called
    assert ctx_mock.stroke.called

def test_body_cam_rec_overlay_dimensions():
    overlay = BodyCamRecOverlay(width=1920, height=1080)
    assert overlay.local_bounds() == (0.0, 0.0, 1920.0, 1080.0)
    assert overlay.width == 1920
    assert overlay.height == 1080

def test_body_cam_rec_overlay_draw():
    overlay = BodyCamRecOverlay(width=1920, height=1080, officer_id="TEST_ID", dept="TEST_DEPT")
    ctx_mock = MagicMock()

    class Extents:
        width = 100.0
    ctx_mock.text_extents.return_value = Extents()

    overlay.draw(ctx_mock, time=0.0)

    assert ctx_mock.save.called
    assert ctx_mock.restore.called
    assert ctx_mock.show_text.called

    calls = [args[0][0] for args in ctx_mock.show_text.call_args_list if args and args[0]]
    assert "TEST_DEPT" in calls

    # Check that a timestamp in format YYYY-MM-DDTHH:MM:SSZ was drawn
    timestamp_regex = re.compile(r'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z')
    assert any(timestamp_regex.match(text) for text in calls), "Timestamp not correctly formatted"
