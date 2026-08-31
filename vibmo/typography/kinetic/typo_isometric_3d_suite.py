import math
from typing import Any, Optional
import cairo

from vibmo.core.color import Color, colors
from vibmo.core.signal import Signal, AnimationAction
from vibmo.core.easing import Ease, EasingFunc
from vibmo.core.vector import Vector2D
from vibmo.scene.node import Node

class IsometricExtruded3DText(Node):
    """
    Bold 3D block lettering extruded along isometric 30-degree angles with shaded side facets.
    """
    def __init__(self, text: str, font_size: float = 64.0, font_family: str = "Inter",
                 color: Color = colors.WHITE, depth: int = 10, angle_deg: float = 30.0, **kwargs):
        super().__init__(**kwargs)
        self.text = text
        self.font_size = Signal(float(font_size), f"{self.name}.font_size")
        self.font_family = font_family
        self.color = Signal(color, f"{self.name}.color")
        self.depth = int(depth)
        self.angle_deg = angle_deg
        self.gleam_progress = Signal(-1.0, f"{self.name}.gleam_progress")
        self.gleam_color = Color(1.0, 1.0, 1.0, 0.85)

    def gleam(
        self,
        duration: float = 1.2,
        delay: float = 0.0,
        ease: Optional[EasingFunc] = None,
        color: Optional[Color] = None,
    ) -> AnimationAction:
        """Sweeps a brilliant specular light gleam across the 3D extruded lettering."""
        self.gleam_progress.set(0.0)
        if color is not None:
            self.gleam_color = Color.from_any(color)
        e = ease or Ease.in_out_cubic
        return self.gleam_progress.to(1.0, duration=duration, ease=e, delay=delay)

    def _setup_cairo_font(self, ctx: cairo.Context, font_size: float) -> None:
        ctx.select_font_face(self.font_family, cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
        ctx.set_font_size(font_size)

    def draw(self, ctx: Any, time: float = 0.0) -> None:
        fs = self.font_size.get(time)
        c = self.color.get(time)

        ctx.save()
        self._setup_cairo_font(ctx, fs)

        angle_rad = math.radians(self.angle_deg)
        dx = math.cos(angle_rad)
        dy = math.sin(angle_rad)

        # Draw extrusion layers (back to front)
        for i in range(int(self.depth), 0, -1):
            offset_x = i * dx
            offset_y = i * dy
            
            # Simple shading based on depth
            shade_factor = 0.5 + 0.3 * (1.0 - (i / self.depth))
            r = min(1.0, c.r * shade_factor)
            g = min(1.0, c.g * shade_factor)
            b = min(1.0, c.b * shade_factor)

            ctx.save()
            ctx.set_source_rgba(r, g, b, c.a)
            ctx.move_to(offset_x, offset_y + fs * 0.88)
            ctx.show_text(self.text)
            ctx.restore()

        # Draw top layer
        ctx.set_source_rgba(c.r, c.g, c.b, c.a)
        ctx.move_to(0, fs * 0.88)
        ctx.show_text(self.text)

        # Specular gleam overlay pass
        gp = float(self.gleam_progress.get(time))
        if 0.0 <= gp <= 1.0:
            ctx.save()
            ctx.move_to(0, fs * 0.88)
            ctx.text_path(self.text)
            ctx.clip()

            extents = ctx.text_extents(self.text)
            text_width = extents.width if extents.width > 0 else fs * len(self.text) * 0.7
            gleam_w = fs * 1.5
            gx = -gleam_w + (text_width + gleam_w * 2) * gp
            gc = self.gleam_color

            pat = cairo.LinearGradient(gx, 0, gx + gleam_w, 0)
            pat.add_color_stop_rgba(0.0, gc.r, gc.g, gc.b, 0.0)
            pat.add_color_stop_rgba(0.5, gc.r, gc.g, gc.b, gc.a)
            pat.add_color_stop_rgba(1.0, gc.r, gc.g, gc.b, 0.0)
            mat = cairo.Matrix(1, 0, -0.5, 1, 0, 0)
            pat.set_matrix(mat)
            ctx.set_source(pat)
            ctx.paint()
            ctx.restore()

        ctx.restore()
        super().draw(ctx, time)

class CastShadowExtrusion(Node):
    """
    Deep floor contact cast shadow with soft directional blur for 3D text.
    """
    def __init__(self, text: str, font_size: float = 64.0, font_family: str = "Inter",
                 shadow_color: Color = colors.BLACK, offset_x: float = 20.0, offset_y: float = 20.0,
                 blur_steps: int = 5, **kwargs):
        super().__init__(**kwargs)
        self.text = text
        self.font_size = Signal(float(font_size), f"{self.name}.font_size")
        self.font_family = font_family
        self.shadow_color = Signal(shadow_color, f"{self.name}.shadow_color")
        self.offset_x = offset_x
        self.offset_y = offset_y
        self.blur_steps = blur_steps

    def _setup_cairo_font(self, ctx: cairo.Context, font_size: float) -> None:
        ctx.select_font_face(self.font_family, cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
        ctx.set_font_size(font_size)

    def draw(self, ctx: Any, time: float = 0.0) -> None:
        fs = self.font_size.get(time)
        sc = self.shadow_color.get(time)

        ctx.save()
        self._setup_cairo_font(ctx, fs)

        # Simulate blur by drawing multiple semi-transparent layers slightly offset
        for i in range(self.blur_steps):
            step_alpha = (sc.a / self.blur_steps) * 0.5
            blur_offset_x = self.offset_x + (i - self.blur_steps / 2) * 1.5
            blur_offset_y = self.offset_y + (i - self.blur_steps / 2) * 1.5

            ctx.save()
            ctx.set_source_rgba(sc.r, sc.g, sc.b, step_alpha)
            ctx.move_to(blur_offset_x, blur_offset_y + fs * 0.88)
            ctx.show_text(self.text)
            ctx.restore()

        ctx.restore()
        super().draw(ctx, time)

class BevelGleamLight(Node):
    """
    Animated light glint sliding across the top extruded bevel edges.
    """
    def __init__(self, text: str, font_size: float = 64.0, font_family: str = "Inter",
                 gleam_color: Color = Color(1.0, 1.0, 1.0, 0.8), **kwargs):
        super().__init__(**kwargs)
        self.text = text
        self.font_size = Signal(float(font_size), f"{self.name}.font_size")
        self.font_family = font_family
        self.gleam_color = Signal(gleam_color, f"{self.name}.gleam_color")
        self.progress = Signal(0.0, f"{self.name}.progress")

    def gleam(
        self,
        duration: float = 1.2,
        delay: float = 0.0,
        ease: Optional[EasingFunc] = None,
    ) -> AnimationAction:
        self.progress.set(0.0)
        e = ease or Ease.in_out_cubic
        return self.progress.to(1.0, duration=duration, ease=e, delay=delay)

    def _setup_cairo_font(self, ctx: cairo.Context, font_size: float) -> None:
        ctx.select_font_face(self.font_family, cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
        ctx.set_font_size(font_size)

    def draw(self, ctx: Any, time: float = 0.0) -> None:
        prog = self.progress.get(time)
        fs = self.font_size.get(time)
        gc = self.gleam_color.get(time)

        ctx.save()
        self._setup_cairo_font(ctx, fs)
        
        # Clip to the text path
        ctx.move_to(0, fs * 0.88)
        ctx.text_path(self.text)
        ctx.clip()
        
        extents = ctx.text_extents(self.text)
        text_width = extents.width
        
        # Calculate gleam position
        gleam_width = fs * 1.5
        gleam_x = -gleam_width + (text_width + gleam_width * 2) * prog
        
        # Draw the sliding gleam
        pat = cairo.LinearGradient(gleam_x, 0, gleam_x + gleam_width, 0)
        pat.add_color_stop_rgba(0, gc.r, gc.g, gc.b, 0.0)
        pat.add_color_stop_rgba(0.5, gc.r, gc.g, gc.b, gc.a)
        pat.add_color_stop_rgba(1, gc.r, gc.g, gc.b, 0.0)

        # Apply a tilt to the gradient for a slanted gleam effect
        matrix = cairo.Matrix(1, 0, -0.5, 1, 0, 0)
        pat.set_matrix(matrix)

        ctx.set_source(pat)
        ctx.paint()

        ctx.restore()
        super().draw(ctx, time)

class IsometricFloatIdle(Node):
    """
    Gentle floating levitation oscillation on the Z-axis (mapped to Y visually).
    """
    def __init__(self, amplitude: float = 10.0, frequency: float = 1.0, **kwargs):
        super().__init__(**kwargs)
        self.amplitude = amplitude
        self.frequency = frequency

    def draw(self, ctx: Any, time: float = 0.0) -> None:
        y_offset = math.sin(time * self.frequency * 2 * math.pi) * self.amplitude
        
        ctx.save()
        ctx.translate(0, y_offset)
        super().draw(ctx, time)
        ctx.restore()
