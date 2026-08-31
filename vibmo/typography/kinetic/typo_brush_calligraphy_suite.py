import cairo
import math
import random
from typing import List, Tuple, Union, Optional, Any
from vibmo.scene.node import Node
from vibmo.core.signal import Signal, AnimationAction
from vibmo.core.color import Color, colors
from vibmo.core.easing import Ease, EasingFunc

def _bezier_point(p0, p1, p2, p3, t):
    """Cubic Bezier interpolation."""
    u = 1.0 - t
    tt = t * t
    uu = u * u
    uup = uu * u
    ttp = tt * t
    x = uup * p0[0] + 3 * uu * t * p1[0] + 3 * u * tt * p2[0] + ttp * p3[0]
    y = uup * p0[1] + 3 * uu * t * p1[1] + 3 * u * tt * p2[1] + ttp * p3[1]
    return (x, y)

class BrushCalligraphyPathReveal(Node):
    """
    Fluid Chinese/Japanese ink calligraphy brush strokes revealing along bezier paths or text outlines.
    """
    def __init__(
        self,
        text_or_path: Union[str, List] = "Zenith",
        path: Optional[List] = None,
        font_size: float = 64.0,
        font_family: str = "Inter",
        color: Any = colors.BLACK,
        stroke_width: float = 5.0,
        **kwargs
    ):
        super().__init__(**kwargs)
        if isinstance(text_or_path, list):
            self.path = text_or_path
            self.text = ""
        elif path is not None:
            self.path = path
            self.text = str(text_or_path) if isinstance(text_or_path, str) else ""
        else:
            self.text = str(text_or_path)
            self.path = []

        self.font_size = Signal(float(font_size), f"{self.name}.font_size")
        self.font_family = font_family
        self.progress = Signal(0.0, f"{self.name}.progress")
        self.color = Color.from_any(color)
        self.stroke_width = Signal(stroke_width, f"{self.name}.stroke_width")

    def draw_strokes(
        self,
        duration: float = 2.0,
        delay: float = 0.0,
        ease: Optional[EasingFunc] = None,
    ) -> AnimationAction:
        """Animates ink calligraphy strokes flowing and revealing with realistic fluid dynamics."""
        self.progress.set(0.0)
        e = ease or Ease.in_out_cubic
        return self.progress.to(1.0, duration=duration, ease=e, delay=delay)

    def draw(self, ctx: cairo.Context, time: float):
        progress = float(self.progress.get(time))
        if progress <= 0:
            return

        if self.text and not self.path:
            # Render text outline reveal with calligraphy brush styling
            fs = self.font_size.get(time)
            ctx.save()
            ctx.select_font_face(self.font_family, cairo.FONT_SLANT_ITALIC, cairo.FONT_WEIGHT_BOLD)
            ctx.set_font_size(fs)
            extents = ctx.text_extents(self.text)
            total_w = extents.width if extents.width > 0 else fs * len(self.text) * 0.7
            
            # Clip rectangle to reveal progress
            ctx.rectangle(0, -fs * 0.5, total_w * progress + 20.0, fs * 2.0)
            ctx.clip()

            # Brush fill + stroke
            ctx.set_source_rgba(*self.color.to_cairo())
            ctx.move_to(0, fs * 0.88)
            ctx.show_text(self.text)

            # Extra bristle ink bleed at leading edge
            lead_x = total_w * progress
            if 0.0 < progress < 1.0:
                ctx.set_source_rgba(self.color.r, self.color.g, self.color.b, 0.4)
                ctx.arc(lead_x, fs * 0.7, fs * 0.15, 0, 2 * math.pi)
                ctx.fill()

            ctx.restore()
            super().draw(ctx, time)
            return

        ctx.set_source_rgba(*self.color.to_cairo())
        ctx.set_line_width(self.stroke_width.get(time))
        ctx.set_line_cap(cairo.LINE_CAP_ROUND)
        ctx.set_line_join(cairo.LINE_JOIN_ROUND)

        total_curves = len(self.path)
        curves_to_draw = progress * total_curves

        ctx.new_path()
        for i, curve in enumerate(self.path):
            if i > curves_to_draw:
                break
            
            p0, p1, p2, p3 = curve
            
            if i == 0:
                ctx.move_to(p0[0], p0[1])

            if i + 1 <= curves_to_draw:
                ctx.curve_to(p1[0], p1[1], p2[0], p2[1], p3[0], p3[1])
            else:
                # Partial curve
                t = curves_to_draw - i
                
                # De Casteljau's algorithm to split curve
                p01 = ((1-t)*p0[0] + t*p1[0], (1-t)*p0[1] + t*p1[1])
                p12 = ((1-t)*p1[0] + t*p2[0], (1-t)*p1[1] + t*p2[1])
                p23 = ((1-t)*p2[0] + t*p3[0], (1-t)*p2[1] + t*p3[1])

                p012 = ((1-t)*p01[0] + t*p12[0], (1-t)*p01[1] + t*p12[1])
                p123 = ((1-t)*p12[0] + t*p23[0], (1-t)*p12[1] + t*p23[1])

                p0123 = ((1-t)*p012[0] + t*p123[0], (1-t)*p012[1] + t*p123[1])
                
                ctx.curve_to(p01[0], p01[1], p012[0], p012[1], p0123[0], p0123[1])

        ctx.stroke()
        super().draw(ctx, time)

class BristleTextureStroke(Node):
    def __init__(self, p0, p1, color=colors.BLACK, num_bristles=5, max_width=10.0):
        super().__init__()
        self.p0 = p0
        self.p1 = p1
        self.color = Color.from_any(color)
        self.num_bristles = num_bristles
        self.max_width = Signal(max_width)
        self.pressure = Signal(1.0)
        self._seed = random.randint(0, 10000)

    def draw(self, ctx: cairo.Context, time: float):
        rng = random.Random(self._seed)
        pressure_val = max(0.1, self.pressure.get())
        current_width = self.max_width.get() * pressure_val
        
        ctx.set_source_rgba(*self.color.with_alpha(0.7).to_cairo())
        ctx.set_line_cap(cairo.LINE_CAP_ROUND)
        
        dx = self.p1[0] - self.p0[0]
        dy = self.p1[1] - self.p0[1]
        length = math.hypot(dx, dy)
        
        if length == 0:
            return
            
        nx = -dy / length
        ny = dx / length
        
        for _ in range(self.num_bristles):
            offset = (rng.random() - 0.5) * current_width
            bristle_width = rng.random() * 2 + 0.5
            
            ctx.set_line_width(bristle_width)
            
            # Simple wavy line
            start_x = self.p0[0] + nx * offset
            start_y = self.p0[1] + ny * offset
            end_x = self.p1[0] + nx * offset
            end_y = self.p1[1] + ny * offset
            
            ctx.move_to(start_x, start_y)
            ctx.line_to(end_x, end_y)
            ctx.stroke()
            
        super().draw(ctx, time)

class InkSplatterBleed(Node):
    def __init__(self, center, color=colors.BLACK, num_splatters=10, max_radius=20.0):
        super().__init__()
        self.center = center
        self.color = Color.from_any(color)
        self.num_splatters = num_splatters
        self.max_radius = Signal(max_radius)
        self.bleed_progress = Signal(0.0) # 0 to 1
        self._seed = random.randint(0, 10000)

    def draw(self, ctx: cairo.Context, time: float):
        rng = random.Random(self._seed)
        progress = max(0.0, min(1.0, self.bleed_progress.get()))
        if progress <= 0:
            return

        for _ in range(self.num_splatters):
            angle = rng.random() * math.pi * 2
            dist = rng.random() * self.max_radius.get() * progress
            radius = (rng.random() * 3 + 1) * (1.0 - dist / (self.max_radius.get() + 0.1))
            
            # Diffusion effect, alpha decreases as radius increases
            alpha = (1.0 - dist / (self.max_radius.get() + 0.1)) * 0.8
            ctx.set_source_rgba(*self.color.with_alpha(alpha).to_cairo())
            
            cx = self.center[0] + math.cos(angle) * dist
            cy = self.center[1] + math.sin(angle) * dist
            
            ctx.arc(cx, cy, radius, 0, math.pi * 2)
            ctx.fill()
            
        super().draw(ctx, time)

class WaterColorWashBackdrop(Node):
    def __init__(self, rect: Tuple[float, float, float, float], color=colors.BLUE, max_alpha=0.3):
        super().__init__()
        self.rect = rect # x, y, width, height
        self.color = Color.from_any(color)
        self.max_alpha = max_alpha
        self.intensity = Signal(1.0)
        self._seed = random.randint(0, 10000)

    def draw(self, ctx: cairo.Context, time: float):
        rng = random.Random(self._seed)
        intensity_val = self.intensity.get()
        if intensity_val <= 0:
            return

        x, y, w, h = self.rect
        
        num_blobs = 5
        for _ in range(num_blobs):
            bx = x + rng.random() * w
            by = y + rng.random() * h
            br = rng.random() * min(w, h) * 0.8 * intensity_val
            
            alpha = rng.random() * self.max_alpha
            
            pat = cairo.RadialGradient(bx, by, 0, bx, by, br)
            pat.add_color_stop_rgba(0, *self.color.with_alpha(alpha).to_cairo())
            pat.add_color_stop_rgba(1, *self.color.with_alpha(0).to_cairo())
            
            ctx.set_source(pat)
            ctx.arc(bx, by, br, 0, math.pi * 2)
            ctx.fill()
            
        super().draw(ctx, time)
