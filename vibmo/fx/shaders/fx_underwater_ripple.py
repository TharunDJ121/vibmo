"""
✦ Vibmo Shaders: Underwater Wave Ripple Refraction Filter
Inspired by Remocn underwater-ripple with 2D fluid refraction displacement.
"""

from __future__ import annotations

import numpy as np
import math
from typing import Any, Optional, Tuple

try:
    from vibmo.fx.filters import Filter
except ImportError:
    class Filter:
        def apply(self, rgba: np.ndarray, time: float = 0.0) -> np.ndarray:
            raise NotImplementedError


class UnderwaterRippleFilter(Filter):
    """
    Simulates fluid surface water refraction and caustics displacement over video frames.
    """
    def __init__(
        self,
        frequency: float = 0.02,
        amplitude: float = 8.0,
        speed: float = 2.5,
        chromatic_shift: float = 2.0,
        **kwargs: Any,
    ):
        self.frequency = frequency
        self.amplitude = amplitude
        self.speed = speed
        self.chromatic_shift = chromatic_shift

    def apply(self, rgba: np.ndarray, time: float = 0.0) -> np.ndarray:
        h, w, _ = rgba.shape
        t = time * self.speed

        # Build coordinate grid
        y_coords, x_coords = np.indices((h, w), dtype=np.float32)

        # 2D Wave displacement
        dx = (np.sin(y_coords * self.frequency + t) *
              np.cos(x_coords * self.frequency * 0.5 - t * 0.8) * self.amplitude)
        dy = (np.cos(x_coords * self.frequency + t * 1.2) *
              np.sin(y_coords * self.frequency * 0.7 + t * 0.5) * self.amplitude)

        # Red, Green, Blue chromatic dispersion coordinates
        r_x = np.clip(x_coords + dx + self.chromatic_shift, 0, w - 1).astype(int)
        r_y = np.clip(y_coords + dy + self.chromatic_shift, 0, h - 1).astype(int)

        g_x = np.clip(x_coords + dx, 0, w - 1).astype(int)
        g_y = np.clip(y_coords + dy, 0, h - 1).astype(int)

        b_x = np.clip(x_coords + dx - self.chromatic_shift, 0, w - 1).astype(int)
        b_y = np.clip(y_coords + dy - self.chromatic_shift, 0, h - 1).astype(int)

        out = np.zeros_like(rgba)
        out[:, :, 0] = rgba[r_y, r_x, 0]
        out[:, :, 1] = rgba[g_y, g_x, 1]
        out[:, :, 2] = rgba[b_y, b_x, 2]
        out[:, :, 3] = rgba[:, :, 3]

        return out
