import math
import cairo
from typing import Any, Optional

from vibmo.core.color import Color, colors
from vibmo.core.vector import Vector2D
from vibmo.core.signal import Signal, AnimationAction
from vibmo.core.easing import Ease, EasingFunc
from vibmo.scene.node import Node

class SlitScanVideoSynthText(Node):
    """
    1970s analog video synth typography with continuous horizontal 
    and vertical spatial slit-scan stretching.
    """
    def __init__(self, text: str, font_size: float = 48.0, font_family: str = "Inter", 
                 color: Color = colors.WHITE, scan_speed: float = 1.0, 
                 amplitude: float = 10.0, frequency: float = 0.05, **kwargs):
        super().__init__(**kwargs)
        self.text = text
        self.font_size = Signal(float(font_size), f"{self.name}.font_size")
        self.font_family = font_family
        self.color = Signal(color, f"{self.name}.color")
        self.scan_speed = scan_speed
        self.amplitude = amplitude
        self.frequency = frequency
        self.warp_progress = Signal(1.0, f"{self.name}.warp_progress")

    def warp_scan(
        self,
        duration: float = 2.0,
        delay: float = 0.0,
        ease: Optional[EasingFunc] = None,
    ) -> AnimationAction:
        """Animates a dynamic optical slit-scan warp sweep across the text."""
        self.warp_progress.set(0.0)
        e = ease or Ease.in_out_sine
        return self.warp_progress.to(1.0, duration=duration, ease=e, delay=delay)
        
    def _setup_cairo_font(self, ctx: cairo.Context, font_size: float) -> None:
        ctx.select_font_face(self.font_family, cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
        ctx.set_font_size(font_size)

    def draw(self, ctx: Any, time: float = 0.0) -> None:
        fs = self.font_size.get(time)
        c = self.color.get(time)

        ctx.save()
        self._setup_cairo_font(ctx, fs)
        
        # Approximate extents for scanning
        extents = ctx.text_extents(self.text)
        width = extents.width if extents.width > 0 else fs * len(self.text)
        height = fs
        
        # We simulate slit-scan by drawing the text multiple times, clipped to thin horizontal strips.
        # We apply an X offset to each strip based on a sine wave.
        num_slits = max(10, int(height))
        slit_height = height / num_slits

        for i in range(num_slits):
            y_base = i * slit_height
            
            # Continuous stretching math
            t_offset = time * self.scan_speed
            x_shift = math.sin((y_base * self.frequency) + t_offset) * self.amplitude
            
            ctx.save()
            
            # Clip to current slit
            ctx.rectangle(0, y_base, width + self.amplitude * 2, slit_height)
            ctx.clip()
            
            # Apply distortion shift
            ctx.translate(x_shift, 0)
            
            ctx.set_source_rgba(*c.to_cairo())
            ctx.move_to(0, fs * 0.88)
            ctx.show_text(self.text)
            
            ctx.restore()

        ctx.restore()
        super().draw(ctx, time)

class AnalogFeedbackSmear(Node):
    """
    Flowing temporal trails smearing behind moving letters with feedback decay.
    """
    def __init__(self, text: str, font_size: float = 48.0, font_family: str = "Inter", 
                 color: Color = colors.CYAN, trail_length: int = 15, 
                 feedback_decay: float = 0.8, trail_offset: Vector2D = Vector2D(-2.0, 1.0), **kwargs):
        super().__init__(**kwargs)
        self.text = text
        self.font_size = Signal(float(font_size), f"{self.name}.font_size")
        self.font_family = font_family
        self.color = Signal(color, f"{self.name}.color")
        self.trail_length = trail_length
        self.feedback_decay = feedback_decay
        
        # Convert offset to signal to allow animation if needed, but for now fixed vector
        if isinstance(trail_offset, Vector2D):
             self.trail_offset_x = Signal(trail_offset.x)
             self.trail_offset_y = Signal(trail_offset.y)
        else:
             self.trail_offset_x = Signal(-2.0)
             self.trail_offset_y = Signal(1.0)
             
    def _setup_cairo_font(self, ctx: cairo.Context, font_size: float) -> None:
        ctx.select_font_face(self.font_family, cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
        ctx.set_font_size(font_size)

    def draw(self, ctx: Any, time: float = 0.0) -> None:
        fs = self.font_size.get(time)
        c = self.color.get(time)
        
        tx = self.trail_offset_x.get(time)
        ty = self.trail_offset_y.get(time)

        ctx.save()
        self._setup_cairo_font(ctx, fs)
        
        # Draw from back (tail) to front
        for i in range(self.trail_length - 1, -1, -1):
            alpha_mult = math.pow(self.feedback_decay, i)
            # Avoid drawing virtually invisible trails
            if alpha_mult < 0.01:
                continue
                
            alpha = c.a * alpha_mult
            
            # Dynamic movement: we can optionally make the trails wave over time, 
            # but standard smear is just spatial offset
            x_shift = i * tx
            y_shift = i * ty
            
            ctx.save()
            ctx.set_source_rgba(c.r, c.g, c.b, alpha)
            ctx.translate(x_shift, y_shift)
            ctx.move_to(0, fs * 0.88)
            ctx.show_text(self.text)
            ctx.restore()

        ctx.restore()
        super().draw(ctx, time)

class ChromaWarpWave(Node):
    """
    Rainbow color cycle shifting through smearing distortion bands.
    """
    def __init__(self, text: str, font_size: float = 48.0, font_family: str = "Inter", 
                 wave_speed: float = 2.0, cycle_speed: float = 3.0, **kwargs):
        super().__init__(**kwargs)
        self.text = text
        self.font_size = Signal(float(font_size), f"{self.name}.font_size")
        self.font_family = font_family
        self.wave_speed = wave_speed
        self.cycle_speed = cycle_speed
        
    def _setup_cairo_font(self, ctx: cairo.Context, font_size: float) -> None:
        ctx.select_font_face(self.font_family, cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
        ctx.set_font_size(font_size)

    def _hue_to_rgb(self, p: float, q: float, t: float) -> float:
        if t < 0: t += 1
        if t > 1: t -= 1
        if t < 1/6: return p + (q - p) * 6 * t
        if t < 1/2: return q
        if t < 2/3: return p + (q - p) * (2/3 - t) * 6
        return p

    def _hsl_to_rgb(self, h: float, s: float, l: float) -> tuple:
        if s == 0:
            return l, l, l
        
        q = l * (1 + s) if l < 0.5 else l + s - l * s
        p = 2 * l - q
        
        r = self._hue_to_rgb(p, q, h + 1/3)
        g = self._hue_to_rgb(p, q, h)
        b = self._hue_to_rgb(p, q, h - 1/3)
        
        return r, g, b

    def draw(self, ctx: Any, time: float = 0.0) -> None:
        fs = self.font_size.get(time)

        ctx.save()
        self._setup_cairo_font(ctx, fs)
        
        extents = ctx.text_extents(self.text)
        width = extents.width if extents.width > 0 else fs * len(self.text)
        height = fs
        
        num_bands = max(10, int(width / 2))
        band_width = width / num_bands

        for i in range(num_bands):
            x_base = i * band_width
            
            # Chroma warp: hue maps to X position and time
            normalized_x = i / num_bands
            hue = (normalized_x + time * self.cycle_speed) % 1.0
            
            r, g, b = self._hsl_to_rgb(hue, 1.0, 0.5)
            
            # Spatial warp: Y displacement based on sine wave
            y_shift = math.sin(normalized_x * math.pi * 4 + time * self.wave_speed) * (fs * 0.2)
            
            ctx.save()
            
            ctx.rectangle(x_base, -fs * 0.5, band_width, height * 2)
            ctx.clip()
            
            ctx.translate(0, y_shift)
            
            ctx.set_source_rgba(r, g, b, 1.0)
            ctx.move_to(0, fs * 0.88)
            ctx.show_text(self.text)
            
            ctx.restore()

        ctx.restore()
        super().draw(ctx, time)

class CRTScanBeamWipe(Node):
    """
    High-voltage electron beam sweep drawing out the title text.
    """
    def __init__(self, text: str, font_size: float = 48.0, font_family: str = "Inter", 
                 color: Color = colors.GREEN_500, beam_color: Color = colors.WHITE, 
                 beam_width: float = 10.0, **kwargs):
        super().__init__(**kwargs)
        self.text = text
        self.font_size = Signal(float(font_size), f"{self.name}.font_size")
        self.font_family = font_family
        self.color = Signal(color, f"{self.name}.color")
        self.beam_color = Signal(beam_color, f"{self.name}.beam_color")
        self.beam_width = beam_width
        
        self.sweep_progress = Signal(0.0, f"{self.name}.sweep_progress")

    def _setup_cairo_font(self, ctx: cairo.Context, font_size: float) -> None:
        ctx.select_font_face(self.font_family, cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
        ctx.set_font_size(font_size)

    def draw(self, ctx: Any, time: float = 0.0) -> None:
        prog = self.sweep_progress.get(time)
        if prog <= 0.0:
            super().draw(ctx, time)
            return

        fs = self.font_size.get(time)
        c = self.color.get(time)
        bc = self.beam_color.get(time)

        ctx.save()
        self._setup_cairo_font(ctx, fs)
        
        extents = ctx.text_extents(self.text)
        width = extents.width if extents.width > 0 else fs * len(self.text)
        height = fs
        
        # Calculate current X position of the beam
        current_x = width * prog
        
        # Draw the revealed text
        ctx.save()
        ctx.rectangle(0, -fs*0.2, current_x, height * 1.5)
        ctx.clip()
        ctx.set_source_rgba(*c.to_cairo())
        ctx.move_to(0, fs * 0.88)
        ctx.show_text(self.text)
        ctx.restore()
        
        # Draw the bright electron beam itself
        if prog < 1.0:
            ctx.save()
            
            # The beam is a vertical line at current_x
            beam_start_x = max(0, current_x - self.beam_width)
            beam_w = current_x - beam_start_x
            
            # Clip to text alpha so the beam only shows "inside" the letters
            # In pure pycairo this requires grouping or using a mask.
            # We'll use a mask approach:
            
            ctx.push_group()
            # Draw text as alpha mask
            ctx.set_source_rgba(1, 1, 1, 1)
            ctx.move_to(0, fs * 0.88)
            ctx.show_text(self.text)
            
            # Change operator to IN to keep only the intersection with the rectangle
            ctx.set_operator(cairo.OPERATOR_IN)
            ctx.set_source_rgba(*bc.to_cairo())
            ctx.rectangle(beam_start_x, -fs*0.2, beam_w, height * 1.5)
            ctx.fill()
            
            ctx.pop_group_to_source()
            ctx.paint()
            
            # Draw a glowing vertical line over everything
            ctx.set_source_rgba(bc.r, bc.g, bc.b, bc.a * 0.5)
            ctx.rectangle(current_x - 2, -fs*0.2, 4, height * 1.5)
            ctx.fill()
            
            ctx.restore()

        ctx.restore()
        super().draw(ctx, time)

