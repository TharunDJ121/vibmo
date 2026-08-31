"""
Tier 3 E2E Tests: Pairwise Cross-Feature Combinations.
Tests combinatorial interactions across all 7 asset suites:
Backdrops x Hardware Enclosures x AI UI x Charts x Kinetic Typography x Audio SFX x Viewport Shaders.
"""

import pytest
import cairo
from .conftest import assert_valid_audio_array, assert_cairo_draw_safe

from vibmo.scene.scene import Scene
from vibmo.core.color import Color, colors
from vibmo.fx.filters import Vignette, FilmGrain

# Backdrops
from vibmo.fx.backgrounds.bg_mesh_gradient_flow import MeshGradientFlow
from vibmo.fx.backgrounds.bg_cyber_grid_horizon import CyberGridHorizon
from vibmo.fx.backgrounds.bg_digital_matrix_rain import DigitalMatrixRain
from vibmo.fx.backgrounds.bg_circuit_board_traces import PcbCircuitTracesFlow
from vibmo.fx.backgrounds.bg_fluid_caustics import FluidWaterCaustics
from vibmo.fx.backgrounds.bg_cosmic_nebula import CosmicNebula
from vibmo.fx.backgrounds.bg_topographic_contours import TopographicContours
from vibmo.fx.backgrounds.bg_sunset_horizon_glow import CalifornianSunsetBackdrop
from vibmo.fx.backgrounds.bg_geometric_tessellation import PenroseTilingFlow
from vibmo.fx.backgrounds.bg_minimal_studio_infinity import MinimalStudioInfinity
from vibmo.fx.backgrounds.bg_isometric_city_grid import IsometricCityGrid
from vibmo.fx.backgrounds.bg_particle_constellation import ParticleConstellation
from vibmo.fx.backgrounds.bg_bokeh_light_bubbles import BokehLightBubbles
from vibmo.fx.backgrounds.bg_hyperspace_tunnel import HyperspaceTunnel
from vibmo.fx.backgrounds.bg_retro_crt_scanlines import CrtPhosphorScanlineBackdrop

# Hardware Frames
from vibmo.product.hardware.hw_foldable_device_suite import FoldableDeviceFrame
from vibmo.product.hardware.hw_super_ultrawide_suite import SuperUltrawideMonitorFrame
from vibmo.product.hardware.hw_vintage_crt_suite import RetroArcadeCrtCabinet
from vibmo.product.hardware.hw_cyberdeck_terminal_suite import CyberdeckChassisFrame
from vibmo.product.hardware.hw_eink_tablet_suite import MinimalistEInkTabletFrame
from vibmo.product.hardware.hw_spatial_visor_suite import SpatialVisorFrame
from vibmo.product.hardware.hw_smartwatch_rugged_suite import RuggedSmartwatchFrame
from vibmo.product.hardware.hw_pos_retail_suite import PosTerminalFrame
from vibmo.product.hardware.hw_multi_monitor_suite import MultiMonitorDeveloperRig
from vibmo.product.hardware.hw_smart_tv_display_suite import OledCinemaTvFrame
from vibmo.product.hardware.hw_automotive_cockpit_suite import AutomotiveCockpitDash
from vibmo.product.hardware.hw_smart_home_hub_suite import SmartHomeHubFrame
from vibmo.product.hardware.hw_gaming_handheld_suite import HandheldGamingConsoleFrame
from vibmo.product.hardware.hw_camera_viewfinder_suite import CameraViewfinderOverlay
from vibmo.product.hardware.hw_cctv_surveillance_suite import CctvQuadViewOverlay

# AI UI
from vibmo.product.ai.ui_token_streamer_suite import StreamingTokenOutput
from vibmo.product.ai.ui_code_sandbox_suite import CodeSandboxPlayground
from vibmo.product.ai.ui_embeddings_space_suite import VectorEmbeddingsVisualizer
from vibmo.product.ai.ui_pricing_matrix_suite import PricingTierMatrix
from vibmo.product.ai.ui_git_pr_timeline_suite import GitPrTimeline
from vibmo.product.ai.ui_tree_of_thought_suite import TreeOfThoughtTree
from vibmo.product.ai.ui_diffusion_canvas_suite import DiffusionCanvas
from vibmo.product.ai.ui_webhook_feed_suite import WebhookActivityFeed

# Charts
from vibmo.charts.chart_candlestick_pro_suite import CandlestickChartPro
from vibmo.charts.chart_speedometer_hud_suite import SpeedometerNeedleGauge
from vibmo.charts.chart_waterfall_flow_suite import WaterfallCostChart
from vibmo.charts.chart_sunburst_radial_suite import SunburstRadialHierarchy
from vibmo.charts.chart_treemap_market_suite import TreemapMarketCapGrid
from vibmo.charts.chart_sankey_flow_suite import SankeyFlowDiagram

# Typography
from vibmo.typography.kinetic.typo_glitch_decryptor_suite import GlitchDecryptorText
from vibmo.typography.kinetic.typo_terminal_typewriter_suite import PhosphorTerminalTypewriter
from vibmo.typography.kinetic.typo_liquid_wave_suite import LiquidWaveText
from vibmo.typography.kinetic.typo_hologram_chroma_suite import HologramChromaText
from vibmo.typography.kinetic.typo_badge_stamp_slam_suite import RubberStampTitleSlam
from vibmo.typography.kinetic.typo_split_flap_suite import SplitFlapAirportBoard
from vibmo.typography.kinetic.typo_odometer_tumbler_suite import OdometerTumblerCounter
from vibmo.typography.kinetic.typo_brush_calligraphy_suite import BrushCalligraphyPathReveal
from vibmo.typography.kinetic.typo_elastic_squash_bounce_suite import ElasticSquashBounceTitle
from vibmo.typography.kinetic.typo_particle_flame_suite import ParticleFlameText
from vibmo.typography.kinetic.typo_slit_scan_synth_suite import SlitScanVideoSynthText

# Audio
from vibmo.audio.generators.sfx_whoosh_designer_suite import WhooshDesignerSuite
from vibmo.audio.generators.sfx_impact_sub_suite import ImpactSubSuite
from vibmo.audio.generators.sfx_glitch_stutter_suite import GlitchStutterSuite
from vibmo.audio.generators.sfx_keyboard_foley_suite import KeyboardFoleySuite
from vibmo.audio.generators.sfx_liquid_bubbles_suite import LiquidBubblesSuite
from vibmo.audio.generators.sfx_ambient_drone_suite import AmbientDroneSuite
from vibmo.audio.generators.sfx_riser_tension_suite import RiserTensionSuite
from vibmo.audio.generators.sfx_paper_card_suite import PaperCardSuite
from vibmo.audio.generators.sfx_cyber_ui_suite import CyberUISFXSuite
from vibmo.audio.generators.sfx_camera_shutter_suite import CameraShutterSuite
from vibmo.audio.generators.sfx_retro_8bit_suite import Retro8BitSuite
from vibmo.audio.generators.sfx_chimes_harmonic_suite import ChimesHarmonicSuite
from vibmo.audio.generators.sfx_alarm_siren_suite import AlarmSirenSuite
from vibmo.audio.generators.sfx_laser_plasma_suite import LaserPlasmaSuite
from vibmo.audio.generators.sfx_vinyl_crackle_suite import VinylCrackleSuite

# Shaders
from vibmo.fx.shaders import (
    CrtPhosphorBloomShader,
    VhsTapeTrackingShader,
    AnamorphicStreakFlare,
    LiquidGlassRefractionFilter,
    AsciiMatrixArtFilter,
)


def test_combo_01_mesh_gradient_foldable_token_streamer(scene_1080p):
    bg = MeshGradientFlow(colors=[colors.INDIGO, colors.CYAN])
    phone = FoldableDeviceFrame(fold_angle=20.0)
    streamer = StreamingTokenOutput(text="Streaming live LLM tokens...")
    phone.add_screen(streamer)
    
    scene_1080p.add(bg)
    scene_1080p.add(phone)
    scene_1080p.add_post_fx(Vignette(intensity=0.3))
    
    sfx = WhooshDesignerSuite.cinematic_passby()
    assert_valid_audio_array(sfx)
    assert_cairo_draw_safe(scene_1080p)


def test_combo_02_cyber_grid_ultrawide_candlestick(scene_1080p):
    bg = CyberGridHorizon(grid_color=colors.CYAN)
    monitor = SuperUltrawideMonitorFrame(width=1600, curve_depth=40.0)
    chart = CandlestickChartPro(data=[
        {"open": 100, "high": 120, "low": 95, "close": 115},
        {"open": 115, "high": 130, "low": 110, "close": 128},
    ])
    monitor.add_screen(chart)
    
    scene_1080p.add(bg)
    scene_1080p.add(monitor)
    scene_1080p.add_post_fx(AnamorphicStreakFlare(threshold=0.8))
    
    sfx = ImpactSubSuite.cinematic_trailer_sub_drop()
    assert_valid_audio_array(sfx)
    assert_cairo_draw_safe(scene_1080p)


def test_combo_03_matrix_rain_arcade_crt_decryptor(scene_1080p):
    bg = DigitalMatrixRain(density=40)
    arcade = RetroArcadeCrtCabinet()
    title = GlitchDecryptorText("CYBER CORE")
    arcade.add_screen(title)
    
    scene_1080p.add(bg)
    scene_1080p.add(arcade)
    scene_1080p.add_post_fx(CrtPhosphorBloomShader(bloom=1.2))
    
    sfx = GlitchStutterSuite.digital_stutter_burst()
    assert_valid_audio_array(sfx)
    assert_cairo_draw_safe(scene_1080p)


def test_combo_04_circuit_traces_cyberdeck_code_sandbox(scene_1080p):
    bg = PcbCircuitTracesFlow(pulse_speed=2.0)
    deck = CyberdeckChassisFrame(mechanical_switches=True)
    code = CodeSandboxPlayground(code="print('Cyberdeck Initialized')")
    deck.add_screen(code)
    
    scene_1080p.add(bg)
    scene_1080p.add(deck)
    
    sfx = KeyboardFoleySuite.clicky_blue_switch()
    assert_valid_audio_array(sfx)
    assert_cairo_draw_safe(scene_1080p)


def test_combo_05_fluid_caustics_eink_liquid_wave(scene_1080p):
    bg = FluidWaterCaustics(refraction=1.2)
    tablet = MinimalistEInkTabletFrame()
    wave = LiquidWaveText("FLUID HARMONY")
    tablet.add_screen(wave)
    
    scene_1080p.add(bg)
    scene_1080p.add(tablet)
    scene_1080p.add_post_fx(LiquidGlassRefractionFilter(refraction=0.3))
    
    sfx = LiquidBubblesSuite.water_bubble_pop()
    assert_valid_audio_array(sfx)
    assert_cairo_draw_safe(scene_1080p)


def test_combo_06_cosmic_nebula_spatial_visor_embeddings(scene_1080p):
    bg = CosmicNebula(swirl_speed=0.3)
    visor = SpatialVisorFrame(eye_tracking_glow=True)
    vec = VectorEmbeddingsVisualizer(num_points=50)
    visor.add_screen(vec)
    
    scene_1080p.add(bg)
    scene_1080p.add(visor)
    
    sfx = AmbientDroneSuite.sci_fi_deep_space_drone()
    assert_valid_audio_array(sfx)
    assert_cairo_draw_safe(scene_1080p)


def test_combo_07_topographic_smartwatch_speedometer(scene_1080p):
    bg = TopographicContours(speed=0.5)
    watch = RuggedSmartwatchFrame()
    speedo = SpeedometerNeedleGauge(value=85.0)
    watch.add_screen(speedo)
    
    scene_1080p.add(bg)
    scene_1080p.add(watch)
    
    sfx = RiserTensionSuite.shepard_tone_riser()
    assert_valid_audio_array(sfx)
    assert_cairo_draw_safe(scene_1080p)


def test_combo_08_sunset_pos_pricing_rubber_stamp(scene_1080p):
    bg = CalifornianSunsetBackdrop()
    pos = PosTerminalFrame()
    pricing = PricingTierMatrix()
    pos.add_screen(pricing)
    stamp = RubberStampTitleSlam("ENTERPRISE APPROVED", color=colors.ROSE)
    
    scene_1080p.add(bg)
    scene_1080p.add(pos)
    scene_1080p.add(stamp)
    
    sfx = PaperCardSuite.card_flip_shuffle()
    assert_valid_audio_array(sfx)
    assert_cairo_draw_safe(scene_1080p)


def test_combo_09_tessellation_multi_monitor_git_waterfall(scene_1080p):
    bg = PenroseTilingFlow()
    rig = MultiMonitorDeveloperRig(left_vertical=True)
    git = GitPrTimeline(pr_number=88)
    waterfall = WaterfallCostChart(steps=[100, -30, 50, -20, 100])
    rig.add_screen(git)
    
    scene_1080p.add(bg)
    scene_1080p.add(rig)
    scene_1080p.add(waterfall)
    
    sfx = CyberUISFXSuite.holographic_click()
    assert_valid_audio_array(sfx)
    assert_cairo_draw_safe(scene_1080p)


def test_combo_10_studio_infinity_oled_tv_sunburst_split_flap(scene_1080p):
    bg = MinimalStudioInfinity(rim_light=True)
    tv = OledCinemaTvFrame()
    sunburst = SunburstRadialHierarchy()
    tv.add_screen(sunburst)
    board = SplitFlapAirportBoard(rows=2, cols=12)
    
    scene_1080p.add(bg)
    scene_1080p.add(tv)
    scene_1080p.add(board)
    scene_1080p.add_post_fx(AsciiMatrixArtFilter(char_size=16))
    
    sfx = CameraShutterSuite.dslr_rapid_burst()
    assert_valid_audio_array(sfx)
    assert_cairo_draw_safe(scene_1080p)


def test_combo_11_city_grid_cockpit_treemap_odometer(scene_1080p):
    bg = IsometricCityGrid(pulse_lights=True)
    dash = AutomotiveCockpitDash(hud_gauges=True)
    treemap = TreemapMarketCapGrid()
    dash.add_screen(treemap)
    odo = OdometerTumblerCounter(start_val=1000, end_val=5000)
    
    scene_1080p.add(bg)
    scene_1080p.add(dash)
    scene_1080p.add(odo)
    
    sfx = Retro8BitSuite.arcade_coin_jump()
    assert_valid_audio_array(sfx)
    assert_cairo_draw_safe(scene_1080p)


def test_combo_12_particle_constellation_hub_sankey_calligraphy(scene_1080p):
    bg = ParticleConstellation(particle_count=60)
    hub = SmartHomeHubFrame()
    sankey = SankeyFlowDiagram()
    hub.add_screen(sankey)
    brush = BrushCalligraphyPathReveal("Zenith Flow")
    
    scene_1080p.add(bg)
    scene_1080p.add(hub)
    scene_1080p.add(brush)
    
    sfx = ChimesHarmonicSuite.celestial_wind_chime()
    assert_valid_audio_array(sfx)
    assert_cairo_draw_safe(scene_1080p)


def test_combo_13_bokeh_handheld_tree_of_thought_squash(scene_1080p):
    bg = BokehLightBubbles(bubble_count=25)
    console = HandheldGamingConsoleFrame(theme="cyber_neon")
    tot = TreeOfThoughtTree()
    console.add_screen(tot)
    title = ElasticSquashBounceTitle("VICTORY!")
    
    scene_1080p.add(bg)
    scene_1080p.add(console)
    scene_1080p.add(title)
    
    sfx = AlarmSirenSuite.emergency_klaxon_sweep()
    assert_valid_audio_array(sfx)
    assert_cairo_draw_safe(scene_1080p)


def test_combo_14_hyperspace_viewfinder_diffusion_flame(scene_1080p):
    bg = HyperspaceTunnel(warp_speed=3.0)
    view = CameraViewfinderOverlay(hud_style="cinema")
    diff = DiffusionCanvas()
    fire = ParticleFlameText("WARP VELOCITY")
    
    scene_1080p.add(bg)
    scene_1080p.add(view)
    scene_1080p.add(diff)
    scene_1080p.add(fire)
    
    sfx = LaserPlasmaSuite.plasma_beam_fire()
    assert_valid_audio_array(sfx)
    assert_cairo_draw_safe(scene_1080p)


def test_combo_15_crt_scanlines_cctv_webhook_slitscan_vhs(scene_1080p):
    bg = CrtPhosphorScanlineBackdrop()
    cctv = CctvQuadViewOverlay(timestamp=True)
    feed = WebhookActivityFeed()
    cctv.add(feed)
    synth = SlitScanVideoSynthText("FEEDBACK LOOP")
    
    scene_1080p.add(bg)
    scene_1080p.add(cctv)
    scene_1080p.add(synth)
    scene_1080p.add_post_fx(VhsTapeTrackingShader(noise=0.15))
    
    sfx = VinylCrackleSuite.vintage_turntable_hiss()
    assert_valid_audio_array(sfx)
    assert_cairo_draw_safe(scene_1080p)
