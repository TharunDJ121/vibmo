"""
Analytical and Numerical Damped Harmonic Oscillator Spring Physics.
"""

from __future__ import annotations
import math
from typing import Tuple


class Spring:
    """
    High-precision analytical damped spring simulation:
    m * x'' + c * x' + k * (x - target) = 0
    """

    __slots__ = (
        "mass",
        "stiffness",
        "damping",
        "initial_velocity",
        "omega0",
        "zeta",
        "omega_d",
        "_settling_duration",
    )

    def __init__(
        self,
        stiffness: float = 100.0,
        damping: float = 10.0,
        mass: float = 1.0,
        initial_velocity: float = 0.0,
    ) -> None:
        self.mass = max(1e-4, float(mass))
        self.stiffness = max(1e-4, float(stiffness))
        self.damping = max(0.0, float(damping))
        self.initial_velocity = float(initial_velocity)

        # Undamped angular frequency
        self.omega0 = math.sqrt(self.stiffness / self.mass)
        # Damping ratio
        self.zeta = self.damping / (2.0 * math.sqrt(self.stiffness * self.mass))
        # Damped angular frequency
        if self.zeta < 1.0:
            self.omega_d = self.omega0 * math.sqrt(1.0 - self.zeta * self.zeta)
        else:
            self.omega_d = 0.0

        self._settling_duration = self._compute_settling_time()

    @property
    def settling_duration(self) -> float:
        return self._settling_duration

    def _compute_settling_time(self, threshold: float = 0.001, max_time: float = 10.0) -> float:
        """Finds the time in seconds after which the displacement remains within threshold."""
        dt = 0.02
        t = 0.0
        last_outside = 0.0
        while t <= max_time:
            val = self.evaluate(t, start=0.0, target=1.0)
            if abs(val - 1.0) > threshold:
                last_outside = t
            t += dt
        return max(0.2, min(max_time, last_outside + 0.1))

    def evaluate(self, t: float, start: float = 0.0, target: float = 1.0) -> float:
        """Evaluates spring displacement at time t seconds."""
        if t <= 0.0:
            return start

        delta = start - target
        v0 = self.initial_velocity

        if self.zeta < 1.0:
            # Underdamped
            decay = math.exp(-self.zeta * self.omega0 * t)
            c1 = delta
            c2 = (v0 + self.zeta * self.omega0 * delta) / self.omega_d
            pos = decay * (c1 * math.cos(self.omega_d * t) + c2 * math.sin(self.omega_d * t))
            return target + pos
        elif abs(self.zeta - 1.0) < 1e-6:
            # Critically damped
            decay = math.exp(-self.omega0 * t)
            c1 = delta
            c2 = v0 + self.omega0 * delta
            pos = decay * (c1 + c2 * t)
            return target + pos
        else:
            # Overdamped
            alpha = self.omega0 * math.sqrt(self.zeta * self.zeta - 1.0)
            r1 = -self.zeta * self.omega0 + alpha
            r2 = -self.zeta * self.omega0 - alpha
            c2 = (v0 - r1 * delta) / (r2 - r1)
            c1 = delta - c2
            pos = c1 * math.exp(r1 * t) + c2 * math.exp(r2 * t)
            return target + pos


class SpringEasing:
    """Wraps a Spring so it acts as a normalized [0, 1] easing function over duration."""

    def __init__(
        self,
        stiffness: float = 100.0,
        damping: float = 10.0,
        mass: float = 1.0,
        initial_velocity: float = 0.0,
    ) -> None:
        self.spring = Spring(stiffness=stiffness, damping=damping, mass=mass, initial_velocity=initial_velocity)
        self.duration = self.spring.settling_duration

    def __call__(self, t_normalized: float) -> float:
        # Map normalized [0, 1] to actual physical settling time
        t_seconds = max(0.0, min(1.0, t_normalized)) * self.duration
        return self.spring.evaluate(t_seconds, start=0.0, target=1.0)
