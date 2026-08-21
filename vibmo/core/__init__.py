"""
Core mathematical and physical foundations of Vibmo.
"""

from vibmo.core.vector import Vector2D, Vector3D
from vibmo.core.matrix import Matrix3x3
from vibmo.core.color import Color, LinearGradient, RadialGradient, ColorStop, colors
from vibmo.core.easing import Ease, CubicBezier, EasingFunc
from vibmo.core.spring import Spring, SpringEasing
from vibmo.core.signal import Signal, AnimationAction, AnimationSegment

__all__ = [
    "Vector2D",
    "Vector3D",
    "Matrix3x3",
    "Color",
    "LinearGradient",
    "RadialGradient",
    "ColorStop",
    "colors",
    "Ease",
    "CubicBezier",
    "EasingFunc",
    "Spring",
    "SpringEasing",
    "Signal",
    "AnimationAction",
    "AnimationSegment",
]
