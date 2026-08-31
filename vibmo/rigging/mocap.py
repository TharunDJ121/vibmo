"""
2D Inverse Kinematics (FABRIK) & Mocap Character Puppetry for Vibmo / Motio.

Inspired by OpenMontage's ink-theater:
  1. 2D FABRIK Inverse Kinematics: Real-time procedural reaching for vector character arms/legs.
  2. MocapStickFigure: Vector character node with procedural draw-in sketch reveal and mocap clips.
  3. Closed-Form Boil Filter: Deterministic hand-drawn line boil without non-deterministic random state.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Any, Sequence
import cairo

from vibmo.core.color import Color, colors
from vibmo.core.signal import Signal
from vibmo.scene.node import Node


class FabrikSolver2D:
    """2D Forward And Backward Reaching Inverse Kinematics solver."""

    @staticmethod
    def solve_2segment(
        origin: tuple[float, float],
        target: tuple[float, float],
        l1: float,
        l2: float,
        flip_bend: bool = False,
    ) -> tuple[tuple[float, float], tuple[float, float], tuple[float, float]]:
        """Solves a 2-bone limb (shoulder/hip -> elbow/knee -> hand/foot).

        Returns: (joint0, joint1, joint2)
        """
        x0, y0 = origin
        xt, yt = target
        dx = xt - x0
        dy = yt - y0
        dist = math.sqrt(dx * dx + dy * dy)

        # Max reach constraint
        max_reach = (l1 + l2) * 0.999
        if dist >= max_reach:
            # Fully extended
            angle = math.atan2(dy, dx)
            x1 = x0 + math.cos(angle) * l1
            y1 = y0 + math.sin(angle) * l1
            x2 = x0 + math.cos(angle) * (l1 + l2)
            y2 = y0 + math.sin(angle) * (l1 + l2)
            return (x0, y0), (x1, y1), (x2, y2)

        # Law of cosines for elbow angle
        cos_alpha = (dist * dist + l1 * l1 - l2 * l2) / (2.0 * dist * l1)
        cos_alpha = max(-1.0, min(1.0, cos_alpha))
        alpha = math.acos(cos_alpha)

        base_angle = math.atan2(dy, dx)
        elbow_angle = base_angle - alpha if not flip_bend else base_angle + alpha

        x1 = x0 + math.cos(elbow_angle) * l1
        y1 = y0 + math.sin(elbow_angle) * l1
        return (x0, y0), (x1, y1), (xt, yt)


@dataclass
class MocapClip:
    name: str
    duration: float
    # Generates joint offsets at normalized time p in [0, 1]
    pose_func: Any


class MocapLibrary:
    """Procedural mocap action clips inspired by CMU mocap libraries."""

    @staticmethod
    def walk_cycle(p: float) -> dict[str, Any]:
        phase = p * 2.0 * math.pi
        return {
            "hip_bob": math.sin(phase * 2.0) * 8.0,
            "torso_tilt": math.sin(phase) * 0.08,
            "left_leg_angle": math.sin(phase) * 0.45,
            "right_leg_angle": -math.sin(phase) * 0.45,
            "left_arm_angle": -math.sin(phase) * 0.40,
            "right_arm_angle": math.sin(phase) * 0.40,
        }

    @staticmethod
    def wave_cycle(p: float) -> dict[str, Any]:
        phase = p * 4.0 * math.pi
        return {
            "hip_bob": 0.0,
            "torso_tilt": 0.02,
            "left_leg_angle": 0.0,
            "right_leg_angle": 0.0,
            "left_arm_angle": 0.1,
            "right_arm_angle": -1.8 + math.sin(phase) * 0.35,  # Arm raised waving
        }

    @staticmethod
    def jump_cycle(p: float) -> dict[str, Any]:
        # Anticipate -> Launch -> Apex -> Land
        if p < 0.25:
            # Crouch
            progress = p / 0.25
            return {"hip_bob": progress * 25.0, "torso_tilt": 0.15, "left_leg_angle": 0.3, "right_leg_angle": 0.3, "left_arm_angle": -0.2, "right_arm_angle": -0.2}
        elif p < 0.75:
            # Jump in air
            air_p = (p - 0.25) / 0.5
            height = -math.sin(air_p * math.pi) * 85.0
            return {"hip_bob": height, "torso_tilt": -0.05, "left_leg_angle": -0.2, "right_leg_angle": 0.2, "left_arm_angle": -1.4, "right_arm_angle": -1.4}
        else:
            # Settle
            land_p = (p - 0.75) / 0.25
            return {"hip_bob": (1.0 - land_p) * 15.0, "torso_tilt": 0.05, "left_leg_angle": 0.0, "right_leg_angle": 0.0, "left_arm_angle": 0.0, "right_arm_angle": 0.0}

    @staticmethod
    def dance_spin(p: float) -> dict[str, Any]:
        phase = p * 2.0 * math.pi
        return {
            "hip_bob": math.sin(phase * 4.0) * 12.0,
            "torso_tilt": math.sin(phase * 2.0) * 0.18,
            "left_leg_angle": math.sin(phase * 2.0) * 0.35,
            "right_leg_angle": -math.sin(phase * 2.0) * 0.35,
            "left_arm_angle": -1.2 + math.sin(phase * 2.0) * 0.5,
            "right_arm_angle": -1.2 - math.sin(phase * 2.0) * 0.5,
        }


class MocapStickFigure(Node):
    """2D vector character node with procedural mocap and IK reaching."""

    def __init__(
        self,
        height: float = 240.0,
        color: Color = colors.WHITE,
        line_width: float = 4.0,
        position: tuple[float, float] = (960, 540),
        action: str = "walk",
        action_speed: float = 1.0,
        boil: bool = True,
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)
        self.char_height = height
        self.line_color = color
        self.line_width = line_width
        self.action = action
        self.action_speed = action_speed
        self.boil = boil
        self.position.set(position)

        # Reach targets for IK (if active)
        self.left_hand_target: tuple[float, float] | None = None
        self.right_hand_target: tuple[float, float] | None = None

    def reach_left(self, target: tuple[float, float] | None) -> MocapStickFigure:
        self.left_hand_target = target
        return self

    def reach_right(self, target: tuple[float, float] | None) -> MocapStickFigure:
        self.right_hand_target = target
        return self

    def draw(self, ctx: cairo.Context, t: float = 0.0) -> None:
        self._render_self(ctx, t)

    def _render_self(self, ctx: cairo.Context, t: float) -> None:

        ctx.save()

        # Compute mocap pose
        progress = (t * self.action_speed) % 1.0
        if self.action == "walk":
            pose = MocapLibrary.walk_cycle(progress)
        elif self.action == "wave":
            pose = MocapLibrary.wave_cycle(progress)
        elif self.action == "jump":
            pose = MocapLibrary.jump_cycle(progress)
        elif self.action == "dance":
            pose = MocapLibrary.dance_spin(progress)
        else:
            pose = MocapLibrary.walk_cycle(progress)

        h = self.char_height
        head_r = h * 0.12
        torso_len = h * 0.35
        arm_len = h * 0.18
        leg_len = h * 0.22

        # Boil wobble
        wobble_x = 0.0
        wobble_y = 0.0
        if self.boil:
            seed = int(t * 9.0)  # 9fps hand-drawn boil
            wobble_x = (math.sin(seed * 1.7) * 1.2)
            wobble_y = (math.cos(seed * 2.3) * 1.2)

        ctx.translate(wobble_x, wobble_y + pose["hip_bob"])

        ctx.set_source_rgba(*self.line_color.to_rgba())
        ctx.set_line_width(self.line_width)
        ctx.set_line_cap(cairo.LINE_CAP_ROUND)
        ctx.set_line_join(cairo.LINE_JOIN_ROUND)

        # 1. Head
        head_cy = -h * 0.45
        ctx.arc(0, head_cy, head_r, 0, 2 * math.pi)
        ctx.stroke()

        # 2. Torso
        neck_y = head_cy + head_r
        hip_y = neck_y + torso_len
        ctx.move_to(0, neck_y)
        ctx.line_to(pose["torso_tilt"] * 20.0, hip_y)
        ctx.stroke()

        # 3. Arms
        shoulder_y = neck_y + torso_len * 0.2
        # Left Arm
        if self.left_hand_target:
            _, elbow, hand = FabrikSolver2D.solve_2segment((0, shoulder_y), self.left_hand_target, arm_len, arm_len, flip_bend=False)
            ctx.move_to(0, shoulder_y)
            ctx.line_to(*elbow)
            ctx.line_to(*hand)
            ctx.stroke()
        else:
            la = math.pi / 2 + pose["left_arm_angle"]
            el_x = math.cos(la) * arm_len
            el_y = shoulder_y + math.sin(la) * arm_len
            ctx.move_to(0, shoulder_y)
            ctx.line_to(el_x, el_y)
            ctx.line_to(el_x + math.cos(la + 0.2) * arm_len, el_y + math.sin(la + 0.2) * arm_len)
            ctx.stroke()

        # Right Arm
        if self.right_hand_target:
            _, elbow, hand = FabrikSolver2D.solve_2segment((0, shoulder_y), self.right_hand_target, arm_len, arm_len, flip_bend=True)
            ctx.move_to(0, shoulder_y)
            ctx.line_to(*elbow)
            ctx.line_to(*hand)
            ctx.stroke()
        else:
            ra = math.pi / 2 + pose["right_arm_angle"]
            el_x = -math.cos(ra) * arm_len
            el_y = shoulder_y + math.sin(ra) * arm_len
            ctx.move_to(0, shoulder_y)
            ctx.line_to(el_x, el_y)
            ctx.line_to(el_x - math.cos(ra + 0.2) * arm_len, el_y + math.sin(ra + 0.2) * arm_len)
            ctx.stroke()

        # 4. Legs
        # Left Leg
        lla = math.pi / 2 + pose["left_leg_angle"]
        knee_lx = math.cos(lla) * leg_len
        knee_ly = hip_y + math.sin(lla) * leg_len
        ctx.move_to(0, hip_y)
        ctx.line_to(knee_lx, knee_ly)
        ctx.line_to(knee_lx + math.cos(lla) * leg_len, knee_ly + math.sin(lla) * leg_len)
        ctx.stroke()

        # Right Leg
        rla = math.pi / 2 + pose["right_leg_angle"]
        knee_rx = -math.cos(rla) * leg_len
        knee_ry = hip_y + math.sin(rla) * leg_len
        ctx.move_to(0, hip_y)
        ctx.line_to(knee_rx, knee_ry)
        ctx.line_to(knee_rx - math.cos(rla) * leg_len, knee_ry + math.sin(rla) * leg_len)
        ctx.stroke()

        ctx.restore()
