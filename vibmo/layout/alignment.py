"""
Anchor positioning presets and relative alignment helpers.
"""

from __future__ import annotations
from enum import Enum
from typing import Tuple
from vibmo.core.vector import Vector2D


class Align(Enum):
    TOP_LEFT = "top_left"
    TOP_CENTER = "top_center"
    TOP_RIGHT = "top_right"
    CENTER_LEFT = "center_left"
    CENTER = "center"
    CENTER_RIGHT = "center_right"
    BOTTOM_LEFT = "bottom_left"
    BOTTOM_CENTER = "bottom_center"
    BOTTOM_RIGHT = "bottom_right"

    @classmethod
    def to_anchor(cls, align: Align, width: float, height: float) -> Vector2D:
        """Calculates anchor point vector from alignment and dimensions."""
        if align == cls.TOP_LEFT:
            return Vector2D(0.0, 0.0)
        elif align == cls.TOP_CENTER:
            return Vector2D(width * 0.5, 0.0)
        elif align == cls.TOP_RIGHT:
            return Vector2D(width, 0.0)
        elif align == cls.CENTER_LEFT:
            return Vector2D(0.0, height * 0.5)
        elif align == cls.CENTER:
            return Vector2D(width * 0.5, height * 0.5)
        elif align == cls.CENTER_RIGHT:
            return Vector2D(width, height * 0.5)
        elif align == cls.BOTTOM_LEFT:
            return Vector2D(0.0, height)
        elif align == cls.BOTTOM_CENTER:
            return Vector2D(width * 0.5, height)
        elif align == cls.BOTTOM_RIGHT:
            return Vector2D(width, height)
        return Vector2D(0.0, 0.0)
