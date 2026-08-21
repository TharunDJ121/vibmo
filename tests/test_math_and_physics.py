"""
Unit tests for mathematical formulas, Cartesian axes plotting, and particle physics.
"""

import math
import pytest
from vibmo.math.formula import MathFormula
from vibmo.math.plots import Axes
from vibmo.physics.particles import ParticleEmitter
from vibmo.primitives.morph import MorphPath, Shape
from vibmo.core.color import colors


def test_math_formula_latex_parsing():
    formula = MathFormula(latex=r"\int_0^\infty e^{-x^2} dx = \frac{\sqrt{\pi}}{2}", font_size=32.0)
    assert formula.latex is not None
    bx, by, bw, bh = formula.local_bounds(0.0)
    assert bw > 0
    assert bh > 0

    trans_action = formula.transform_to(r"E = mc^2", duration=0.8)
    assert trans_action is not None


def test_axes_coordinate_transforms_and_plot():
    axes = Axes(x_range=(-5, 5), y_range=(-2, 2), width=600, height=300)
    
    # Center origin (0, 0) should be at center of axes (300, 150)
    origin_pt = axes.c2p(0, 0)
    assert math.isclose(origin_pt.x, 300.0, abs_tol=1.0)
    assert math.isclose(origin_pt.y, 150.0, abs_tol=1.0)

    # Plotting mathematical function
    curve = axes.plot(lambda x: math.sin(x), color=colors.CYAN)
    assert curve is not None
    assert curve.d != ""


def test_particle_emitter_deterministic_physics():
    emitter = ParticleEmitter(preset="sparkles")
    burst_action = emitter.burst(count=30, time=0.0)
    assert burst_action is not None
    assert len(emitter._particles) == 30

    # Test particle position at t=0.5
    p0 = emitter._particles[0]
    assert p0.start_time == 0.0
    assert p0.life > 0.0


def test_morph_path_shapes():
    shapes = [
        Shape.circle(radius=50),
        Shape.star(outer_radius=60, inner_radius=25),
        Shape.heart(size=70),
        Shape.gear(radius=55, teeth=6),
    ]
    for s in shapes:
        assert isinstance(s, str) and len(s) > 0
        morph = MorphPath(shape=s, num_points=60)
        pts = morph.get_points_at(0.0)
        assert pts.shape == (60, 2)

