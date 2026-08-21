import pytest
import cairo
import numpy as np

from vibmo.fx.backgrounds.bg_mesh_gradient_flow import (
    MeshGradientFlow,
    AuroraGradientWave,
    LiquidPlasmaBackdrop,
)

def render_node(node, time):
    surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, int(node.width), int(node.height))
    ctx = cairo.Context(surface)
    node.draw(ctx, time=time)
    buf = surface.get_data()
    return np.ndarray(shape=(int(node.height), int(node.width), 4), dtype=np.uint8, buffer=buf).copy()

def test_mesh_gradient_flow_animation():
    bg = MeshGradientFlow(width=200, height=200)
    frame_0 = render_node(bg, time=0.0)
    frame_1_5 = render_node(bg, time=1.5)
    
    # Assert non-identical frames (verifying dynamic non-static movement)
    assert not np.array_equal(frame_0, frame_1_5), "MeshGradientFlow should be animated, but frames are identical."

def test_aurora_gradient_wave_animation():
    bg = AuroraGradientWave(width=200, height=200)
    frame_0 = render_node(bg, time=0.0)
    frame_1_5 = render_node(bg, time=1.5)
    
    assert not np.array_equal(frame_0, frame_1_5), "AuroraGradientWave should be animated, but frames are identical."

def test_liquid_plasma_backdrop_animation():
    bg = LiquidPlasmaBackdrop(width=200, height=200)
    frame_0 = render_node(bg, time=0.0)
    frame_1_5 = render_node(bg, time=1.5)
    
    assert not np.array_equal(frame_0, frame_1_5), "LiquidPlasmaBackdrop should be animated, but frames are identical."
