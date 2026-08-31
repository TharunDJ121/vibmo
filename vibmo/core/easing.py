"""
Comprehensive Easing Curves and Custom Cubic Bezier Evaluator for fluid motion design.
"""

from __future__ import annotations
import math
from typing import Callable, Union

EasingFunc = Callable[[float], float]


def linear(t: float) -> float:
    return t


def in_quad(t: float) -> float:
    return t * t


def out_quad(t: float) -> float:
    return t * (2.0 - t)


def in_out_quad(t: float) -> float:
    return 2.0 * t * t if t < 0.5 else -1.0 + (4.0 - 2.0 * t) * t


def in_cubic(t: float) -> float:
    return t * t * t


def out_cubic(t: float) -> float:
    t1 = t - 1.0
    return t1 * t1 * t1 + 1.0


def in_out_cubic(t: float) -> float:
    return 4.0 * t * t * t if t < 0.5 else (t - 1.0) * (2.0 * t - 2.0) * (2.0 * t - 2.0) + 1.0


def in_quart(t: float) -> float:
    return t * t * t * t


def out_quart(t: float) -> float:
    t1 = t - 1.0
    return 1.0 - t1 * t1 * t1 * t1


def in_out_quart(t: float) -> float:
    t1 = t - 1.0
    return 8.0 * t * t * t * t if t < 0.5 else 1.0 - 8.0 * t1 * t1 * t1 * t1


def in_expo(t: float) -> float:
    return 0.0 if t <= 0.0 else math.pow(2.0, 10.0 * (t - 1.0))


def out_expo(t: float) -> float:
    return 1.0 if t >= 1.0 else 1.0 - math.pow(2.0, -10.0 * t)


def in_out_expo(t: float) -> float:
    if t <= 0.0:
        return 0.0
    if t >= 1.0:
        return 1.0
    if t < 0.5:
        return 0.5 * math.pow(2.0, (20.0 * t) - 10.0)
    return 1.0 - 0.5 * math.pow(2.0, (-20.0 * t) + 10.0)


def in_circ(t: float) -> float:
    return 1.0 - math.sqrt(max(0.0, 1.0 - t * t))


def out_circ(t: float) -> float:
    t1 = t - 1.0
    return math.sqrt(max(0.0, 1.0 - t1 * t1))


def in_out_circ(t: float) -> float:
    if t < 0.5:
        return 0.5 * (1.0 - math.sqrt(max(0.0, 1.0 - 4.0 * t * t)))
    t2 = 2.0 * t - 2.0
    return 0.5 * (math.sqrt(max(0.0, 1.0 - t2 * t2)) + 1.0)


def in_back(t: float, s: float = 1.70158) -> float:
    return t * t * ((s + 1.0) * t - s)


def out_back(t: float, s: float = 1.70158) -> float:
    t1 = t - 1.0
    return t1 * t1 * ((s + 1.0) * t1 + s) + 1.0


def in_out_back(t: float, s: float = 1.70158 * 1.525) -> float:
    t2 = t * 2.0
    if t2 < 1.0:
        return 0.5 * (t2 * t2 * ((s + 1.0) * t2 - s))
    t3 = t2 - 2.0
    return 0.5 * (t3 * t3 * ((s + 1.0) * t3 + s) + 2.0)


def out_bounce(t: float) -> float:
    if t < (1.0 / 2.75):
        return 7.5625 * t * t
    elif t < (2.0 / 2.75):
        t1 = t - (1.5 / 2.75)
        return 7.5625 * t1 * t1 + 0.75
    elif t < (2.5 / 2.75):
        t1 = t - (2.25 / 2.75)
        return 7.5625 * t1 * t1 + 0.9375
    else:
        t1 = t - (2.625 / 2.75)
        return 7.5625 * t1 * t1 + 0.984375


def in_bounce(t: float) -> float:
    return 1.0 - out_bounce(1.0 - t)


def in_out_bounce(t: float) -> float:
    return 0.5 * in_bounce(t * 2.0) if t < 0.5 else 0.5 * out_bounce(t * 2.0 - 1.0) + 0.5


def in_elastic(t: float) -> float:
    if t <= 0.0:
        return 0.0
    if t >= 1.0:
        return 1.0
    p = 0.3
    s = p / 4.0
    t1 = t - 1.0
    return -math.pow(2.0, 10.0 * t1) * math.sin((t1 - s) * (2.0 * math.pi) / p)


def out_elastic(t: float) -> float:
    if t <= 0.0:
        return 0.0
    if t >= 1.0:
        return 1.0
    p = 0.3
    s = p / 4.0
    return math.pow(2.0, -10.0 * t) * math.sin((t - s) * (2.0 * math.pi) / p) + 1.0


def in_out_elastic(t: float) -> float:
    if t <= 0.0:
        return 0.0
    if t >= 1.0:
        return 1.0
    p = 0.3 * 1.5
    s = p / 4.0
    t1 = t * 2.0 - 1.0
    if t1 < 0.0:
        return -0.5 * (math.pow(2.0, 10.0 * t1) * math.sin((t1 - s) * (2.0 * math.pi) / p))
    return math.pow(2.0, -10.0 * t1) * math.sin((t1 - s) * (2.0 * math.pi) / p) * 0.5 + 1.0


class CubicBezier:
    """Cubic Bezier curve evaluator with high-performance Newton-Raphson inversion."""

    __slots__ = ("x1", "y1", "x2", "y2")

    def __init__(self, x1: float, y1: float, x2: float, y2: float) -> None:
        self.x1 = float(x1)
        self.y1 = float(y1)
        self.x2 = float(x2)
        self.y2 = float(y2)

    def _sample_curve_x(self, t: float) -> float:
        # ((1-3x2+3x1)*t + (3x2-6x1))*t + 3x1)*t
        cx = 3.0 * self.x1
        bx = 3.0 * (self.x2 - self.x1) - cx
        ax = 1.0 - cx - bx
        return ((ax * t + bx) * t + cx) * t

    def _sample_curve_y(self, t: float) -> float:
        cy = 3.0 * self.y1
        by = 3.0 * (self.y2 - self.y1) - cy
        ay = 1.0 - cy - by
        return ((ay * t + by) * t + cy) * t

    def _sample_curve_derivative_x(self, t: float) -> float:
        cx = 3.0 * self.x1
        bx = 3.0 * (self.x2 - self.x1) - cx
        ax = 1.0 - cx - bx
        return (3.0 * ax * t + 2.0 * bx) * t + cx

    def _solve_curve_x(self, x: float, epsilon: float = 1e-6) -> float:
        # Newton-Raphson iteration
        t2 = x
        for _ in range(8):
            x2 = self._sample_curve_x(t2) - x
            if abs(x2) < epsilon:
                return t2
            d2 = self._sample_curve_derivative_x(t2)
            if abs(d2) < 1e-6:
                break
            t2 -= x2 / d2

        # Fallback binary subdivision
        t0 = 0.0
        t1 = 1.0
        t2 = x
        while t0 < t1:
            x2 = self._sample_curve_x(t2)
            if abs(x2 - x) < epsilon:
                return t2
            if x > x2:
                t0 = t2
            else:
                t1 = t2
            t2 = (t1 - t0) * 0.5 + t0
        return t2

    def __call__(self, t: float) -> float:
        if t <= 0.0:
            return 0.0
        if t >= 1.0:
            return 1.0
        return self._sample_curve_y(self._solve_curve_x(t))


def in_sine(t: float) -> float:
    return 1.0 - math.cos((t * math.pi) / 2.0)


def out_sine(t: float) -> float:
    return math.sin((t * math.pi) / 2.0)


def in_out_sine(t: float) -> float:
    return -0.5 * (math.cos(math.pi * t) - 1.0)


class Ease:
    """Convenient registry and builder for motion graphics easing curves."""

    linear = staticmethod(linear)
    in_sine = staticmethod(in_sine)
    out_sine = staticmethod(out_sine)
    in_out_sine = staticmethod(in_out_sine)
    in_quad = staticmethod(in_quad)
    out_quad = staticmethod(out_quad)
    in_out_quad = staticmethod(in_out_quad)
    in_cubic = staticmethod(in_cubic)
    out_cubic = staticmethod(out_cubic)
    in_out_cubic = staticmethod(in_out_cubic)
    in_quart = staticmethod(in_quart)
    out_quart = staticmethod(out_quart)
    in_out_quart = staticmethod(in_out_quart)
    in_expo = staticmethod(in_expo)
    out_expo = staticmethod(out_expo)
    in_out_expo = staticmethod(in_out_expo)
    in_circ = staticmethod(in_circ)
    out_circ = staticmethod(out_circ)
    in_out_circ = staticmethod(in_out_circ)
    in_back = staticmethod(in_back)
    out_back = staticmethod(out_back)
    in_out_back = staticmethod(in_out_back)
    in_elastic = staticmethod(in_elastic)
    out_elastic = staticmethod(out_elastic)
    in_out_elastic = staticmethod(in_out_elastic)
    in_bounce = staticmethod(in_bounce)
    out_bounce = staticmethod(out_bounce)
    in_out_bounce = staticmethod(in_out_bounce)

    # Modern Motion Presets
    smooth = staticmethod(CubicBezier(0.4, 0.0, 0.2, 1.0))
    anticipate = staticmethod(CubicBezier(0.36, 0.0, 0.66, -0.56))
    snappy = staticmethod(CubicBezier(0.12, 0.8, 0.32, 1.0))

    @staticmethod
    def bezier(x1: float, y1: float, x2: float, y2: float) -> CubicBezier:
        return CubicBezier(x1, y1, x2, y2)

    @staticmethod
    def spring(stiffness: float = 100.0, damping: float = 10.0, mass: float = 1.0, initial_velocity: float = 0.0):
        from vibmo.core.spring import SpringEasing
        return SpringEasing(stiffness=stiffness, damping=damping, mass=mass, initial_velocity=initial_velocity)
