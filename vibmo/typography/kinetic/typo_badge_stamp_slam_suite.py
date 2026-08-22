import math
import random
from typing import Any, Tuple, Optional, List
import cairo

from vibmo.core.color import Color, colors
from vibmo.core.vector import Vector2D
from vibmo.core.signal import Signal, AnimationAction
from vibmo.core.easing import Ease
from vibmo.scene.node import Node


class DustPuffShockwave(Node):
    """
    Radial ring of dust and impact particles bursting outward upon stamp impact.
    """
    def __init__(self, color: Color = colors.GRAY, particle_count: int = 12, **kwargs):
        super().__init__(**kwargs)
        self.color = Signal(color, f"{self.name}.color")
        self.particle_count = particle_count
        self.progress = Signal(0.0, f"{self.name}.progress")
        self._rng = random.Random(id(self))
        self.particles = []
        for _ in range(self.particle_count):
            angle = self._rng.uniform(0, 2 * math.pi)
            speed = self._rng.uniform(50, 150)
            size = self._rng.uniform(2, 6)
            self.particles.append((angle, speed, size))

    def burst(self, duration: float = 0.5, delay: float = 0.0) -> AnimationAction:
        action = self.progress.to(1.0, duration=duration, ease=Ease.out_expo, delay=delay)
        action.apply_at(0.0) # Apply immediately so timeline isn't strictly required
        return action

    def draw(self, ctx: Any, time: float = 0.0) -> None:
        prog = self.progress.get(time)
        if prog <= 0.0 or prog >= 1.0:
            super().draw(ctx, time)
            return
            
        color = self.color.get(time)
        ctx.set_source_rgba(*color.to_cairo())
        
        for angle, speed, size in self.particles:
            dist = speed * prog
            x = math.cos(angle) * dist
            y = math.sin(angle) * dist
            
            ctx.arc(x, y, size * (1.0 - prog), 0, 2 * math.pi)
            ctx.fill()
            
        # Also draw an expanding ring
        ctx.arc(0, 0, 100 * prog, 0, 2 * math.pi)
        ctx.set_line_width(2.0 * (1.0 - prog))
        ctx.stroke()
        
        super().draw(ctx, time)


class InkedTextureMask(Node):
    """
    Grungy worn rubber stamp ink texture overlay with distressed edges.
    """
    def __init__(self, width: float = 200.0, height: float = 100.0, **kwargs):
        super().__init__(**kwargs)
        self.width = Signal(float(width), f"{self.name}.width")
        self.height = Signal(float(height), f"{self.name}.height")
        self._rng = random.Random(id(self))
        
        # Precompute some noise points for distress
        self.noise_points = []
        for _ in range(50):
            nx = self._rng.uniform(-0.5, 0.5)
            ny = self._rng.uniform(-0.5, 0.5)
            ns = self._rng.uniform(2, 8)
            self.noise_points.append((nx, ny, ns))

    def draw(self, ctx: Any, time: float = 0.0) -> None:
        w = self.width.get(time)
        h = self.height.get(time)
        
        ctx.save()
        ctx.set_operator(cairo.OPERATOR_DEST_OUT)
        ctx.set_source_rgba(0, 0, 0, 1) # Full opacity to cut out
        
        for nx, ny, ns in self.noise_points:
            x = nx * w
            y = ny * h
            ctx.arc(x, y, ns, 0, 2 * math.pi)
            ctx.fill()
            
        ctx.restore()
        super().draw(ctx, time)


class SpringReboundSettling(Node):
    """
    Bouncy elastic rebound physics settling into resting angle.
    """
    def __init__(self, resting_angle: float = 0.0, **kwargs):
        super().__init__(**kwargs)
        self.resting_angle = resting_angle
        self.rebound_progress = Signal(0.0, f"{self.name}.rebound_progress")
        
    def settle(self, duration: float = 0.6, delay: float = 0.0) -> AnimationAction:
        action = self.rebound_progress.to(1.0, duration=duration, ease=Ease.out_elastic, delay=delay)
        action.apply_at(0.0)
        return action
        
    def draw(self, ctx: Any, time: float = 0.0) -> None:
        prog = self.rebound_progress.get(time)
        
        start_angle = self.resting_angle - math.radians(15) 
        current_angle = start_angle + (self.resting_angle - start_angle) * prog
        
        ctx.save()
        if 0.0 < prog < 1.0:
            ctx.rotate(current_angle)
        elif prog >= 1.0:
            ctx.rotate(self.resting_angle)
        else:
            ctx.rotate(start_angle)
            
        super().draw(ctx, time)
        ctx.restore()


class RubberStampTitleSlam(Node):
    """
    Circular/rectangular badge title that drops from huge scale (3.0x) and slams down at 1.0x with camera shake.
    """
    def __init__(self, text: str, font_size: float = 64.0, font_family: str = "Inter", color: Color = colors.RED, **kwargs):
        super().__init__(**kwargs)
        self.text = text
        self.font_size = Signal(float(font_size), f"{self.name}.font_size")
        self.font_family = font_family
        self.color = Signal(color, f"{self.name}.color")
        
        self.slam_progress = Signal(0.0, f"{self.name}.slam_progress")
        self.shake_progress = Signal(0.0, f"{self.name}.shake_progress")
        
        # Add sub-components
        self.shockwave = DustPuffShockwave(color=color, name=f"{self.name}_shockwave")
        self.rebound = SpringReboundSettling(resting_angle=0.0, name=f"{self.name}_rebound")
        self.texture_mask = InkedTextureMask(width=font_size * len(text) * 0.6, height=font_size * 1.5, name=f"{self.name}_mask")
        
        # Let's attach them logically so the scene graph manages them.
        self.add(self.shockwave)
        
        self.scale.set((3.0, 3.0))
        self._rng = random.Random(id(self))

    def slam(self, delay: float = 0.1, duration: float = 0.6) -> AnimationAction:
        action_slam = self.scale.to((1.0, 1.0), duration=duration * 0.5, ease=Ease.in_expo, delay=delay)
        action_slam.apply_at(0.0)
        
        impact_time = delay + duration * 0.5
        self.shockwave.burst(duration=0.5, delay=impact_time)
        
        shake_action = self.shake_progress.to(1.0, duration=0.3, ease=Ease.linear, delay=impact_time)
        shake_action.apply_at(0.0)
        
        self.rebound.settle(duration=duration * 0.5, delay=impact_time)
        
        return action_slam
        
    def _setup_cairo_font(self, ctx: cairo.Context, font_size: float) -> None:
        ctx.select_font_face(self.font_family, cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
        ctx.set_font_size(font_size)

    def draw(self, ctx: Any, time: float = 0.0) -> None:
        shake_prog = self.shake_progress.get(time)
        shake_x = 0.0
        shake_y = 0.0
        if 0.0 < shake_prog < 1.0:
            intensity = (1.0 - shake_prog) * 10.0
            shake_x = (self._rng.random() * 2 - 1) * intensity
            shake_y = (self._rng.random() * 2 - 1) * intensity
            
        ctx.save()
        ctx.translate(shake_x, shake_y)
        
        # We also want the rebound rotation
        prog_reb = self.rebound.rebound_progress.get(time)
        start_angle = self.rebound.resting_angle - math.radians(15)
        current_angle = start_angle + (self.rebound.resting_angle - start_angle) * prog_reb
        if 0.0 < prog_reb < 1.0:
            ctx.rotate(current_angle)
        elif prog_reb >= 1.0:
            ctx.rotate(self.rebound.resting_angle)
        else:
            ctx.rotate(start_angle)
            
        # Draw text
        fs = self.font_size.get(time)
        c = self.color.get(time)
        ctx.set_source_rgba(*c.to_cairo())
        self._setup_cairo_font(ctx, fs)
        
        extents = ctx.text_extents(self.text)
        x = -(extents.width / 2 + extents.x_bearing)
        y = -(extents.height / 2 + extents.y_bearing)
        ctx.move_to(x, y)
        ctx.show_text(self.text)
        
        # Border
        ctx.set_line_width(4.0)
        padding = 10.0
        w = extents.width + padding * 2
        h = extents.height + padding * 2
        bx = -w / 2
        by = -h / 2
        ctx.rectangle(bx, by, w, h)
        ctx.stroke()
        
        # Apply texture mask
        self.texture_mask.draw(ctx, time)
        
        ctx.restore()
        
        super().draw(ctx, time)
