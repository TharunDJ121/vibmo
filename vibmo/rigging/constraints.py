"""
Rigging, Layer Constraints, LookAt, Follow, and Path Tracking.
"""

from __future__ import annotations
import math
from typing import Any, Callable, Optional, Sequence, Tuple, Union
from vibmo.core.vector import Vector2D
from vibmo.scene.node import Node


class Constraint:
    """Base class for transform constraints and rigging solvers."""

    def apply(self, node: Node, time: float) -> None:
        raise NotImplementedError


class LookAtConstraint(Constraint):
    """
    Orients a Node's rotation to continuously point directly towards a target Node or coordinate.
    """

    def __init__(self, target: Union[Node, Vector2D, Sequence[float]], offset_angle: float = 0.0) -> None:
        self.target = target
        self.offset_angle = float(offset_angle)

    def apply(self, node: Node, time: float) -> None:
        node_pos = node.position.get(time)
        if isinstance(self.target, Node):
            target_pos = self.target.position.get(time)
        else:
            target_pos = Vector2D.from_any(self.target)

        dx = target_pos.x - node_pos.x
        dy = target_pos.y - node_pos.y
        angle = math.atan2(dy, dx) + self.offset_angle
        node.rotation.set(angle)


class FollowConstraint(Constraint):
    """
    Locks or smoothly tracks a Node's position to another Node with offset and damping.
    """

    def __init__(
        self,
        target: Node,
        offset: Union[Vector2D, Sequence[float]] = (0.0, 0.0),
        maintain_offset: bool = False,
    ) -> None:
        self.target = target
        self.offset = Vector2D.from_any(offset)
        self.maintain_offset = maintain_offset

    def apply(self, node: Node, time: float) -> None:
        target_pos = self.target.position.get(time)
        new_pos = Vector2D(target_pos.x + self.offset.x, target_pos.y + self.offset.y)
        node.position.set(new_pos)


class PathConstraint(Constraint):
    """
    Constrains a Node's position (and optionally rotation) along a 2D Bézier Path trajectory.
    """

    def __init__(
        self,
        points: Sequence[Sequence[float]],
        progress: float = 0.0,
        orient_to_path: bool = True,
    ) -> None:
        self.points = [Vector2D.from_any(p) for p in points]
        self.progress = float(progress)
        self.orient_to_path = orient_to_path

    def apply(self, node: Node, time: float) -> None:
        if not self.points:
            return
        if len(self.points) == 1:
            node.position.set(self.points[0])
            return

        prog = max(0.0, min(1.0, self.progress))
        total_segs = len(self.points) - 1
        seg_idx = min(int(prog * total_segs), total_segs - 1)
        seg_t = (prog * total_segs) - seg_idx

        p0 = self.points[seg_idx]
        p1 = self.points[seg_idx + 1]

        x = p0.x + (p1.x - p0.x) * seg_t
        y = p0.y + (p1.y - p0.y) * seg_t
        node.position.set(Vector2D(x, y))

        if self.orient_to_path:
            dx = p1.x - p0.x
            dy = p1.y - p0.y
            node.rotation.set(math.atan2(dy, dx))
