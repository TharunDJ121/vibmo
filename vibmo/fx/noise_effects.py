"""
Noise and Grain effects inspired by Remotion's noise and texture filters.
Includes Noise, WhiteNoise, Speckle, Scanlines, and TVSignalOff.
"""

from __future__ import annotations
import math
import numpy as np
from typing import Any, Optional, Tuple, Union, Callable
from enum import Enum
from dataclasses import dataclass

from vibmo.core.color import Color, colors


class NoiseType(Enum):
    """Types of noise generation."""
    WHITE = "white"
    PERLIN = "perlin"
    FRACTAL = "fractal"
    SIMPLEX = "simplex"
    CELLULAR = "cellular"


@dataclass
class NoiseParams:
    """Parameters for noise generation."""
    scale: float = 1.0
    octaves: int = 4
    persistence: float = 0.5
    lacunarity: float = 2.0
    speed: float = 1.0
    intensity: float = 0.5


class Noise:
    """
    Procedural multi-octave coherent / fractal noise overlay.
    Generates smooth, animated organic noise patterns.
    """

    def __init__(
        self,
        intensity: float = 0.15,
        scale: float = 4.0,
        octaves: int = 3,
        speed: float = 1.0,
        monochrome: bool = True,
        blend_mode: str = "overlay",
    ) -> None:
        self.intensity = max(0.0, min(1.0, float(intensity)))
        self.scale = max(0.1, float(scale))
        self.octaves = max(1, int(octaves))
        self.speed = float(speed)
        self.monochrome = monochrome
        self.blend_mode = blend_mode

    def _generate_noise_layer(self, h: int, w: int, freq: float, seed: int) -> np.ndarray:
        """Generate smooth bilinear-interpolated noise grid."""
        gh = max(2, int(h / freq))
        gw = max(2, int(w / freq))
        rng = np.random.RandomState(seed)
        grid = rng.uniform(0.0, 1.0, (gh, gw)).astype(np.float32)

        from scipy.ndimage import zoom
        zh = h / gh
        zw = w / gw
        layer = zoom(grid, (zh, zw), order=1)[:h, :w]
        return layer

    def apply(self, rgba: np.ndarray, time: float = 0.0) -> np.ndarray:
        """Apply coherent noise overlay onto RGBA image."""
        if self.intensity <= 1e-4:
            return rgba

        h, w, _ = rgba.shape
        t_seed = int((time * self.speed * 100) % 100000)

        # Build multi-octave fractal noise
        accum = np.zeros((h, w), dtype=np.float32)
        total_amp = 0.0
        amp = 1.0
        freq = max(4.0, 64.0 / self.scale)

        for i in range(self.octaves):
            layer = self._generate_noise_layer(h, w, freq, t_seed + i * 31)
            accum += layer * amp
            total_amp += amp
            amp *= 0.5
            freq = max(2.0, freq * 0.5)

        accum = (accum / max(1e-4, total_amp)) - 0.5  # Range -0.5 to +0.5

        out = rgba.copy()
        rgb = rgba[:, :, :3].astype(np.float32) / 255.0

        if self.monochrome:
            noise_3ch = np.repeat(accum[:, :, np.newaxis], 3, axis=2)
        else:
            n2 = self._generate_noise_layer(h, w, max(4.0, 32.0 / self.scale), t_seed + 101) - 0.5
            n3 = self._generate_noise_layer(h, w, max(4.0, 32.0 / self.scale), t_seed + 202) - 0.5
            noise_3ch = np.stack([accum, n2, n3], axis=2)

        # Blend
        if self.blend_mode == "add":
            rgb = np.clip(rgb + noise_3ch * self.intensity, 0.0, 1.0)
        elif self.blend_mode == "screen":
            n_pos = np.clip(noise_3ch * self.intensity + 0.5, 0.0, 1.0)
            rgb = 1.0 - (1.0 - rgb) * (1.0 - n_pos * self.intensity)
        else:  # overlay / soft light
            rgb = np.clip(rgb + noise_3ch * self.intensity * 2.0, 0.0, 1.0)

        out[:, :, :3] = (rgb * 255.0).astype(np.uint8)
        return out


class WhiteNoise:
    """
    High-frequency digital TV static and quantum white noise.
    """

    def __init__(
        self,
        intensity: float = 0.08,
        monochrome: bool = True,
        luminance_weighted: bool = True,
        fps_lock: Optional[int] = None,
    ) -> None:
        self.intensity = max(0.0, min(1.0, float(intensity)))
        self.monochrome = monochrome
        self.luminance_weighted = luminance_weighted
        self.fps_lock = fps_lock

    def apply(self, rgba: np.ndarray, time: float = 0.0) -> np.ndarray:
        if self.intensity <= 1e-4:
            return rgba

        h, w, _ = rgba.shape
        t = math.floor(time * self.fps_lock) if self.fps_lock else time
        seed = int((t * 1000) % 2147483647)
        rng = np.random.RandomState(seed)

        rgb = rgba[:, :, :3].astype(np.float32)

        if self.monochrome:
            noise = rng.randn(h, w, 1).astype(np.float32) * self.intensity * 255.0
        else:
            noise = rng.randn(h, w, 3).astype(np.float32) * self.intensity * 255.0

        if self.luminance_weighted:
            luma = (0.299 * rgb[:, :, 0] + 0.587 * rgb[:, :, 1] + 0.114 * rgb[:, :, 2]) / 255.0
            weight = np.clip(np.sin(luma * np.pi) * 1.25, 0.0, 1.0)[:, :, np.newaxis]
            noise = noise * weight

        out = rgba.copy()
        out[:, :, :3] = np.clip(rgb + noise, 0, 255).astype(np.uint8)
        return out


class Speckle:
    """
    Organic vintage film dirt, dust flecks, and hair speckles overlay.
    """

    def __init__(
        self,
        density: float = 0.003,
        size_range: Tuple[int, int] = (1, 4),
        scratches: bool = True,
        dark_speckles: bool = True,
        light_speckles: bool = True,
    ) -> None:
        self.density = max(0.0001, min(0.05, float(density)))
        self.size_range = size_range
        self.scratches = scratches
        self.dark_speckles = dark_speckles
        self.light_speckles = light_speckles

    def apply(self, rgba: np.ndarray, time: float = 0.0) -> np.ndarray:
        h, w, _ = rgba.shape
        seed = int((time * 24.0) % 10000)  # Jump every 24 fps frame
        rng = np.random.RandomState(seed)

        num_speckles = int(h * w * self.density * 0.05)
        if num_speckles <= 0:
            return rgba

        out = rgba.copy()
        rgb = out[:, :, :3]

        for _ in range(num_speckles):
            cx = rng.randint(0, w)
            cy = rng.randint(0, h)
            sz = rng.randint(self.size_range[0], self.size_range[1] + 1)
            is_light = rng.choice([True, False])

            if (is_light and not self.light_speckles) or (not is_light and not self.dark_speckles):
                continue

            val = 255 if is_light else 10
            x0, x1 = max(0, cx - sz), min(w, cx + sz)
            y0, y1 = max(0, cy - sz), min(h, cy + sz)
            rgb[y0:y1, x0:x1] = (rgb[y0:y1, x0:x1].astype(np.float32) * 0.3 + val * 0.7).astype(np.uint8)

        if self.scratches and rng.uniform(0.0, 1.0) < 0.45:
            sx = rng.randint(10, w - 10)
            opacity = rng.uniform(0.15, 0.45)
            scratch_w = rng.randint(1, 2)
            for c in range(3):
                rgb[:, sx:sx + scratch_w, c] = np.clip(
                    rgb[:, sx:sx + scratch_w, c].astype(np.float32) * (1.0 - opacity) + 240.0 * opacity,
                    0, 255
                ).astype(np.uint8)

        return out


class Scanlines:
    """
    CRT television / Retro monitor scanlines with phosphor glow and rolling beam.
    """

    def __init__(
        self,
        spacing: int = 4,
        intensity: float = 0.25,
        roll_speed: float = 0.2,
        phosphor_glow: bool = True,
        curvature: float = 0.0,
    ) -> None:
        self.spacing = max(2, int(spacing))
        self.intensity = max(0.0, min(1.0, float(intensity)))
        self.roll_speed = float(roll_speed)
        self.phosphor_glow = phosphor_glow
        self.curvature = float(curvature)

    def apply(self, rgba: np.ndarray, time: float = 0.0) -> np.ndarray:
        if self.intensity <= 1e-4:
            return rgba

        h, w, _ = rgba.shape
        y_idx = np.arange(h, dtype=np.float32)

        phase = (time * self.roll_speed * h) % self.spacing
        pattern = 0.5 + 0.5 * np.sin((y_idx + phase) * (2.0 * math.pi / self.spacing))
        
        mask = (1.0 - self.intensity * (1.0 - pattern)).astype(np.float32)[:, np.newaxis, np.newaxis]

        out = rgba.copy()
        rgb = rgba[:, :, :3].astype(np.float32) * mask

        if self.phosphor_glow:
            rgb[:, :, 1] = np.clip(rgb[:, :, 1] * 1.03, 0, 255)

        out[:, :, :3] = np.clip(rgb, 0, 255).astype(np.uint8)
        return out


class TVSignalOff:
    """
    Retro CRT Television turn-off animation effect.
    Collapses image vertically into a bright slit, then into a glowing central dot, then disappears.
    """

    def __init__(
        self,
        progress: float = 0.0,
        flash_intensity: float = 1.5,
        beam_color: Union[Color, str] = colors.WHITE,
    ) -> None:
        self.progress = max(0.0, min(1.0, float(progress)))
        self.flash_intensity = float(flash_intensity)
        self.beam_color = Color.from_any(beam_color)

    def apply(self, rgba: np.ndarray, time: float = 0.0) -> np.ndarray:
        p = self.progress
        if p <= 0.0:
            return rgba
        if p >= 1.0:
            return np.zeros_like(rgba)

        h, w, _ = rgba.shape
        out = np.zeros_like(rgba)
        cx, cy = w // 2, h // 2

        if p < 0.6:
            norm_p = p / 0.6
            v_scale = max(0.002, (1.0 - norm_p) ** 2)
            slit_h = max(2, int(h * v_scale))

            from PIL import Image
            pil_img = Image.fromarray(rgba)
            collapsed = pil_img.resize((w, slit_h), Image.Resampling.BILINEAR)
            arr = np.array(collapsed)

            flare = 1.0 + norm_p * (self.flash_intensity - 1.0)
            arr[:, :, :3] = np.clip(arr[:, :, :3].astype(np.float32) * flare, 0, 255).astype(np.uint8)

            y_start = max(0, cy - slit_h // 2)
            y_end = min(h, y_start + slit_h)
            actual_h = y_end - y_start
            out[y_start:y_end, :, :] = arr[:actual_h, :, :]

        elif p < 0.9:
            norm_p = (p - 0.6) / 0.3
            h_scale = max(0.002, (1.0 - norm_p) ** 3)
            dot_w = max(2, int(w * h_scale))
            dot_h = max(2, int(6 * (1.0 - norm_p)))

            x_start = max(0, cx - dot_w // 2)
            x_end = min(w, x_start + dot_w)
            y_start = max(0, cy - dot_h // 2)
            y_end = min(h, y_start + dot_h)

            bc = np.array([self.beam_color.r * 255, self.beam_color.g * 255, self.beam_color.b * 255], dtype=np.uint8)
            out[y_start:y_end, x_start:x_end, :3] = bc
            out[y_start:y_end, x_start:x_end, 3] = 255

        else:
            norm_p = (p - 0.9) / 0.1
            alpha = max(0.0, 1.0 - norm_p)
            dot_r = max(1, int(3 * alpha))
            y, x = np.ogrid[:h, :w]
            dist = np.hypot(x - cx, y - cy)
            dot_mask = np.clip(1.0 - dist / (dot_r + 1.0), 0.0, 1.0) * alpha
            
            for c in range(3):
                out[:, :, c] = (self.beam_color[c] * 255.0 * dot_mask).astype(np.uint8)
            out[:, :, 3] = (dot_mask * 255.0).astype(np.uint8)

        return out


# Convenience functions
def noise(intensity: float = 0.15, scale: float = 4.0, octaves: int = 3, **kwargs: Any) -> Noise:
    return Noise(intensity=intensity, scale=scale, octaves=octaves, **kwargs)


def white_noise(intensity: float = 0.08, monochrome: bool = True, **kwargs: Any) -> WhiteNoise:
    return WhiteNoise(intensity=intensity, monochrome=monochrome, **kwargs)


def speckle(density: float = 0.003, **kwargs: Any) -> Speckle:
    return Speckle(density=density, **kwargs)


def scanlines(spacing: int = 4, intensity: float = 0.25, **kwargs: Any) -> Scanlines:
    return Scanlines(spacing=spacing, intensity=intensity, **kwargs)


def tv_signal_off(progress: float = 0.0, **kwargs: Any) -> TVSignalOff:
    return TVSignalOff(progress=progress, **kwargs)
