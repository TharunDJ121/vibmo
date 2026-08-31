"""
Professional 32-bit Float Color Grading Engine.
Implements Lift/Gamma/Gain/Offset 3-way color wheels, Contrast/Pivot, Daylight Temperature, Tint, and Color Boost.
"""

from __future__ import annotations
import math
import numpy as np
from typing import Any, Optional, Tuple, Union
from vibmo.core.color import Color


class ColorGrade:
    """
    Cinematic 32-bit floating-point color grading post-fx filter.
    Applies DaVinci Resolve-style primary grading mathematics across the frame.
    """

    def __init__(
        self,
        lift: Union[Tuple[float, float, float], float] = (0.0, 0.0, 0.0),
        gamma: Union[Tuple[float, float, float], float] = (0.0, 0.0, 0.0),
        gain: Union[Tuple[float, float, float], float] = (1.0, 1.0, 1.0),
        offset: Union[Tuple[float, float, float], float] = (0.0, 0.0, 0.0),
        contrast: float = 1.0,
        pivot: float = 0.435,
        temperature: float = 0.0,  # -1.0 (cool/blue) to +1.0 (warm/amber)
        tint: float = 0.0,         # -1.0 (green) to +1.0 (magenta)
        saturation: float = 1.0,   # 0.0 (B&W) to 2.0 (super saturated)
        color_boost: float = 0.0,  # Non-linear vibrance preserving already saturated tones
        use_s_curve: bool = True,
    ) -> None:
        def _to_triplet(val: Union[Tuple[float, float, float], float], default: float) -> np.ndarray:
            if isinstance(val, (int, float)):
                return np.array([float(val), float(val), float(val)], dtype=np.float32)
            if len(val) == 3:
                return np.array([float(val[0]), float(val[1]), float(val[2])], dtype=np.float32)
            return np.array([default, default, default], dtype=np.float32)

        self.lift = _to_triplet(lift, 0.0)
        self.gamma = _to_triplet(gamma, 0.0)
        self.gain = _to_triplet(gain, 1.0)
        self.offset = _to_triplet(offset, 0.0)
        self.contrast = float(contrast)
        self.pivot = float(pivot)
        self.temperature = float(temperature)
        self.tint = float(tint)
        self.saturation = float(saturation)
        self.color_boost = float(color_boost)
        self.use_s_curve = use_s_curve

    def apply(self, rgba: np.ndarray, time: float = 0.0) -> np.ndarray:
        """
        Executes color grading transformation on uint8 RGBA frame buffer.
        """
        if rgba.size == 0:
            return rgba

        # Convert uint8 RGB [0, 255] to float32 [0.0, 1.0]
        rgb = rgba[:, :, :3].astype(np.float32) / 255.0
        
        # 1. Temperature & Tint adjustment (LMS chromatic adaptation approximation)
        if abs(self.temperature) > 1e-4 or abs(self.tint) > 1e-4:
            # Warm shifts Red up, Blue down; Cool shifts Blue up, Red down
            temp_shift = np.array([self.temperature * 0.12, 0.0, -self.temperature * 0.12], dtype=np.float32)
            # Tint shifts Green down / Magenta up or vice-versa
            tint_shift = np.array([self.tint * 0.06, -self.tint * 0.12, self.tint * 0.06], dtype=np.float32)
            rgb += temp_shift + tint_shift

        # 2. Lift / Gamma / Gain / Offset 3-Way Primary Grading
        # Luminance calculation (ITU-R BT.709 coefficients)
        lum = (0.2126 * rgb[:, :, 0] + 0.7152 * rgb[:, :, 1] + 0.0722 * rgb[:, :, 2])[:, :, np.newaxis]
        
        # Lift weight (peaks at 0, drops to 0 at 1)
        w_lift = np.maximum(0.0, 1.0 - lum)
        # Gamma weight (peaks at midtones 0.5)
        w_gamma = np.maximum(0.0, 1.0 - np.abs(2.0 * lum - 1.0))
        # Gain weight (peaks at 1.0)
        w_gain = lum

        # Apply transfer function: Output = Lift*(1-L) + Gamma*(MidWeight) + Gain*L + Offset
        # For Lift/Gain: Gain scales highlights, Lift offsets shadows
        # Standard grading: Out = (RGB * Gain + Lift * (1 - RGB))^(1 / (1 + Gamma)) + Offset
        rgb_graded = (
            rgb * self.gain +
            self.lift * w_lift +
            self.gamma * w_gamma +
            self.offset
        )

        # 3. Contrast & Pivot with Optional S-Curve
        if abs(self.contrast - 1.0) > 1e-4:
            if self.use_s_curve:
                # Soft Sigmoid S-curve contrast expansion around pivot
                centered = rgb_graded - self.pivot
                # Sigmoid derivative slope = contrast
                s_curve = centered * self.contrast
                # Smooth soft clipping at highlights and shadows
                rgb_graded = self.pivot + np.tanh(s_curve * 1.5) / 1.5
            else:
                rgb_graded = self.pivot + (rgb_graded - self.pivot) * self.contrast

        # 4. Saturation & Color Boost (Vibrance)
        if abs(self.saturation - 1.0) > 1e-4 or abs(self.color_boost) > 1e-4:
            curr_lum = (0.2126 * rgb_graded[:, :, 0] + 0.7152 * rgb_graded[:, :, 1] + 0.0722 * rgb_graded[:, :, 2])[:, :, np.newaxis]
            
            # Base Saturation
            sat_factor = self.saturation
            
            # Color Boost: boosts less-saturated pixels more, protects already saturated tones
            if abs(self.color_boost) > 1e-4:
                # Calculate current pixel saturation [0, 1]
                max_c = np.max(rgb_graded, axis=2, keepdims=True)
                min_c = np.min(rgb_graded, axis=2, keepdims=True)
                pixel_sat = np.where(max_c > 1e-5, (max_c - min_c) / np.maximum(1e-5, max_c), 0.0)
                boost_weight = (1.0 - pixel_sat) * self.color_boost
                sat_factor += boost_weight

            rgb_graded = curr_lum + (rgb_graded - curr_lum) * sat_factor

        # Clip final values to [0, 255] uint8 range
        final_rgb = np.clip(rgb_graded * 255.0, 0.0, 255.0).astype(np.uint8)

        out = rgba.copy()
        out[:, :, :3] = final_rgb
        return out
