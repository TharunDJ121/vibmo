"""
Motion Path Engine: Animate nodes along arbitrary SVG paths and Bézier curves with automatic tangential orientation.
"""

from __future__ import annotations
import math
from typing import Any, List, Optional, Sequence, Tuple, Union
import svgelements

from vibmo.core.vector import Vector2D
from vibmo.core.signal import Signal, AnimationAction
from vibmo.core.easing import Ease, EasingFunc
from vibmo.primitives.path import Path


class _MotionPathBinding:
    def __init__(self, svg_path: svgelements.Path, progress_sig: Signal, auto_orient: bool = True, offset_angle: float = 0.0):
        self.svg_path = svg_path
        self.progress_sig = progress_sig
        self.auto_orient = auto_orient
        self.offset_angle = offset_angle

    def get_pos(self, t: float) -> Vector2D:
        p_val = max(0.0, min(1.0, float(self.progress_sig.get(t))))
        try:
            pt = self.svg_path.point(p_val)
            return Vector2D(float(pt.x), float(pt.y))
        except Exception:
            return Vector2D(0.0, 0.0)

    def get_rotation(self, t: float) -> float:
        if not self.auto_orient:
            return 0.0
        p_val = max(0.0, min(1.0, float(self.progress_sig.get(t))))
        eps = 1e-3
        p0 = max(0.0, p_val - eps)
        p1 = min(1.0, p_val + eps)
        try:
            pt0 = self.svg_path.point(p0)
            pt1 = self.svg_path.point(p1)
            dx = float(pt1.x - pt0.x)
            dy = float(pt1.y - pt0.y)
            return math.atan2(dy, dx) + self.offset_angle
        except Exception:
            return 0.0


class MotionPathAction(AnimationAction):
    """Animates a node along an SVG path curve."""

    def __init__(
        self,
        node: Any,
        path_or_d: Union[str, Path, svgelements.Path],
        duration: float = 2.0,
        auto_orient: bool = True,
        offset_angle: float = 0.0,
        ease: EasingFunc = Ease.in_out_cubic,
        delay: float = 0.0,
    ) -> None:
        self.node = node
        if isinstance(path_or_d, Path):
            self.svg_path = path_or_d._svg_path
        elif isinstance(path_or_d, str):
            self.svg_path = svgelements.Path(path_or_d)
        else:
            self.svg_path = path_or_d

        self.progress_sig = Signal(0.0, f"{node.name}.motion_path_progress")
        self.binding = _MotionPathBinding(self.svg_path, self.progress_sig, auto_orient, offset_angle)
        
        # Bind position & rotation
        self.node.position.bind(lambda t: self.binding.get_pos(t))
        if auto_orient:
            self.node.rotation.bind(lambda t: self.binding.get_rotation(t))

        super().__init__(
            signal=self.progress_sig,
            target_value=1.0,
            duration=duration,
            ease=ease,
            delay=delay,
        )
