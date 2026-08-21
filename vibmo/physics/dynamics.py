"""
Dynamics simulation engine for pendulums, elastic recoil, and collision bounce dynamics.
"""

from __future__ import annotations
import math
from typing import Any, Callable, Optional, Tuple


class PendulumDynamics:
    """
    Physical simple pendulum motion with gravity and air resistance drag:
    theta''(t) + (b/m)*theta'(t) + (g/L)*sin(theta) = 0
    """

    def __init__(
        self,
        length: float = 200.0,
        initial_angle_deg: float = 35.0,
        damping: float = 0.08,
        gravity: float = 980.0,
    ) -> None:
        self.length = max(1.0, float(length))
        self.theta0 = math.radians(initial_angle_deg)
        self.damping = float(damping)
        self.g = float(gravity)
        self.omega = math.sqrt(self.g / self.length)

    def angle_at(self, t: float) -> float:
        """Returns the pendulum angle in radians at timestamp t."""
        decay = math.exp(-self.damping * t)
        return self.theta0 * decay * math.cos(self.omega * t)

    def position_at(self, t: float, origin: Tuple[float, float] = (0.0, 0.0)) -> Tuple[float, float]:
        """Returns the (x, y) coordinates of the pendulum bob at timestamp t."""
        angle = self.angle_at(t)
        x = origin[0] + math.sin(angle) * self.length
        y = origin[1] + math.cos(angle) * self.length
        return (x, y)


class BounceDynamics:
    """
    Simulates physical coefficient of restitution gravity bounce against a floor plane.
    """

    def __init__(
        self,
        height: float = 300.0,
        restitution: float = 0.65,
        gravity: float = 1200.0,
    ) -> None:
        self.h0 = max(0.0, float(height))
        self.e = max(0.0, min(0.99, float(restitution)))
        self.g = max(1.0, float(gravity))

    def evaluate(self, t: float) -> float:
        """Returns the normalized altitude (1.0 at initial height, 0.0 on ground) at timestamp t."""
        if t <= 0.0:
            return 1.0

        # Calculate bounce intervals
        t_cur = t
        v = 0.0
        h = self.h0

        # First drop
        t_first = math.sqrt(2.0 * self.h0 / self.g)
        if t_cur <= t_first:
            return 1.0 - (0.5 * self.g * t_cur ** 2) / self.h0

        t_cur -= t_first
        v_rebound = math.sqrt(2.0 * self.g * self.h0) * self.e

        # Subsequent bounces
        for _ in range(20):
            t_flight = 2.0 * v_rebound / self.g
            if t_cur <= t_flight:
                y = v_rebound * t_cur - 0.5 * self.g * t_cur ** 2
                return max(0.0, min(1.0, y / self.h0))
            t_cur -= t_flight
            v_rebound *= self.e
            if v_rebound < 1.0:
                return 0.0

        return 0.0
