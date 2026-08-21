"""
Particle Physics Force Fields: Vortex, Turbulence, Gravity, and Attractors.
"""

from __future__ import annotations
import math
from typing import Any, Tuple, Union
from vibmo.core.vector import Vector2D


class ForceField:
    """Base class for physics forces affecting particle trajectories."""

    def calculate_force(self, pos: Vector2D, vel: Vector2D, time: float) -> Vector2D:
        raise NotImplementedError


class GravityField(ForceField):
    """Uniform linear directional gravity field."""

    def __init__(self, gravity: Union[Vector2D, Tuple[float, float]] = (0.0, 980.0)) -> None:
        self.gravity = Vector2D.from_any(gravity)

    def calculate_force(self, pos: Vector2D, vel: Vector2D, time: float) -> Vector2D:
        return self.gravity


class VortexForce(ForceField):
    """Circular rotational vortex swirl force around a center point."""

    def __init__(
        self,
        center: Union[Vector2D, Tuple[float, float]] = (960.0, 540.0),
        strength: float = 300.0,
        inward_pull: float = 50.0,
    ) -> None:
        self.center = Vector2D.from_any(center)
        self.strength = float(strength)
        self.inward_pull = float(inward_pull)

    def calculate_force(self, pos: Vector2D, vel: Vector2D, time: float) -> Vector2D:
        dx = pos.x - self.center.x
        dy = pos.y - self.center.y
        dist = math.hypot(dx, dy)
        if dist < 1.0:
            return Vector2D(0.0, 0.0)

        # Tangent vector perpendicular to radius
        tangent_x = -dy / dist
        tangent_y = dx / dist

        # Radial inward pull
        inward_x = -dx / dist
        inward_y = -dy / dist

        fx = tangent_x * self.strength + inward_x * self.inward_pull
        fy = tangent_y * self.strength + inward_y * self.inward_pull
        return Vector2D(fx, fy)


class TurbulentNoiseField(ForceField):
    """Simulates organic atmospheric turbulence using trigonometric harmonic noise."""

    def __init__(self, strength: float = 200.0, speed: float = 1.0, frequency: float = 0.005) -> None:
        self.strength = float(strength)
        self.speed = float(speed)
        self.frequency = float(frequency)

    def calculate_force(self, pos: Vector2D, vel: Vector2D, time: float) -> Vector2D:
        t = time * self.speed
        fx = math.sin(pos.y * self.frequency + t) * math.cos(pos.x * self.frequency * 0.5 + t * 0.7) * self.strength
        fy = math.cos(pos.x * self.frequency + t) * math.sin(pos.y * self.frequency * 0.5 + t * 0.7) * self.strength
        return Vector2D(fx, fy)


class AttractorPoint(ForceField):
    """Newtonian point mass gravitational attractor."""

    def __init__(self, center: Union[Vector2D, Tuple[float, float]], mass: float = 50000.0) -> None:
        self.center = Vector2D.from_any(center)
        self.mass = float(mass)

    def calculate_force(self, pos: Vector2D, vel: Vector2D, time: float) -> Vector2D:
        dx = self.center.x - pos.x
        dy = self.center.y - pos.y
        dist_sq = max(100.0, dx * dx + dy * dy)
        dist = math.sqrt(dist_sq)
        f = (self.mass / dist_sq)
        return Vector2D((dx / dist) * f, (dy / dist) * f)
