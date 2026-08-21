"""
Chroma Keyer, Green / Blue Screen Removal, and Despill Color Suppression.
"""

from __future__ import annotations
import math
import numpy as np
from typing import Any, Optional, Tuple, Union
from vibmo.core.color import Color, colors


class ChromaKey:
    """
    High-speed vectorized Chroma Keyer (Green Screen / Blue Screen Removal)
    with edge softness falloff and despill color cast suppression.
    """

    def __init__(
        self,
        key_color: Union[Color, str] = Color.hex("#00ff00"),
        tolerance: float = 0.35,
        softness: float = 0.15,
        despill: float = 0.75,
    ) -> None:
        self.key_color = Color.from_any(key_color) if isinstance(key_color, (str, Color)) else Color.hex("#00ff00")
        self.tolerance = float(tolerance)
        self.softness = max(1e-4, float(softness))
        self.despill = float(despill)

    def apply(self, rgba: np.ndarray, time: float = 0.0) -> np.ndarray:
        """Processes RGBA buffer in-place or copies, returning keyed RGBA array."""
        out = rgba.copy()
        rgb = out[:, :, :3].astype(np.float32) / 255.0

        # Calculate Euclidean distance in normalized RGB space to key color
        kr, kg, kb = self.key_color.r, self.key_color.g, self.key_color.b
        dr = rgb[:, :, 0] - kr
        dg = rgb[:, :, 1] - kg
        db = rgb[:, :, 2] - kb
        dist = np.sqrt(dr * dr + dg * dg + db * db)

        # Compute alpha matte with smooth ramp
        inner = self.tolerance
        outer = self.tolerance + self.softness
        alpha = np.clip((dist - inner) / (outer - inner), 0.0, 1.0)

        # Despill green cast: green cannot exceed average of red and blue
        if self.despill > 0.01 and kg > 0.5:
            rb_avg = (rgb[:, :, 0] + rgb[:, :, 2]) * 0.5
            spill = np.maximum(0.0, rgb[:, :, 1] - rb_avg)
            rgb[:, :, 1] = np.clip(rgb[:, :, 1] - spill * self.despill, 0.0, 1.0)

        # Update output
        out[:, :, :3] = (rgb * 255.0).astype(np.uint8)
        orig_alpha = out[:, :, 3].astype(np.float32) / 255.0
        out[:, :, 3] = (orig_alpha * alpha * 255.0).astype(np.uint8)

        return out
