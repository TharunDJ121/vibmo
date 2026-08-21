"""
Deterministic, stateless generative particle systems for cinematic motion graphics.
Works perfectly with parallel, out-of-order frame rendering.
"""

from __future__ import annotations
import math
import random

from typing import Any, List, Optional, Tuple, Union
import cairo

from vibmo.core.vector import Vector2D
from vibmo.core.color import Color, colors
from vibmo.scene.node import Node
from vibmo.core.signal import AnimationAction


class ParticleDef:
    """Deterministic trajectory definition for a single particle."""
    __slots__ = (
        "start_time", "life", "start_pos", "velocity", "acceleration",
        "start_scale", "end_scale", "start_color", "end_color",
        "angular_vel", "drag"
    )
    def __init__(
        self,
        start_time: float,
        life: float,
        start_pos: Vector2D,
        velocity: Vector2D,
        acceleration: Vector2D,
        start_scale: float,
        end_scale: float,
        start_color: Color,
        end_color: Color,
        angular_vel: float,
        drag: float,
    ):
        self.start_time = start_time
        self.life = life
        self.start_pos = start_pos
        self.velocity = velocity
        self.acceleration = acceleration
        self.start_scale = start_scale
        self.end_scale = end_scale
        self.start_color = start_color
        self.end_color = end_color
        self.angular_vel = angular_vel
        self.drag = drag


class ParticleEmitter(Node):
    """
    Generative particle system node. Emits deterministic particles based on presets.
    """

    def __init__(
        self,
        preset: str = "sparkles",  # "sparkles", "confetti", "ambient_dust"
        gravity: Union[Vector2D, Tuple[float, float]] = (0.0, 980.0),
        drag: float = 0.0,
        colors_palette: Optional[List[Color]] = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)
        self.preset = preset
        self.gravity = Vector2D.from_any(gravity)
        self.drag = drag
        self.colors_palette = colors_palette or [colors.WHITE, colors.AMBER, colors.PINK, colors.CYAN]
        self._particles: List[ParticleDef] = []
        self.forces: List[Any] = []

    def add_force(self, *forces: Any) -> ParticleEmitter:
        """Adds physical force fields (VortexForce, TurbulentNoiseField, AttractorPoint)."""
        self.forces.extend(forces)
        return self

    def bind_audio(
        self,
        analyzer: Any,
        band: str = "bass",
        duration: float = 5.0,
        fps: float = 30.0,
        threshold: float = 0.6,
        burst_count: int = 20,
    ) -> None:
        """Procedurally spawns particle bursts synced to audio transients/bass beats."""
        total_frames = int(duration * fps)
        for i in range(total_frames):
            t = i / fps
            val = analyzer.bass(t) if band == "bass" else (analyzer.treble(t) if band == "treble" else analyzer.rms(t))
            if val >= threshold:
                self.burst(count=burst_count, time=t)

    def burst(self, count: int = 50, time: float = 0.0) -> None:

        """Injects a burst of particles starting at the given time."""
        rnd = random.Random(hash(self.name) + int(time * 1000))  # Deterministic seed based on time
        
        for _ in range(count):
            angle = rnd.uniform(0, math.pi * 2)
            
            if self.preset == "confetti":
                speed = rnd.uniform(300, 1200)
                life = rnd.uniform(2.0, 4.0)
                scale = rnd.uniform(0.5, 1.5)
                end_scale = scale
                ang_vel = rnd.uniform(-10.0, 10.0)
                drag = 1.2
            elif self.preset == "sparkles":
                speed = rnd.uniform(100, 500)
                life = rnd.uniform(0.5, 1.5)
                scale = rnd.uniform(0.3, 0.8)
                end_scale = 0.0
                ang_vel = rnd.uniform(-3.0, 3.0)
                drag = 0.5
            else: # ambient
                speed = rnd.uniform(10, 50)
                life = rnd.uniform(4.0, 8.0)
                scale = rnd.uniform(0.1, 0.4)
                end_scale = 0.0
                ang_vel = rnd.uniform(-1.0, 1.0)
                drag = 0.1

            vx = math.cos(angle) * speed
            vy = math.sin(angle) * speed
            
            color = rnd.choice(self.colors_palette)
            
            self._particles.append(ParticleDef(
                start_time=time,
                life=life,
                start_pos=Vector2D(0.0, 0.0),
                velocity=Vector2D(vx, vy),
                acceleration=self.gravity,
                start_scale=scale,
                end_scale=end_scale,
                start_color=color,
                end_color=color.with_alpha(0.0),
                angular_vel=ang_vel,
                drag=drag,
            ))

        from vibmo.core.signal import AnimationAction
        from vibmo.core.easing import Ease
        # Return a safe yieldable action representing the burst settling duration
        return AnimationAction(self.opacity, float(self.opacity.get(0.0)), duration=1.5, ease=Ease.linear, delay=0.0)

    def emit(self, duration: float, rate: float = 30.0, start_time: float = 0.0) -> AnimationAction:
        """Streams particles over a duration (rate is particles per second)."""
        count = int(duration * rate)
        for i in range(count):
            t = start_time + (i / rate)
            self.burst(count=1, time=t)
        
        from vibmo.core.signal import AnimationAction
        from vibmo.core.easing import Ease
        return AnimationAction(self.opacity, float(self.opacity.get(0.0)), duration=duration, ease=Ease.linear, delay=start_time)


    def draw(self, ctx: Any, time: float = 0.0) -> None:
        ctx.save()
        
        for p in self._particles:
            age = time - p.start_time
            if age <= 0 or age >= p.life:
                continue
                
            progress = age / p.life
            
            # Deterministic Physics Integration
            # For linear drag: v = v0 * exp(-drag * t) + g/drag * (1 - exp(-drag * t))
            # Pos: x = x0 + v0/drag * (1 - exp(-drag * t)) + g/drag * t - g/drag^2 * (1 - exp(-drag * t))
            if p.drag > 0.001:
                exp_d = math.exp(-p.drag * age)
                inv_d = 1.0 / p.drag
                px = p.start_pos.x + p.velocity.x * inv_d * (1.0 - exp_d) + p.acceleration.x * inv_d * age - p.acceleration.x * inv_d * inv_d * (1.0 - exp_d)
                py = p.start_pos.y + p.velocity.y * inv_d * (1.0 - exp_d) + p.acceleration.y * inv_d * age - p.acceleration.y * inv_d * inv_d * (1.0 - exp_d)
            else:
                px = p.start_pos.x + p.velocity.x * age + 0.5 * p.acceleration.x * age * age
                py = p.start_pos.y + p.velocity.y * age + 0.5 * p.acceleration.y * age * age

            # Apply additional force fields
            if self.forces:
                for force in self.forces:
                    f = force.calculate_force(Vector2D(px, py), p.velocity, time)
                    px += f.x * 0.5 * (age ** 2) * 0.05
                    py += f.y * 0.5 * (age ** 2) * 0.05

            scale = p.start_scale + (p.end_scale - p.start_scale) * progress

            rot = p.angular_vel * age
            
            # Color interpolate
            r = p.start_color.r + (p.end_color.r - p.start_color.r) * progress
            g = p.start_color.g + (p.end_color.g - p.start_color.g) * progress
            b = p.start_color.b + (p.end_color.b - p.start_color.b) * progress
            a = p.start_color.a + (p.end_color.a - p.start_color.a) * progress

            ctx.save()
            ctx.translate(px, py)
            ctx.rotate(rot)
            ctx.scale(scale, scale)
            
            ctx.set_source_rgba(r, g, b, a)
            
            if self.preset == "confetti":
                ctx.rectangle(-4, -8, 8, 16)
                ctx.fill()
            else:
                ctx.arc(0, 0, 5, 0, math.pi * 2)
                ctx.fill()
                
            ctx.restore()

        ctx.restore()
