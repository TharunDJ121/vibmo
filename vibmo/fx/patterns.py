"""
Pattern and texture effects inspired by Remotion's pattern library.
Includes Checkerboard, Gridlines, Rings, Starburst, and custom pattern generators.
"""

from __future__ import annotations
import math
import numpy as np
from typing import Any, Optional, Tuple, Union, Callable
from enum import Enum
from dataclasses import dataclass, field

from vibmo.core.color import Color, colors


class PatternOrigin(Enum):
    """Origin point for pattern effects."""
    CENTER = "center"
    TOP_LEFT = "top-left"
    TOP_RIGHT = "top-right"
    BOTTOM_LEFT = "bottom-left"
    BOTTOM_RIGHT = "bottom-right"


@dataclass
class PatternParams:
    """Common parameters for pattern effects."""
    color1: Union[Color, str] = field(default_factory=lambda: colors.WHITE)
    color2: Union[Color, str] = field(default_factory=lambda: colors.BLACK)
    scale: float = 1.0
    opacity: float = 1.0
    rotation: float = 0.0  # Degrees
    origin: PatternOrigin = PatternOrigin.CENTER


class Checkerboard:
    """
    Animated checkerboard pattern effect.
    Creates a classic checkerboard with customizable colors and scale.
    """

    def __init__(self, 
                 width: int = 1920,
                 height: int = 1080,
                 color1: Union[Color, str] = colors.WHITE,
                 color2: Union[Color, str] = colors.BLACK,
                 square_size: int = 50,
                 rotation: float = 0.0,
                 opacity: float = 1.0) -> None:
        self.width = width
        self.height = height
        self.color1 = Color.from_any(color1) if isinstance(color1, (str, Color)) else colors.WHITE
        self.color2 = Color.from_any(color2) if isinstance(color2, (str, Color)) else colors.BLACK
        self.square_size = square_size
        self.rotation = rotation
        self.opacity = opacity

    def render(self, time: float = 0.0) -> np.ndarray:
        """Render the checkerboard pattern."""
        h, w = self.height, self.width
        
        # Create checkerboard pattern
        x = np.arange(w)
        y = np.arange(h)
        X, Y = np.meshgrid(x, y)
        
        # Checkerboard logic
        checker = ((X // self.square_size + Y // self.square_size) % 2 == 0)
        
        # Create color array
        pattern = np.zeros((h, w, 4), dtype=np.uint8)
        
        # Fill with colors
        c1_arr = np.array([self.color1.r * 255, self.color1.g * 255, self.color1.b * 255, 255], dtype=np.uint8)
        c2_arr = np.array([self.color2.r * 255, self.color2.g * 255, self.color2.b * 255, 255], dtype=np.uint8)
        
        pattern[checker] = c1_arr
        pattern[~checker] = c2_arr
        
        # Apply rotation if needed
        if self.rotation != 0:
            from PIL import Image
            pil_img = Image.fromarray(pattern, "RGBA")
            rotated = pil_img.rotate(self.rotation, expand=False, fillcolor=(0, 0, 0, 0))
            pattern = np.array(rotated)
        
        # Apply opacity
        if self.opacity < 1.0:
            pattern[:, :, 3] = (pattern[:, :, 3] * self.opacity).astype(np.uint8)
        
        return pattern


class Gridlines:
    """
    Grid overlay effect with customizable spacing and colors.
    Useful for technical diagrams and design overlays.
    """

    def __init__(self,
                 width: int = 1920,
                 height: int = 1080,
                 line_color: Union[Color, str] = colors.GRAY,
                 background_color: Union[Color, str] = colors.TRANSPARENT,
                 spacing: int = 100,
                 line_width: int = 2,
                 opacity: float = 0.5) -> None:
        self.width = width
        self.height = height
        self.line_color = Color.from_any(line_color) if isinstance(line_color, (str, Color)) else colors.GRAY
        self.background_color = Color.from_any(background_color) if isinstance(background_color, (str, Color)) else colors.TRANSPARENT
        self.spacing = spacing
        self.line_width = line_width
        self.opacity = opacity

    def render(self, time: float = 0.0) -> np.ndarray:
        """Render the grid overlay."""
        h, w = self.height, self.width
        
        # Create background
        grid = np.zeros((h, w, 4), dtype=np.uint8)
        
        # Fill background
        bg_arr = np.array([self.background_color.r * 255, self.background_color.g * 255, 
                          self.background_color.b * 255, self.background_color.a * 255], dtype=np.uint8)
        grid[:, :] = bg_arr
        
        # Create line color
        line_arr = np.array([self.line_color.r * 255, self.line_color.g * 255, 
                            self.line_color.b * 255, 255], dtype=np.uint8)
        
        # Draw vertical lines
        for x in range(0, w, self.spacing):
            if x + self.line_width <= w:
                grid[:, x:x + self.line_width] = line_arr
        
        # Draw horizontal lines
        for y in range(0, h, self.spacing):
            if y + self.line_width <= h:
                grid[y:y + self.line_width, :] = line_arr
        
        # Apply opacity
        if self.opacity < 1.0:
            grid[:, :, 3] = (grid[:, :, 3] * self.opacity).astype(np.uint8)
        
        return grid


class RingsCenter(Enum):
    """Center point for rings pattern."""
    CENTER = "center"
    TOP_LEFT = "top-left"
    TOP_RIGHT = "top-right"
    BOTTOM_LEFT = "bottom-left"
    BOTTOM_RIGHT = "bottom-right"


class Rings:
    """
    Concentric rings pattern effect.
    Creates radial ring patterns with customizable spacing and colors.
    """

    def __init__(self,
                 width: int = 1920,
                 height: int = 1080,
                 color1: Union[Color, str] = colors.WHITE,
                 color2: Union[Color, str] = colors.BLACK,
                 ring_spacing: int = 50,
                 center: Union[str, RingsCenter] = RingsCenter.CENTER,
                 opacity: float = 1.0) -> None:
        self.width = width
        self.height = height
        self.color1 = Color.from_any(color1) if isinstance(color1, (str, Color)) else colors.WHITE
        self.color2 = Color.from_any(color2) if isinstance(color2, (str, Color)) else colors.BLACK
        self.ring_spacing = ring_spacing
        self.center = RingsCenter(center) if isinstance(center, str) else center
        self.opacity = opacity

    def render(self, time: float = 0.0) -> np.ndarray:
        """Render the concentric rings pattern."""
        h, w = self.height, self.width
        
        # Determine center point
        if self.center == RingsCenter.CENTER:
            cx, cy = w // 2, h // 2
        elif self.center == RingsCenter.TOP_LEFT:
            cx, cy = 0, 0
        elif self.center == RingsCenter.TOP_RIGHT:
            cx, cy = w, 0
        elif self.center == RingsCenter.BOTTOM_LEFT:
            cx, cy = 0, h
        else:  # BOTTOM_RIGHT
            cx, cy = w, h
        
        # Create coordinate grid
        y, x = np.ogrid[:h, :w]
        
        # Calculate distance from center
        dist = np.sqrt((x - cx)**2 + (y - cy)**2)
        
        # Create ring pattern
        rings = (dist // self.ring_spacing) % 2 == 0
        
        # Create color array
        pattern = np.zeros((h, w, 4), dtype=np.uint8)
        
        c1_arr = np.array([self.color1.r * 255, self.color1.g * 255, self.color1.b * 255, 255], dtype=np.uint8)
        c2_arr = np.array([self.color2.r * 255, self.color2.g * 255, self.color2.b * 255, 255], dtype=np.uint8)
        
        pattern[rings] = c1_arr
        pattern[~rings] = c2_arr
        
        # Apply opacity
        if self.opacity < 1.0:
            pattern[:, :, 3] = (pattern[:, :, 3] * self.opacity).astype(np.uint8)
        
        return pattern


class StarburstOrigin(Enum):
    """Origin point for starburst effect."""
    CENTER = "center"
    TOP_LEFT = "top-left"
    TOP_RIGHT = "top-right"
    BOTTOM_LEFT = "bottom-left"
    BOTTOM_RIGHT = "bottom-right"


class Starburst:
    """
    Radial starburst pattern effect.
    Creates dramatic radiating lines from a center point.
    """

    def __init__(self,
                 width: int = 1920,
                 height: int = 1080,
                 color: Union[Color, str] = colors.WHITE,
                 ray_count: int = 12,
                 ray_length: float = 0.8,  # Fraction of screen diagonal
                 ray_width: float = 0.05,  # Fraction of ray length
                 origin: Union[str, StarburstOrigin] = StarburstOrigin.CENTER,
                 rotation: float = 0.0,
                 opacity: float = 1.0) -> None:
        self.width = width
        self.height = height
        self.color = Color.from_any(color) if isinstance(color, (str, Color)) else colors.WHITE
        self.ray_count = ray_count
        self.ray_length = ray_length
        self.ray_width = ray_width
        self.origin = StarburstOrigin(origin) if isinstance(origin, str) else origin
        self.rotation = rotation
        self.opacity = opacity

    def render(self, time: float = 0.0) -> np.ndarray:
        """Render the starburst pattern."""
        h, w = self.height, self.width
        
        # Determine center point
        if self.origin == StarburstOrigin.CENTER:
            cx, cy = w // 2, h // 2
        elif self.origin == StarburstOrigin.TOP_LEFT:
            cx, cy = 0, 0
        elif self.origin == StarburstOrigin.TOP_RIGHT:
            cx, cy = w, 0
        elif self.origin == StarburstOrigin.BOTTOM_LEFT:
            cx, cy = 0, h
        else:  # BOTTOM_RIGHT
            cx, cy = w, h
        
        # Create coordinate grid
        y, x = np.ogrid[:h, :w]
        
        # Calculate angle and distance from center
        dx = x - cx
        dy = y - cy
        angle = np.arctan2(dy, dx) + np.radians(self.rotation)
        dist = np.sqrt(dx**2 + dy**2)
        
        # Calculate screen diagonal for ray length
        diagonal = math.sqrt(w**2 + h**2)
        max_dist = diagonal * self.ray_length
        
        # Create starburst pattern
        # Each ray occupies an angular segment
        angle_segment = 2 * math.pi / self.ray_count
        ray_angular_width = angle_segment * self.ray_width
        
        # Normalize angle to [0, 2π]
        angle = (angle + 2 * math.pi) % (2 * math.pi)
        
        # Determine which ray segment each pixel belongs to
        ray_index = (angle / angle_segment).astype(int)
        ray_center_angle = ray_index * angle_segment + angle_segment / 2
        
        # Check if pixel is within ray width
        angular_diff = np.abs(angle - ray_center_angle)
        angular_diff = np.minimum(angular_diff, 2 * math.pi - angular_diff)  # Handle wrap-around
        
        within_ray = (angular_diff < ray_angular_width / 2) & (dist < max_dist)
        
        # Create color array
        pattern = np.zeros((h, w, 4), dtype=np.uint8)
        c_arr = np.array([self.color.r * 255, self.color.g * 255, self.color.b * 255, 255], dtype=np.uint8)
        
        pattern[within_ray] = c_arr
        
        # Apply opacity
        if self.opacity < 1.0:
            pattern[:, :, 3] = (pattern[:, :, 3] * self.opacity).astype(np.uint8)
        
        return pattern


class Pattern:
    """
    Custom pattern generator with mathematical functions.
    Allows creation of complex procedural patterns.
    """

    def __init__(self,
                 width: int = 1920,
                 height: int = 1080,
                 pattern_func: Callable = None,
                 color1: Union[Color, str] = colors.WHITE,
                 color2: Union[Color, str] = colors.BLACK,
                 scale: float = 1.0,
                 opacity: float = 1.0) -> None:
        self.width = width
        self.height = height
        self.pattern_func = pattern_func or self._default_pattern
        self.color1 = Color.from_any(color1) if isinstance(color1, (str, Color)) else colors.WHITE
        self.color2 = Color.from_any(color2) if isinstance(color2, (str, Color)) else colors.BLACK
        self.scale = scale
        self.opacity = opacity

    def _default_pattern(self, x: float, y: float, time: float) -> float:
        """Default sine wave pattern."""
        return math.sin(x * 0.1 + time) * math.cos(y * 0.1 + time)

    def render(self, time: float = 0.0) -> np.ndarray:
        """Render the custom pattern."""
        h, w = self.height, self.width
        
        # Create coordinate grid
        y, x = np.ogrid[:h, :w]
        
        # Normalize coordinates
        nx = x / self.scale
        ny = y / self.scale
        
        # Apply pattern function
        pattern_mask = np.zeros((h, w), dtype=float)
        
        for i in range(h):
            for j in range(w):
                pattern_mask[i, j] = self.pattern_func(nx[i, j], ny[i, j], time)
        
        # Normalize to [0, 1]
        pattern_mask = (pattern_mask - pattern_mask.min()) / (pattern_mask.max() - pattern_mask.min() + 1e-6)
        
        # Create color array
        pattern = np.zeros((h, w, 4), dtype=np.uint8)
        
        c1_arr = np.array([self.color1.r * 255, self.color1.g * 255, self.color1.b * 255, 255], dtype=np.uint8)
        c2_arr = np.array([self.color2.r * 255, self.color2.g * 255, self.color2.b * 255, 255], dtype=np.uint8)
        
        # Interpolate colors based on pattern
        for i in range(h):
            for j in range(w):
                t = pattern_mask[i, j]
                pattern[i, j] = (c1_arr * (1 - t) + c2_arr * t).astype(np.uint8)
        
        # Apply opacity
        if self.opacity < 1.0:
            pattern[:, :, 3] = (pattern[:, :, 3] * self.opacity).astype(np.uint8)
        
        return pattern


class Tile:
    """
    Tiling pattern effect.
    Repeats a sub-pattern across the screen in a grid.
    """

    def __init__(self,
                 width: int = 1920,
                 height: int = 1080,
                 tile_width: int = 100,
                 tile_height: int = 100,
                 tile_pattern: Callable = None,
                 color1: Union[Color, str] = colors.WHITE,
                 color2: Union[Color, str] = colors.BLACK,
                 opacity: float = 1.0) -> None:
        self.width = width
        self.height = height
        self.tile_width = tile_width
        self.tile_height = tile_height
        self.tile_pattern = tile_pattern or self._default_tile_pattern
        self.color1 = Color.from_any(color1) if isinstance(color1, (str, Color)) else colors.WHITE
        self.color2 = Color.from_any(color2) if isinstance(color2, (str, Color)) else colors.BLACK
        self.opacity = opacity

    def _default_tile_pattern(self, tile_x: int, tile_y: int, pixel_x: int, pixel_y: int) -> bool:
        """Default diagonal tile pattern."""
        return (pixel_x + pixel_y) % 2 == 0

    def render(self, time: float = 0.0) -> np.ndarray:
        """Render the tiled pattern."""
        h, w = self.height, self.width
        
        # Create color array
        pattern = np.zeros((h, w, 4), dtype=np.uint8)
        
        c1_arr = np.array([self.color1.r * 255, self.color1.g * 255, self.color1.b * 255, 255], dtype=np.uint8)
        c2_arr = np.array([self.color2.r * 255, self.color2.g * 255, self.color2.b * 255, 255], dtype=np.uint8)
        
        # Create tiles
        num_tiles_x = math.ceil(w / self.tile_width)
        num_tiles_y = math.ceil(h / self.tile_height)
        
        for tile_y in range(num_tiles_y):
            for tile_x in range(num_tiles_x):
                # Calculate tile boundaries
                x_start = tile_x * self.tile_width
                x_end = min(x_start + self.tile_width, w)
                y_start = tile_y * self.tile_height
                y_end = min(y_start + self.tile_height, h)
                
                # Generate tile pattern
                for y in range(y_start, y_end):
                    for x in range(x_start, x_end):
                        pixel_x = x - x_start
                        pixel_y = y - y_start
                        
                        if self.tile_pattern(tile_x, tile_y, pixel_x, pixel_y):
                            pattern[y, x] = c1_arr
                        else:
                            pattern[y, x] = c2_arr
        
        # Apply opacity
        if self.opacity < 1.0:
            pattern[:, :, 3] = (pattern[:, :, 3] * self.opacity).astype(np.uint8)
        
        return pattern


class ZigzagDirection(Enum):
    """Direction for zigzag pattern."""
    HORIZONTAL = "horizontal"
    VERTICAL = "vertical"
    DIAGONAL = "diagonal"


class Zigzag:
    """
    Zigzag pattern effect.
    Creates alternating diagonal line patterns.
    """

    def __init__(self,
                 width: int = 1920,
                 height: int = 1080,
                 color1: Union[Color, str] = colors.WHITE,
                 color2: Union[Color, str] = colors.BLACK,
                 wavelength: int = 100,
                 amplitude: int = 50,
                 direction: Union[str, ZigzagDirection] = ZigzagDirection.HORIZONTAL,
                 opacity: float = 1.0) -> None:
        self.width = width
        self.height = height
        self.color1 = Color.from_any(color1) if isinstance(color1, (str, Color)) else colors.WHITE
        self.color2 = Color.from_any(color2) if isinstance(color2, (str, Color)) else colors.BLACK
        self.wavelength = wavelength
        self.amplitude = amplitude
        self.direction = ZigzagDirection(direction) if isinstance(direction, str) else direction
        self.opacity = opacity

    def render(self, time: float = 0.0) -> np.ndarray:
        """Render the zigzag pattern."""
        h, w = self.height, self.width
        
        # Create coordinate grid
        y, x = np.ogrid[:h, :w]
        
        # Create zigzag pattern
        if self.direction == ZigzagDirection.HORIZONTAL:
            # Horizontal zigzag
            zigzag = ((x + self.amplitude * np.sin(2 * math.pi * y / self.wavelength)) % (2 * self.wavelength)) < self.wavelength
        elif self.direction == ZigzagDirection.VERTICAL:
            # Vertical zigzag
            zigzag = ((y + self.amplitude * np.sin(2 * math.pi * x / self.wavelength)) % (2 * self.wavelength)) < self.wavelength
        else:  # DIAGONAL
            # Diagonal zigzag
            zigzag = ((x + y + self.amplitude * np.sin(2 * math.pi * (x + y) / self.wavelength)) % (2 * self.wavelength)) < self.wavelength
        
        # Create color array
        pattern = np.zeros((h, w, 4), dtype=np.uint8)
        
        c1_arr = np.array([self.color1.r * 255, self.color1.g * 255, self.color1.b * 255, 255], dtype=np.uint8)
        c2_arr = np.array([self.color2.r * 255, self.color2.g * 255, self.color2.b * 255, 255], dtype=np.uint8)
        
        pattern[zigzag] = c1_arr
        pattern[~zigzag] = c2_arr
        
        # Apply opacity
        if self.opacity < 1.0:
            pattern[:, :, 3] = (pattern[:, :, 3] * self.opacity).astype(np.uint8)
        
        return pattern


# Convenience functions for creating pattern effects with common presets

def checkerboard(square_size: int = 50, **kwargs) -> Checkerboard:
    """Create a checkerboard pattern with common defaults."""
    return Checkerboard(square_size=square_size, **kwargs)


def gridlines(spacing: int = 100, **kwargs) -> Gridlines:
    """Create a grid overlay with common defaults."""
    return Gridlines(spacing=spacing, **kwargs)


def rings(ring_spacing: int = 50, **kwargs) -> Rings:
    """Create concentric rings with common defaults."""
    return Rings(ring_spacing=ring_spacing, **kwargs)


def starburst(ray_count: int = 12, **kwargs) -> Starburst:
    """Create a starburst pattern with common defaults."""
    return Starburst(ray_count=ray_count, **kwargs)


def pattern(pattern_func: callable = None, **kwargs) -> Pattern:
    """Create a custom pattern with common defaults."""
    return Pattern(pattern_func=pattern_func, **kwargs)


def tile(tile_width: int = 100, tile_height: int = 100, **kwargs) -> Tile:
    """Create a tiled pattern with common defaults."""
    return Tile(tile_width=tile_width, tile_height=tile_height, **kwargs)


def zigzag(wavelength: int = 100, **kwargs) -> Zigzag:
    """Create a zigzag pattern with common defaults."""
    return Zigzag(wavelength=wavelength, **kwargs)