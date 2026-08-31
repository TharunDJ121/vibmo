"""
Tier 1 E2E Tests: Hardware Chassis & Device Enclosures (Section 3).
Covers all 15 hardware enclosures with >=5 tests per feature.
"""

import pytest
import cairo
from .conftest import assert_cairo_draw_safe

from vibmo.scene.scene import Scene
from vibmo.primitives.rect import Rect
from vibmo.typography.text import Text
from vibmo.core.color import Color, colors

from vibmo.product.hardware.hw_foldable_device_suite import FoldableDeviceFrame
from vibmo.product.hardware.hw_smartwatch_rugged_suite import RuggedSmartwatchFrame
from vibmo.product.hardware.hw_super_ultrawide_suite import SuperUltrawideMonitorFrame
from vibmo.product.hardware.hw_pos_retail_suite import PosTerminalFrame
from vibmo.product.hardware.hw_camera_viewfinder_suite import CameraViewfinderOverlay
from vibmo.product.hardware.hw_eink_tablet_suite import MinimalistEInkTabletFrame
from vibmo.product.hardware.hw_smart_home_hub_suite import SmartHomeHubFrame
from vibmo.product.hardware.hw_vintage_crt_suite import RetroArcadeCrtCabinet
from vibmo.product.hardware.hw_cctv_surveillance_suite import CctvQuadViewOverlay
from vibmo.product.hardware.hw_spatial_visor_suite import SpatialVisorFrame
from vibmo.product.hardware.hw_smart_tv_display_suite import OledCinemaTvFrame
from vibmo.product.hardware.hw_automotive_cockpit_suite import AutomotiveCockpitDash
from vibmo.product.hardware.hw_gaming_handheld_suite import HandheldGamingConsoleFrame
from vibmo.product.hardware.hw_cyberdeck_terminal_suite import CyberdeckChassisFrame
from vibmo.product.hardware.hw_multi_monitor_suite import MultiMonitorDeveloperRig


# ============================================================================
# 1. Foldable Device Frame (>=5 tests)
# ============================================================================

def test_foldable_device_frame_defaults():
    frame = FoldableDeviceFrame()
    assert_cairo_draw_safe(frame)


def test_foldable_device_frame_add_screen():
    frame = FoldableDeviceFrame()
    screen_content = Rect(width=400, height=600, color=colors.CYAN)
    frame.add_screen(screen_content)
    assert_cairo_draw_safe(frame)


def test_foldable_device_frame_fold_angle():
    frame_folded = FoldableDeviceFrame(fold_angle=45.0)
    frame_flat = FoldableDeviceFrame(fold_angle=0.0)
    assert_cairo_draw_safe(frame_folded)
    assert_cairo_draw_safe(frame_flat)


def test_foldable_device_frame_custom_dimensions():
    frame = FoldableDeviceFrame(width=800, height=1000)
    assert_cairo_draw_safe(frame)


def test_foldable_device_frame_multi_timestamp():
    frame = FoldableDeviceFrame()
    frame.add_screen(Text("Foldable Screen", font_size=24, color=colors.WHITE))
    assert_cairo_draw_safe(frame, timestamps=(0.0, 1.0, 2.5))


# ============================================================================
# 2. Rugged Smartwatch Frame (>=5 tests)
# ============================================================================

def test_rugged_smartwatch_defaults():
    watch = RuggedSmartwatchFrame()
    assert_cairo_draw_safe(watch)


def test_rugged_smartwatch_add_screen():
    watch = RuggedSmartwatchFrame()
    screen = Rect(width=200, height=200, color=colors.EMERALD)
    watch.add_screen(screen)
    assert_cairo_draw_safe(watch)


def test_rugged_smartwatch_bezel_styles():
    watch_titanium = RuggedSmartwatchFrame(bezel_color=colors.SLATE_400)
    watch_black = RuggedSmartwatchFrame(bezel_color=colors.BLACK)
    assert_cairo_draw_safe(watch_titanium)
    assert_cairo_draw_safe(watch_black)


def test_rugged_smartwatch_custom_strap():
    watch = RuggedSmartwatchFrame(strap_color=colors.AMBER)
    assert_cairo_draw_safe(watch)


def test_rugged_smartwatch_animation_frame():
    watch = RuggedSmartwatchFrame()
    watch.add_screen(Text("120 BPM", font_size=28, color=colors.ROSE))
    assert_cairo_draw_safe(watch, timestamps=(0.0, 0.5, 1.5))


# ============================================================================
# 3. Super Ultrawide Monitor Frame (>=5 tests)
# ============================================================================

def test_super_ultrawide_defaults():
    monitor = SuperUltrawideMonitorFrame()
    assert_cairo_draw_safe(monitor)


def test_super_ultrawide_curve_depth():
    monitor_curved = SuperUltrawideMonitorFrame(curve_depth=50.0)
    monitor_flat = SuperUltrawideMonitorFrame(curve_depth=0.0)
    assert_cairo_draw_safe(monitor_curved)
    assert_cairo_draw_safe(monitor_flat)


def test_super_ultrawide_add_screen():
    monitor = SuperUltrawideMonitorFrame()
    content = Rect(width=1600, height=600, color=colors.DARK_NAVY)
    monitor.add_screen(content)
    assert_cairo_draw_safe(monitor)


def test_super_ultrawide_custom_aspect():
    monitor = SuperUltrawideMonitorFrame(width=1800, height=600)
    assert_cairo_draw_safe(monitor)


def test_super_ultrawide_stand_and_bezel():
    monitor = SuperUltrawideMonitorFrame(stand=True, bezel_thickness=12.0)
    assert_cairo_draw_safe(monitor)


# ============================================================================
# 4. Point-of-Sale Retail Terminal (>=5 tests)
# ============================================================================

def test_pos_terminal_defaults():
    pos = PosTerminalFrame()
    assert_cairo_draw_safe(pos)


def test_pos_terminal_add_screen():
    pos = PosTerminalFrame()
    pos.add_screen(Text("$42.50 Paid", font_size=32, color=colors.EMERALD))
    assert_cairo_draw_safe(pos)


def test_pos_terminal_nfc_card_reader():
    pos = PosTerminalFrame(nfc_sensor=True)
    assert_cairo_draw_safe(pos)


def test_pos_terminal_receipt_printer_slot():
    pos = PosTerminalFrame(receipt_slot=True)
    assert_cairo_draw_safe(pos)


def test_pos_terminal_custom_dimensions():
    pos = PosTerminalFrame(width=600, height=750)
    assert_cairo_draw_safe(pos)


# ============================================================================
# 5. Camera Viewfinder Overlay (>=5 tests)
# ============================================================================

def test_camera_viewfinder_defaults():
    viewfinder = CameraViewfinderOverlay()
    assert_cairo_draw_safe(viewfinder)


def test_camera_viewfinder_hud_styles():
    v_broadcast = CameraViewfinderOverlay(hud_style="broadcast")
    v_cinema = CameraViewfinderOverlay(hud_style="cinema")
    assert_cairo_draw_safe(v_broadcast)
    assert_cairo_draw_safe(v_cinema)


def test_camera_viewfinder_recording_indicator():
    viewfinder = CameraViewfinderOverlay(rec_indicator=True)
    assert_cairo_draw_safe(viewfinder)


def test_camera_viewfinder_gridlines():
    viewfinder = CameraViewfinderOverlay(rule_of_thirds=True, center_cross=True)
    assert_cairo_draw_safe(viewfinder)


def test_camera_viewfinder_custom_telemetry():
    viewfinder = CameraViewfinderOverlay(iso=800, shutter="1/50", fps=24)
    assert_cairo_draw_safe(viewfinder)


# ============================================================================
# 6. E-Ink Tablet Frame (>=5 tests)
# ============================================================================

def test_eink_tablet_defaults():
    tablet = MinimalistEInkTabletFrame()
    assert_cairo_draw_safe(tablet)


def test_eink_tablet_add_screen():
    tablet = MinimalistEInkTabletFrame()
    tablet.add_screen(Text("Document Notes Page 1", font_size=20, color=colors.BLACK))
    assert_cairo_draw_safe(tablet)


def test_eink_tablet_stylus_pen():
    tablet = MinimalistEInkTabletFrame(stylus_pen=True)
    assert_cairo_draw_safe(tablet)


def test_eink_tablet_paper_texture():
    tablet = MinimalistEInkTabletFrame(paper_tone="warm_canvas")
    assert_cairo_draw_safe(tablet)


def test_eink_tablet_bezel_scale():
    tablet = MinimalistEInkTabletFrame(bezel_width=30.0)
    assert_cairo_draw_safe(tablet)


# ============================================================================
# 7. Smart Home Hub Frame (>=5 tests)
# ============================================================================

def test_smart_home_hub_defaults():
    hub = SmartHomeHubFrame()
    assert_cairo_draw_safe(hub)


def test_smart_home_hub_stand_tilt():
    hub_tilted = SmartHomeHubFrame(stand_tilt=25.0)
    assert_cairo_draw_safe(hub_tilted)


def test_smart_home_hub_add_screen():
    hub = SmartHomeHubFrame()
    hub.add_screen(Text("72° Living Room", font_size=36, color=colors.CYAN))
    assert_cairo_draw_safe(hub)


def test_smart_home_hub_fabric_base():
    hub = SmartHomeHubFrame(base_color=colors.SLATE_800)
    assert_cairo_draw_safe(hub)


def test_smart_home_hub_dimensions():
    hub = SmartHomeHubFrame(width=700, height=450)
    assert_cairo_draw_safe(hub)


# ============================================================================
# 8. Retro Arcade CRT Cabinet (>=5 tests)
# ============================================================================

def test_arcade_crt_defaults():
    arcade = RetroArcadeCrtCabinet()
    assert_cairo_draw_safe(arcade)


def test_arcade_crt_add_screen():
    arcade = RetroArcadeCrtCabinet()
    arcade.add_screen(Rect(width=320, height=240, color=colors.PURPLE))
    assert_cairo_draw_safe(arcade)


def test_arcade_crt_joystick_and_buttons():
    arcade = RetroArcadeCrtCabinet(controls=True)
    assert_cairo_draw_safe(arcade)


def test_arcade_crt_marquee_glow():
    arcade = RetroArcadeCrtCabinet(marquee_text="VIBMO 1984")
    assert_cairo_draw_safe(arcade)


def test_arcade_crt_curved_screen():
    arcade = RetroArcadeCrtCabinet(barrel_curvature=0.15)
    assert_cairo_draw_safe(arcade)


# ============================================================================
# 9. CCTV Surveillance Quad View (>=5 tests)
# ============================================================================

def test_cctv_quad_view_defaults():
    cctv = CctvQuadViewOverlay()
    assert_cairo_draw_safe(cctv)


def test_cctv_quad_view_timestamp_overlay():
    cctv = CctvQuadViewOverlay(timestamp=True)
    assert_cairo_draw_safe(cctv)


def test_cctv_quad_view_channel_labels():
    cctv = CctvQuadViewOverlay(channels=["CAM 01", "CAM 02", "CAM 03", "CAM 04"])
    assert_cairo_draw_safe(cctv)


def test_cctv_quad_view_active_channel():
    cctv = CctvQuadViewOverlay(active_channel=2)
    assert_cairo_draw_safe(cctv)


def test_cctv_quad_view_rec_glitch():
    cctv = CctvQuadViewOverlay(rec_indicator=True, noise_level=0.1)
    assert_cairo_draw_safe(cctv)


# ============================================================================
# 10. Spatial Visor VR Frame (>=5 tests)
# ============================================================================

def test_spatial_visor_defaults():
    visor = SpatialVisorFrame()
    assert_cairo_draw_safe(visor)


def test_spatial_visor_eye_tracking_glow():
    visor = SpatialVisorFrame(eye_tracking_glow=True)
    assert_cairo_draw_safe(visor)


def test_spatial_visor_add_screen():
    visor = SpatialVisorFrame()
    visor.add_screen(Text("Spatial HUD 3D", font_size=32, color=colors.CYAN))
    assert_cairo_draw_safe(visor)


def test_spatial_visor_headband_strap():
    visor = SpatialVisorFrame(strap=True, strap_color=colors.SLATE_800)
    assert_cairo_draw_safe(visor)


def test_spatial_visor_glass_reflection():
    visor = SpatialVisorFrame(glass_reflection=True)
    assert_cairo_draw_safe(visor)


# ============================================================================
# 11. OLED Cinema TV Frame (>=5 tests)
# ============================================================================

def test_oled_cinema_tv_defaults():
    tv = OledCinemaTvFrame()
    assert_cairo_draw_safe(tv)


def test_oled_cinema_tv_add_screen():
    tv = OledCinemaTvFrame()
    tv.add_screen(Rect(width=1280, height=720, color=colors.DARK_NAVY))
    assert_cairo_draw_safe(tv)


def test_oled_cinema_tv_stand_style():
    tv_pedestal = OledCinemaTvFrame(stand_style="center_pedestal")
    tv_wall = OledCinemaTvFrame(stand_style="wall_mount")
    assert_cairo_draw_safe(tv_pedestal)
    assert_cairo_draw_safe(tv_wall)


def test_oled_cinema_tv_ambient_backlight():
    tv = OledCinemaTvFrame(ambient_glow=True, glow_color=colors.CYAN)
    assert_cairo_draw_safe(tv)


def test_oled_cinema_tv_dimensions():
    tv = OledCinemaTvFrame(width=1400, height=800)
    assert_cairo_draw_safe(tv)


# ============================================================================
# 12. Automotive Cockpit Dash (>=5 tests)
# ============================================================================

def test_automotive_cockpit_defaults():
    dash = AutomotiveCockpitDash()
    assert_cairo_draw_safe(dash)


def test_automotive_cockpit_hud_gauges():
    dash = AutomotiveCockpitDash(hud_gauges=True)
    assert_cairo_draw_safe(dash)


def test_automotive_cockpit_speed_and_rpm():
    dash = AutomotiveCockpitDash(speed=110, rpm=3500)
    assert_cairo_draw_safe(dash)


def test_automotive_cockpit_add_screen():
    dash = AutomotiveCockpitDash()
    dash.add_screen(Text("Turn Right in 200m", font_size=28, color=colors.CYAN))
    assert_cairo_draw_safe(dash)


def test_automotive_cockpit_theme():
    dash_sport = AutomotiveCockpitDash(theme="sport_red")
    dash_eco = AutomotiveCockpitDash(theme="eco_cyan")
    assert_cairo_draw_safe(dash_sport)
    assert_cairo_draw_safe(dash_eco)


# ============================================================================
# 13. Gaming Handheld Console Frame (>=5 tests)
# ============================================================================

def test_gaming_handheld_defaults():
    handheld = HandheldGamingConsoleFrame()
    assert_cairo_draw_safe(handheld)


def test_gaming_handheld_theme_cyber_neon():
    handheld = HandheldGamingConsoleFrame(theme="cyber_neon")
    assert_cairo_draw_safe(handheld)


def test_gaming_handheld_add_screen():
    handheld = HandheldGamingConsoleFrame()
    handheld.add_screen(Rect(width=800, height=480, color=colors.BLACK))
    assert_cairo_draw_safe(handheld)


def test_gaming_handheld_dpad_and_thumbsticks():
    handheld = HandheldGamingConsoleFrame(thumbsticks=True, dpad=True)
    assert_cairo_draw_safe(handheld)


def test_gaming_handheld_shoulder_triggers():
    handheld = HandheldGamingConsoleFrame(shoulder_buttons=True)
    assert_cairo_draw_safe(handheld)


# ============================================================================
# 14. Cyberdeck Chassis Frame (>=5 tests)
# ============================================================================

def test_cyberdeck_chassis_defaults():
    deck = CyberdeckChassisFrame()
    assert_cairo_draw_safe(deck)


def test_cyberdeck_chassis_mechanical_switches():
    deck = CyberdeckChassisFrame(mechanical_switches=True)
    assert_cairo_draw_safe(deck)


def test_cyberdeck_chassis_add_screen():
    deck = CyberdeckChassisFrame()
    deck.add_screen(Text("NEO-TOKYO CYBERDECK OS v4.2", font_size=24, color=colors.EMERALD))
    assert_cairo_draw_safe(deck)


def test_cyberdeck_chassis_carrying_handle():
    deck = CyberdeckChassisFrame(carrying_handle=True)
    assert_cairo_draw_safe(deck)


def test_cyberdeck_chassis_patch_cables():
    deck = CyberdeckChassisFrame(patch_cables=True)
    assert_cairo_draw_safe(deck)


# ============================================================================
# 15. Multi-Monitor Developer Rig (>=5 tests)
# ============================================================================

def test_multi_monitor_rig_defaults():
    rig = MultiMonitorDeveloperRig()
    assert_cairo_draw_safe(rig)


def test_multi_monitor_rig_left_vertical():
    rig = MultiMonitorDeveloperRig(left_vertical=True)
    assert_cairo_draw_safe(rig)


def test_multi_monitor_rig_right_vertical():
    rig = MultiMonitorDeveloperRig(right_vertical=True)
    assert_cairo_draw_safe(rig)


def test_multi_monitor_rig_add_screens():
    rig = MultiMonitorDeveloperRig()
    rig.add_screen(Rect(width=800, height=450, color=colors.DARK_NAVY))
    assert_cairo_draw_safe(rig)


def test_multi_monitor_rig_desk_mount_arm():
    rig = MultiMonitorDeveloperRig(desk_arm=True)
    assert_cairo_draw_safe(rig)
