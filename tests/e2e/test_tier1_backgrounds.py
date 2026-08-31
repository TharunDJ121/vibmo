"""
Tier 1 E2E Tests: Non-Static Animated Backdrops (Section 2).
Covers all 15 procedural backdrop generators with >=5 tests per feature.
"""

import pytest
import cairo
from .conftest import assert_cairo_draw_safe

from vibmo.scene.scene import Scene
from vibmo.core.color import Color, colors
from vibmo.fx.backgrounds.bg_mesh_gradient_flow import MeshGradientFlow
from vibmo.fx.backgrounds.bg_cyber_grid_horizon import CyberGridHorizon
from vibmo.fx.backgrounds.bg_digital_matrix_rain import DigitalMatrixRain
from vibmo.fx.backgrounds.bg_fluid_caustics import FluidWaterCaustics, FluidCaustics
from vibmo.fx.backgrounds.bg_topographic_contours import TopographicContours
from vibmo.fx.backgrounds.bg_circuit_board_traces import PcbCircuitTracesFlow, CircuitBoardTraces
from vibmo.fx.backgrounds.bg_cosmic_nebula import CosmicNebula
from vibmo.fx.backgrounds.bg_retro_crt_scanlines import CrtPhosphorScanlineBackdrop
from vibmo.fx.backgrounds.bg_sunset_horizon_glow import CalifornianSunsetBackdrop
from vibmo.fx.backgrounds.bg_geometric_tessellation import PenroseTilingFlow
from vibmo.fx.backgrounds.bg_bokeh_light_bubbles import BokehLightBubbles
from vibmo.fx.backgrounds.bg_hyperspace_tunnel import HyperspaceTunnel
from vibmo.fx.backgrounds.bg_minimal_studio_infinity import MinimalStudioInfinity
from vibmo.fx.backgrounds.bg_isometric_city_grid import IsometricCityGrid
from vibmo.fx.backgrounds.bg_particle_constellation import ParticleConstellation


# ============================================================================
# 1. Mesh Gradient Flow (>=5 tests)
# ============================================================================

def test_mesh_gradient_flow_defaults():
    bg = MeshGradientFlow()
    assert bg.width == 1920.0
    assert bg.height == 1080.0
    assert_cairo_draw_safe(bg)


def test_mesh_gradient_flow_custom_colors():
    bg = MeshGradientFlow(colors=[colors.INDIGO, colors.CYAN, colors.ROSE])
    assert len(bg.colors) == 3
    assert_cairo_draw_safe(bg)


def test_mesh_gradient_flow_speed_and_complexity():
    bg = MeshGradientFlow(speed=1.5, complexity=6)
    assert bg.speed == 1.5
    assert bg.complexity == 6
    assert_cairo_draw_safe(bg)


def test_mesh_gradient_flow_different_aspect_ratios():
    bg_vert = MeshGradientFlow(width=1080, height=1920)
    bg_sq = MeshGradientFlow(width=1080, height=1080)
    assert_cairo_draw_safe(bg_vert, width=1080, height=1920)
    assert_cairo_draw_safe(bg_sq, width=1080, height=1080)


def test_mesh_gradient_flow_time_evolution():
    bg = MeshGradientFlow()
    surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, 1920, 1080)
    ctx = cairo.Context(surface)
    for t in [0.0, 1.25, 2.5, 5.0]:
        ctx.save()
        bg.draw(ctx, time=t)
        ctx.restore()


# ============================================================================
# 2. Cyber Grid Horizon (>=5 tests)
# ============================================================================

def test_cyber_grid_horizon_defaults():
    grid = CyberGridHorizon()
    assert grid.grid_color is not None
    assert_cairo_draw_safe(grid)


def test_cyber_grid_horizon_custom_perspective():
    grid = CyberGridHorizon(perspective=0.9, horizon_y=600.0)
    assert grid.perspective == 0.9
    assert_cairo_draw_safe(grid)


def test_cyber_grid_horizon_speeds():
    grid_fast = CyberGridHorizon(speed=2.0)
    grid_slow = CyberGridHorizon(speed=0.2)
    assert_cairo_draw_safe(grid_fast)
    assert_cairo_draw_safe(grid_slow)


def test_cyber_grid_horizon_glow_lines():
    grid = CyberGridHorizon(grid_color=colors.FUCHSIA, glow=True)
    assert_cairo_draw_safe(grid)


def test_cyber_grid_horizon_vertical_canvas():
    grid = CyberGridHorizon(width=1080, height=1920)
    assert_cairo_draw_safe(grid, width=1080, height=1920)


# ============================================================================
# 3. Digital Matrix Rain (>=5 tests)
# ============================================================================

def test_digital_matrix_rain_defaults():
    rain = DigitalMatrixRain()
    assert_cairo_draw_safe(rain)


def test_digital_matrix_rain_density():
    rain_dense = DigitalMatrixRain(density=60)
    rain_sparse = DigitalMatrixRain(density=15)
    assert_cairo_draw_safe(rain_dense)
    assert_cairo_draw_safe(rain_sparse)


def test_digital_matrix_rain_glow_color():
    rain_cyan = DigitalMatrixRain(glow_color=colors.CYAN)
    rain_amber = DigitalMatrixRain(glow_color=colors.AMBER)
    assert_cairo_draw_safe(rain_cyan)
    assert_cairo_draw_safe(rain_amber)


def test_digital_matrix_rain_speed_variation():
    rain = DigitalMatrixRain(fall_speed=3.0)
    assert_cairo_draw_safe(rain)


def test_digital_matrix_rain_multi_timestamp():
    rain = DigitalMatrixRain()
    for t in [0.0, 0.5, 1.0, 2.0, 4.0]:
        assert_cairo_draw_safe(rain, timestamps=(t,))


# ============================================================================
# 4. Fluid Caustics (>=5 tests)
# ============================================================================

def test_fluid_caustics_defaults():
    caustics = FluidCaustics()
    assert_cairo_draw_safe(caustics)


def test_fluid_caustics_refraction_levels():
    c_low = FluidCaustics(refraction=0.5)
    c_high = FluidCaustics(refraction=2.0)
    assert_cairo_draw_safe(c_low)
    assert_cairo_draw_safe(c_high)


def test_fluid_caustics_custom_palette():
    caustics = FluidCaustics(water_color=colors.DARK_NAVY, light_color=colors.CYAN)
    assert_cairo_draw_safe(caustics)


def test_fluid_caustics_speed():
    caustics = FluidCaustics(speed=1.5)
    assert caustics.speed == 1.5
    assert_cairo_draw_safe(caustics)


def test_fluid_water_caustics_alias():
    caustics = FluidWaterCaustics()
    assert_cairo_draw_safe(caustics)


# ============================================================================
# 5. Topographic Contours (>=5 tests)
# ============================================================================

def test_topographic_contours_defaults():
    topo = TopographicContours()
    assert_cairo_draw_safe(topo)


def test_topographic_contours_line_spacing():
    topo_dense = TopographicContours(line_spacing=12)
    topo_wide = TopographicContours(line_spacing=48)
    assert_cairo_draw_safe(topo_dense)
    assert_cairo_draw_safe(topo_wide)


def test_topographic_contours_custom_colors():
    topo = TopographicContours(line_color=colors.EMERALD, bg_color=colors.BLACK)
    assert_cairo_draw_safe(topo)


def test_topographic_contours_speed():
    topo = TopographicContours(speed=0.8)
    assert_cairo_draw_safe(topo)


def test_topographic_contours_non_standard_resolutions():
    topo_sq = TopographicContours(width=720, height=720)
    assert_cairo_draw_safe(topo_sq, width=720, height=720)


# ============================================================================
# 6. Circuit Board Traces (>=5 tests)
# ============================================================================

def test_circuit_board_traces_defaults():
    pcb = PcbCircuitTracesFlow()
    assert_cairo_draw_safe(pcb)


def test_circuit_board_traces_alias():
    pcb = CircuitBoardTraces()
    assert_cairo_draw_safe(pcb)


def test_circuit_board_traces_pulse_speed():
    pcb = PcbCircuitTracesFlow(pulse_speed=2.5)
    assert pcb.pulse_speed == 2.5
    assert_cairo_draw_safe(pcb)


def test_circuit_board_traces_custom_colors():
    pcb = PcbCircuitTracesFlow(trace_color=colors.CYAN, pulse_color=colors.WHITE)
    assert_cairo_draw_safe(pcb)


def test_circuit_board_traces_num_traces():
    pcb = PcbCircuitTracesFlow(num_traces=35)
    assert pcb.num_traces == 35
    assert_cairo_draw_safe(pcb)


# ============================================================================
# 7. Cosmic Nebula (>=5 tests)
# ============================================================================

def test_cosmic_nebula_defaults():
    nebula = CosmicNebula()
    assert_cairo_draw_safe(nebula)


def test_cosmic_nebula_star_count():
    nebula_stars = CosmicNebula(star_count=200)
    assert nebula_stars.star_count == 200
    assert_cairo_draw_safe(nebula_stars)


def test_cosmic_nebula_swirl_speed():
    nebula = CosmicNebula(swirl_speed=0.5)
    assert nebula.swirl_speed == 0.5
    assert_cairo_draw_safe(nebula)


def test_cosmic_nebula_palette():
    nebula = CosmicNebula(primary_color=colors.PURPLE, secondary_color=colors.CYAN)
    assert_cairo_draw_safe(nebula)


def test_cosmic_nebula_progression():
    nebula = CosmicNebula()
    for t in [0.0, 1.0, 3.0, 5.0]:
        assert_cairo_draw_safe(nebula, timestamps=(t,))


# ============================================================================
# 8. Retro CRT Scanlines (>=5 tests)
# ============================================================================

def test_retro_crt_scanlines_defaults():
    crt = CrtPhosphorScanlineBackdrop()
    assert_cairo_draw_safe(crt)


def test_retro_crt_scanlines_gap():
    crt = CrtPhosphorScanlineBackdrop(scanline_gap=8)
    assert_cairo_draw_safe(crt)


def test_retro_crt_scanlines_curvature():
    crt = CrtPhosphorScanlineBackdrop(curvature=0.2)
    assert_cairo_draw_safe(crt)


def test_retro_crt_scanlines_phosphor_color():
    crt = CrtPhosphorScanlineBackdrop(phosphor_tint=colors.EMERALD)
    assert_cairo_draw_safe(crt)


def test_retro_crt_scanlines_flicker():
    crt = CrtPhosphorScanlineBackdrop(flicker_intensity=0.1)
    assert_cairo_draw_safe(crt)


# ============================================================================
# 9. Sunset Horizon Glow (>=5 tests)
# ============================================================================

def test_sunset_horizon_glow_defaults():
    sunset = CalifornianSunsetBackdrop()
    assert_cairo_draw_safe(sunset)


def test_sunset_horizon_glow_sun_radius():
    sunset = CalifornianSunsetBackdrop(sun_radius=220)
    assert_cairo_draw_safe(sunset)


def test_sunset_horizon_glow_atmospheric_haze():
    sunset = CalifornianSunsetBackdrop(atmospheric_haze=0.5)
    assert_cairo_draw_safe(sunset)


def test_sunset_horizon_glow_custom_sun_color():
    sunset = CalifornianSunsetBackdrop(sun_color=colors.AMBER)
    assert_cairo_draw_safe(sunset)


def test_sunset_horizon_glow_vertical_frame():
    sunset = CalifornianSunsetBackdrop(width=1080, height=1920)
    assert_cairo_draw_safe(sunset, width=1080, height=1920)


# ============================================================================
# 10. Geometric Tessellation (>=5 tests)
# ============================================================================

def test_geometric_tessellation_defaults():
    tess = PenroseTilingFlow()
    assert_cairo_draw_safe(tess)


def test_geometric_tessellation_poly_types():
    tess_hex = PenroseTilingFlow(pattern_style="hexagonal")
    tess_pen = PenroseTilingFlow(pattern_style="penrose")
    assert_cairo_draw_safe(tess_hex)
    assert_cairo_draw_safe(tess_pen)


def test_geometric_tessellation_morph_speed():
    tess = PenroseTilingFlow(morph_speed=1.5)
    assert tess.morph_speed == 1.5
    assert_cairo_draw_safe(tess)


def test_geometric_tessellation_line_color():
    tess = PenroseTilingFlow(line_color=colors.CYAN)
    assert_cairo_draw_safe(tess)


def test_geometric_tessellation_scale():
    tess = PenroseTilingFlow(tile_scale=60.0)
    assert_cairo_draw_safe(tess)


# ============================================================================
# 11. Bokeh Light Bubbles (>=5 tests)
# ============================================================================

def test_bokeh_light_bubbles_defaults():
    bokeh = BokehLightBubbles()
    assert_cairo_draw_safe(bokeh)


def test_bokeh_light_bubbles_bubble_count():
    bokeh_few = BokehLightBubbles(bubble_count=15)
    bokeh_many = BokehLightBubbles(bubble_count=60)
    assert bokeh_few.bubble_count == 15
    assert bokeh_many.bubble_count == 60
    assert_cairo_draw_safe(bokeh_few)
    assert_cairo_draw_safe(bokeh_many)


def test_bokeh_light_bubbles_blur_radius():
    bokeh = BokehLightBubbles(blur_radius=50.0)
    assert_cairo_draw_safe(bokeh)


def test_bokeh_light_bubbles_palette():
    bokeh = BokehLightBubbles(palette=[colors.ROSE, colors.PURPLE, colors.BLUE])
    assert_cairo_draw_safe(bokeh)


def test_bokeh_light_bubbles_drift_speed():
    bokeh = BokehLightBubbles(drift_speed=1.8)
    assert_cairo_draw_safe(bokeh)


# ============================================================================
# 12. Hyperspace Tunnel (>=5 tests)
# ============================================================================

def test_hyperspace_tunnel_defaults():
    tunnel = HyperspaceTunnel()
    assert_cairo_draw_safe(tunnel)


def test_hyperspace_tunnel_warp_speed():
    tunnel_fast = HyperspaceTunnel(warp_speed=3.5)
    assert tunnel_fast.warp_speed == 3.5
    assert_cairo_draw_safe(tunnel_fast)


def test_hyperspace_tunnel_streak_count():
    tunnel = HyperspaceTunnel(streak_count=150)
    assert tunnel.streak_count == 150
    assert_cairo_draw_safe(tunnel)


def test_hyperspace_tunnel_streak_color():
    tunnel = HyperspaceTunnel(streak_color=colors.CYAN)
    assert_cairo_draw_safe(tunnel)


def test_hyperspace_tunnel_time_progression():
    tunnel = HyperspaceTunnel()
    for t in [0.0, 0.5, 1.5, 3.0]:
        assert_cairo_draw_safe(tunnel, timestamps=(t,))


# ============================================================================
# 13. Minimal Studio Infinity (>=5 tests)
# ============================================================================

def test_minimal_studio_infinity_defaults():
    studio = MinimalStudioInfinity()
    assert_cairo_draw_safe(studio)


def test_minimal_studio_infinity_horizon_y():
    studio = MinimalStudioInfinity(horizon_y=750.0)
    assert studio.horizon_y == 750.0
    assert_cairo_draw_safe(studio)


def test_minimal_studio_infinity_rim_light():
    studio_rim = MinimalStudioInfinity(rim_light=True)
    studio_no_rim = MinimalStudioInfinity(rim_light=False)
    assert_cairo_draw_safe(studio_rim)
    assert_cairo_draw_safe(studio_no_rim)


def test_minimal_studio_infinity_custom_colors():
    studio = MinimalStudioInfinity(floor_color=colors.SLATE_800, wall_color=colors.DARK_NAVY)
    assert_cairo_draw_safe(studio)


def test_minimal_studio_infinity_square_aspect():
    studio = MinimalStudioInfinity(width=1080, height=1080)
    assert_cairo_draw_safe(studio, width=1080, height=1080)


# ============================================================================
# 14. Isometric City Grid (>=5 tests)
# ============================================================================

def test_isometric_city_grid_defaults():
    city = IsometricCityGrid()
    assert_cairo_draw_safe(city)


def test_isometric_city_grid_building_count():
    city = IsometricCityGrid(building_count=70)
    assert city.building_count == 70
    assert_cairo_draw_safe(city)


def test_isometric_city_grid_pulse_lights():
    city = IsometricCityGrid(pulse_lights=True)
    assert_cairo_draw_safe(city)


def test_isometric_city_grid_grid_size():
    city = IsometricCityGrid(grid_size=12)
    assert_cairo_draw_safe(city)


def test_isometric_city_grid_building_palette():
    city = IsometricCityGrid(building_color=colors.SLATE_900, window_color=colors.CYAN)
    assert_cairo_draw_safe(city)


# ============================================================================
# 15. Particle Constellation (>=5 tests)
# ============================================================================

def test_particle_constellation_defaults():
    const = ParticleConstellation()
    assert_cairo_draw_safe(const)


def test_particle_constellation_particle_count():
    const_dense = ParticleConstellation(particle_count=120)
    const_sparse = ParticleConstellation(particle_count=30)
    assert const_dense.particle_count == 120
    assert const_sparse.particle_count == 30
    assert_cairo_draw_safe(const_dense)
    assert_cairo_draw_safe(const_sparse)


def test_particle_constellation_link_radius():
    const = ParticleConstellation(link_radius=150.0)
    assert const.link_radius == 150.0
    assert_cairo_draw_safe(const)


def test_particle_constellation_colors():
    const = ParticleConstellation(particle_color=colors.EMERALD, link_color=colors.CYAN)
    assert_cairo_draw_safe(const)


def test_particle_constellation_animation_movement():
    const = ParticleConstellation(speed=1.5)
    for t in [0.0, 1.0, 2.0, 4.0]:
        assert_cairo_draw_safe(const, timestamps=(t,))
