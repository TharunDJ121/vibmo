"""
Master verification tests for Section 3 (Hardware Chassis & Device Enclosures).
Tests all 15 suites, all 15 Frame classes, AGENTS.md usage recipes,
unified .add_screen() API, and real PyCairo surface rendering.
"""
import cairo
import pytest
from vibmo.scene.node import Node
from vibmo.layout.container import FlexContainer
from vibmo.product.hardware import (
    # 15 Core Suite Classes
    FoldableDeviceSuite,
    SmartwatchRuggedSuite,
    SuperUltrawideSuite,
    PosRetailSuite,
    CameraViewfinderSuite,
    EInkTabletSuite,
    SmartHomeHubSuite,
    VintageCrtSuite,
    CctvSurveillanceSuite,
    SpatialVisorSuite,
    SmartTvDisplaySuite,
    AutomotiveCockpitSuite,
    GamingHandheldSuite,
    CyberdeckTerminalSuite,
    MultiMonitorSuite,
    # 15 Core Frame Classes
    FoldableDeviceFrame,
    RuggedSmartwatchFrame,
    SuperUltrawideMonitorFrame,
    PosTerminalFrame,
    CameraViewfinderOverlay,
    MinimalistEInkTabletFrame,
    SmartHomeHubFrame,
    RetroArcadeCrtCabinet,
    CctvQuadViewOverlay,
    SpatialVisorFrame,
    OledCinemaTvFrame,
    AutomotiveCockpitDash,
    HandheldGamingConsoleFrame,
    CyberdeckChassisFrame,
    MultiMonitorDeveloperRig,
)


@pytest.fixture
def cairo_ctx() -> cairo.Context:
    surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, 1920, 1080)
    return cairo.Context(surface)


def test_section3_agents_md_recipes(cairo_ctx: cairo.Context) -> None:
    """Test all 15 canonical recipes specified in AGENTS.md Section 3."""
    app_ui = FlexContainer(width=200, height=200)

    # 1. Foldable Device
    phone = FoldableDeviceFrame(fold_angle=30.0)
    phone.add_screen(app_ui)
    assert phone.fold_angle.get(0.0) == 30.0
    phone.draw(cairo_ctx, 0.0)
    phone_from_suite = FoldableDeviceSuite.phone(fold_angle=30.0)
    assert isinstance(phone_from_suite, FoldableDeviceFrame)

    # 2. Rugged Smartwatch
    health_ui = FlexContainer(width=100, height=100)
    watch = RuggedSmartwatchFrame()
    watch.add_screen(health_ui)
    watch.draw(cairo_ctx, 0.0)
    watch_from_suite = SmartwatchRuggedSuite.watch()
    assert isinstance(watch_from_suite, RuggedSmartwatchFrame)

    # 3. Super Ultrawide 32:9
    monitor = SuperUltrawideMonitorFrame(width=1600, curve_depth=45)
    monitor.add_screen(app_ui)
    assert monitor.width_val == 1600.0
    assert monitor.curve_depth == 45.0
    monitor.draw(cairo_ctx, 0.0)
    monitor_from_suite = SuperUltrawideSuite.monitor(width=1600, curve_depth=45)
    assert isinstance(monitor_from_suite, SuperUltrawideMonitorFrame)

    # 4. Point-of-Sale Retail
    checkout_ui = FlexContainer(width=50, height=80)
    pos = PosTerminalFrame()
    pos.add_screen(checkout_ui)
    pos.draw(cairo_ctx, 0.0)
    pos_from_suite = PosRetailSuite.terminal()
    assert isinstance(pos_from_suite, PosTerminalFrame)

    # 5. Camera Viewfinder
    rig = CameraViewfinderOverlay(hud_style="broadcast")
    rig.add_screen(app_ui)
    assert rig.hud_style == "broadcast"
    rig.draw(cairo_ctx, 0.0)
    rig_from_suite = CameraViewfinderSuite.overlay(hud_style="broadcast")
    assert isinstance(rig_from_suite, CameraViewfinderOverlay)

    # 6. E-Ink Tablet
    notes_ui = FlexContainer(width=400, height=600)
    tablet = MinimalistEInkTabletFrame()
    tablet.add_screen(notes_ui)
    tablet.draw(cairo_ctx, 0.0)
    tablet_from_suite = EInkTabletSuite.tablet()
    assert isinstance(tablet_from_suite, MinimalistEInkTabletFrame)

    # 7. Smart Home Hub
    home_ui = FlexContainer(width=400, height=300)
    hub = SmartHomeHubFrame(stand_tilt=20)
    hub.add_screen(home_ui)
    assert hub.stand_tilt == 20.0
    hub.draw(cairo_ctx, 0.0)
    hub_from_suite = SmartHomeHubSuite.hub(stand_tilt=20)
    assert isinstance(hub_from_suite, SmartHomeHubFrame)

    # 8. Retro Arcade CRT
    game_node = Node(name="game_node")
    arcade = RetroArcadeCrtCabinet()
    arcade.add_screen(game_node)
    arcade.draw(cairo_ctx, 0.0)
    arcade_from_suite = VintageCrtSuite.arcade_cabinet()
    assert isinstance(arcade_from_suite, RetroArcadeCrtCabinet)

    # 9. CCTV Surveillance
    cctv = CctvQuadViewOverlay(timestamp=True, rec_indicator=True)
    cctv.add_screen(app_ui, quadrant=1)
    assert cctv.show_timestamp is True
    assert cctv.rec_indicator is True
    cctv.draw(cairo_ctx, 0.0)
    cctv_from_suite = CctvSurveillanceSuite.quad_view(timestamp=True, rec_indicator=True)
    assert isinstance(cctv_from_suite, CctvQuadViewOverlay)

    # 10. Spatial Visor VR
    visor = SpatialVisorFrame(eye_tracking_glow=True)
    visor.add_screen(app_ui)
    assert visor.eye_tracking_glow is True
    visor.draw(cairo_ctx, 0.0)
    visor_from_suite = SpatialVisorSuite.visor(eye_tracking_glow=True)
    assert isinstance(visor_from_suite, SpatialVisorFrame)

    # 11. OLED Cinema TV
    tv = OledCinemaTvFrame(stand_style="center_pedestal")
    tv.add_screen(app_ui)
    assert tv.stand_style == "center_pedestal"
    tv.draw(cairo_ctx, 0.0)
    tv_from_suite = SmartTvDisplaySuite.tv(stand_style="center_pedestal")
    assert isinstance(tv_from_suite, OledCinemaTvFrame)

    # 12. Automotive Cockpit
    dash = AutomotiveCockpitDash(hud_gauges=True)
    dash.add_screen(app_ui)
    assert dash.hud_gauges is True
    dash.draw(cairo_ctx, 0.0)
    dash_from_suite = AutomotiveCockpitSuite.dash(hud_gauges=True)
    assert isinstance(dash_from_suite, AutomotiveCockpitDash)

    # 13. Gaming Handheld
    switch_mock = HandheldGamingConsoleFrame(theme="cyber_neon")
    switch_mock.add_screen(app_ui)
    assert switch_mock.theme == "cyber_neon"
    switch_mock.draw(cairo_ctx, 0.0)
    switch_from_suite = GamingHandheldSuite.console(theme="cyber_neon")
    assert isinstance(switch_from_suite, HandheldGamingConsoleFrame)

    # 14. Cyberdeck Terminal
    deck = CyberdeckChassisFrame(mechanical_switches=True)
    deck.add_screen(app_ui)
    assert deck.mechanical_switches is True
    deck.draw(cairo_ctx, 0.0)
    deck_from_suite = CyberdeckTerminalSuite.chassis(mechanical_switches=True)
    assert isinstance(deck_from_suite, CyberdeckChassisFrame)

    # 15. Multi-Monitor Rig
    dev_rig = MultiMonitorDeveloperRig(left_vertical=True)
    dev_rig.add_screen(app_ui)
    assert dev_rig.left_vertical is True
    assert dev_rig.left_screen is not None
    dev_rig.draw(cairo_ctx, 0.0)
    rig_from_suite = MultiMonitorSuite.developer_rig(left_vertical=True)
    assert isinstance(rig_from_suite, MultiMonitorDeveloperRig)


def test_all_15_frames_add_screen_content_api(cairo_ctx: cairo.Context) -> None:
    """Verify that .add_screen_content(*nodes) is available and functional on all 15 chassis frames."""
    frames = [
        FoldableDeviceFrame(fold_angle=30.0),
        RuggedSmartwatchFrame(),
        SuperUltrawideMonitorFrame(width=1600, curve_depth=45),
        PosTerminalFrame(),
        CameraViewfinderOverlay(hud_style="broadcast"),
        MinimalistEInkTabletFrame(),
        SmartHomeHubFrame(stand_tilt=20),
        RetroArcadeCrtCabinet(),
        CctvQuadViewOverlay(timestamp=True, rec_indicator=True),
        SpatialVisorFrame(eye_tracking_glow=True),
        OledCinemaTvFrame(stand_style="center_pedestal"),
        AutomotiveCockpitDash(hud_gauges=True),
        HandheldGamingConsoleFrame(theme="cyber_neon"),
        CyberdeckChassisFrame(mechanical_switches=True),
        MultiMonitorDeveloperRig(left_vertical=True),
    ]

    for frame in frames:
        child = FlexContainer(width=100, height=100)
        ret = frame.add_screen_content(child)
        assert ret is frame, f"{frame.__class__.__name__}.add_screen_content did not return self"
        frame.draw(cairo_ctx, 0.0)


def test_god_import_all_hardware_symbols() -> None:
    """Verify all 15 suites and frames are exported through God-import."""
    import vibmo
    for sym in [
        "FoldableDeviceSuite", "FoldableDeviceFrame",
        "SmartwatchRuggedSuite", "RuggedSmartwatchFrame",
        "SuperUltrawideSuite", "SuperUltrawideMonitorFrame",
        "PosRetailSuite", "PosTerminalFrame",
        "CameraViewfinderSuite", "CameraViewfinderOverlay",
        "EInkTabletSuite", "MinimalistEInkTabletFrame",
        "SmartHomeHubSuite", "SmartHomeHubFrame",
        "VintageCrtSuite", "RetroArcadeCrtCabinet",
        "CctvSurveillanceSuite", "CctvQuadViewOverlay",
        "SpatialVisorSuite", "SpatialVisorFrame",
        "SmartTvDisplaySuite", "OledCinemaTvFrame",
        "AutomotiveCockpitSuite", "AutomotiveCockpitDash",
        "GamingHandheldSuite", "HandheldGamingConsoleFrame",
        "CyberdeckTerminalSuite", "CyberdeckChassisFrame",
        "MultiMonitorSuite", "MultiMonitorDeveloperRig",
    ]:
        assert hasattr(vibmo, sym), f"Symbol {sym} missing from vibmo God-import namespace"
        assert sym in vibmo.__all__, f"Symbol {sym} missing from vibmo.__all__"
