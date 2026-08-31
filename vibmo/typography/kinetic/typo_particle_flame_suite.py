import math
import random
from typing import Any, Tuple, Optional, List
import cairo

from vibmo.core.color import Color, colors
from vibmo.core.vector import Vector2D
from vibmo.core.signal import Signal, AnimationAction
from vibmo.core.easing import Ease
from vibmo.scene.node import Node


def _extract_text_points(ctx: cairo.Context, text: str, x: float, y: float, font_family: str, font_size: float, density: int = 1) -> List[Tuple[float, float]]:
    """Helper to extract outline points from text for particle generation."""
    ctx.save()
    ctx.select_font_face(font_family, cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
    ctx.set_font_size(font_size)
    ctx.move_to(x, y)
    ctx.text_path(text)
    
    path = ctx.copy_path_flat()
    ctx.new_path() # Clear path
    ctx.restore()
    
    points = []
    # Cairo copy_path_flat returns an iterator of tuples (path_type, points_tuple)
    for type_, pts in path:
        if type_ in (cairo.PATH_MOVE_TO, cairo.PATH_LINE_TO):
            # Just sample some points to avoid too many particles
            if random.random() < (0.1 * density):
                points.append(pts)
    return points


class ParticleFlameText(Node):
    """
    Text outlines that emit ascending heat shimmer, fiery orange sparks, and smoke trails.
    """
    def __init__(self, text: str, font_size: float = 48.0, font_family: str = "Inter",
                 color: Color = colors.ORANGE, **kwargs):
        super().__init__(**kwargs)
        self.text = text
        self.font_size = Signal(float(font_size), f"{self.name}.font_size")
        self.font_family = font_family
        self.color = Signal(color, f"{self.name}.color")
        self.progress = Signal(0.0, f"{self.name}.progress")
        self.disintegrate_progress = Signal(0.0, f"{self.name}.disintegrate_progress")
        
        self._rng = random.Random(hash(text) + id(self))
        self._particles = []
        self._initialized = False

    def _setup_cairo_font(self, ctx: cairo.Context, font_size: float) -> None:
        ctx.select_font_face(self.font_family, cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
        ctx.set_font_size(font_size)

    def ignite(self, duration: float = 2.0, delay: float = 0.0, ease: Optional[Any] = None) -> AnimationAction:
        self.progress.set(0.0)
        e = ease or Ease.linear
        return self.progress.to(1.0, duration=duration, ease=e, delay=delay)

    def disintegrate(self, duration: float = 3.0, delay: float = 0.0, ease: Optional[Any] = None) -> AnimationAction:
        """Disintegrates flaming letters into ascending ember sparks and dissipating smoke."""
        self.disintegrate_progress.set(0.0)
        e = ease or Ease.in_out_quad
        return self.disintegrate_progress.to(1.0, duration=duration, ease=e, delay=delay)

    def draw(self, ctx: Any, time: float = 0.0) -> None:
        prog = self.progress.get(time)
        dis_prog = self.disintegrate_progress.get(time)
        fs = self.font_size.get(time)
        c = self.color.get(time)

        # Ensure random is consistent for visual generation without state-mutation bugs
        self._rng.seed(int(time * 10) + id(self))

        if not self._initialized:
            # Extract points just once when first drawing
            # For simplicity, we just use the first frame's position and scale
            self._particles = _extract_text_points(ctx, self.text, 0, fs * 0.88, self.font_family, fs, density=5)
            self._initialized = True

        ctx.save()
        
        # Draw base text slightly glowing (fading out during disintegration)
        base_alpha = (1.0 - dis_prog) if dis_prog > 0.0 else 1.0
        if base_alpha > 0.01:
            self._setup_cairo_font(ctx, fs)
            ctx.set_source_rgba(c.r, c.g, c.b, c.a * (0.8 + 0.2 * math.sin(time * 10)) * base_alpha)
            ctx.move_to(0, fs * 0.88)
            ctx.show_text(self.text)
        
        # Draw flames / disintegrating embers
        active_prog = max(prog, dis_prog)
        if active_prog > 0:
            for px, py in self._particles:
                # Add ascending motion based on progress and noise
                noise_x = (self._rng.random() - 0.5) * (10 + 40 * dis_prog) * active_prog
                noise_y = -self._rng.random() * (50 + 100 * dis_prog) * active_prog
                
                size = self._rng.random() * 3 + 1
                alpha = max(0, 1.0 - prog) * self._rng.random()
                
                # Sparks
                ctx.set_source_rgba(1.0, 0.6, 0.1, alpha)
                ctx.arc(px + noise_x, py + noise_y, size, 0, 2 * math.pi)
                ctx.fill()
                
                # Smoke
                if self._rng.random() > 0.7:
                    ctx.set_source_rgba(0.2, 0.2, 0.2, alpha * 0.5)
                    ctx.arc(px + noise_x * 2, py + noise_y * 1.5 - 10, size * 2, 0, 2 * math.pi)
                    ctx.fill()

        ctx.restore()
        super().draw(ctx, time)


class DisintegratingEmbers(Node):
    """
    Letters disintegrating into glowing embers blown away by directional wind.
    """
    def __init__(self, text: str, font_size: float = 48.0, font_family: str = "Inter",
                 color: Color = colors.RED, wind_dir: Vector2D = Vector2D(100, -50), **kwargs):
        super().__init__(**kwargs)
        self.text = text
        self.font_size = Signal(float(font_size), f"{self.name}.font_size")
        self.font_family = font_family
        self.color = Signal(color, f"{self.name}.color")
        self.wind_dir = wind_dir
        self.disintegrate_progress = Signal(0.0, f"{self.name}.disintegrate_progress")
        
        self._rng = random.Random(hash(text) + id(self))
        self._embers = []
        self._initialized = False

    def disintegrate(self, duration: float = 3.0) -> AnimationAction:
        return self.disintegrate_progress.to(1.0, duration=duration, ease=Ease.in_out_quad)

    def draw(self, ctx: Any, time: float = 0.0) -> None:
        prog = self.disintegrate_progress.get(time)
        fs = self.font_size.get(time)
        c = self.color.get(time)
        
        if not self._initialized:
            self._embers = _extract_text_points(ctx, self.text, 0, fs * 0.88, self.font_family, fs, density=8)
            # Pre-assign individual random speeds to embers to keep them deterministic but varied
            rng_init = random.Random(id(self))
            self._ember_speeds = [rng_init.random() * 0.5 + 0.5 for _ in self._embers]
            self._initialized = True

        ctx.save()

        # We draw the remaining text only if progress < 1
        if prog < 1.0:
            ctx.select_font_face(self.font_family, cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
            ctx.set_font_size(fs)
            
            # Fade out text based on progress
            ctx.set_source_rgba(c.r, c.g, c.b, c.a * (1.0 - prog))
            ctx.move_to(0, fs * 0.88)
            ctx.show_text(self.text)

        # Draw embers moving in wind direction
        if prog > 0:
            self._rng.seed(int(time * 20) + id(self))
            for i, (px, py) in enumerate(self._embers):
                # Disintegrate starts from left to right (rough heuristic)
                ember_start = (px / (len(self.text) * fs * 0.6)) * 0.5
                if prog > ember_start:
                    local_prog = (prog - ember_start) / (1.0 - ember_start)
                    
                    speed = self._ember_speeds[i]
                    dx = self.wind_dir.x * local_prog * speed
                    dy = self.wind_dir.y * local_prog * speed
                    
                    # Add turbulent noise
                    dx += (self._rng.random() - 0.5) * 15 * local_prog
                    dy += (self._rng.random() - 0.5) * 15 * local_prog
                    
                    size = max(0.1, (1.0 - local_prog) * 3)
                    alpha = max(0, 1.0 - local_prog)
                    
                    # Core ember
                    ctx.set_source_rgba(1.0, 0.4, 0.0, alpha)
                    ctx.arc(px + dx, py + dy, size, 0, 2 * math.pi)
                    ctx.fill()
                    
                    # Glow
                    ctx.set_source_rgba(1.0, 0.2, 0.0, alpha * 0.4)
                    ctx.arc(px + dx, py + dy, size * 2.5, 0, 2 * math.pi)
                    ctx.fill()
                    
        ctx.restore()
        super().draw(ctx, time)


class IgnitionSparkBurst(Node):
    """
    Initial explosion of spark particles outlining the typography.
    """
    def __init__(self, text: str, font_size: float = 48.0, font_family: str = "Inter",
                 color: Color = colors.YELLOW, **kwargs):
        super().__init__(**kwargs)
        self.text = text
        self.font_size = Signal(float(font_size), f"{self.name}.font_size")
        self.font_family = font_family
        self.color = Signal(color, f"{self.name}.color")
        self.burst_progress = Signal(0.0, f"{self.name}.burst_progress")
        
        self._rng = random.Random(hash(text) + id(self))
        self._sparks = []
        self._initialized = False

    def burst(self, duration: float = 0.8) -> AnimationAction:
        return self.burst_progress.to(1.0, duration=duration, ease=Ease.out_expo)

    def draw(self, ctx: Any, time: float = 0.0) -> None:
        prog = self.burst_progress.get(time)
        fs = self.font_size.get(time)
        c = self.color.get(time)

        if not self._initialized:
            self._sparks = _extract_text_points(ctx, self.text, 0, fs * 0.88, self.font_family, fs, density=10)
            rng_init = random.Random(id(self))
            self._spark_dirs = [(rng_init.random() - 0.5) * 2, (rng_init.random() - 0.5) * 2]
            # Generate unique random directions for each spark
            self._spark_dirs = []
            for _ in self._sparks:
                self._spark_dirs.extend([(rng_init.random() - 0.5) * 2, (rng_init.random() - 0.5) * 2])
            self._spark_speeds = [rng_init.random() * 40 + 20 for _ in self._sparks]
            self._initialized = True

        ctx.save()

        # Draw the text fading in as the burst happens
        ctx.select_font_face(self.font_family, cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
        ctx.set_font_size(fs)
        ctx.set_source_rgba(c.r, c.g, c.b, c.a * prog)
        ctx.move_to(0, fs * 0.88)
        ctx.show_text(self.text)

        # Draw sparks expanding outwards
        if prog > 0 and prog < 1.0:
            for i, (px, py) in enumerate(self._sparks):
                idx = i * 2
                # Wrap indices just in case
                dx = self._spark_dirs[idx % len(self._spark_dirs)]
                dy = self._spark_dirs[(idx + 1) % len(self._spark_dirs)]
                speed = self._spark_speeds[i % len(self._spark_speeds)]
                
                dist = speed * prog
                
                # Sparks fade out quickly
                alpha = max(0, 1.0 - (prog * 1.5))
                size = max(0.1, 2.0 * (1.0 - prog))
                
                ctx.set_source_rgba(1.0, 0.8, 0.2, alpha)
                ctx.move_to(px + dx * dist * 0.8, py + dy * dist * 0.8)
                ctx.line_to(px + dx * dist, py + dy * dist)
                ctx.set_line_width(size)
                ctx.stroke()

        ctx.restore()
        super().draw(ctx, time)


class SmokeDissipateHeading(Node):
    """
    Soft volumetric smoke plumes dissolving typography into darkness.
    """
    def __init__(self, text: str, font_size: float = 48.0, font_family: str = "Inter",
                 color: Color = colors.SLATE_400, **kwargs):
        super().__init__(**kwargs)
        self.text = text
        self.font_size = Signal(float(font_size), f"{self.name}.font_size")
        self.font_family = font_family
        self.color = Signal(color, f"{self.name}.color")
        self.dissipate_progress = Signal(0.0, f"{self.name}.dissipate_progress")
        
        self._rng = random.Random(hash(text) + id(self))
        self._smoke_points = []
        self._initialized = False

    def dissipate(self, duration: float = 4.0) -> AnimationAction:
        return self.dissipate_progress.to(1.0, duration=duration, ease=Ease.linear)

    def draw(self, ctx: Any, time: float = 0.0) -> None:
        prog = self.dissipate_progress.get(time)
        fs = self.font_size.get(time)
        c = self.color.get(time)

        if not self._initialized:
            self._smoke_points = _extract_text_points(ctx, self.text, 0, fs * 0.88, self.font_family, fs, density=3)
            rng_init = random.Random(id(self))
            self._smoke_params = [(rng_init.random() * 20 - 10, rng_init.random() * -30 - 10, rng_init.random() * 10 + 5) for _ in self._smoke_points]
            self._initialized = True

        ctx.save()

        # Text dissolves
        text_alpha = max(0, 1.0 - (prog * 2.0)) # Text fades out fast
        if text_alpha > 0:
            ctx.select_font_face(self.font_family, cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
            ctx.set_font_size(fs)
            ctx.set_source_rgba(c.r, c.g, c.b, c.a * text_alpha)
            ctx.move_to(0, fs * 0.88)
            ctx.show_text(self.text)

        # Smoke plumes expand and rise
        if prog > 0:
            self._rng.seed(int(time * 5) + id(self))
            for i, (px, py) in enumerate(self._smoke_points):
                vx, vy, base_size = self._smoke_params[i]
                
                # Add swirling motion
                swirl_x = math.sin(prog * 10 + i) * 15 * prog
                
                dx = vx * prog + swirl_x
                dy = vy * prog * 2
                
                size = base_size + (prog * 40)
                
                # Smoke alpha increases then fades out
                smoke_alpha = math.sin(prog * math.pi) * 0.3 * c.a
                
                # Add jitter
                jx = (self._rng.random() - 0.5) * 5
                jy = (self._rng.random() - 0.5) * 5
                
                # Create radial gradient for soft smoke
                pat = cairo.RadialGradient(px + dx + jx, py + dy + jy, 0, px + dx + jx, py + dy + jy, size)
                # Dark smoke color
                pat.add_color_stop_rgba(0, 0.1, 0.1, 0.1, smoke_alpha)
                pat.add_color_stop_rgba(1, 0.1, 0.1, 0.1, 0.0)
                
                ctx.set_source(pat)
                ctx.arc(px + dx + jx, py + dy + jy, size, 0, 2 * math.pi)
                ctx.fill()

        ctx.restore()
        super().draw(ctx, time)
