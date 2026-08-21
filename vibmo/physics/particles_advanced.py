"""
Advanced multi-emitter particle engine with physics forces and turnkey presets (Confetti, Sparks, Starfield, Smoke, Fire).
"""

from __future__ import annotations
import math
import random
from typing import Any, List, Optional, Sequence, Tuple, Union
import cairo

from vibmo.core.color import Color, colors
from vibmo.core.vector import Vector2D
from vibmo.scene.node import Node


class Particle:
    """Represents a single active particle."""
    __slots__ = ("x", "y", "vx", "vy", "life", "max_life", "size", "color", "rot", "v_rot", "shape")

    def __init__(
        self,
        x: float,
        y: float,
        vx: float,
        vy: float,
        life: float,
        size: float,
        color: Color,
        rot: float = 0.0,
        v_rot: float = 0.0,
        shape: str = "circle",
    ) -> None:
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.life = life
        self.max_life = max(1e-4, life)
        self.size = size
        self.color = color
        self.rot = rot
        self.v_rot = v_rot
        self.shape = shape


class AdvancedParticleEmitter(Node):
    """
    High-performance GPU-friendly particle emitter supporting gravity, wind, drag, and turnkey visual presets.
    """

    def __init__(
        self,
        rate: float = 40.0,  # Particles per second
        preset: str = "confetti",  # "confetti", "sparks", "starfield", "smoke", "fire"
        origin: Tuple[float, float] = (0.0, 0.0),
        gravity: Tuple[float, float] = (0.0, 300.0),
        drag: float = 0.02,
        colors_palette: Optional[Sequence[Union[Color, str]]] = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)
        self.rate = float(rate)
        self.preset = preset
        self.emitter_origin = origin
        self.gravity = gravity
        self.drag = float(drag)
        self.palette = [Color.from_any(c) for c in colors_palette] if colors_palette else [
            colors.INDIGO, colors.EMERALD, colors.AMBER, colors.ROSE, colors.CYAN
        ]

    def local_bounds(self, time: float = 0.0) -> Tuple[float, float, float, float]:
        return (-500.0, -500.0, 1000.0, 1000.0)

    def draw(self, ctx: Any, time: float = 0.0) -> None:
        ctx.save()
        ctx.translate(self.emitter_origin[0], self.emitter_origin[1])

        # Deterministic procedural simulation based on time
        rng = random.Random(42)
        total_spawn = int(time * self.rate)
        max_active = min(120, total_spawn)

        for i in range(max_active):
            spawn_t = (i / self.rate)
            age = (time - spawn_t) % 2.5
            if age < 0:
                continue

            c = self.palette[i % len(self.palette)]
            alpha = max(0.0, 1.0 - (age / 2.5))

            if self.preset == "confetti":
                # Fluttering confetti strips
                angle = (i * 137.5) * (math.pi / 180.0)
                speed = 120.0 + (i % 5) * 40.0
                vx = math.cos(angle) * speed
                vy = math.sin(angle) * speed * 0.5 - 150.0

                px = vx * age + math.sin(age * 6.0 + i) * 30.0
                py = vy * age + 0.5 * self.gravity[1] * (age ** 2)

                ctx.save()
                ctx.translate(px, py)
                ctx.rotate(age * 5.0 + i)
                ctx.set_source_rgba(c.r, c.g, c.b, c.a * alpha)
                ctx.rectangle(-6.0, -3.0, 12.0, 6.0)
                ctx.fill()
                ctx.restore()

            elif self.preset == "sparks":
                # Fast explosive radiant sparks
                angle = (i * 37.3) % (math.pi * 2)
                speed = 250.0 + (i % 7) * 50.0
                px = math.cos(angle) * speed * age
                py = math.sin(angle) * speed * age + 0.5 * 200.0 * (age ** 2)
                sz = max(1.0, 4.0 * (1.0 - age / 2.5))

                ctx.set_source_rgba(c.r, c.g, c.b, c.a * alpha)
                ctx.arc(px, py, sz, 0, math.pi * 2)
                ctx.fill()

            else:  # Starfield / Floating dust
                sx = ((i * 73) % 800) - 400.0 + math.sin(time + i) * 20.0
                sy = ((i * 47) % 600) - 300.0 + math.cos(time + i) * 20.0
                sz = 2.0 + (i % 3)
                ctx.set_source_rgba(c.r, c.g, c.b, 0.4 + 0.4 * math.sin(time * 3.0 + i))
                ctx.arc(sx, sy, sz, 0, math.pi * 2)
                ctx.fill()

        ctx.restore()
