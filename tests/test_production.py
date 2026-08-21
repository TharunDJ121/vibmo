"""
Automated Production Test Suite verifying signal determinism, morphing, compositing, and layout.
"""

import math
import numpy as np
import pytest
from vibmo import (
    Scene,
    Signal,
    Ease,
    Vector2D,
    Color,
    colors,
    MorphPath,
    Shape,
    Precomp,
    AlphaMatte,
    Rect,
    Circle,
    GlassCard,
    KineticText,
    MetricCounter,
    Matrix3D,
)
from vibmo.layout.flexbox import FlexLayout


def test_signals_and_springs():
    sig = Signal(0.0, "test_sig")
    action = sig.to(100.0, duration=1.0, ease=Ease.spring(stiffness=150, damping=12))
    action.apply_at(0.0)
    
    val_0 = sig.get(0.0)
    val_05 = sig.get(0.5)
    val_10 = sig.get(1.0)
    
    assert val_0 == 0.0
    assert val_05 > 0.0
    assert abs(val_10 - 100.0) < 1.0  # Settled near target


def test_morph_path_determinism():
    morph = MorphPath(shape=Shape.circle(60.0), num_points=80)
    action = morph.morph_to(Shape.star(outer_radius=80.0, inner_radius=35.0), duration=1.0)
    action.apply_at(0.0)
    
    pts_0 = morph.get_points_at(0.0)
    pts_05 = morph.get_points_at(0.5)
    pts_10 = morph.get_points_at(1.0)
    
    assert pts_0.shape == (80, 2)
    assert pts_05.shape == (80, 2)
    assert pts_10.shape == (80, 2)
    assert not np.array_equal(pts_0, pts_10)


def test_matrix3d_perspective():
    mat = Matrix3D.translation(100, 200, 0).multiply(Matrix3D.rotation_z(math.pi * 0.5))
    x, y, z = mat.project_point(10, 0, 0)
    assert abs(x - 100.0) < 1e-3
    assert abs(y - 210.0) < 1e-3


def test_flex_layout_computation():
    c1 = Rect(width=100, height=50)
    c2 = Rect(width=200, height=50)
    w, h, pos = FlexLayout.compute([c1, c2], direction="row", gap=20.0, padding=10.0)
    
    assert w == 100 + 200 + 20 + 20  # 340
    assert h == 50 + 20               # 70
    assert pos[0] == (10.0, 10.0)
    assert pos[1] == (130.0, 10.0)


def test_compositing_graph_render():
    s = Scene(width=640, height=360, duration=1.0)
    target = Rect(width=200, height=200, fill=colors.CYAN)
    mask = Circle(radius=50, fill=colors.WHITE, position=(100, 100))
    masked = AlphaMatte(target=target, matte=mask)
    
    card = GlassCard(direction="column", padding=16.0, position=(50, 50))
    card.add(KineticText("Test Metric", font_size=16.0), MetricCounter(start_val=0, end_val=100))
    
    s.add(masked, card)
    rgba = s._rasterizer.render_frame(s.nodes, time=0.5, background=colors.DARK_NAVY)
    
    assert rgba.shape == (360, 640, 4)
    assert rgba.dtype == np.uint8
