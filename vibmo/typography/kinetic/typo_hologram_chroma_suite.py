import math
import random
from typing import Any
import cairo

from vibmo.core.color import Color, colors
from vibmo.core.vector import Vector2D
from vibmo.core.signal import Signal
from vibmo.scene.node import Node

class HologramChromaText(Node):
    """Shimmering semi-transparent holographic typography with moving rainbow specular sheen."""
    def __init__(self, text: str, font_size: float = 48.0, font_family: str = "Inter", **kwargs):
        super().__init__(**kwargs)
        self.text = text
        self.font_size = Signal(float(font_size), f"{self.name}.font_size")
        self.font_family = font_family

    def _setup_cairo_font(self, ctx: cairo.Context, font_size: float) -> None:
        ctx.select_font_face(self.font_family, cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
        ctx.set_font_size(font_size)

    def draw(self, ctx: Any, time: float = 0.0) -> None:
        fs = self.font_size.get(time)
        ctx.save()
        self._setup_cairo_font(ctx, fs)
        
        extents = ctx.text_extents(self.text)
        width = extents.width
        
        gradient = cairo.LinearGradient(0, 0, width, 0)
        
        for i in range(11):
            offset = i / 10.0
            # hue shifts over space (offset) and time
            hue = (offset + time * 0.5) % 1.0
            color = Color.hsl(hue * 360, 0.8, 0.6, 0.7)
            r, g, b, a = color.to_cairo()
            gradient.add_color_stop_rgba(offset, r, g, b, a)
            
        ctx.set_source(gradient)
        ctx.move_to(0, fs)
        ctx.show_text(self.text)
        
        ctx.restore()
        super().draw(ctx, time)

class InterferenceFringeLines(Node):
    """Horizontal optical thin-film interference lines drifting across letter surfaces."""
    def __init__(self, text: str, font_size: float = 48.0, font_family: str = "Inter", **kwargs):
        super().__init__(**kwargs)
        self.text = text
        self.font_size = Signal(float(font_size), f"{self.name}.font_size")
        self.font_family = font_family

    def _setup_cairo_font(self, ctx: cairo.Context, font_size: float) -> None:
        ctx.select_font_face(self.font_family, cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
        ctx.set_font_size(font_size)

    def draw(self, ctx: Any, time: float = 0.0) -> None:
        fs = self.font_size.get(time)
        ctx.save()
        self._setup_cairo_font(ctx, fs)
        
        extents = ctx.text_extents(self.text)
        width = extents.width
        
        # Create text path and clip to draw "across letter surfaces"
        ctx.move_to(0, fs)
        ctx.text_path(self.text)
        ctx.clip()
        
        line_height = 3.0
        num_lines = int((fs * 1.5) / line_height) + 2
        
        # Drift based on time
        y_offset = (time * 15.0) % line_height
        
        ctx.set_line_width(line_height * 0.8)
        
        # Expand bounds slightly outside strictly calculated range for seamless wrapping
        for i in range(-2, num_lines + 2):
            y = i * line_height + y_offset - (fs * 0.2)
            
            hue = ((y / fs) * 2.0 + time * 0.2) % 1.0
            color = Color.hsl(hue * 360, 0.9, 0.7, 0.6)
            
            ctx.set_source_rgba(*color.to_cairo())
            ctx.move_to(0, y)
            ctx.line_to(width, y)
            ctx.stroke()
            
        ctx.restore()
        super().draw(ctx, time)

class HologramEmitterCone(Node):
    """Semi-transparent blue projection light beam radiating from floor emitter up to text."""
    def __init__(self, width: float = 200.0, height: float = 300.0, emitter_width: float = 40.0, **kwargs):
        super().__init__(**kwargs)
        self.width = Signal(float(width), f"{self.name}.width")
        self.height = Signal(float(height), f"{self.name}.height")
        self.emitter_width = Signal(float(emitter_width), f"{self.name}.emitter_width")

    def draw(self, ctx: Any, time: float = 0.0) -> None:
        w = self.width.get(time)
        h = self.height.get(time)
        ew = self.emitter_width.get(time)
        
        ctx.save()
        
        # Cone path: Top is wide (w), Bottom is narrow (ew)
        ctx.move_to(-w/2, 0)
        ctx.line_to(w/2, 0)
        ctx.line_to(ew/2, h)
        ctx.line_to(-ew/2, h)
        ctx.close_path()
        
        # Gradient from bottom (h) to top (0)
        gradient = cairo.LinearGradient(0, h, 0, 0)
        gradient.add_color_stop_rgba(0.0, 0.0, 0.5, 1.0, 0.8)
        gradient.add_color_stop_rgba(1.0, 0.0, 0.8, 1.0, 0.0)
        
        ctx.set_source(gradient)
        ctx.fill()
        
        # Emitter base
        ctx.save()
        ctx.translate(0, h)
        ctx.scale(1.0, 0.2)
        ctx.arc(0, 0, ew/2, 0, 2 * math.pi)
        ctx.set_source_rgba(0.0, 0.8, 1.0, 0.9)
        ctx.fill()
        ctx.restore()
        
        ctx.restore()
        super().draw(ctx, time)

class GlitchDeconstruct(Node):
    """Subtle holographic signal flutter and glitch deconstruction."""
    def __init__(self, text: str, font_size: float = 48.0, font_family: str = "Inter", **kwargs):
        super().__init__(**kwargs)
        self.text = text
        self.font_size = Signal(float(font_size), f"{self.name}.font_size")
        self.font_family = font_family
        self._rng = random.Random()

    def _setup_cairo_font(self, ctx: cairo.Context, font_size: float) -> None:
        ctx.select_font_face(self.font_family, cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
        ctx.set_font_size(font_size)

    def draw(self, ctx: Any, time: float = 0.0) -> None:
        fs = self.font_size.get(time)
        
        # Time-based seeding for rapid frame-by-frame flutter
        self._rng.seed(int(time * 24.0) + id(self))
        
        ctx.save()
        self._setup_cairo_font(ctx, fs)
        
        glitch_amount = self._rng.random() * 5.0
        
        # Cyan channel offset
        ctx.save()
        ctx.set_source_rgba(0.0, 1.0, 1.0, 0.6)
        ctx.move_to(-glitch_amount, fs)
        ctx.show_text(self.text)
        ctx.restore()
        
        # Magenta channel offset
        ctx.save()
        ctx.set_source_rgba(1.0, 0.0, 1.0, 0.6)
        ctx.move_to(glitch_amount, fs)
        ctx.show_text(self.text)
        ctx.restore()
        
        # Main text
        ctx.save()
        ctx.set_source_rgba(1.0, 1.0, 1.0, 0.9)
        ctx.move_to(0, fs)
        ctx.show_text(self.text)
        ctx.restore()
        
        # Horizontal slice glitch masking
        num_slices = 5
        if self._rng.random() > 0.5:
            extents = ctx.text_extents(self.text)
            w = extents.width
            for _ in range(num_slices):
                y = self._rng.random() * fs * 1.5
                h = self._rng.random() * 4.0
                offset = (self._rng.random() - 0.5) * 15.0
                
                ctx.save()
                ctx.rectangle(-20, y, w + 40, h)
                ctx.clip()
                ctx.set_source_rgba(1.0, 1.0, 1.0, 0.5)
                ctx.move_to(offset, fs)
                ctx.show_text(self.text)
                ctx.restore()
                
        ctx.restore()
        super().draw(ctx, time)

