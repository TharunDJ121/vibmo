import cairo
import numpy as np
from vibmo.fx.backgrounds.bg_mesh_gradient_flow import (
    MeshGradientFlow,
    AuroraGradientWave,
    LiquidPlasmaBackdrop
)

def render_node(node, time):
    w, h = int(node.width.get(time)), int(node.height.get(time))
    surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, w, h)
    ctx = cairo.Context(surface)
    node.draw(ctx, time)

    # Get surface data as numpy array
    buf = surface.get_data()
    arr = np.ndarray(shape=(h, w, 4), dtype=np.uint8, buffer=buf)
    return np.copy(arr)

def test_mesh_gradient_flow_dynamic():
    bg = MeshGradientFlow(width=200, height=150, resolution_scale=0.1)

    frame0 = render_node(bg, time=0.0)
    frame1 = render_node(bg, time=1.5)

    assert not np.array_equal(frame0, frame1), "Frames should be different due to dynamic movement"

def test_aurora_gradient_wave_dynamic():
    bg = AuroraGradientWave(width=200, height=150, resolution_scale=0.1)

    frame0 = render_node(bg, time=0.0)
    frame1 = render_node(bg, time=1.5)

    assert not np.array_equal(frame0, frame1), "Frames should be different due to dynamic movement"

def test_liquid_plasma_backdrop_dynamic():
    bg = LiquidPlasmaBackdrop(width=200, height=150, resolution_scale=0.1)

    frame0 = render_node(bg, time=0.0)
    frame1 = render_node(bg, time=1.5)

    assert not np.array_equal(frame0, frame1), "Frames should be different due to dynamic movement"
