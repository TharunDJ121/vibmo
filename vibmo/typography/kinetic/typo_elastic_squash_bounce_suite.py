import math
from typing import Any, Tuple
import cairo

from vibmo.core.color import Color, colors
from vibmo.core.vector import Vector2D
from vibmo.core.signal import Signal, AnimationAction
from vibmo.core.easing import Ease
from vibmo.scene.node import Node
from vibmo.typography.text import Text

class ElasticSquashBounceTitle(Node):
    def __init__(self, text: str, font_size: float = 64.0, font_family: str = "Inter", color: Color = colors.WHITE, **kwargs):
        super().__init__(**kwargs)
        self.text = text
        self.font_size = Signal(font_size, f"{self.name}.font_size")
        self.font_family = font_family
        self.color = Signal(color, f"{self.name}.color")
        
        self.bounce_progress = Signal(0.0, f"{self.name}.bounce_progress")

    def bounce_in(self, duration: float = 0.8) -> AnimationAction:
        return self.bounce_progress.to(1.0, duration=duration, ease=Ease.linear)

    def draw(self, ctx: Any, time: float = 0.0) -> None:
        prog = self.bounce_progress.get(time)
        fs = self.font_size.get(time)
        c = self.color.get(time)
        
        # Calculate bounce physics (height and squash)
        # We simulate a drop that bounces and squashes on impact
        # We'll use a damped sine wave for the y position
        if prog < 1.0:
            # Drop from top (e.g. y = -200) to 0, then bounce
            # A simple approximation for bounce + squash:
            # Let's map progress [0, 1] to a drop and bounce.
            pass
        
        # To maintain Volume = Scale_X * Scale_Y = 1.0:
        # Scale_X = 1.0 / Scale_Y
        
        scale_y = 1.0
        
        # Fall and bounce logic
        if prog <= 0.0:
            y_offset = -300.0
            scale_y = 1.0
        elif prog >= 1.0:
            y_offset = 0.0
            scale_y = 1.0
        else:
            # Fall phase: 0 to 0.4
            if prog < 0.4:
                # Accelerate down
                t = prog / 0.4
                y_offset = -300.0 * (1.0 - t * t)
                scale_y = 1.0 + 0.2 * t # Slight stretch while falling
            else:
                # Bounce and squash phase: 0.4 to 1.0
                t = (prog - 0.4) / 0.6
                
                # We need a damped oscillation around 0
                # When y hits 0, it squashes. 
                # Damped sine for squash:
                wobble = math.exp(-t * 5.0) * math.cos(t * math.pi * 4.0)
                
                # Wobble dictates scale_y.
                # When wobble is positive (first impact), scale_y is small (squash).
                # scale_y goes from e.g. 0.4 up to 1.0.
                # So we can use 1.0 - 0.6 * wobble
                scale_y = 1.0 - 0.5 * wobble
                
                # Make sure scale_y doesn't go to 0
                scale_y = max(0.1, scale_y)
                
                # The text stays at y=0 during the squash
                y_offset = 0.0
        
        scale_x = 1.0 / scale_y
        
        ctx.save()
        
        # We want to scale around the bottom center of the text.
        # First we need text extents to find the center
        ctx.select_font_face(self.font_family, cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
        ctx.set_font_size(fs)
        extents = ctx.text_extents(self.text)
        
        # Center x, bottom y
        cx = extents.x_bearing + extents.width / 2.0
        cy = 0.0 # Our base line
        
        ctx.translate(cx, cy + y_offset)
        ctx.scale(scale_x, scale_y)
        ctx.translate(-cx, -cy)
        
        ctx.set_source_rgba(c.r, c.g, c.b, c.a)
        ctx.move_to(0, 0)
        ctx.show_text(self.text)
        
        ctx.restore()
        super().draw(ctx, time)

class RhythmicImpactPumping(Node):
    def __init__(self, text: str, font_size: float = 64.0, font_family: str = "Inter", color: Color = colors.WHITE, bpm: float = 120.0, **kwargs):
        super().__init__(**kwargs)
        self.text = text
        self.font_size = Signal(font_size, f"{self.name}.font_size")
        self.font_family = font_family
        self.color = Signal(color, f"{self.name}.color")
        self.bpm = bpm

    def draw(self, ctx: Any, time: float = 0.0) -> None:
        fs = self.font_size.get(time)
        c = self.color.get(time)
        
        bps = self.bpm / 60.0
        beat_time = time * bps
        
        # Sawtooth wave for beat: peaks at integer beat_time, drops sharply
        beat_phase = beat_time % 1.0
        
        # Pump scale: pops up on beat, exponential decay
        scale = 1.0 + 0.3 * math.exp(-beat_phase * 5.0)
        
        ctx.save()
        
        ctx.select_font_face(self.font_family, cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
        ctx.set_font_size(fs)
        extents = ctx.text_extents(self.text)
        
        cx = extents.x_bearing + extents.width / 2.0
        cy = extents.y_bearing + extents.height / 2.0
        
        ctx.translate(cx, cy)
        ctx.scale(scale, scale)
        ctx.translate(-cx, -cy)
        
        ctx.set_source_rgba(c.r, c.g, c.b, c.a)
        ctx.move_to(0, 0)
        ctx.show_text(self.text)
        
        ctx.restore()
        super().draw(ctx, time)

class JellyMorphTypography(Node):
    def __init__(self, text: str, font_size: float = 64.0, font_family: str = "Inter", color: Color = colors.WHITE, **kwargs):
        super().__init__(**kwargs)
        self.text = text
        self.font_size = Signal(font_size, f"{self.name}.font_size")
        self.font_family = font_family
        self.color = Signal(color, f"{self.name}.color")
        self.progress = Signal(0.0, f"{self.name}.progress")

    def draw(self, ctx: Any, time: float = 0.0) -> None:
        prog = self.progress.get(time)
        fs = self.font_size.get(time)
        c = self.color.get(time)
        
        # Jelly oscillation that settles over time
        # We can just use time for continuous wobble, or prog for one-shot
        # Let's make it continuous based on time, but scaled by a wobble intensity
        # Or if prog is used, it's a one shot wobble. Let's do one-shot.
        if prog <= 0.0 or prog >= 1.0:
            scale_x, scale_y = 1.0, 1.0
        else:
            wobble = math.exp(-prog * 4.0) * math.sin(prog * math.pi * 6.0)
            scale_x = 1.0 + 0.3 * wobble
            scale_y = 1.0 / scale_x # Volume conservation!

        ctx.save()
        
        ctx.select_font_face(self.font_family, cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
        ctx.set_font_size(fs)
        extents = ctx.text_extents(self.text)
        
        cx = extents.x_bearing + extents.width / 2.0
        cy = extents.y_bearing + extents.height / 2.0
        
        ctx.translate(cx, cy)
        ctx.scale(scale_x, scale_y)
        ctx.translate(-cx, -cy)
        
        ctx.set_source_rgba(c.r, c.g, c.b, c.a)
        ctx.move_to(0, 0)
        ctx.show_text(self.text)
        
        ctx.restore()
        super().draw(ctx, time)

class ComicSpeedLines(Node):
    def __init__(self, radius: float = 100.0, line_count: int = 12, color: Color = colors.WHITE, **kwargs):
        super().__init__(**kwargs)
        self.radius = Signal(radius, f"{self.name}.radius")
        self.line_count = line_count
        self.color = Signal(color, f"{self.name}.color")
        self.progress = Signal(0.0, f"{self.name}.progress")

    def burst(self, duration: float = 0.5) -> AnimationAction:
        return self.progress.to(1.0, duration=duration, ease=Ease.out_expo)

    def draw(self, ctx: Any, time: float = 0.0) -> None:
        prog = self.progress.get(time)
        if prog <= 0.0 or prog >= 1.0:
            return
            
        r = self.radius.get(time)
        c = self.color.get(time)
        
        ctx.save()
        ctx.set_source_rgba(c.r, c.g, c.b, c.a * (1.0 - prog))
        ctx.set_line_width(4.0)
        ctx.set_line_cap(cairo.LINE_CAP_ROUND)
        
        inner_r = r + prog * 50.0
        outer_r = inner_r + (1.0 - prog) * 100.0
        
        for i in range(self.line_count):
            angle = i * (2.0 * math.pi / self.line_count)
            cos_a = math.cos(angle)
            sin_a = math.sin(angle)
            
            ctx.move_to(inner_r * cos_a, inner_r * sin_a)
            ctx.line_to(outer_r * cos_a, outer_r * sin_a)
            ctx.stroke()
            
        ctx.restore()
        super().draw(ctx, time)
