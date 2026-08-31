import numpy as np
import scipy.ndimage as ndimage
from typing import Any, Optional, Tuple, Union

try:
    from vibmo.fx.filters import Filter
except ImportError:
    class Filter:
        def apply(self, rgba: np.ndarray, time: float = 0.0) -> np.ndarray:
            raise NotImplementedError

class ThresholdGlowPass(Filter):
    """High-pass luminance threshold filter isolating intense specular points."""
    def __init__(self, threshold: float = 0.8, intensity: float = 1.0, **kwargs: Any):
        self.threshold = float(threshold)
        self.intensity = float(intensity)

    def apply(self, rgba: np.ndarray, time: float = 0.0) -> np.ndarray:
        rgb = rgba[:, :, :3].astype(np.float32) / 255.0

        luma = 0.2126 * rgb[:, :, 0] + 0.7152 * rgb[:, :, 1] + 0.0722 * rgb[:, :, 2]
        mask = np.clip((luma - self.threshold) / (1.0 - self.threshold + 1e-6), 0.0, 1.0)

        glow = rgb * mask[:, :, np.newaxis] * self.intensity
        out_rgb = np.clip(glow * 255.0, 0, 255).astype(np.uint8)

        out = rgba.copy()
        out[:, :, :3] = out_rgb
        return out

class AnamorphicStreakFlareShader(Filter):
    """Horizontal cinematic cyan/cobalt blue streak flares radiating from bright highlight sources."""
    def __init__(
        self,
        threshold: float = 0.8,
        streak_length: float = 50.0,
        intensity: float = 2.0,
        color: Any = (0.0, 0.5, 1.0),
        **kwargs: Any
    ):
        self.threshold = float(threshold)
        self.streak_length = float(streak_length)
        self.intensity = float(intensity)
        if hasattr(color, "r") and hasattr(color, "g") and hasattr(color, "b"):
            self.color = np.array([color.r, color.g, color.b], dtype=np.float32)
        else:
            self.color = np.array(color, dtype=np.float32)

    def apply(self, rgba: np.ndarray, time: float = 0.0) -> np.ndarray:
        rgb = rgba[:, :, :3].astype(np.float32) / 255.0

        luma = 0.2126 * rgb[:, :, 0] + 0.7152 * rgb[:, :, 1] + 0.0722 * rgb[:, :, 2]
        mask = np.clip((luma - self.threshold) / (1.0 - self.threshold + 1e-6), 0.0, 1.0)
        highlights = rgb * mask[:, :, np.newaxis]

        streak = np.zeros_like(highlights)
        for c in range(3):
            streak[:, :, c] = ndimage.gaussian_filter1d(highlights[:, :, c], sigma=self.streak_length, axis=1)

        streak = streak * self.color[np.newaxis, np.newaxis, :] * self.intensity

        out_rgb = np.clip((rgb + streak) * 255.0, 0, 255).astype(np.uint8)
        out = rgba.copy()
        out[:, :, :3] = out_rgb
        return out

class LensGhostArtifacts(Filter):
    """Secondary optical lens reflection rings and polygonal aperture ghosts along optical axis."""
    def __init__(self, threshold: float = 0.9, intensity: float = 0.5, ghosts: int = 3, dispersion: float = 0.05):
        self.threshold = threshold
        self.intensity = intensity
        self.ghosts = ghosts
        self.dispersion = dispersion

    def apply(self, rgba: np.ndarray, time: float = 0.0) -> np.ndarray:
        h, w, _ = rgba.shape
        rgb = rgba[:, :, :3].astype(np.float32) / 255.0

        luma = 0.2126 * rgb[:, :, 0] + 0.7152 * rgb[:, :, 1] + 0.0722 * rgb[:, :, 2]
        mask = np.clip((luma - self.threshold) / (1.0 - self.threshold + 1e-6), 0.0, 1.0)
        highlights = rgb * mask[:, :, np.newaxis]

        center_x, center_y = w / 2.0, h / 2.0
        y, x = np.mgrid[0:h, 0:w]

        dx = x - center_x
        dy = y - center_y

        ghost_sum = np.zeros_like(rgb)

        for i in range(1, self.ghosts + 1):
            if self.ghosts > 1:
                scale = -1.0 + (i - 1) / (self.ghosts - 1) * 2.0
            else:
                scale = -1.0

            if abs(scale) < 0.1:
                scale = -0.5

            for c in range(3):
                color_scale = 1.0 + (c - 1) * self.dispersion
                mapped_x = center_x + dx * scale * color_scale
                mapped_y = center_y + dy * scale * color_scale

                ghost_c = ndimage.map_coordinates(highlights[:, :, c], [mapped_y, mapped_x], order=1, mode='constant', cval=0.0)
                ghost_sum[:, :, c] += ghost_c * self.intensity / self.ghosts

        out_rgb = np.clip((rgb + ghost_sum) * 255.0, 0, 255).astype(np.uint8)
        out = rgba.copy()
        out[:, :, :3] = out_rgb
        return out

class StarburstSpikeCross(Filter):
    """4-point star cross sparkle on direct pinpoint specular highlights."""
    def __init__(self, threshold: float = 0.9, size: float = 20.0, intensity: float = 1.0):
        self.threshold = threshold
        self.size = size
        self.intensity = intensity

    def apply(self, rgba: np.ndarray, time: float = 0.0) -> np.ndarray:
        rgb = rgba[:, :, :3].astype(np.float32) / 255.0

        luma = 0.2126 * rgb[:, :, 0] + 0.7152 * rgb[:, :, 1] + 0.0722 * rgb[:, :, 2]
        mask = np.clip((luma - self.threshold) / (1.0 - self.threshold + 1e-6), 0.0, 1.0)
        highlights = rgb * mask[:, :, np.newaxis]

        spike_x = np.zeros_like(highlights)
        spike_y = np.zeros_like(highlights)

        for c in range(3):
            spike_x[:, :, c] = ndimage.gaussian_filter1d(highlights[:, :, c], sigma=self.size, axis=1)
            spike_y[:, :, c] = ndimage.gaussian_filter1d(highlights[:, :, c], sigma=self.size, axis=0)

        starburst = (spike_x + spike_y) * self.intensity
        out_rgb = np.clip((rgb + starburst) * 255.0, 0, 255).astype(np.uint8)

        out = rgba.copy()
        out[:, :, :3] = out_rgb
        return out


# Semantic Aliases
AnamorphicStreakFlare = AnamorphicStreakFlareShader
HorizontalBlueStreak = AnamorphicStreakFlareShader

__all__ = [
    "ThresholdGlowPass",
    "AnamorphicStreakFlareShader",
    "AnamorphicStreakFlare",
    "HorizontalBlueStreak",
    "LensGhostArtifacts",
    "StarburstSpikeCross",
]
