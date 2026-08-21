"""
Motion Tracking and Feature Point Follower.
"""

from __future__ import annotations
import math
from typing import Any, Dict, List, Optional, Sequence, Tuple, Union
from vibmo.core.vector import Vector2D
from vibmo.scene.node import Node


class PointTracker:
    """
    2D Feature Point Tracker.
    Stores tracked trajectories and binds target Node positions to the tracked feature.
    """

    def __init__(self, keyframe_points: Sequence[Tuple[float, float, float]]) -> None:
        # List of (time, x, y)
        self.tracks = sorted(list(keyframe_points), key=lambda pt: pt[0])

    def get_position(self, time: float) -> Vector2D:
        """Interpolates tracked position at timestamp t."""
        if not self.tracks:
            return Vector2D(0.0, 0.0)
        if time <= self.tracks[0][0]:
            return Vector2D(self.tracks[0][1], self.tracks[0][2])
        if time >= self.tracks[-1][0]:
            return Vector2D(self.tracks[-1][1], self.tracks[-1][2])

        for i in range(len(self.tracks) - 1):
            t0, x0, y0 = self.tracks[i]
            t1, x1, y1 = self.tracks[i + 1]
            if t0 <= time <= t1:
                prog = (time - t0) / max(1e-4, t1 - t0)
                x = x0 + (x1 - x0) * prog
                y = y0 + (y1 - y0) * prog
                return Vector2D(x, y)

        return Vector2D(self.tracks[-1][1], self.tracks[-1][2])

    def attach(self, node: Node, offset: Union[Vector2D, Sequence[float]] = (0, 0)) -> None:
        """Binds a Node's position to follow this tracked path."""
        off = Vector2D.from_any(offset)
        node.position.bind(lambda t: Vector2D(self.get_position(t).x + off.x, self.get_position(t).y + off.y))
