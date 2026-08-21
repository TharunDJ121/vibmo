"""
Unit tests for AI Agent ergonomics, fuzzy kwarg validation, spring physics, matrix math, and turnkey builders.
"""

import math
import pytest
from vibmo.core.errors import validate_kwargs, VibmoParameterError
from vibmo.core.spring import Spring
from vibmo.core.easing import Ease, CubicBezier
from vibmo.core.vector import Vector2D
from vibmo.core.matrix import Matrix3x3
from vibmo.core.color import Color
from vibmo.spatial.perspective import Projective3DWarp
from vibmo.templates.turnkey import create_saas_launch_scene
from vibmo.timeline.scheduler import all, sequence, wait, Choreographer
from vibmo.scene.scene import Scene


def test_fuzzy_kwarg_validation():
    allowed = {"fill", "stroke", "stroke_width", "corner_radius", "padding"}
    
    # 1. Valid kwargs pass with no error
    validate_kwargs("CustomComponent", {"fill": "#fff", "padding": 16}, allowed)

    # 2. Misspelled parameter raises VibmoParameterError with "Did you mean...?"
    with pytest.raises(VibmoParameterError) as exc_info:
        validate_kwargs("CustomComponent", {"fil": "#fff"}, allowed)
    assert "Did you mean 'fill'?" in str(exc_info.value)


def test_spring_physics_damping_regimes():
    # Underdamped (zeta < 1)
    s_under = Spring(stiffness=150.0, damping=10.0, mass=1.0)
    assert s_under.evaluate(0.0) == 0.0
    assert math.isclose(s_under.evaluate(5.0), 1.0, abs_tol=0.01)

    # Critically damped (zeta = 1)
    c_crit = 2.0 * math.sqrt(100.0 * 1.0)  # 20.0
    s_crit = Spring(stiffness=100.0, damping=c_crit, mass=1.0)
    assert math.isclose(s_crit.evaluate(5.0), 1.0, abs_tol=0.01)

    # Overdamped (zeta > 1)
    s_over = Spring(stiffness=50.0, damping=35.0, mass=1.0)
    assert math.isclose(s_over.evaluate(5.0), 1.0, abs_tol=0.01)


def test_cubic_bezier_newton_raphson():
    bez = CubicBezier(0.25, 0.1, 0.25, 1.0)
    assert math.isclose(bez(0.0), 0.0, abs_tol=1e-5)
    assert math.isclose(bez(1.0), 1.0, abs_tol=1e-5)
    assert 0.0 <= bez(0.5) <= 1.0


def test_vector2d_polar_and_rotations():
    v = Vector2D.from_polar(radius=10.0, angle_rad=0.0)
    assert math.isclose(v.x, 10.0) and math.isclose(v.y, 0.0)

    v_rot = v.rotate(math.pi / 2)
    assert math.isclose(v_rot.x, 0.0, abs_tol=1e-5)
    assert math.isclose(v_rot.y, 10.0, abs_tol=1e-5)

    dot_prod = v.dot(v_rot)
    assert math.isclose(dot_prod, 0.0, abs_tol=1e-5)


def test_matrix3x3_compose_and_inverse():
    mat = Matrix3x3.compose(
        position=(100.0, 200.0),
        scale=(2.0, 2.0),
        rotation_rad=0.0,
    )
    p = mat.transform_point(Vector2D(10.0, 10.0))
    # 100 + 2*10 = 120, 200 + 2*10 = 220
    assert math.isclose(p.x, 120.0) and math.isclose(p.y, 220.0)

    inv = mat.inverse()
    p_orig = inv.transform_point(p)
    assert math.isclose(p_orig.x, 10.0, abs_tol=1e-4)
    assert math.isclose(p_orig.y, 10.0, abs_tol=1e-4)


def test_projective_3d_warp_quad():
    quad = Projective3DWarp.project_quad(
        local_bounds=(0, 0, 400, 300),
        pos=Vector2D(500, 400),
        scale=Vector2D(1.0, 1.0),
        rotation_z=0.0,
        rotate_x=0.2,
        rotate_y=-0.3,
        anchor=Vector2D(0, 0),
        focal_dist=1200.0,
    )
    assert len(quad) == 4
    for pt in quad:
        assert len(pt) == 2


def test_color_polymorphic_parsing():
    c_hex = Color.from_any("#6366f1")
    assert math.isclose(c_hex.r, 0.388, abs_tol=0.05)

    c_tuple = Color.from_any((1.0, 0.5, 0.2, 0.8))
    assert c_tuple.a == 0.8

    c_inst = Color.from_any(c_hex)
    assert c_inst == c_hex


def test_turnkey_saas_launch_scene():
    scene = create_saas_launch_scene(
        app_title="PulsePro",
        app_url="https://pulsepro.dev",
        headline="Autonomous Motion",
        metric_label="MRR",
        metric_start=50000,
        metric_end=120000,
        duration=4.0,
    )
    assert scene is not None
    assert scene.duration >= 4.0
    assert len(scene.nodes) >= 1


    # Validate scene is 100% sound
    issues = scene.validate()
    assert issues == []


def test_choreographer_mixed_action_groups():
    scene = Scene(duration=3.0)
    c = Choreographer()

    def my_choreography():
        yield wait(0.5)
        yield all([wait(0.2), wait(0.4)])
        yield sequence([wait(0.1), wait(0.2)])

    total_t = c.run(my_choreography)
    # 0.5 + max(0.2, 0.4) + (0.1 + 0.2) = 0.5 + 0.4 + 0.3 = 1.2
    assert math.isclose(total_t, 1.2, abs_tol=0.05)
