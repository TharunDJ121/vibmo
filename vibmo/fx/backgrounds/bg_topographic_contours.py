import math
import numpy as np
import cairo
import skimage.measure
from scipy.ndimage import zoom
from typing import Any, Tuple, Optional, List
from vibmo.scene.node import Node
from vibmo.core.signal import Signal
from vibmo.core.color import Color, colors

def generate_noise_layer(h: int, w: int, freq: float, seed: int, time: float) -> np.ndarray:
    rng = np.random.RandomState(seed)
    
    # We want a grid that's larger so we can pan through it
    grid_h = max(3, int(h / freq) + 2)
    grid_w = max(3, int(w / freq) + 2)
    
    # Generate static random grid for this seed
    grid = rng.uniform(-1.0, 1.0, size=(grid_h, grid_w)).astype(np.float32)
    
    # Calculate continuous pan offsets based on time
    # This ensures smooth transition
    pan_y = (time * 0.2) % 1.0
    pan_x = (time * 0.15) % 1.0
    
    # Interpolate to target resolution
    zh = h / (grid_h - 2)
    zw = w / (grid_w - 2)
    
    layer_large = zoom(grid, (zh, zw), order=1)
    
    # Now slice out the h x w region with smooth offset
    pixel_offset_y = int(pan_y * zh)
    pixel_offset_x = int(pan_x * zw)
    
    return layer_large[pixel_offset_y:pixel_offset_y+h, pixel_offset_x:pixel_offset_x+w]

class AnimatedTopographicContours(Node):
    """
    Smooth vector isolines derived from multi-octave 2D noise slowly shifting and breathing over time.
    """
    def __init__(
        self,
        width: float = 1920.0,
        height: float = 1080.0,
        line_spacing: Optional[float] = None,
        speed: float = 1.0,
        name: str = "AnimatedTopographicContours",
        **kwargs: Any
    ) -> None:
        super().__init__(name=name)
        self.width = width
        self.height = height
        self.line_color = Color.from_any(kwargs.get('line_color', colors.WHITE))
        self.line_width = kwargs.get('line_width', 2.0)
        self.line_spacing = line_spacing
        if line_spacing is not None:
            self.levels = max(3, int(self.height / line_spacing))
        else:
            self.levels = kwargs.get('levels', 10)
        self.octaves = kwargs.get('octaves', 3)
        self.noise_scale = kwargs.get('scale', 100.0)
        self.speed = speed
        self.grid_resolution = kwargs.get('grid_resolution', 20) # step size for Marching Squares
        
    def local_bounds(self, time: float = 0.0) -> Tuple[float, float, float, float]:
        return (0.0, 0.0, self.width, self.height)
        
    def _get_noise(self, time: float) -> np.ndarray:
        w = int(self.width / self.grid_resolution) + 1
        h = int(self.height / self.grid_resolution) + 1
        
        accum = np.zeros((h, w), dtype=np.float32)
        total_amp = 0.0
        amp = 1.0
        freq = max(4.0, min(w, h) * (10.0 / self.noise_scale))
        
        base_seed = hash(self.name) % 10000
        
        for i in range(self.octaves):
            layer = generate_noise_layer(h, w, freq, base_seed + i * 31, time * self.speed * (i + 1) * 0.5)
            accum += layer * amp
            total_amp += amp
            amp *= 0.5
            freq = max(2.0, freq * 0.5)
            
        accum = (accum / max(1e-4, total_amp))
        return accum

    def draw(self, ctx: Any, time: float = 0.0) -> None:
        # Generate noise field
        noise = self._get_noise(time)
        h, w = noise.shape
        
        ctx.set_source_rgba(self.line_color.r, self.line_color.g, self.line_color.b, self.line_color.a * self.world_opacity(time))
        ctx.set_line_width(self.line_width)
        
        # Marching Squares to draw isolines
        min_val = float(np.min(noise))
        max_val = float(np.max(noise))
        if max_val == min_val:
            return
            
        thresholds = np.linspace(min_val, max_val, self.levels + 2)[1:-1]
        
        for threshold in thresholds:
                # find_contours returns a list of (row, col) coordinates
            contours = skimage.measure.find_contours(noise, threshold)
            for contour in contours:
                ctx.new_path()
                for i, (r, c) in enumerate(contour):
                    x = c * self.grid_resolution
                    y = r * self.grid_resolution
                    if i == 0:
                        ctx.move_to(x, y)
                    else:
                        ctx.line_to(x, y)
                
                # Check if it should be closed
                if len(contour) > 2:
                    start = contour[0]
                    end = contour[-1]
                    if np.linalg.norm(start - end) < 1e-5:
                        ctx.close_path()
                ctx.stroke()

class BathymetricMapBackdrop(Node):
    """
    Tiered depth-colored stepped elevation slices with subtle edge glow.
    """
    def __init__(self, width: float = 1920.0, height: float = 1080.0, name: str = "BathymetricMapBackdrop", **kwargs: Any) -> None:
        super().__init__(name=name)
        self.width = width
        self.height = height
        self.levels = kwargs.get('levels', 5)
        
        # Base colors from deep to shallow
        self.base_color = Color.from_any(kwargs.get('base_color', Color.from_hex('#0d47a1')))
        self.shallow_color = Color.from_any(kwargs.get('shallow_color', Color.from_hex('#64b5f6')))
        
        self.octaves = kwargs.get('octaves', 3)
        self.noise_scale = kwargs.get('scale', 120.0)
        self.speed = kwargs.get('speed', 0.8)
        self.grid_resolution = kwargs.get('grid_resolution', 20)
        self.glow_width = kwargs.get('glow_width', 4.0)

    def local_bounds(self, time: float = 0.0) -> Tuple[float, float, float, float]:
        return (0.0, 0.0, self.width, self.height)

    def _get_noise(self, time: float) -> np.ndarray:
        w = int(self.width / self.grid_resolution) + 1
        h = int(self.height / self.grid_resolution) + 1
        
        accum = np.zeros((h, w), dtype=np.float32)
        total_amp = 0.0
        amp = 1.0
        freq = max(4.0, min(w, h) * (10.0 / self.noise_scale))
        
        base_seed = hash(self.name) % 10000
        
        for i in range(self.octaves):
            layer = generate_noise_layer(h, w, freq, base_seed + i * 31, time * self.speed * (i + 1) * 0.5)
            accum += layer * amp
            total_amp += amp
            amp *= 0.5
            freq = max(2.0, freq * 0.5)
            
        accum = (accum / max(1e-4, total_amp))
        return accum

    def draw(self, ctx: Any, time: float = 0.0) -> None:
        noise = self._get_noise(time)
        
        min_val = float(np.min(noise))
        max_val = float(np.max(noise))
        if max_val == min_val:
            return
            
        thresholds = np.linspace(min_val, max_val, self.levels + 2)[1:-1]
        
        opacity = self.world_opacity(time)
        
        # Draw background base color
        ctx.set_source_rgba(self.base_color.r, self.base_color.g, self.base_color.b, self.base_color.a * opacity)
        ctx.rectangle(0, 0, self.width, self.height)
        ctx.fill()
        
        for i, threshold in enumerate(thresholds):
            progress = (i + 1) / self.levels
            
            # Sub-level color
            color = self.base_color.lerp(self.shallow_color, progress)
            
            # Generate mask via skimage for finding shapes
            mask = noise > threshold
            
            contours = skimage.measure.find_contours(mask, 0.5)
            for contour in contours:
                ctx.new_path()
                for j, (r, c) in enumerate(contour):
                    x = c * self.grid_resolution
                    y = r * self.grid_resolution
                    if j == 0:
                        ctx.move_to(x, y)
                    else:
                        ctx.line_to(x, y)
                
                # Check closing
                if len(contour) > 2:
                    start = contour[0]
                    end = contour[-1]
                    if np.linalg.norm(start - end) < 1e-5:
                        ctx.close_path()
                
                # Fill the slice (since mask is "greater than threshold", the shapes represent the higher elevations)
                # First fill
                ctx.set_source_rgba(color.r, color.g, color.b, color.a * opacity)
                ctx.fill_preserve()
                
                # Edge glow
                # A brighter variant of the color
                glow_color = color.lerp(Color(1.0, 1.0, 1.0, 1.0), 0.3)
                ctx.set_source_rgba(glow_color.r, glow_color.g, glow_color.b, glow_color.a * opacity * 0.5)
                ctx.set_line_width(self.glow_width)
                ctx.stroke()

class RadarElevationSweep(Node):
    """
    Topographic map illuminated by a rotating 360-degree radar beam sweep.
    """
    def __init__(self, width: float = 1920.0, height: float = 1080.0, name: str = "RadarElevationSweep", **kwargs: Any) -> None:
        super().__init__(name=name)
        self.width = width
        self.height = height
        
        self.radar_color = Color.from_any(kwargs.get('radar_color', Color.from_hex('#4caf50')))
        self.base_color = Color.from_any(kwargs.get('base_color', Color.from_hex('#1b5e20')))
        
        self.levels = kwargs.get('levels', 8)
        self.line_width = kwargs.get('line_width', 1.5)
        self.rpm = kwargs.get('rpm', 15.0) # revolutions per minute
        
        self.octaves = kwargs.get('octaves', 3)
        self.noise_scale = kwargs.get('scale', 150.0)
        self.speed = kwargs.get('speed', 0.5)
        self.grid_resolution = kwargs.get('grid_resolution', 20)
        
        self.center_x = kwargs.get('center_x', width / 2)
        self.center_y = kwargs.get('center_y', height / 2)

    def local_bounds(self, time: float = 0.0) -> Tuple[float, float, float, float]:
        return (0.0, 0.0, self.width, self.height)

    def _get_noise(self, time: float) -> np.ndarray:
        w = int(self.width / self.grid_resolution) + 1
        h = int(self.height / self.grid_resolution) + 1
        
        accum = np.zeros((h, w), dtype=np.float32)
        total_amp = 0.0
        amp = 1.0
        freq = max(4.0, min(w, h) * (10.0 / self.noise_scale))
        
        base_seed = hash(self.name) % 10000
        
        for i in range(self.octaves):
            layer = generate_noise_layer(h, w, freq, base_seed + i * 31, time * self.speed * (i + 1) * 0.5)
            accum += layer * amp
            total_amp += amp
            amp *= 0.5
            freq = max(2.0, freq * 0.5)
            
        accum = (accum / max(1e-4, total_amp))
        return accum

    def draw(self, ctx: Any, time: float = 0.0) -> None:
        noise = self._get_noise(time)
        opacity = self.world_opacity(time)
        
        # Base dim grid/bg
        ctx.set_source_rgba(self.base_color.r * 0.2, self.base_color.g * 0.2, self.base_color.b * 0.2, self.base_color.a * opacity)
        ctx.rectangle(0, 0, self.width, self.height)
        ctx.fill()
        
        min_val = float(np.min(noise))
        max_val = float(np.max(noise))
        if max_val == min_val:
            return
            
        thresholds = np.linspace(min_val, max_val, self.levels + 2)[1:-1]
        
        
        # Calculate current radar angle (0 to 2*pi)
        # rpm: revs per min. so rps = rpm / 60
        # angle = time * rps * 2pi
        rps = self.rpm / 60.0
        current_angle = (time * rps * 2 * math.pi) % (2 * math.pi)
        
        # We will draw the contours, but use a cairo mesh or radial gradient if supported.
        # But standard cairo gradients are linear or radial. For an angular sweep (conic gradient),
        # cairo mesh pattern is needed, which is tricky. 
        # A simpler robust way: 
        # Draw all contours with dim base color.
        # Then setup a clip path for a pie wedge or use a cairo MeshPattern to draw the sweeping glow.
        
        ctx.set_line_width(self.line_width)
        
        # 1. Draw all dim isolines
        ctx.set_source_rgba(self.base_color.r * 0.5, self.base_color.g * 0.5, self.base_color.b * 0.5, opacity)
        for threshold in thresholds:
            contours = skimage.measure.find_contours(noise, threshold)
            for contour in contours:
                ctx.new_path()
                for j, (r, c) in enumerate(contour):
                    x = c * self.grid_resolution
                    y = r * self.grid_resolution
                    if j == 0:
                        ctx.move_to(x, y)
                    else:
                        ctx.line_to(x, y)
                if len(contour) > 2:
                    if np.linalg.norm(contour[0] - contour[-1]) < 1e-5:
                        ctx.close_path()
                ctx.stroke()
        
        # 2. Draw radar sweeping glow overlay using cairo Mesh pattern
        # The sweep is an angular sector fading behind the current angle.
        # Let's say the sweep trail length is 60 degrees (pi/3).
        trail_angle = math.pi / 2.0
        
        mesh = cairo.MeshPattern()
        
        radius = max(self.width, self.height) * 1.5
        
        num_segments = 20
        # Sweep goes from (current_angle - trail_angle) to current_angle
        # Since we use mesh, we can assign vertex colors.
        
        for i in range(num_segments):
            angle1 = current_angle - trail_angle + (i / num_segments) * trail_angle
            angle2 = current_angle - trail_angle + ((i + 1) / num_segments) * trail_angle
            
            # alpha linearly increases from 0 at the tail to 1 at the head
            alpha1 = (i / num_segments) * opacity
            alpha2 = ((i + 1) / num_segments) * opacity
            
            mesh.begin_patch()
            mesh.move_to(self.center_x, self.center_y)
            mesh.line_to(self.center_x + math.cos(angle1) * radius, self.center_y + math.sin(angle1) * radius)
            mesh.line_to(self.center_x + math.cos(angle2) * radius, self.center_y + math.sin(angle2) * radius)
            mesh.line_to(self.center_x, self.center_y)
            
            # Colors for 4 corners of patch
            mesh.set_corner_color_rgba(0, self.radar_color.r, self.radar_color.g, self.radar_color.b, alpha1)
            mesh.set_corner_color_rgba(1, self.radar_color.r, self.radar_color.g, self.radar_color.b, 0.0) # outer tail
            mesh.set_corner_color_rgba(2, self.radar_color.r, self.radar_color.g, self.radar_color.b, 0.0) # outer head
            mesh.set_corner_color_rgba(3, self.radar_color.r, self.radar_color.g, self.radar_color.b, alpha2)
            mesh.end_patch()
        
        # To just illuminate the isolines and not the background, we use the mesh pattern
        # with compositing mode IN onto a mask, but cairo python has limits.
        # An easier way: just set the blend mode to ADD or OVERLAY to light up the map below.
        ctx.save()
        ctx.set_operator(cairo.Operator.ADD)
        ctx.set_source(mesh)
        ctx.rectangle(0, 0, self.width, self.height)
        ctx.fill()
        
        # Add the radar center sweep line
        ctx.set_source_rgba(self.radar_color.r, self.radar_color.g, self.radar_color.b, opacity)
        ctx.set_line_width(2.0)
        ctx.move_to(self.center_x, self.center_y)
        ctx.line_to(self.center_x + math.cos(current_angle) * radius, self.center_y + math.sin(current_angle) * radius)
        ctx.stroke()
        
        ctx.restore()


# Semantic Alias
TopographicContours = AnimatedTopographicContours

__all__ = [
    "AnimatedTopographicContours",
    "TopographicContours",
    "BathymetricMapBackdrop",
    "RadarElevationSweep",
]
