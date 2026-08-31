"""
Unit tests explicitly verifying AGENTS.md Section 2 Backdrops catalog recipes,
aliases, dispatchers, and constructor kwargs.
"""

import cairo
import numpy as np
import pytest

from vibmo.core.color import colors, Color
from vibmo.fx.backgrounds import (
    MeshGradientFlow,
    CyberGridHorizon,
    DigitalMatrixRain,
    FluidCaustics,
    TopographicContours,
    CircuitBoardTraces,
    CosmicNebula,
    RetroCrtScanlines,
    SunsetHorizonGlow,
    GeometricTessellation,
    BokehLightBubbles,
    HyperspaceTunnel,
    MinimalStudioInfinity,
    IsometricCityGrid,
    ParticleConstellation,
    # Underlying classes
    CrtPhosphorScanlineBackdrop,
    CalifornianSunsetBackdrop,
    HexagonalHoneyGridPulse,
    VoronoiCellEvolution,
    PenroseTilingFlow,
)


def _draw_to_surface(node, width=320, height=240, time=0.0):
    surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, width, height)
    ctx = cairo.Context(surface)
    if hasattr(node, "draw"):
        node.draw(ctx, time)
    elif hasattr(node, "render"):
        class DummySurface:
            def __init__(self, w, h):
                self.surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, w, h)
                self.context = cairo.Context(self.surface)
        class DummyRenderCtx:
            def get_surface(self, w, h):
                return DummySurface(w, h)
        node.render(time, DummyRenderCtx())
    return surface


def test_recipe_1_mesh_gradient_flow():
    bg = MeshGradientFlow(colors=[colors.INDIGO, colors.CYAN], speed=0.8)
    assert bg.speed_multiplier == 0.8
    assert len(bg.colors_list) >= 2
    surf = _draw_to_surface(bg, 320, 240, time=0.5)
    assert surf is not None


def test_recipe_2_cyber_grid_horizon():
    bg = CyberGridHorizon(grid_color=colors.CYAN, perspective=0.8)
    assert bg.horizon_pitch(0.0) == 0.8
    surf = _draw_to_surface(bg, 320, 240, time=0.5)
    assert surf is not None


def test_recipe_3_digital_matrix_rain():
    bg = DigitalMatrixRain(density=40, glow_color=colors.EMERALD)
    assert bg.density == 40
    assert bg.glow_color == colors.EMERALD
    surf = _draw_to_surface(bg, 320, 240, time=0.5)
    assert surf is not None


def test_recipe_4_fluid_caustics():
    bg = FluidCaustics(refraction=1.2, speed=0.5)
    assert bg.refraction == 1.2
    assert bg.speed == 0.5
    surf = _draw_to_surface(bg, 320, 240, time=0.5)
    assert surf is not None


def test_recipe_5_topographic_contours():
    bg = TopographicContours(line_spacing=24, speed=0.4)
    assert bg.line_spacing == 24
    assert bg.speed == 0.4
    surf = _draw_to_surface(bg, 320, 240, time=0.5)
    assert surf is not None


def test_recipe_6_circuit_board_traces():
    bg = CircuitBoardTraces(pulse_speed=1.5, trace_color=colors.CYAN)
    assert bg.pulse_speed == 1.5
    assert bg.trace_color == colors.CYAN
    surf = _draw_to_surface(bg, 320, 240, time=0.5)
    assert surf is not None


def test_recipe_7_cosmic_nebula():
    bg = CosmicNebula(swirl_speed=0.2, star_count=120)
    assert bg.swirl_speed == 0.2
    assert bg.star_count == 120
    surf = _draw_to_surface(bg, 320, 240, time=0.5)
    assert surf is not None


def test_recipe_8_retro_crt_scanlines():
    bg = RetroCrtScanlines(curvature=0.1, scanline_gap=4)
    assert bg.curvature == 0.1
    assert bg.scanline_spacing == 4.0
    assert issubclass(RetroCrtScanlines, CrtPhosphorScanlineBackdrop) or RetroCrtScanlines is CrtPhosphorScanlineBackdrop
    surf = _draw_to_surface(bg, 320, 240, time=0.5)
    assert surf is not None


def test_recipe_9_sunset_horizon_glow():
    bg = SunsetHorizonGlow(sun_radius=180, atmospheric_haze=0.3)
    assert bg.sun_radius == 180.0
    assert bg.atmospheric_haze == 0.3
    assert issubclass(SunsetHorizonGlow, CalifornianSunsetBackdrop) or SunsetHorizonGlow is CalifornianSunsetBackdrop
    surf = _draw_to_surface(bg, 320, 240, time=0.5)
    assert surf is not None


def test_recipe_10_geometric_tessellation():
    # Hexagon
    bg_hex = GeometricTessellation(poly_type="hexagon", morph_speed=1.0)
    assert isinstance(bg_hex._delegate, HexagonalHoneyGridPulse)
    surf_hex = _draw_to_surface(bg_hex, 320, 240, time=0.5)
    assert surf_hex is not None

    # Voronoi
    bg_voro = GeometricTessellation(poly_type="voronoi", morph_speed=1.2)
    assert isinstance(bg_voro._delegate, VoronoiCellEvolution)
    surf_voro = _draw_to_surface(bg_voro, 320, 240, time=0.5)
    assert surf_voro is not None

    # Penrose
    bg_pen = GeometricTessellation(poly_type="penrose", morph_speed=0.8)
    assert isinstance(bg_pen._delegate, PenroseTilingFlow)
    surf_pen = _draw_to_surface(bg_pen, 320, 240, time=0.5)
    assert surf_pen is not None


def test_recipe_11_bokeh_light_bubbles():
    bg = BokehLightBubbles(bubble_count=35, blur_radius=40)
    assert bg.count == 35
    assert bg.blur_radius == 40.0
    surf = _draw_to_surface(bg, 320, 240, time=0.5)
    assert surf is not None


def test_recipe_12_hyperspace_tunnel():
    bg = HyperspaceTunnel(warp_speed=2.5, streak_color=colors.BLUE)
    assert bg.speed.get(0.0) == 2.5
    assert bg.ring_color.get(0.0) == colors.BLUE
    surf = _draw_to_surface(bg, 320, 240, time=0.5)
    assert surf is not None


def test_recipe_13_minimal_studio_infinity():
    bg = MinimalStudioInfinity(horizon_y=700, rim_light=True)
    assert bg.horizon_y.get(0.0) == 700.0
    assert bg.rim_light is True
    surf = _draw_to_surface(bg, 320, 240, time=0.5)
    assert surf is not None


def test_recipe_14_isometric_city_grid():
    bg = IsometricCityGrid(building_count=50, pulse_lights=True)
    assert bg.pulse_lights is True
    assert bg.grid_size > 0
    surf = _draw_to_surface(bg, 320, 240, time=0.5)
    assert surf is not None


def test_recipe_15_particle_constellation():
    bg = ParticleConstellation(particle_count=80, link_radius=120)
    assert bg.num_particles == 80
    assert bg.connection_distance == 120.0
    surf = _draw_to_surface(bg, 320, 240, time=0.5)
    assert surf is not None


def test_all_15_backdrops_exported():
    expected_backdrops = [
        "MeshGradientFlow",
        "CyberGridHorizon",
        "DigitalMatrixRain",
        "FluidCaustics",
        "TopographicContours",
        "CircuitBoardTraces",
        "CosmicNebula",
        "RetroCrtScanlines",
        "SunsetHorizonGlow",
        "GeometricTessellation",
        "BokehLightBubbles",
        "HyperspaceTunnel",
        "MinimalStudioInfinity",
        "IsometricCityGrid",
        "ParticleConstellation",
    ]
    import vibmo.fx.backgrounds as bg_mod
    for name in expected_backdrops:
        assert hasattr(bg_mod, name), f"Missing {name} in vibmo.fx.backgrounds"
        assert name in bg_mod.__all__, f"{name} not in vibmo.fx.backgrounds.__all__"
