"""
Parametric Bezier path evaluator, tangent-aligned motion paths, and path trim progression.
"""

from __future__ import annotations
import math
from typing import Any, Callable, List, Optional, Tuple, Union
from vibmo.core.vector import Vector2D
from vibmo.scene.node import Node
from vibmo.core.signal import Signal, AnimationAction
from vibmo.core.easing import Ease, EasingFunc


class CubicBezierCurve:
    """
    Parametric Cubic Bézier curve defined by P0 (start), P1 (control 1), P2 (control 2), P3 (end).
    """

    def __init__(
        self,
        p0: Tuple[float, float],
        p1: Tuple[float, float],
        p2: Tuple[float, float],
        p3: Tuple[float, float],
    ) -> None:
        self.p0 = p0
        self.p1 = p1
        self.p2 = p2
        self.p3 = p3

    def evaluate(self, t: float) -> Tuple[float, float]:
        """Evaluate (x, y) at parameter t in [0, 1]."""
        t = max(0.0, min(1.0, float(t)))
        u = 1.0 - t
        tt = t * t
        uu = u * u
        uuu = uu * u
        ttt = tt * t

        x = uuu * self.p0[0] + 3.0 * uu * t * self.p1[0] + 3.0 * u * tt * self.p2[0] + ttt * self.p3[0]
        y = uuu * self.p0[1] + 3.0 * uu * t * self.p1[1] + 3.0 * u * tt * self.p2[1] + ttt * self.p3[1]
        return (x, y)

    def tangent_angle(self, t: float) -> float:
        """Evaluate tangent angle (in radians) along the curve at parameter t."""
        t = max(0.0, min(1.0, float(t)))
        u = 1.0 - t
        dx = 3.0 * u * u * (self.p1[0] - self.p0[0]) + 6.0 * u * t * (self.p2[0] - self.p1[0]) + 3.0 * t * t * (self.p3[0] - self.p2[0])
        dy = 3.0 * u * u * (self.p1[1] - self.p0[1]) + 6.0 * u * t * (self.p2[1] - self.p1[1]) + 3.0 * t * t * (self.p3[1] - self.p2[1])
        return math.atan2(dy, dx)


class PathFollower(Node):
    """
    Container node that glides its child nodes along a parametric curve with automatic tangent rotation.
    """

    def __init__(
        self,
        curve: CubicBezierCurve,
        align_rotation: bool = True,
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)
        self.curve = curve
        self.align_rotation = align_rotation
        self.progress = Signal(0.0, f"{self.name}.progress")

    def follow(self, duration: float = 2.0, ease: Optional[EasingFunc] = None) -> AnimationAction:
        return self.progress.to(1.0, duration=duration, ease=ease or Ease.in_out_cubic)

    def draw(self, ctx: Any, time: float = 0.0) -> None:
        p = float(self.progress.get(time))
        x, y = self.curve.evaluate(p)

        ctx.save()
        ctx.translate(x, y)
        if self.align_rotation:
            angle = self.curve.tangent_angle(p)
            ctx.rotate(angle)

        # Draw child nodes at origin
        super().draw(ctx, time)
        ctx.restore()
