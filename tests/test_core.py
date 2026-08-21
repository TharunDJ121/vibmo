"""
Unit tests for Vibmo core mathematics, color interpolation, spring physics, and easing curves.
"""

import math
import pytest
from vibmo.core.vector import Vector2D, Vector3D
from vibmo.core.matrix import Matrix3x3
from vibmo.core.color import Color, colors
from vibmo.core.easing import Ease
from vibmo.core.spring import Spring


def test_vector2d_arithmetic():
    v1 = Vector2D(10, 20)
    v2 = Vector2D(5, 5)
    
    assert v1 + v2 == Vector2D(15, 25)
    assert v1 - v2 == Vector2D(5, 15)
    assert v1 * 2 == Vector2D(20, 40)
    assert v1 / 2 == Vector2D(5, 10)
    assert math.isclose(v1.magnitude, math.hypot(10, 20))
    assert math.isclose(v1.dot(v2), 150)


def test_matrix3x3_transformations():
    # Translation + Scaling
    m = Matrix3x3.translation(100, 50).multiply(Matrix3x3.scaling(2, 2))
    p = m.transform_point(Vector2D(10, 10))
    assert math.isclose(p.x, 120)
    assert math.isclose(p.y, 70)

    # Invertibility
    inv = m.inverse()
    orig = inv.transform_point(p)
    assert math.isclose(orig.x, 10)
    assert math.isclose(orig.y, 10)


def test_color_oklab_interpolation():
    c1 = Color.hex("#6366F1")
    c2 = Color.hex("#EC4899")
    mid = c1.lerp(c2, 0.5, space="oklab")
    assert 0.0 <= mid.r <= 1.0
    assert 0.0 <= mid.g <= 1.0
    assert 0.0 <= mid.b <= 1.0
    assert mid.a == 1.0


def test_spring_physics():
    spring = Spring(stiffness=120, damping=12)
    # Starts at 0, target is 1
    v0 = spring.evaluate(0.0, start=0.0, target=1.0)
    assert math.isclose(v0, 0.0, abs_tol=1e-5)
    
    # Over time, settles to 1.0
    v_settled = spring.evaluate(spring.settling_duration + 0.5, start=0.0, target=1.0)
    assert math.isclose(v_settled, 1.0, abs_tol=0.01)


def test_cubic_bezier_easing():
    # Ease.out_expo start and end
    assert math.isclose(Ease.out_expo(0.0), 0.0, abs_tol=1e-5)
    assert math.isclose(Ease.out_expo(1.0), 1.0, abs_tol=1e-5)


def test_vector3d_math():
    v1 = Vector3D(1.0, 0.0, 0.0)
    v2 = Vector3D(0.0, 1.0, 0.0)
    cross = v1.cross(v2)
    assert math.isclose(cross.z, 1.0)
    assert math.isclose(v1.dot(v2), 0.0)
    
    mid = v1.lerp(v2, 0.5)
    assert math.isclose(mid.x, 0.5) and math.isclose(mid.y, 0.5)


def test_matrix4x4_perspective_projection():
    from vibmo.core.matrix import Matrix4x4
    m_id = Matrix4x4.identity()
    assert len(m_id.m) == 16

    m_trans = Matrix4x4.translation(10, 20, 30)
    p_trans = m_trans.transform_point((0, 0, 0))
    assert math.isclose(p_trans.x, 10.0)
    assert math.isclose(p_trans.y, 20.0)
    assert math.isclose(p_trans.z, 30.0)


def test_color_space_conversions_and_shades():
    c = Color(0.5, 0.2, 0.8, 1.0)
    c_alpha = c.with_alpha(0.4)
    assert c_alpha.a == 0.4

    c_light = c.lighten(0.1)
    assert c_light.r >= c.r or c_light.g >= c.g or c_light.b >= c.b

    c_dark = c.darken(0.1)
    assert c_dark is not None

    # HSL color factory
    c_hsl = Color.hsl(0.6, 0.8, 0.5)
    assert c_hsl.r >= 0.0 and c_hsl.b >= 0.0



def test_spring_and_bezier_custom_easings():
    custom_spring = Ease.spring(stiffness=200, damping=15, mass=1.0)
    v0 = custom_spring(0.0)
    v1 = custom_spring(1.0)
    assert math.isclose(v0, 0.0, abs_tol=1e-4)
    assert math.isclose(v1, 1.0, abs_tol=0.05)

    custom_bez = Ease.bezier(0.4, 0.0, 0.2, 1.0)
    assert math.isclose(custom_bez(0.0), 0.0, abs_tol=1e-5)
    assert math.isclose(custom_bez(1.0), 1.0, abs_tol=1e-5)

    assert 0.0 <= custom_bez(0.5) <= 1.0
