"""
Distortion effects inspired by Remotion's distortion library.
Includes BarrelDistortion, Fisheye, Wave, LiquidContours, Skew, and CornerPin.
"""

from __future__ import annotations
import math
import numpy as np
from typing import Any, Optional, Tuple, Union
from enum import Enum
from dataclasses import dataclass


class DistortionType(Enum):
    """Types of distortion effects."""
    BARREL = "barrel"
    PINCUSHION = "pincushion"
    FISHEYE = "fisheye"
    WAVE = "wave"
    LIQUID = "liquid"
    SPHERICAL = "spherical"


@dataclass
class DistortionParams:
    """Parameters for distortion effects."""
    strength: float = 0.5
    center_x: float = 0.5  # Normalized 0-1
    center_y: float = 0.5  # Normalized 0-1
    radius: float = 1.0  # Normalized 0-1
    aspect_ratio: float = 1.0


class BarrelDistortion:
    """
    Barrel and pincushion lens distortion effect.
    Simulates camera lens distortion with adjustable strength.
    """

    def __init__(self,
                 strength: float = 0.3,
                 distortion_type: Union[str, DistortionType] = DistortionType.BARREL,
                 center: Tuple[float, float] = (0.5, 0.5)) -> None:
        self.strength = max(-1.0, min(1.0, strength))
        self.distortion_type = DistortionType(distortion_type) if isinstance(distortion_type, str) else distortion_type
        self.center = center

    def apply(self, rgba: np.ndarray, time: float = 0.0) -> np.ndarray:
        """Apply barrel/pincushion distortion to image."""
        if abs(self.strength) < 0.01:
            return rgba
            
        h, w, c = rgba.shape
        result = np.zeros_like(rgba)
        
        # Create coordinate grid
        y, x = np.ogrid[:h, :w]
        
        # Normalize coordinates to center
        cx, cy = self.center[0] * w, self.center[1] * h
        dx = (x - cx) / (w / 2)
        dy = (y - cy) / (h / 2)
        
        # Calculate distance from center
        r2 = dx**2 + dy**2
        
        # Apply distortion based on type
        if self.distortion_type == DistortionType.BARREL:
            # Barrel distortion (positive strength)
            factor = 1.0 + self.strength * r2
        elif self.distortion_type == DistortionType.PINCUSHION:
            # Pincushion distortion (negative strength)
            factor = 1.0 - self.strength * r2
        else:
            factor = 1.0 + self.strength * r2
        
        # Calculate new coordinates
        new_x = cx + dx * factor * (w / 2)
        new_y = cy + dy * factor * (h / 2)
        
        # Clamp coordinates to image bounds
        new_x = np.clip(new_x, 0, w - 1).astype(int)
        new_y = np.clip(new_y, 0, h - 1).astype(int)
        
        # Sample from original image
        for i in range(h):
            for j in range(w):
                result[i, j] = rgba[new_y[i, j], new_x[i, j]]
        
        return result


class Fisheye:
    """
    Fisheye lens distortion effect.
    Creates dramatic wide-angle distortion with circular image.
    """

    def __init__(self,
                 strength: float = 0.5,
                 aperture: float = 180.0) -> None:
        self.strength = max(0.0, min(1.0, strength))
        self.aperture = max(90.0, min(180.0, aperture))

    def apply(self, rgba: np.ndarray, time: float = 0.0) -> np.ndarray:
        """Apply fisheye distortion to image."""
        if self.strength < 0.01:
            return rgba
            
        h, w, c = rgba.shape
        result = np.zeros_like(rgba)
        
        # Create coordinate grid
        y, x = np.ogrid[:h, :w]
        
        # Center coordinates
        cx, cy = w / 2, h / 2
        dx = x - cx
        dy = y - cy
        
        # Calculate distance and angle
        r = np.sqrt(dx**2 + dy**2)
        theta = np.arctan2(dy, dx)
        
        # Maximum radius
        max_r = min(cx, cy)
        
        # Apply fisheye distortion
        # Map radius using fisheye formula
        aperture_rad = math.radians(self.aperture)
        new_r = r * (1 + self.strength * (r / max_r)**2)
        
        # Clamp to avoid extreme distortion
        new_r = np.clip(new_r, 0, max_r)
        
        # Convert back to Cartesian coordinates
        new_x = cx + new_r * np.cos(theta)
        new_y = cy + new_r * np.sin(theta)
        
        # Clamp coordinates
        new_x = np.clip(new_x, 0, w - 1).astype(int)
        new_y = np.clip(new_y, 0, h - 1).astype(int)
        
        # Sample from original image
        for i in range(h):
            for j in range(w):
                result[i, j] = rgba[new_y[i, j], new_x[i, j]]
        
        return result


class Wave:
    """
    Wave displacement distortion effect.
    Creates organic wave patterns in the image.
    """

    def __init__(self,
                 amplitude: float = 20.0,
                 frequency: float = 0.05,
                 phase: float = 0.0,
                 direction: str = "horizontal") -> None:
        self.amplitude = amplitude
        self.frequency = frequency
        self.phase = phase
        self.direction = direction.lower()

    def apply(self, rgba: np.ndarray, time: float = 0.0) -> np.ndarray:
        """Apply wave distortion to image."""
        if self.amplitude < 0.1:
            return rgba
            
        h, w, c = rgba.shape
        result = np.zeros_like(rgba)
        
        # Create coordinate grid
        y, x = np.ogrid[:h, :w]
        
        # Apply wave displacement
        if self.direction == "horizontal":
            # Horizontal wave (displace x)
            displacement = self.amplitude * np.sin(2 * math.pi * self.frequency * y + self.phase + time * 2)
            new_x = x + displacement
            new_y = y
        elif self.direction == "vertical":
            # Vertical wave (displace y)
            displacement = self.amplitude * np.sin(2 * math.pi * self.frequency * x + self.phase + time * 2)
            new_x = x
            new_y = y + displacement
        elif self.direction == "radial":
            # Radial wave
            cx, cy = w / 2, h / 2
            dx = x - cx
            dy = y - cy
            r = np.sqrt(dx**2 + dy**2)
            theta = np.arctan2(dy, dx)
            
            displacement = self.amplitude * np.sin(2 * math.pi * self.frequency * r + self.phase + time * 2)
            new_r = r + displacement
            new_x = cx + new_r * np.cos(theta)
            new_y = cy + new_r * np.sin(theta)
        else:  # diagonal
            # Diagonal wave
            displacement = self.amplitude * np.sin(2 * math.pi * self.frequency * (x + y) + self.phase + time * 2)
            new_x = x + displacement * 0.707  # cos(45°)
            new_y = y + displacement * 0.707  # sin(45°)
        
        # Clamp coordinates
        new_x = np.clip(new_x, 0, w - 1).astype(int)
        new_y = np.clip(new_y, 0, h - 1).astype(int)
        
        # Sample from original image
        for i in range(h):
            for j in range(w):
                result[i, j] = rgba[new_y[i, j], new_x[i, j]]
        
        return result


class LiquidContours:
    """
    Liquid-like contour distortion effect.
    Creates organic, fluid displacement patterns.
    """

    def __init__(self,
                 complexity: int = 5,
                 amplitude: float = 15.0,
                 frequency: float = 0.02,
                 evolution_speed: float = 1.0) -> None:
        self.complexity = max(1, min(10, complexity))
        self.amplitude = amplitude
        self.frequency = frequency
        self.evolution_speed = evolution_speed

    def apply(self, rgba: np.ndarray, time: float = 0.0) -> np.ndarray:
        """Apply liquid contour distortion to image."""
        if self.amplitude < 0.1:
            return rgba
            
        h, w, c = rgba.shape
        result = np.zeros_like(rgba)
        
        # Create coordinate grid
        y, x = np.ogrid[:h, :w]
        
        # Generate liquid displacement using multiple sine waves
        displacement_x = np.zeros_like(x, dtype=np.float32)
        displacement_y = np.zeros_like(y, dtype=np.float32)
        
        for i in range(self.complexity):
            # Random-ish parameters for each wave component
            angle = (i * 2 * math.pi / self.complexity)
            phase = time * self.evolution_speed + i
            
            # Add wave contribution
            wave_x = math.sin(angle) * math.sin(2 * math.pi * self.frequency * (x * math.cos(angle) + y * math.sin(angle)) + phase)
            wave_y = math.cos(angle) * math.sin(2 * math.pi * self.frequency * (x * math.sin(angle) - y * math.cos(angle)) + phase)
            
            displacement_x += wave_x
            displacement_y += wave_y
        
        # Normalize and scale displacement
        displacement_x = (displacement_x / self.complexity) * self.amplitude
        displacement_y = (displacement_y / self.complexity) * self.amplitude
        
        # Apply displacement
        new_x = x + displacement_x
        new_y = y + displacement_y
        
        # Clamp coordinates
        new_x = np.clip(new_x, 0, w - 1).astype(int)
        new_y = np.clip(new_y, 0, h - 1).astype(int)
        
        # Sample from original image
        for i in range(h):
            for j in range(w):
                result[i, j] = rgba[new_y[i, j], new_x[i, j]]
        
        return result


class Skew:
    """
    Geometric skew distortion effect.
    Applies perspective-like skew transformation.
    """

    def __init__(self,
                 x_skew: float = 0.0,
                 y_skew: float = 0.0,
                 center: Tuple[float, float] = (0.5, 0.5)) -> None:
        self.x_skew = max(-1.0, min(1.0, x_skew))
        self.y_skew = max(-1.0, min(1.0, y_skew))
        self.center = center

    def apply(self, rgba: np.ndarray, time: float = 0.0) -> np.ndarray:
        """Apply skew distortion to image."""
        if abs(self.x_skew) < 0.01 and abs(self.y_skew) < 0.01:
            return rgba
            
        h, w, c = rgba.shape
        result = np.zeros_like(rgba)
        
        # Create coordinate grid
        y, x = np.ogrid[:h, :w]
        
        # Center coordinates
        cx, cy = self.center[0] * w, self.center[1] * h
        dx = x - cx
        dy = y - cy
        
        # Apply skew transformation
        # x' = x + skew_x * y
        # y' = y + skew_y * x
        new_x = x + self.x_skew * dy * 0.5
        new_y = y + self.y_skew * dx * 0.5
        
        # Clamp coordinates
        new_x = np.clip(new_x, 0, w - 1).astype(int)
        new_y = np.clip(new_y, 0, h - 1).astype(int)
        
        # Sample from original image
        for i in range(h):
            for j in range(w):
                result[i, j] = rgba[new_y[i, j], new_x[i, j]]
        
        return result


class CornerPin:
    """
    Corner pinning distortion effect.
    Allows independent positioning of four corners for perspective transformation.
    """

    def __init__(self,
                 top_left: Optional[Tuple[float, float]] = None,
                 top_right: Optional[Tuple[float, float]] = None,
                 bottom_left: Optional[Tuple[float, float]] = None,
                 bottom_right: Optional[Tuple[float, float]] = None) -> None:
        # Default corners (no distortion)
        h, w = 1080, 1920  # Default dimensions
        self.top_left = top_left or (0, 0)
        self.top_right = top_right or (w, 0)
        self.bottom_left = bottom_left or (0, h)
        self.bottom_right = bottom_right or (w, h)

    def apply(self, rgba: np.ndarray, time: float = 0.0) -> np.ndarray:
        """Apply corner pin distortion to image."""
        h, w, c = rgba.shape
        result = np.zeros_like(rgba)
        
        # Check if corners are actually different from default
        default_corners = ((0, 0), (w, 0), (0, h), (w, h))
        current_corners = (self.top_left, self.top_right, self.bottom_left, self.bottom_right)
        
        if current_corners == default_corners:
            return rgba
        
        # Create coordinate grid
        y, x = np.ogrid[:h, :w]
        
        # Normalize coordinates to [0,1]
        norm_x = x / (w - 1)
        norm_y = y / (h - 1)
        
        # Bilinear interpolation for corner pinning
        # Calculate position based on corner weights
        for i in range(h):
            for j in range(w):
                nx, ny = norm_x[i, j], norm_y[i, j]
                
                # Calculate weights for each corner
                w_tl = (1 - nx) * (1 - ny)
                w_tr = nx * (1 - ny)
                w_bl = (1 - nx) * ny
                w_br = nx * ny
                
                # Calculate new position
                new_x = (w_tl * self.top_left[0] + w_tr * self.top_right[0] + 
                         w_bl * self.bottom_left[0] + w_br * self.bottom_right[0])
                new_y = (w_tl * self.top_left[1] + w_tr * self.top_right[1] + 
                         w_bl * self.bottom_left[1] + w_br * self.bottom_right[1])
                
                # Clamp coordinates
                new_x = int(np.clip(new_x, 0, w - 1))
                new_y = int(np.clip(new_y, 0, h - 1))
                
                result[i, j] = rgba[new_y, new_x]
        
        return result


class Spherical:
    """
    Spherical mapping distortion effect.
    Maps image onto a sphere for 3D-like distortion.
    """

    def __init__(self,
                 strength: float = 0.5,
                 center: Tuple[float, float] = (0.5, 0.5)) -> None:
        self.strength = max(0.0, min(1.0, strength))
        self.center = center

    def apply(self, rgba: np.ndarray, time: float = 0.0) -> np.ndarray:
        """Apply spherical distortion to image."""
        if self.strength < 0.01:
            return rgba
            
        h, w, c = rgba.shape
        result = np.zeros_like(rgba)
        
        # Create coordinate grid
        y, x = np.ogrid[:h, :w]
        
        # Center coordinates
        cx, cy = self.center[0] * w, self.center[1] * h
        dx = (x - cx) / (w / 2)
        dy = (y - cy) / (h / 2)
        
        # Calculate distance
        r = np.sqrt(dx**2 + dy**2)
        
        # Apply spherical distortion
        # Uses sphere equation for natural curvature
        max_r = math.sqrt(2)  # Maximum possible distance
        sphere_factor = 1.0 - self.strength * (1 - math.sqrt(max(0, 1 - (r / max_r)**2)))
        
        new_x = cx + dx * sphere_factor * (w / 2)
        new_y = cy + dy * sphere_factor * (h / 2)
        
        # Clamp coordinates
        new_x = np.clip(new_x, 0, w - 1).astype(int)
        new_y = np.clip(new_y, 0, h - 1).astype(int)
        
        # Sample from original image
        for i in range(h):
            for j in range(w):
                result[i, j] = rgba[new_y[i, j], new_x[i, j]]
        
        return result


# Convenience functions for creating distortion effects

def barrel_distortion(strength: float = 0.3) -> BarrelDistortion:
    """Create barrel distortion with common defaults."""
    return BarrelDistortion(strength=strength, distortion_type=DistortionType.BARREL)


def pincushion_distortion(strength: float = 0.3) -> BarrelDistortion:
    """Create pincushion distortion with common defaults."""
    return BarrelDistortion(strength=strength, distortion_type=DistortionType.PINCUSHION)


def fisheye(strength: float = 0.5, aperture: float = 180.0) -> Fisheye:
    """Create fisheye distortion with common defaults."""
    return Fisheye(strength=strength, aperture=aperture)


def wave(amplitude: float = 20.0, frequency: float = 0.05, direction: str = "horizontal") -> Wave:
    """Create wave distortion with common defaults."""
    return Wave(amplitude=amplitude, frequency=frequency, direction=direction)


def liquid_contours(complexity: int = 5, amplitude: float = 15.0) -> LiquidContours:
    """Create liquid contour distortion with common defaults."""
    return LiquidContours(complexity=complexity, amplitude=amplitude)


def skew(x_skew: float = 0.0, y_skew: float = 0.0) -> Skew:
    """Create skew distortion with common defaults."""
    return Skew(x_skew=x_skew, y_skew=y_skew)


def corner_pin(top_left: Tuple[float, float] = None,
              top_right: Tuple[float, float] = None,
              bottom_left: Tuple[float, float] = None,
              bottom_right: Tuple[float, float] = None) -> CornerPin:
    """Create corner pin distortion with common defaults."""
    return CornerPin(top_left=top_left, top_right=top_right, 
                    bottom_left=bottom_left, bottom_right=bottom_right)


def spherical(strength: float = 0.5) -> Spherical:
    """Create spherical distortion with common defaults."""
    return Spherical(strength=strength)


# Aliases
Waves = Wave
waves = wave