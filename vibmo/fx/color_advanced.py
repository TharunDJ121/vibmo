"""
Advanced color effects inspired by Remotion's color correction library.
Includes Duotone, Tint, ColorCorrection, Levels, Curves, and more.
"""

from __future__ import annotations
import math
import numpy as np
from typing import Any, Optional, Tuple, Union, Callable
from enum import Enum
from dataclasses import dataclass


def _get_color_tuple(color_input: Union[str, tuple], default_tuple: tuple = (1.0, 1.0, 1.0, 1.0)) -> tuple:
    """Helper function to get color tuple from various inputs."""
    if isinstance(color_input, tuple):
        return color_input
    elif isinstance(color_input, str):
        # Simple color mapping for common colors
        color_map = {
            'white': (1.0, 1.0, 1.0, 1.0),
            'black': (0.0, 0.0, 0.0, 1.0),
            'red': (1.0, 0.0, 0.0, 1.0),
            'green': (0.0, 1.0, 0.0, 1.0),
            'blue': (0.0, 0.0, 1.0, 1.0),
            'sepia': (0.76, 0.70, 0.50, 1.0),
            'purple': (0.5, 0.0, 0.5, 1.0),
            'orange': (1.0, 0.5, 0.0, 1.0),
            'cyan': (0.0, 1.0, 1.0, 1.0),
            'pink': (1.0, 0.75, 0.8, 1.0),
            'emerald': (0.2, 0.8, 0.4, 1.0),
            'amber': (1.0, 0.75, 0.0, 1.0),
            'navy': (0.0, 0.0, 0.5, 1.0),
            'teal': (0.0, 0.5, 0.5, 1.0),
            'lime': (0.75, 1.0, 0.0, 1.0),
        }
        return color_map.get(color_input.lower(), default_tuple)
    else:
        return default_tuple


class ColorSpace(Enum):
    """Color space for color operations."""
    RGB = "rgb"
    HSL = "hsl"
    HSV = "hsv"
    LAB = "lab"


@dataclass
class ColorGradingParams:
    """Parameters for color grading operations."""
    brightness: float = 0.0
    contrast: float = 0.0
    saturation: float = 0.0
    hue_shift: float = 0.0
    vibrance: float = 0.0
    temperature: float = 0.0  # -1 (cool) to 1 (warm)
    tint: float = 0.0  # -1 (green) to 1 (magenta)


class Duotone:
    """
    Duotone color effect.
    Maps image luminance to two colors for a stylish two-tone effect.
    """

    def __init__(self,
                 light_color: Union[str, tuple] = 'white',
                 dark_color: Union[str, tuple] = 'black',
                 intensity: float = 1.0) -> None:
        self.light_color = _get_color_tuple(light_color, (1.0, 1.0, 1.0, 1.0))
        self.dark_color = _get_color_tuple(dark_color, (0.0, 0.0, 0.0, 1.0))
        self.intensity = max(0.0, min(1.0, intensity))

    def apply(self, rgba: np.ndarray, time: float = 0.0) -> np.ndarray:
        """Apply duotone effect to image."""
        if self.intensity <= 0:
            return rgba
            
        h, w, c = rgba.shape
        result = rgba.copy()
        
        # Calculate luminance
        rgb = rgba[:, :, :3].astype(np.float32)
        luminance = (0.299 * rgb[:, :, 0] + 0.587 * rgb[:, :, 1] + 0.114 * rgb[:, :, 2]) / 255.0
        
        # Create duotone mapping
        light_arr = np.array([self.light_color.r * 255, self.light_color.g * 255, self.light_color.b * 255])
        dark_arr = np.array([self.dark_color.r * 255, self.dark_color.g * 255, self.dark_color.b * 255])
        
        # Map luminance to duotone colors
        for i in range(3):
            duotone_channel = dark_arr[i] + (light_arr[i] - dark_arr[i]) * luminance
            result[:, :, i] = (rgb[:, :, i] * (1 - self.intensity) + duotone_channel * self.intensity).astype(np.uint8)
        
        return result


class Tint:
    """
    Color tint effect.
    Applies a color tint to the image with adjustable intensity.
    """

    def __init__(self,
                 tint_color: Union[str, tuple] = 'sepia',
                 intensity: float = 0.5,
                 blend_mode: str = "multiply") -> None:
        self.tint_color = _get_color_tuple(tint_color, (0.76, 0.70, 0.50, 1.0))
        self.intensity = max(0.0, min(1.0, intensity))
        self.blend_mode = blend_mode.lower()

    def apply(self, rgba: np.ndarray, time: float = 0.0) -> np.ndarray:
        """Apply tint effect to image."""
        if self.intensity <= 0:
            return rgba
            
        h, w, c = rgba.shape
        result = rgba.copy()
        
        # Convert to grayscale for tinting
        rgb = rgba[:, :, :3].astype(np.float32)
        gray = (0.299 * rgb[:, :, 0] + 0.587 * rgb[:, :, 1] + 0.114 * rgb[:, :, 2])
        
        # Apply tint color
        tint_arr = np.array([self.tint_color.r * 255, self.tint_color.g * 255, self.tint_color.b * 255])
        
        if self.blend_mode == "multiply":
            # Multiply blend mode
            for i in range(3):
                tinted = gray * (tint_arr[i] / 255.0)
                result[:, :, i] = (rgb[:, :, i] * (1 - self.intensity) + tinted * self.intensity).astype(np.uint8)
        elif self.blend_mode == "screen":
            # Screen blend mode
            for i in range(3):
                tinted = 255 - ((255 - gray) * (255 - tint_arr[i]) / 255.0)
                result[:, :, i] = (rgb[:, :, i] * (1 - self.intensity) + tinted * self.intensity).astype(np.uint8)
        else:  # normal/overlay
            for i in range(3):
                tinted = gray * (tint_arr[i] / 255.0)
                result[:, :, i] = (rgb[:, :, i] * (1 - self.intensity) + tinted * self.intensity).astype(np.uint8)
        
        return result


class ColorCorrection:
    """
    Advanced color correction with multiple parameters.
    Inspired by professional color grading tools.
    """

    def __init__(self, params: Optional[ColorGradingParams] = None) -> None:
        self.params = params or ColorGradingParams()

    def apply(self, rgba: np.ndarray, time: float = 0.0) -> np.ndarray:
        """Apply color correction to image."""
        h, w, c = rgba.shape
        result = rgba.copy()
        rgb = rgba[:, :, :3].astype(np.float32)
        
        # Apply brightness
        if self.params.brightness != 0:
            brightness_offset = self.params.brightness * 50
            rgb = np.clip(rgb + brightness_offset, 0, 255)
        
        # Apply contrast
        if self.params.contrast != 0:
            contrast_factor = (1.0 + self.params.contrast)
            rgb = np.clip((rgb - 128) * contrast_factor + 128, 0, 255)
        
        # Convert to HSL for saturation and hue operations
        hsl = self._rgb_to_hsl(rgb)
        
        # Apply saturation
        if self.params.saturation != 0:
            saturation_factor = 1.0 + self.params.saturation
            hsl[:, :, 1] = np.clip(hsl[:, :, 1] * saturation_factor, 0, 1)
        
        # Apply hue shift
        if self.params.hue_shift != 0:
            hsl[:, :, 0] = (hsl[:, :, 0] + self.params.hue_shift) % 1.0
        
        # Apply vibrance (affects less saturated colors more)
        if self.params.vibrance != 0:
            saturation = hsl[:, :, 1]
            vibrance_mask = 1.0 - saturation  # More effect on less saturated areas
            hsl[:, :, 1] = np.clip(saturation + vibrance_mask * self.params.vibrance * 0.5, 0, 1)
        
        # Convert back to RGB
        rgb = self._hsl_to_rgb(hsl)
        
        # Apply temperature (warm/cool)
        if self.params.temperature != 0:
            temp = self.params.temperature
            rgb[:, :, 0] = np.clip(rgb[:, :, 0] + temp * 30, 0, 255)  # Red channel
            rgb[:, :, 2] = np.clip(rgb[:, :, 2] - temp * 30, 0, 255)  # Blue channel
        
        # Apply tint (green/magenta)
        if self.params.tint != 0:
            tint = self.params.tint
            rgb[:, :, 1] = np.clip(rgb[:, :, 1] + tint * 20, 0, 255)  # Green channel
            rgb[:, :, 0] = np.clip(rgb[:, :, 0] - tint * 10, 0, 255)  # Red channel
        
        result[:, :, :3] = rgb.astype(np.uint8)
        return result

    def _rgb_to_hsl(self, rgb: np.ndarray) -> np.ndarray:
        """Convert RGB to HSL color space."""
        h, w, c = rgb.shape
        hsl = np.zeros_like(rgb, dtype=np.float32)
        
        r, g, b = rgb[:, :, 0] / 255.0, rgb[:, :, 1] / 255.0, rgb[:, :, 2] / 255.0
        max_val = np.max(rgb, axis=2) / 255.0
        min_val = np.min(rgb, axis=2) / 255.0
        delta = max_val - min_val
        
        # Lightness
        hsl[:, :, 2] = (max_val + min_val) / 2.0
        
        # Saturation
        hsl[:, :, 1] = np.where(delta > 0, delta / (1 - np.abs(2 * hsl[:, :, 2] - 1)), 0)
        
        # Hue
        mask_r = (max_val == r)
        mask_g = (max_val == g) & (~mask_r)
        mask_b = (max_val == b) & (~mask_r) & (~mask_g)
        
        hsl[:, :, 0] = np.where(mask_r, ((g - b) / delta) % 6, hsl[:, :, 0])
        hsl[:, :, 0] = np.where(mask_g, ((b - r) / delta) + 2, hsl[:, :, 0])
        hsl[:, :, 0] = np.where(mask_b, ((r - g) / delta) + 4, hsl[:, :, 0])
        hsl[:, :, 0] = hsl[:, :, 0] / 6.0
        
        return hsl

    def _hsl_to_rgb(self, hsl: np.ndarray) -> np.ndarray:
        """Convert HSL to RGB color space."""
        h, w, c = hsl.shape
        rgb = np.zeros_like(hsl, dtype=np.float32)
        
        h_norm = hsl[:, :, 0] * 6.0
        s = hsl[:, :, 1]
        l = hsl[:, :, 2]
        
        c_val = (1 - np.abs(2 * l - 1)) * s
        x = c_val * (1 - np.abs((h_norm % 2) - 1))
        m = l - c_val / 2.0
        
        # RGB conversion based on hue sector
        sector_0 = (h_norm < 1)
        sector_1 = (h_norm >= 1) & (h_norm < 2)
        sector_2 = (h_norm >= 2) & (h_norm < 3)
        sector_3 = (h_norm >= 3) & (h_norm < 4)
        sector_4 = (h_norm >= 4) & (h_norm < 5)
        sector_5 = (h_norm >= 5)
        
        rgb[:, :, 0] = np.where(sector_0, c_val, np.where(sector_1, x, np.where(sector_4, 0, np.where(sector_5, c_val, x))))
        rgb[:, :, 1] = np.where(sector_1, c_val, np.where(sector_2, x, np.where(sector_3, 0, np.where(sector_4, x, c_val))))
        rgb[:, :, 2] = np.where(sector_3, c_val, np.where(sector_4, x, np.where(sector_5, 0, np.where(sector_0, x, c_val))))
        
        rgb = (rgb + m) * 255.0
        return np.clip(rgb, 0, 255)


class Levels:
    """
    Levels adjustment for shadows, midtones, and highlights.
    Similar to Photoshop's Levels adjustment.
    """

    def __init__(self,
                 input_black: float = 0.0,
                 input_white: float = 255.0,
                 gamma: float = 1.0,
                 output_black: float = 0.0,
                 output_white: float = 255.0) -> None:
        self.input_black = max(0.0, min(255.0, input_black))
        self.input_white = max(0.0, min(255.0, input_white))
        self.gamma = max(0.1, gamma)
        self.output_black = max(0.0, min(255.0, output_black))
        self.output_white = max(0.0, min(255.0, output_white))

    def apply(self, rgba: np.ndarray, time: float = 0.0) -> np.ndarray:
        """Apply levels adjustment to image."""
        h, w, c = rgba.shape
        result = rgba.copy()
        rgb = rgba[:, :, :3].astype(np.float32)
        
        # Calculate input range
        input_range = self.input_white - self.input_black
        if input_range <= 0:
            input_range = 1.0
        
        # Normalize input
        normalized = (rgb - self.input_black) / input_range
        normalized = np.clip(normalized, 0, 1)
        
        # Apply gamma correction
        gamma_corrected = np.power(normalized, 1.0 / self.gamma)
        
        # Apply output range
        output_range = self.output_white - self.output_black
        adjusted = gamma_corrected * output_range + self.output_black
        
        result[:, :, :3] = np.clip(adjusted, 0, 255).astype(np.uint8)
        return result


class Curves:
    """
    Curves adjustment for precise tonal control.
    Uses bezier curves for smooth adjustments.
    """

    def __init__(self,
                 curve_points: Optional[list] = None,
                 master_curve: Optional[Callable[[float], float]] = None) -> None:
        self.curve_points = curve_points or [(0, 0), (255, 255)]
        self.master_curve = master_curve or self._default_curve

    def _default_curve(self, x: float) -> float:
        """Default linear curve."""
        return x

    def _interpolate_curve(self, x: float) -> float:
        """Interpolate value from curve points."""
        if len(self.curve_points) < 2:
            return x
        
        # Find the segment where x falls
        for i in range(len(self.curve_points) - 1):
            x1, y1 = self.curve_points[i]
            x2, y2 = self.curve_points[i + 1]
            
            if x1 <= x <= x2:
                # Linear interpolation
                t = (x - x1) / (x2 - x1) if x2 != x1 else 0
                return y1 + t * (y2 - y1)
        
        # Outside curve range, clamp to endpoints
        if x < self.curve_points[0][0]:
            return self.curve_points[0][1]
        else:
            return self.curve_points[-1][1]

    def apply(self, rgba: np.ndarray, time: float = 0.0) -> np.ndarray:
        """Apply curves adjustment to image."""
        h, w, c = rgba.shape
        result = rgba.copy()
        rgb = rgba[:, :, :3].astype(np.float32)
        
        # Apply curve to each channel
        for channel in range(3):
            # Vectorized curve application
            channel_data = rgb[:, :, channel]
            flat_data = channel_data.flatten()
            
            # Apply curve interpolation
            curved_data = np.array([self._interpolate_curve(val) for val in flat_data])
            curved_data = curved_data.reshape(h, w)
            
            result[:, :, channel] = np.clip(curved_data, 0, 255).astype(np.uint8)
        
        return result


class WhiteBalance:
    """
    White balance adjustment for color temperature correction.
    """

    def __init__(self,
                 temperature: float = 0.0,  # -100 (cool) to 100 (warm)
                 tint: float = 0.0) -> None:  # -100 (green) to 100 (magenta)
        self.temperature = max(-100.0, min(100.0, temperature))
        self.tint = max(-100.0, min(100.0, tint))

    def apply(self, rgba: np.ndarray, time: float = 0.0) -> np.ndarray:
        """Apply white balance adjustment to image."""
        if self.temperature == 0 and self.tint == 0:
            return rgba
            
        h, w, c = rgba.shape
        result = rgba.copy()
        rgb = rgba[:, :, :3].astype(np.float32)
        
        # Temperature adjustment (affects red and blue channels)
        temp_factor = self.temperature / 100.0
        rgb[:, :, 0] = np.clip(rgb[:, :, 0] + temp_factor * 30, 0, 255)  # Red
        rgb[:, :, 2] = np.clip(rgb[:, :, 2] - temp_factor * 30, 0, 255)  # Blue
        
        # Tint adjustment (affects green and magenta)
        tint_factor = self.tint / 100.0
        rgb[:, :, 1] = np.clip(rgb[:, :, 1] + tint_factor * 20, 0, 255)  # Green
        rgb[:, :, 0] = np.clip(rgb[:, :, 0] - tint_factor * 10, 0, 255)  # Red (magenta compensation)
        
        result[:, :, :3] = rgb.astype(np.uint8)
        return result


class Saturation:
    """
    Saturation adjustment with optional vibrance mode.
    """

    def __init__(self,
                 saturation: float = 0.0,  # -1 to 1
                 vibrance_mode: bool = False) -> None:
        self.saturation = max(-1.0, min(1.0, saturation))
        self.vibrance_mode = vibrance_mode

    def apply(self, rgba: np.ndarray, time: float = 0.0) -> np.ndarray:
        """Apply saturation adjustment to image."""
        if self.saturation == 0:
            return rgba
            
        h, w, c = rgba.shape
        result = rgba.copy()
        rgb = rgba[:, :, :3].astype(np.float32)
        
        # Convert to HSL
        hsl = self._rgb_to_hsl(rgb)
        
        if self.vibrance_mode:
            # Vibrance: affects less saturated colors more
            saturation = hsl[:, :, 1]
            vibrance_mask = 1.0 - saturation
            hsl[:, :, 1] = np.clip(saturation + vibrance_mask * self.saturation * 0.5, 0, 1)
        else:
            # Standard saturation
            saturation_factor = 1.0 + self.saturation
            hsl[:, :, 1] = np.clip(hsl[:, :, 1] * saturation_factor, 0, 1)
        
        # Convert back to RGB
        rgb = self._hsl_to_rgb(hsl)
        result[:, :, :3] = rgb.astype(np.uint8)
        return result

    def _rgb_to_hsl(self, rgb: np.ndarray) -> np.ndarray:
        """Convert RGB to HSL."""
        r, g, b = rgb[:, :, 0] / 255.0, rgb[:, :, 1] / 255.0, rgb[:, :, 2] / 255.0
        max_val = np.max(rgb, axis=2)
        min_val = np.min(rgb, axis=2)
        delta = max_val - min_val
        
        hsl = np.zeros_like(rgb)
        hsl[:, :, 2] = (max_val + min_val) / 2.0
        hsl[:, :, 1] = np.where(delta > 0, delta / (1 - np.abs(2 * hsl[:, :, 2] - 1)), 0)
        
        mask_r = (max_val == r)
        mask_g = (max_val == g) & (~mask_r)
        mask_b = (max_val == b) & (~mask_r) & (~mask_g)
        
        hsl[:, :, 0] = np.where(mask_r, ((g - b) / delta) % 6, 0)
        hsl[:, :, 0] = np.where(mask_g, ((b - r) / delta) + 2, hsl[:, :, 0])
        hsl[:, :, 0] = np.where(mask_b, ((r - g) / delta) + 4, hsl[:, :, 0])
        hsl[:, :, 0] = hsl[:, :, 0] / 6.0
        
        return hsl

    def _hsl_to_rgb(self, hsl: np.ndarray) -> np.ndarray:
        """Convert HSL to RGB."""
        h_norm = hsl[:, :, 0] * 6.0
        s = hsl[:, :, 1]
        l = hsl[:, :, 2]
        
        c_val = (1 - np.abs(2 * l - 1)) * s
        x = c_val * (1 - np.abs((h_norm % 2) - 1))
        m = l - c_val / 2.0
        
        rgb = np.zeros_like(hsl)
        rgb[:, :, 0] = np.where((h_norm < 1) | (h_norm >= 5), c_val, np.where((h_norm >= 1) & (h_norm < 2), x, 0))
        rgb[:, :, 1] = np.where((h_norm >= 1) & (h_norm < 3), c_val, np.where((h_norm >= 3) & (h_norm < 4), x, 0))
        rgb[:, :, 2] = np.where((h_norm >= 3) & (h_norm < 5), c_val, np.where((h_norm >= 5) | (h_norm < 1), x, 0))
        
        rgb = (rgb + m) * 255.0
        return np.clip(rgb, 0, 255)


class Vibrance:
    """
    Vibrance adjustment that boosts saturation in less saturated areas.
    """

    def __init__(self, vibrance: float = 0.0) -> None:
        self.vibrance = max(-1.0, min(1.0, vibrance))

    def apply(self, rgba: np.ndarray, time: float = 0.0) -> np.ndarray:
        """Apply vibrance adjustment to image."""
        if self.vibrance == 0:
            return rgba
            
        # Use saturation with vibrance mode
        saturation = Saturation(saturation=self.vibrance, vibrance_mode=True)
        return saturation.apply(rgba, time)


# Convenience functions for common color effects

def duotone(light_color: Union[str, tuple] = 'white', 
            dark_color: Union[str, tuple] = 'black',
            intensity: float = 1.0) -> Duotone:
    """Create a duotone effect with common defaults."""
    return Duotone(light_color=light_color, dark_color=dark_color, intensity=intensity)


def tint(tint_color: Union[str, tuple] = 'sepia',
        intensity: float = 0.5,
        blend_mode: str = "multiply") -> Tint:
    """Create a tint effect with common defaults."""
    return Tint(tint_color=tint_color, intensity=intensity, blend_mode=blend_mode)


def color_correction(brightness: float = 0.0,
                    contrast: float = 0.0,
                    saturation: float = 0.0,
                    hue_shift: float = 0.0) -> ColorCorrection:
    """Create color correction with common parameters."""
    params = ColorGradingParams(
        brightness=brightness,
        contrast=contrast,
        saturation=saturation,
        hue_shift=hue_shift
    )
    return ColorCorrection(params=params)


def levels(input_black: float = 0.0,
           input_white: float = 255.0,
           gamma: float = 1.0) -> Levels:
    """Create levels adjustment with common parameters."""
    return Levels(input_black=input_black, input_white=input_white, gamma=gamma)


def white_balance(temperature: float = 0.0, tint: float = 0.0) -> WhiteBalance:
    """Create white balance adjustment with common parameters."""
    return WhiteBalance(temperature=temperature, tint=tint)


def saturation(saturation: float = 0.0, vibrance_mode: bool = False) -> Saturation:
    """Create saturation adjustment with common parameters."""
    return Saturation(saturation=saturation, vibrance_mode=vibrance_mode)


def vibrance(vibrance: float = 0.0) -> Vibrance:
    """Create vibrance adjustment with common parameters."""
    return Vibrance(vibrance=vibrance)


def curves(curve_points: Optional[List[Tuple[float, float]]] = None) -> Curves:
    """Create curves adjustment with common parameters."""
    return Curves(curve_points=curve_points)