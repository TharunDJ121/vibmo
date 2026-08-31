from typing import Any, List, Optional, Tuple, Union
import math
import cairo

from vibmo.scene.node import Node
from vibmo.core.color import Color, colors
from vibmo.core.vector import Vector2D

try:
    import numpy as np
except ImportError:
    np = None


def noise(x: float, y: float) -> float:
    """Very simple pseudo-noise for organic plasma effect."""
    return math.sin(x * 12.9898 + y * 78.233) * 43758.5453 % 1.0


class MeshGradientFlow(Node):
    """
    Animated 4-point to 9-point multi-color control mesh where gradient color control nodes 
    orbit organically using harmonic sine/cosine paths as time advances.
    """

    def __init__(
        self,
        width: float = 1920.0,
        height: float = 1080.0,
        colors_list: Optional[List[Union[Color, str]]] = None,
        colors: Optional[List[Union[Color, str]]] = None,
        speed_multiplier: float = 1.0,
        speed: Optional[float] = None,
        complexity: Optional[int] = None,
        resolution_scale: float = 1.0,
        auto_resize: bool = True,
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)
        self.width = width
        self.height = height
        self.auto_resize = auto_resize
        self.speed_multiplier = speed if speed is not None else speed_multiplier
        self.complexity = complexity or 4
        self.resolution_scale = resolution_scale

        from vibmo.core.color import colors as c_palette
        resolved_colors = colors if colors is not None else colors_list
        if resolved_colors is None:
            self.colors_list = [
                c_palette.INDIGO,
                c_palette.PURPLE,
                c_palette.CYAN,
                c_palette.EMERALD,
            ]
        else:
            self.colors_list = [Color.from_any(c) for c in resolved_colors]

    @property
    def colors(self) -> List[Color]:
        return self.colors_list

    @property
    def speed(self) -> float:
        return self.speed_multiplier

    def _get_node_pos(self, index: int, t: float) -> Tuple[float, float]:
        """Calculates orbiting path for a control node."""
        w, h = self.width, self.height
        num_nodes = len(self.colors_list)
        base_x = (index % 3) * (w / 2) if num_nodes > 4 else (index % 2) * w
        base_y = (index // 3) * (h / 2) if num_nodes > 4 else (index // 2) * h

        t_adj = t * self.speed_multiplier
        # Harmonic offsets
        freq_x = 0.5 + (index * 0.2)
        freq_y = 0.6 + (index * 0.15)
        phase_x = index * 1.5
        phase_y = index * 2.0

        offset_x = math.sin(t_adj * freq_x + phase_x) * (w * 0.3)
        offset_y = math.cos(t_adj * freq_y + phase_y) * (h * 0.3)

        return base_x + offset_x, base_y + offset_y

    def draw(self, ctx: Any, time: float = 0.0) -> None:
        # MeshGradientFlow typically uses multiple radial gradients overlaid
        ctx.save()

        # Clear background to first color
        base_color = self.colors_list[0]
        ctx.set_source_rgba(base_color.r, base_color.g, base_color.b, base_color.a)
        ctx.rectangle(0, 0, self.width, self.height)
        ctx.fill()

        # Add overlapping radial gradients for other colors
        # using a simple composite approach (e.g. DEST_OVER or ADD)
        ctx.set_operator(cairo.OPERATOR_SCREEN)

        max_radius = math.hypot(self.width, self.height) * 0.6

        for i, color in enumerate(self.colors_list):
            cx, cy = self._get_node_pos(i, time)
            pat = cairo.RadialGradient(cx, cy, 0, cx, cy, max_radius)
            pat.add_color_stop_rgba(0, color.r, color.g, color.b, color.a * 0.8)
            pat.add_color_stop_rgba(1, color.r, color.g, color.b, 0.0)
            
            ctx.set_source(pat)
            ctx.rectangle(0, 0, self.width, self.height)
            ctx.fill()

        ctx.restore()

class AuroraGradientWave(Node):
    """
    Ethereal green/cyan/purple ribbon wave curtains that undulate across dark backdrops.
    """

    def __init__(
        self,
        width: float = 1920.0,
        height: float = 1080.0,
        colors_list: Optional[List[Union[Color, str]]] = None,
        speed_multiplier: float = 1.0,
        resolution_scale: float = 1.0,
        auto_resize: bool = True,
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)
        self.width = width
        self.height = height
        self.auto_resize = auto_resize
        self.speed_multiplier = speed_multiplier
        self.resolution_scale = resolution_scale

        if colors_list is None:
            self.colors_list = [
                colors.EMERALD,
                colors.CYAN,
                colors.PURPLE,
            ]
        else:
            self.colors_list = [Color.from_any(c) for c in colors_list]

    def draw(self, ctx: Any, time: float = 0.0) -> None:
        ctx.save()

        # Base dark background
        ctx.set_source_rgba(0.02, 0.02, 0.05, 1.0)
        ctx.rectangle(0, 0, self.width, self.height)
        ctx.fill()

        ctx.set_operator(cairo.OPERATOR_ADD)

        t_adj = time * self.speed_multiplier
        num_waves = 3
        points_per_wave = 20

        for i in range(num_waves):
            color = self.colors_list[i % len(self.colors_list)]
            ctx.set_source_rgba(color.r, color.g, color.b, color.a * 0.5)
            
            wave_offset_y = self.height * (0.3 + 0.2 * i)
            amplitude = self.height * 0.2
            
            ctx.move_to(0, self.height)
            ctx.line_to(0, wave_offset_y)
            
            for p in range(points_per_wave + 1):
                x = (p / points_per_wave) * self.width
                # Undulation logic
                phase = p * 0.5 + t_adj * (0.5 + 0.2 * i) + i * 1.5
                y = wave_offset_y + math.sin(phase) * amplitude + math.cos(phase * 0.7) * amplitude * 0.5
                ctx.line_to(x, y)
                
            ctx.line_to(self.width, self.height)
            ctx.close_path()
            ctx.fill()
            
        ctx.restore()


class LiquidPlasmaBackdrop(Node):
    """
    Animated Perlin/Simplex-style organic color plasma field.
    """

    def __init__(
        self,
        width: float = 1920.0,
        height: float = 1080.0,
        colors_list: Optional[List[Union[Color, str]]] = None,
        speed_multiplier: float = 1.0,
        resolution_scale: float = 1.0,
        auto_resize: bool = True,
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)
        self.width = width
        self.height = height
        self.auto_resize = auto_resize
        self.speed_multiplier = speed_multiplier
        self.resolution_scale = resolution_scale

        if colors_list is None:
            self.colors_list = [
                colors.RED,
                colors.ORANGE,
                colors.YELLOW,
                colors.PINK,
            ]
        else:
            self.colors_list = [Color.from_any(c) for c in colors_list]

    def draw(self, ctx: Any, time: float = 0.0) -> None:
        if np is None:
            # Fallback if numpy not available, but user wants plasma
            ctx.set_source_rgba(0, 0, 0, 1)
            ctx.rectangle(0, 0, self.width, self.height)
            ctx.fill()
            return
            
        ctx.save()

        # Render at lower resolution for plasma speed
        res_w = int(self.width * self.resolution_scale * 0.1)
        res_h = int(self.height * self.resolution_scale * 0.1)
        if res_w < 1: res_w = 1
        if res_h < 1: res_h = 1

        t_adj = time * self.speed_multiplier

        # Generate a numpy array of pixels
        # For simplicity in cairo drawing without complex shaders,
        # we generate an image surface manually.
        
        # We will create a small cairo image surface
        surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, res_w, res_h)
        buf = surface.get_data()
        a = np.ndarray(shape=(res_h, res_w, 4), dtype=np.uint8, buffer=buf)
        
        # Simple plasma generation
        x = np.linspace(0, 5, res_w)
        y = np.linspace(0, 5, res_h)
        X, Y = np.meshgrid(x, y)
        
        v1 = np.sin(X + t_adj)
        v2 = np.sin(Y + t_adj)
        v3 = np.sin(X + Y + t_adj)
        v4 = np.sin(np.sqrt(X**2 + Y**2) + t_adj)
        
        v = v1 + v2 + v3 + v4 # range approx -4 to 4
        
        # Map v to 0-1
        v_norm = (v + 4) / 8.0
        v_norm = np.clip(v_norm, 0, 1)

        # Interpolate between colors based on v_norm
        num_colors = len(self.colors_list)
        
        color_indices = v_norm * (num_colors - 1)
        idx0 = np.floor(color_indices).astype(int)
        idx1 = np.clip(idx0 + 1, 0, num_colors - 1)
        f = color_indices - idx0
        
        # Create color arrays
        c0_r = np.array([c.r for c in self.colors_list])
        c0_g = np.array([c.g for c in self.colors_list])
        c0_b = np.array([c.b for c in self.colors_list])
        c0_a = np.array([c.a for c in self.colors_list])
        
        r = c0_r[idx0] * (1 - f) + c0_r[idx1] * f
        g = c0_g[idx0] * (1 - f) + c0_g[idx1] * f
        b = c0_b[idx0] * (1 - f) + c0_b[idx1] * f
        alpha = c0_a[idx0] * (1 - f) + c0_a[idx1] * f

        # Set pixel data (ARGB32 format is BGRA in little-endian)
        a[:, :, 0] = (b * 255).astype(np.uint8) # B
        a[:, :, 1] = (g * 255).astype(np.uint8) # G
        a[:, :, 2] = (r * 255).astype(np.uint8) # R
        a[:, :, 3] = (alpha * 255).astype(np.uint8) # A
        
        surface.mark_dirty()
        
        # Draw scaled surface
        ctx.scale(self.width / res_w, self.height / res_h)
        ctx.set_source_surface(surface, 0, 0)
        # Using BILINEAR filter is default, makes it smooth
        ctx.paint()
        
        ctx.restore()
