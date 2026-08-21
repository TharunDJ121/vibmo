import pytest
import numpy as np
import cairo

from vibmo.core.color import colors
from vibmo.fx.backgrounds.bg_fluid_caustics import FluidWaterCaustics, UnderwaterLightRays, PrismaticIridescentWaves

def create_context(width=100, height=100):
    surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, width, height)
    ctx = cairo.Context(surface)
    return ctx, surface

def get_surface_data(surface):
    surface.flush()
    buf = surface.get_data()
    width = surface.get_width()
    height = surface.get_height()
    arr = np.ndarray(shape=(height, width, 4), dtype=np.uint8, buffer=buf)

    rgba = np.zeros_like(arr)
    rgba[:, :, 0] = arr[:, :, 2]  # R
    rgba[:, :, 1] = arr[:, :, 1]  # G
    rgba[:, :, 2] = arr[:, :, 0]  # B
    rgba[:, :, 3] = arr[:, :, 3]  # A
    return rgba

def test_fluid_water_caustics_rendering():
    node = FluidWaterCaustics(width=100, height=100, speed=1.0, color=colors.BLUE)
    ctx, surface = create_context(100, 100)

    node.draw(ctx, time=0.0)
    rgba_t0 = get_surface_data(surface)

    assert rgba_t0.shape == (100, 100, 4)
    assert np.any(rgba_t0 > 0), "Rendered frame should not be empty"

    # Assert base color is present
    # Blue is (0, 0, 255)
    assert np.mean(rgba_t0[:, :, 2]) > 50, "Blue channel should be dominant"

def test_fluid_water_caustics_time_variance():
    node = FluidWaterCaustics(width=100, height=100, speed=1.0)

    ctx1, surface1 = create_context(100, 100)
    node.draw(ctx1, time=0.0)
    rgba_t0 = get_surface_data(surface1)

    ctx2, surface2 = create_context(100, 100)
    node.draw(ctx2, time=1.0)
    rgba_t1 = get_surface_data(surface2)

    assert not np.array_equal(rgba_t0, rgba_t1), "Caustics should animate over time"

def test_underwater_light_rays_rendering():
    node = UnderwaterLightRays(width=100, height=100, speed=1.0, intensity=1.0)
    ctx, surface = create_context(100, 100)

    node.draw(ctx, time=0.0)
    rgba_t0 = get_surface_data(surface)

    assert rgba_t0.shape == (100, 100, 4)
    assert np.any(rgba_t0 > 0), "Rendered frame should not be empty"

def test_underwater_light_rays_time_variance():
    node = UnderwaterLightRays(width=100, height=100, speed=1.0, intensity=1.0)

    ctx1, surface1 = create_context(100, 100)
    node.draw(ctx1, time=0.0)
    rgba_t0 = get_surface_data(surface1)

    ctx2, surface2 = create_context(100, 100)
    node.draw(ctx2, time=1.0)
    rgba_t1 = get_surface_data(surface2)

    assert not np.array_equal(rgba_t0, rgba_t1), "Light rays should animate over time"

def test_prismatic_iridescent_waves_rendering():
    node = PrismaticIridescentWaves(width=100, height=100, speed=1.0)
    ctx, surface = create_context(100, 100)

    node.draw(ctx, time=0.0)
    rgba_t0 = get_surface_data(surface)

    assert rgba_t0.shape == (100, 100, 4)
    assert np.any(rgba_t0 > 0), "Rendered frame should not be empty"
    # Should have color content
    assert np.any(rgba_t0[:, :, 0] > 0)
    assert np.any(rgba_t0[:, :, 1] > 0)
    assert np.any(rgba_t0[:, :, 2] > 0)

def test_prismatic_iridescent_waves_time_variance():
    node = PrismaticIridescentWaves(width=100, height=100, speed=1.0)

    ctx1, surface1 = create_context(100, 100)
    node.draw(ctx1, time=0.0)
    rgba_t0 = get_surface_data(surface1)

    ctx2, surface2 = create_context(100, 100)
    node.draw(ctx2, time=1.0)
    rgba_t1 = get_surface_data(surface2)

    assert not np.array_equal(rgba_t0, rgba_t1), "Iridescent waves should animate over time"
