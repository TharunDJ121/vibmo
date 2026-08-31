import math
import random
from typing import Any, Tuple, Optional, List
import cairo

from vibmo.core.color import Color, colors
from vibmo.core.vector import Vector2D
from vibmo.core.signal import Signal, AnimationAction
from vibmo.core.easing import Ease, EasingFunc
from vibmo.scene.node import Node

class MagneticGravityLetters(Node):
    """
    Typography letters that drop individually under gravity, bounce elastically off canvas floor, 
    and settle into place.
    """
    def __init__(
        self, 
        text: str, 
        font_size: float = 48.0, 
        font_family: str = "Inter", 
        color: Color = colors.WHITE, 
        gravity: float = 2000.0, 
        floor_y: float = 500.0,
        restitution: float = 0.6,
        stagger_time: float = 0.1,
        **kwargs
    ):
        super().__init__(**kwargs)
        self.text = text
        self.font_size = Signal(float(font_size), f"{self.name}.font_size")
        self.font_family = font_family
        self.color = Signal(color, f"{self.name}.color")
        self.gravity = gravity
        self.floor_y = floor_y
        self.restitution = restitution
        self.stagger_time = stagger_time
        self.progress = Signal(0.0, f"{self.name}.progress")

    def snap_reassemble(
        self,
        duration: float = 1.5,
        delay: float = 0.0,
        ease: Optional[Any] = None,
    ) -> AnimationAction:
        """Animates scattered letters snapping back and reassembling under magnetic pull into resting alignment."""
        self.progress.set(0.0)
        e = ease or Ease.out_elastic
        return self.progress.to(1.0, duration=duration, ease=e, delay=delay)
        
    def _setup_cairo_font(self, ctx: cairo.Context, font_size: float) -> None:
        ctx.select_font_face(self.font_family, cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
        ctx.set_font_size(font_size)
        
    def get_letter_y(self, t: float) -> float:
        """Calculate y position based on gravity and bouncing."""
        if t <= 0:
            return 0.0
            
        # Physics simulation formula for bouncing
        # Initial drop height = 0 (relative to original pos)
        # Floor is at floor_y
        
        # Free fall time to floor
        t_drop = math.sqrt(2 * self.floor_y / self.gravity)
        
        if t < t_drop:
            return 0.5 * self.gravity * t**2
            
        t_curr = t - t_drop
        curr_vel = math.sqrt(2 * self.gravity * self.floor_y) * self.restitution
        curr_y = self.floor_y
        
        # Simulate bounces
        # To avoid infinite loops, calculate max bounces or until velocity is very small
        while curr_vel > 1.0:
            # Time for one full parabolic bounce (up and down)
            t_bounce = 2 * curr_vel / self.gravity
            
            if t_curr < t_bounce:
                # We are in this bounce
                return self.floor_y - (curr_vel * t_curr - 0.5 * self.gravity * t_curr**2)
                
            t_curr -= t_bounce
            curr_vel *= self.restitution
            
        return self.floor_y

    def draw(self, ctx: Any, time: float = 0.0) -> None:
        prog = self.progress.get(time)
        fs = self.font_size.get(time)
        c = self.color.get(time)
        
        ctx.save()
        self._setup_cairo_font(ctx, fs)
        ctx.set_source_rgba(c.r, c.g, c.b, c.a)
        
        current_x = 0.0
        # Estimate advancement for glitch effects, or query Cairo
        advancement = fs * 0.6 # rough estimate for fixed width behavior
        
        for i, char in enumerate(self.text):
            # Calculate time for this specific letter
            letter_t = prog - (i * self.stagger_time)
            
            y_offset = self.get_letter_y(letter_t)
            
            ctx.move_to(current_x, fs * 0.88 + y_offset)
            ctx.show_text(char)
            
            extents = ctx.text_extents(char)
            current_x += extents.x_advance
            
        ctx.restore()
        super().draw(ctx, time)

class ExplosiveScatterForce(Node):
    """
    Force pulse that blasts letters into chaos before magnetic snapback.
    """
    def __init__(
        self, 
        text: str, 
        font_size: float = 48.0, 
        font_family: str = "Inter", 
        color: Color = colors.WHITE, 
        explosion_center: Tuple[float, float] = (0.0, 0.0),
        blast_force: float = 1000.0,
        friction: float = 5.0,
        **kwargs
    ):
        super().__init__(**kwargs)
        self.text = text
        self.font_size = Signal(float(font_size), f"{self.name}.font_size")
        self.font_family = font_family
        self.color = Signal(color, f"{self.name}.color")
        self.explosion_center = explosion_center
        self.blast_force = blast_force
        self.friction = friction
        self.progress = Signal(0.0, f"{self.name}.progress")
        self._rng = random.Random(hash(text))
        
    def _setup_cairo_font(self, ctx: cairo.Context, font_size: float) -> None:
        ctx.select_font_face(self.font_family, cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
        ctx.set_font_size(font_size)

    def draw(self, ctx: Any, time: float = 0.0) -> None:
        prog = self.progress.get(time)
        fs = self.font_size.get(time)
        c = self.color.get(time)
        
        ctx.save()
        self._setup_cairo_font(ctx, fs)
        ctx.set_source_rgba(c.r, c.g, c.b, c.a)
        
        current_x = 0.0
        
        for i, char in enumerate(self.text):
            # Base position
            base_x = current_x
            base_y = 0.0
            
            # Vector from explosion center to base position
            dx = base_x - self.explosion_center[0]
            dy = base_y - self.explosion_center[1]
            dist = math.sqrt(dx**2 + dy**2)
            
            # Avoid division by zero
            if dist < 0.1:
                dist = 0.1
                dx = 0.1
                dy = 0.1
                
            # Normalize and add some randomness
            self._rng.seed(hash(char) + i)
            nx = dx / dist + (self._rng.random() - 0.5) * 0.5
            ny = dy / dist + (self._rng.random() - 0.5) * 0.5
            
            # Initial velocity inversely proportional to distance
            v0 = self.blast_force / (dist**0.5)
            
            # Position at time t with friction:
            # x(t) = x0 + v0 * (1 - exp(-friction * t)) / friction
            if prog > 0:
                t = prog
                d_pos = v0 * (1 - math.exp(-self.friction * t)) / self.friction
                
                final_x = base_x + nx * d_pos
                final_y = base_y + ny * d_pos
                
                # Add rotation based on velocity
                rot = nx * d_pos * 0.05
                
                ctx.save()
                ctx.translate(final_x, final_y + fs * 0.88)
                ctx.rotate(rot)
                ctx.move_to(0, 0)
                ctx.show_text(char)
                ctx.restore()
            else:
                ctx.move_to(base_x, base_y + fs * 0.88)
                ctx.show_text(char)
                
            extents = ctx.text_extents(char)
            current_x += extents.x_advance
            
        ctx.restore()
        super().draw(ctx, time)

class MagnetPullReassembly(Node):
    """
    Strong magnetic attraction drawing scattered letters back into perfect headline alignment.
    """
    def __init__(
        self, 
        text: str, 
        font_size: float = 48.0, 
        font_family: str = "Inter", 
        color: Color = colors.WHITE, 
        pull_speed: float = 4.0,
        **kwargs
    ):
        super().__init__(**kwargs)
        self.text = text
        self.font_size = Signal(float(font_size), f"{self.name}.font_size")
        self.font_family = font_family
        self.color = Signal(color, f"{self.name}.color")
        self.pull_speed = pull_speed
        self.progress = Signal(0.0, f"{self.name}.progress")
        self._rng = random.Random(42)

    def snap_reassemble(
        self,
        duration: float = 1.5,
        delay: float = 0.0,
        ease: Optional[Any] = None,
    ) -> AnimationAction:
        self.progress.set(0.0)
        e = ease or Ease.out_elastic
        return self.progress.to(1.0, duration=duration, ease=e, delay=delay)

    def _setup_cairo_font(self, ctx: cairo.Context, font_size: float) -> None:
        ctx.select_font_face(self.font_family, cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
        ctx.set_font_size(font_size)

    def draw(self, ctx: Any, time: float = 0.0) -> None:
        prog = self.progress.get(time)
        fs = self.font_size.get(time)
        c = self.color.get(time)
        
        ctx.save()
        self._setup_cairo_font(ctx, fs)
        ctx.set_source_rgba(c.r, c.g, c.b, c.a)
        
        current_x = 0.0
        
        for i, char in enumerate(self.text):
            # Target position
            target_x = current_x
            target_y = 0.0
            
            # Initial scattered position
            self._rng.seed(hash(char) + i * 1337)
            scatter_x = target_x + (self._rng.random() - 0.5) * 800
            scatter_y = target_y + (self._rng.random() - 0.5) * 600
            
            # Exponential decay to target
            factor = math.exp(-self.pull_speed * prog)
            
            # Smooth snap at the end
            if factor < 0.01:
                factor = 0.0
                
            curr_x = target_x + (scatter_x - target_x) * factor
            curr_y = target_y + (scatter_y - target_y) * factor
            
            # Rotation interpolates as well
            rot = (scatter_x - target_x) * 0.01 * factor
            
            ctx.save()
            ctx.translate(curr_x, curr_y + fs * 0.88)
            ctx.rotate(rot)
            ctx.move_to(0, 0)
            ctx.show_text(char)
            ctx.restore()
                
            extents = ctx.text_extents(char)
            current_x += extents.x_advance
            
        ctx.restore()
        super().draw(ctx, time)

class FloorContactShadow(Node):
    """
    Dynamic shadow expanding as letters approach ground.
    """
    def __init__(
        self,
        floor_y: float = 500.0,
        max_shadow_width: float = 100.0,
        max_shadow_height: float = 20.0,
        shadow_color: Color = Color.rgba(0, 0, 0, 0.5),
        **kwargs
    ):
        super().__init__(**kwargs)
        self.floor_y = floor_y
        self.max_shadow_width = max_shadow_width
        self.max_shadow_height = max_shadow_height
        self.shadow_color = shadow_color
        # Track the object's y position
        self.object_y = Signal(0.0, f"{self.name}.object_y")
        
    def draw(self, ctx: Any, time: float = 0.0) -> None:
        obj_y = self.object_y.get(time)
        
        # Calculate distance to floor
        dist = self.floor_y - obj_y
        
        if dist < 0:
            dist = 0
            
        # Shadow scales up as object approaches floor
        # Max scale at floor, 0 scale at e.g. 500px above
        max_dist = 500.0
        scale = max(0.0, 1.0 - (dist / max_dist))
        
        # Opacity also increases
        alpha = scale * self.shadow_color.a
        
        if scale > 0.01:
            w = self.max_shadow_width * scale
            h = self.max_shadow_height * scale
            
            ctx.save()
            
            ctx.translate(0, self.floor_y)
            ctx.scale(w, h)
            
            ctx.arc(0, 0, 1, 0, 2 * math.pi)
            
            ctx.set_source_rgba(self.shadow_color.r, self.shadow_color.g, self.shadow_color.b, alpha)
            ctx.fill()
            
            ctx.restore()
            
        super().draw(ctx, time)
