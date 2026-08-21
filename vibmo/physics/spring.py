"""
High-fidelity second-order physical spring engine and damped harmonic oscillator.
"""

from __future__ import annotations
import math
from typing import Any, Callable, List, Optional, Tuple, Union
from dataclasses import dataclass


@dataclass
class SpringParameters:
    """Parameters for a physical spring simulation."""
    stiffness: float = 180.0
    damping: float = 12.0
    mass: float = 1.0
    initial_velocity: float = 0.0
    rest_threshold: float = 0.001


class SpringSimulation:
    """
    Simulates second-order differential damped harmonic spring physics:
    m * x'' + c * x' + k * (x - target) = 0
    """

    def __init__(
        self,
        stiffness: float = 180.0,
        damping: float = 12.0,
        mass: float = 1.0,
        initial_velocity: float = 0.0,
    ) -> None:
        self.k = float(stiffness)
        self.c = float(damping)
        self.m = max(1e-4, float(mass))
        self.v0 = float(initial_velocity)

        # Derived physical characteristics
        # Damping ratio zeta = c / (2 * sqrt(k * m))
        self.omega0 = math.sqrt(self.k / self.m)  # Undamped natural angular frequency
        self.zeta = self.c / (2.0 * math.sqrt(self.k * self.m))  # Damping ratio
        self.omega_d = self.omega0 * math.sqrt(max(0.0, 1.0 - self.zeta ** 2))  # Damped angular frequency

    def evaluate(self, t: float) -> float:
        """Evaluate normalized spring position at time t (starts at 0.0, settles at 1.0)."""
        if t <= 0.0:
            return 0.0

        zeta = self.zeta
        w0 = self.omega0
        wd = self.omega_d

        if zeta < 1.0:
            # Underdamped (oscillates and settles with overshoot)
            decay = math.exp(-zeta * w0 * t)
            c1 = 1.0
            c2 = (zeta * w0 + self.v0) / max(1e-4, wd)
            pos = 1.0 - decay * (c1 * math.cos(wd * t) + c2 * math.sin(wd * t))
            return pos
        elif abs(zeta - 1.0) < 1e-4:
            # Critically damped (fastest settle without overshoot)
            decay = math.exp(-w0 * t)
            pos = 1.0 - decay * (1.0 + (w0 + self.v0) * t)
            return pos
        else:
            # Overdamped
            alpha = math.sqrt(zeta ** 2 - 1.0) * w0
            decay = math.exp(-zeta * w0 * t)
            pos = 1.0 - decay * (math.cosh(alpha * t) + ((zeta * w0 + self.v0) / alpha) * math.sinh(alpha * t))
            return pos

    def make_easing(self, duration: float = 1.0) -> Callable[[float], float]:
        """Convert spring simulation into a normalized [0, 1] easing function."""
        return lambda p: self.evaluate(p * duration)
