import math
import numpy as np
from typing import Any, Optional, Dict, Union, Tuple
from vibmo.scene.node import Node
from vibmo.core.color import Color, colors

class CrtPhosphorScanlineBackdrop(Node):
    """
    Moving horizontal cathode ray tube scanlines with rolling vertical 
    retrace sync bars and subtle curvature vignette.
    """
    def __init__(
        self,
        width: float = 1920,
        height: float = 1080,
        scanline_spacing: float = 4.0,
        scanline_intensity: float = 0.4,
        roll_speed: float = 1.0,
        retrace_bar_height: float = 150.0,
        base_color: Union[Color, str] = "#0a0f0a",
        scanline_color: Union[Color, str] = "#33ff33",
        curvature: float = 0.05,
        **kwargs: Any
    ):
        super().__init__(**kwargs)
        self.width = float(width)
        self.height = float(height)
        self.scanline_spacing = float(scanline_spacing)
        self.scanline_intensity = float(scanline_intensity)
        self.roll_speed = float(roll_speed)
        self.retrace_bar_height = float(retrace_bar_height)
        self.base_color = Color.from_any(base_color)
        self.scanline_color = Color.from_any(scanline_color)
        self.curvature = float(curvature)

    def draw(self, ctx: Any, time: float = 0.0) -> None:
        import cairo
        
        # Base background
        ctx.save()
        ctx.set_source_rgba(self.base_color.r, self.base_color.g, self.base_color.b, self.base_color.a)
        ctx.rectangle(0, 0, self.width, self.height)
        ctx.fill()
        
        # Scanlines
        # We can implement it as a pattern or by directly drawing lines
        # Drawing many lines might be slow, so let's draw them directly but optimized or use numpy + cairo ImageSurface if needed
        # Alternatively, we can draw a set of horizontal rectangles
        
        ctx.set_operator(cairo.OPERATOR_ADD)
        
        # We will do a simple drawing approach for vector canvas
        num_lines = int(self.height / self.scanline_spacing) + 1
        
        ctx.set_line_width(self.scanline_spacing * 0.5)
        
        # Calculate moving phase
        phase_y = (time * self.roll_speed * 50.0) % self.scanline_spacing
        
        ctx.set_source_rgba(
            self.scanline_color.r * self.scanline_intensity,
            self.scanline_color.g * self.scanline_intensity,
            self.scanline_color.b * self.scanline_intensity,
            self.scanline_color.a
        )
        
        # Draw from -1 to ensure seamless wrapping without visual jumps
        for i in range(-1, num_lines + 1):
            y = i * self.scanline_spacing + phase_y
            ctx.move_to(0, y)
            ctx.line_to(self.width, y)
        ctx.stroke()
        
        # Rolling Retrace sync bar
        retrace_y = (time * self.roll_speed * 150.0) % (self.height + self.retrace_bar_height) - self.retrace_bar_height
        
        grad = cairo.LinearGradient(0, retrace_y, 0, retrace_y + self.retrace_bar_height)
        grad.add_color_stop_rgba(0, self.scanline_color.r, self.scanline_color.g, self.scanline_color.b, 0.0)
        grad.add_color_stop_rgba(0.5, self.scanline_color.r, self.scanline_color.g, self.scanline_color.b, 0.15)
        grad.add_color_stop_rgba(1, self.scanline_color.r, self.scanline_color.g, self.scanline_color.b, 0.0)
        
        ctx.set_source(grad)
        ctx.rectangle(0, retrace_y, self.width, self.retrace_bar_height)
        ctx.fill()
        
        # Curvature Vignette
        if self.curvature > 0:
            ctx.set_operator(cairo.OPERATOR_OVER)
            cx, cy = self.width / 2.0, self.height / 2.0
            r = math.hypot(cx, cy)
            
            vignette = cairo.RadialGradient(cx, cy, r * (1.0 - self.curvature * 2), cx, cy, r)
            vignette.add_color_stop_rgba(0, 0, 0, 0, 0)
            vignette.add_color_stop_rgba(1, 0, 0, 0, 0.8)
            
            ctx.set_source(vignette)
            ctx.rectangle(0, 0, self.width, self.height)
            ctx.fill()
            
        ctx.restore()

class TVSignalNoiseStatic(Node):
    """
    Dynamic analog TV static snow with adjustable grain coarseness and frequency hum.
    """
    def __init__(
        self,
        width: float = 1920,
        height: float = 1080,
        coarseness: int = 4,
        intensity: float = 0.5,
        hum_frequency: float = 60.0,
        color_tint: Union[Color, str, None] = None,
        **kwargs: Any
    ):
        super().__init__(**kwargs)
        self.width = float(width)
        self.height = float(height)
        self.coarseness = max(1, int(coarseness))
        self.intensity = max(0.0, min(1.0, float(intensity)))
        self.hum_frequency = float(hum_frequency)
        self.color_tint = Color.from_any(color_tint) if color_tint else None

    def draw(self, ctx: Any, time: float = 0.0) -> None:
        import cairo
        
        ctx.save()
        
        # Generate noise image surface using numpy
        w = int(self.width / self.coarseness)
        h = int(self.height / self.coarseness)
        
        if w <= 0 or h <= 0:
            ctx.restore()
            return
            
        # Seed based on time to get dynamic noise
        rng = np.random.default_rng(seed=int(time * 1000) % 2147483647)
        
        # Create random grayscale noise
        noise = rng.integers(0, 255, (h, w), dtype=np.uint8)
        
        # Add hum (horizontal bands of varying intensity)
        if self.hum_frequency > 0:
            hum_phase = time * self.hum_frequency
            y_idx = np.arange(h)
            hum = 0.8 + 0.2 * np.sin(y_idx * 0.1 + hum_phase)
            noise = (noise * hum[:, np.newaxis]).clip(0, 255).astype(np.uint8)
        
        # Create RGBA array for cairo
        rgba = np.zeros((h, w, 4), dtype=np.uint8)
        
        if self.color_tint:
            # Tinted noise
            r, g, b = int(self.color_tint.r * 255), int(self.color_tint.g * 255), int(self.color_tint.b * 255)
            rgba[:, :, 0] = (noise * (r / 255.0)).astype(np.uint8) # B (cairo is ARGB/BGRA typically, let's use standard RGB mapping below if we use from_buffer)
            rgba[:, :, 1] = (noise * (g / 255.0)).astype(np.uint8)
            rgba[:, :, 2] = (noise * (b / 255.0)).astype(np.uint8)
        else:
            rgba[:, :, 0] = noise
            rgba[:, :, 1] = noise
            rgba[:, :, 2] = noise
            
        rgba[:, :, 3] = int(255 * self.intensity) # Alpha
        
        # Cairo expects ARGB32 in native endianness (usually BGRA in memory on little-endian)
        # Let's map it safely. numpy array [R, G, B, A] -> B, G, R, A
        cairo_data = np.zeros((h, w, 4), dtype=np.uint8)
        cairo_data[:, :, 0] = rgba[:, :, 2] # B
        cairo_data[:, :, 1] = rgba[:, :, 1] # G
        cairo_data[:, :, 2] = rgba[:, :, 0] # R
        cairo_data[:, :, 3] = rgba[:, :, 3] # A
        
        # Premultiply alpha
        alpha_norm = self.intensity
        if alpha_norm < 1.0:
            cairo_data[:, :, 0] = (cairo_data[:, :, 0] * alpha_norm).astype(np.uint8)
            cairo_data[:, :, 1] = (cairo_data[:, :, 1] * alpha_norm).astype(np.uint8)
            cairo_data[:, :, 2] = (cairo_data[:, :, 2] * alpha_norm).astype(np.uint8)

        stride = cairo.ImageSurface.format_stride_for_width(cairo.FORMAT_ARGB32, w)
        if cairo_data.strides[0] != stride:
            # Ensure stride matches
            new_data = np.zeros((h, stride), dtype=np.uint8)
            new_data[:, :w*4] = cairo_data.reshape((h, w*4))
            cairo_data = new_data
        else:
            cairo_data = cairo_data.ravel()
            
        surface = cairo.ImageSurface.create_for_data(cairo_data, cairo.FORMAT_ARGB32, w, h, stride)
        
        ctx.scale(self.coarseness, self.coarseness)
        ctx.set_source_surface(surface, 0, 0)
        
        # We must keep a reference to cairo_data while surface is alive, 
        # but since we draw immediately and discard, it's fine.
        ctx.paint()
        ctx.restore()

class VcrBlueScreenGlitch(Node):
    """
    Nostalgic 1990s VCR bright blue screen with animated tracking noise bars at bottom.
    """
    def __init__(
        self,
        width: float = 1920,
        height: float = 1080,
        blue_color: Union[Color, str] = "#0000AA",
        tracking_height: float = 120.0,
        tracking_speed: float = 2.0,
        show_play_text: bool = True,
        **kwargs: Any
    ):
        super().__init__(**kwargs)
        self.width = float(width)
        self.height = float(height)
        self.blue_color = Color.from_any(blue_color)
        self.tracking_height = float(tracking_height)
        self.tracking_speed = float(tracking_speed)
        self.show_play_text = show_play_text

    def draw(self, ctx: Any, time: float = 0.0) -> None:
        import cairo
        
        ctx.save()
        
        # Bright blue background
        ctx.set_source_rgba(self.blue_color.r, self.blue_color.g, self.blue_color.b, self.blue_color.a)
        ctx.rectangle(0, 0, self.width, self.height)
        ctx.fill()
        
        # 'PLAY' Text overlay
        if self.show_play_text:
            ctx.select_font_face("monospace", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
            ctx.set_font_size(60)
            
            # Simple text drop shadow
            ctx.set_source_rgba(0, 0, 0, 0.5)
            ctx.move_to(85, 105)
            ctx.show_text("PLAY ►")
            
            ctx.set_source_rgba(1, 1, 1, 0.9)
            ctx.move_to(80, 100)
            ctx.show_text("PLAY ►")
            
        # Tracking noise at the bottom
        # Animate the tracking bar moving slightly up and down
        rng = np.random.default_rng(seed=int(time * 30) % 100000)
        
        base_y = self.height - self.tracking_height - 20 + math.sin(time * self.tracking_speed) * 40
        
        # Draw multiple horizontal noise lines
        num_lines = int(self.tracking_height / 4)
        for i in range(num_lines):
            line_y = base_y + i * 4
            if line_y < 0 or line_y > self.height:
                continue
                
            # Line thickness
            line_h = rng.uniform(1, 4)
            
            # Line intensity (white/grey with some static)
            intensity = rng.uniform(0.3, 0.8)
            ctx.set_source_rgba(1, 1, 1, intensity)
            
            # X offset and width
            x_start = rng.uniform(0, self.width * 0.2)
            line_w = self.width - x_start - rng.uniform(0, self.width * 0.2)
            
            ctx.rectangle(x_start, line_y, line_w, line_h)
            ctx.fill()
            
            # Draw some random static dots around the line
            for _ in range(5):
                dx = rng.uniform(0, self.width)
                dy = line_y + rng.uniform(-10, 10)
                dw = rng.uniform(2, 10)
                dh = rng.uniform(1, 3)
                ctx.set_source_rgba(1, 1, 1, rng.uniform(0.5, 0.9))
                ctx.rectangle(dx, dy, dw, dh)
                ctx.fill()

        ctx.restore()
