import pytest
import numpy as np
from vibmo.fx.backgrounds.bg_cyber_grid_horizon import CyberGridHorizon
from vibmo.core.color import colors

class DummySurface:
    def __init__(self, w, h):
        import cairo
        self.surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, w, h)
        self.context = cairo.Context(self.surface)

class DummyRenderCtx:
    def get_surface(self, w, h):
        return DummySurface(w, h)

def test_cyber_grid_horizon_init():
    node = CyberGridHorizon(name="grid", width=800, height=600)
    assert node.width == 800
    assert node.height == 600
    assert node.grid_color(0.0) == colors.CYAN

def test_cyber_grid_horizon_render():
    node = CyberGridHorizon(width=400, height=300)
    ctx = DummyRenderCtx()
    node.render(0.0, ctx)
    node.render(1.0, ctx)

from vibmo.fx.backgrounds.bg_cyber_grid_horizon import NeonSunBackdrop

def test_neon_sun_backdrop_init():
    node = NeonSunBackdrop(name="sun", radius=200)
    assert node.radius_val(0.0) == 200.0
    assert node.core_color(0.0) == colors.AMBER

def test_neon_sun_backdrop_render():
    node = NeonSunBackdrop(radius=100)
    ctx = DummyRenderCtx()
    node.render(0.0, ctx)
    node.render(1.0, ctx)

from vibmo.fx.backgrounds.bg_cyber_grid_horizon import WireframeMountainHorizon

def test_wireframe_mountain_horizon_init():
    node = WireframeMountainHorizon(name="mountains", width=800, height=300)
    assert node.width == 800
    assert node.height == 300
    assert node.line_color(0.0) == colors.PINK

def test_wireframe_mountain_horizon_render():
    node = WireframeMountainHorizon(width=400, height=150)
    ctx = DummyRenderCtx()
    node.render(0.0, ctx)
    node.render(1.0, ctx)
