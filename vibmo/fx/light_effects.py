"""
Light and optical effects inspired by Remotion's optical and glow library.
Includes LightLeak, Shine, LensFlare, GodRays, and ThermalVision.
"""

from __future__ import annotations
import math
import numpy as np
from PIL import Image, ImageFilter
from typing import Any, Optional, Tuple, Union, List
from enum import Enum
from dataclasses import dataclass

from vibmo.core.color import Color, colors


class ThermalPalette(Enum):
    IRONBOW = "ironbow"
    RAINBOW = "rainbow"
    FIRE = "fire"
    CYBERPUNK = "cyberpunk"
    ARCTIC = "arctic"


class LightLeak:
    """
    Anamorphic organic light leak with color shifts and drifting lens flares.
    Adds cinematic vintage or futuristic warmth to footage and motion cards.
    """

    def __init__(
        self,
        intensity: float = 0.6,
        color: Union[Color, str] = colors.AMBER,
        secondary_color: Union[Color, str] = colors.ROSE,
        speed: float = 0.5,
        position: Tuple[float, float] = (0.2, 0.2),  # Normalized 0-1
        radius: float = 0.6,
    ) -> None:
        self.intensity = max(0.0, min(2.0, float(intensity)))
        self.color = Color.from_any(color)
        self.secondary_color = Color.from_any(secondary_color)
        self.speed = float(speed)
        self.position = position
        self.radius = max(0.1, float(radius))

    def apply(self, rgba: np.ndarray, time: float = 0.0) -> np.ndarray:
        if self.intensity <= 1e-4:
            return rgba

        h, w, _ = rgba.shape
        # Organic orbital motion
        drift_x = math.sin(time * self.speed * 1.5) * 0.15
        drift_y = math.cos(time * self.speed * 1.1) * 0.12
        cx = int((self.position[0] + drift_x) * w)
        cy = int((self.position[1] + drift_y) * h)

        y, x = np.ogrid[:h, :w]
        dist = np.hypot(x - cx, y - cy)
        max_r = math.hypot(w, h) * self.radius

        # Soft falloff
        falloff = np.clip(1.0 - (dist / max_r), 0.0, 1.0) ** 1.8
        falloff_mask = falloff[:, :, np.newaxis]

        # Dual color blending
        c1 = np.array([self.color.r, self.color.g, self.color.b], dtype=np.float32)
        c2 = np.array([self.secondary_color.r, self.secondary_color.g, self.secondary_color.b], dtype=np.float32)
        
        mix_t = 0.5 + 0.5 * math.sin(time * self.speed * 2.0)
        leak_color = c1 * (1.0 - mix_t) + c2 * mix_t

        rgb = rgba[:, :, :3].astype(np.float32) / 255.0
        # Screen blend
        leak_layer = leak_color * falloff_mask * self.intensity
        screened = 1.0 - (1.0 - rgb) * (1.0 - np.clip(leak_layer, 0.0, 1.0))

        out = rgba.copy()
        out[:, :, :3] = (np.clip(screened, 0.0, 1.0) * 255.0).astype(np.uint8)
        return out


class Shine:
    """
    Linear light sweep / glossy sheen across elements.
    Sweeps a glowing band across the layer based on progress (0.0 to 1.0).
    """

    def __init__(
        self,
        progress: float = 0.0,
        angle: float = 35.0,
        width: float = 0.25,
        intensity: float = 0.8,
        color: Union[Color, str] = colors.WHITE,
        mask_by_alpha: bool = True,
    ) -> None:
        self.progress = float(progress)
        self.angle = float(angle)
        self.width = max(0.05, min(1.0, float(width)))
        self.intensity = max(0.0, min(2.0, float(intensity)))
        self.color = Color.from_any(color)
        self.mask_by_alpha = mask_by_alpha

    def apply(self, rgba: np.ndarray, time: float = 0.0) -> np.ndarray:
        if self.intensity <= 1e-4 or not (-0.5 <= self.progress <= 1.5):
            return rgba

        h, w, _ = rgba.shape
        rad = math.radians(self.angle)
        cos_a, sin_a = math.cos(rad), math.sin(rad)

        y, x = np.ogrid[:h, :w]
        # Projected distance along angle
        proj = (x * cos_a + y * sin_a)
        min_p = 0.0
        max_p = w * abs(cos_a) + h * abs(sin_a)
        
        # Center of the sweep
        center = min_p + self.progress * (max_p - min_p)
        band_w = (max_p - min_p) * self.width

        dist = np.abs(proj - center) / max(1.0, band_w * 0.5)
        shine_mask = np.clip(1.0 - dist, 0.0, 1.0) ** 2.0
        shine_mask = shine_mask[:, :, np.newaxis]

        if self.mask_by_alpha:
            alpha_mask = (rgba[:, :, 3:4].astype(np.float32) / 255.0)
            shine_mask = shine_mask * alpha_mask

        shine_rgb = np.array([self.color.r, self.color.g, self.color.b], dtype=np.float32) * self.intensity * 255.0
        rgb = rgba[:, :, :3].astype(np.float32)

        out = rgba.copy()
        out[:, :, :3] = np.clip(rgb + shine_mask * shine_rgb, 0, 255).astype(np.uint8)
        return out


class LensFlare:
    """
    Multi-element optical lens flare with primary burst, anamorphic streaks, halo rings, and ghost discs.
    """

    def __init__(
        self,
        position: Tuple[float, float] = (0.3, 0.3),
        intensity: float = 1.0,
        color: Union[Color, str] = colors.CYAN,
        streak_length: float = 0.6,
        ghosts: int = 4,
    ) -> None:
        self.position = position
        self.intensity = max(0.0, min(2.0, float(intensity)))
        self.color = Color.from_any(color)
        self.streak_length = max(0.1, float(streak_length))
        self.ghosts = max(0, int(ghosts))

    def apply(self, rgba: np.ndarray, time: float = 0.0) -> np.ndarray:
        if self.intensity <= 1e-4:
            return rgba

        h, w, _ = rgba.shape
        fx = int(self.position[0] * w)
        fy = int(self.position[1] * h)
        cx, cy = w // 2, h // 2

        out = rgba.copy()
        rgb = rgba[:, :, :3].astype(np.float32)
        flare_acc = np.zeros((h, w, 3), dtype=np.float32)

        y, x = np.ogrid[:h, :w]
        dist_f = np.hypot(x - fx, y - fy)

        # 1. Primary Core Burst
        core_r = min(w, h) * 0.08
        core = np.clip(1.0 - (dist_f / core_r), 0.0, 1.0) ** 2.5
        flare_acc += core[:, :, np.newaxis] * 255.0

        # 2. Horizontal Anamorphic Streak
        streak_w = w * self.streak_length
        streak_h = max(2.0, h * 0.015)
        streak = np.exp(-((x - fx) ** 2) / (2 * (streak_w * 0.5) ** 2) - ((y - fy) ** 2) / (2 * streak_h ** 2))
        flare_acc += streak[:, :, np.newaxis] * np.array([self.color.r, self.color.g, self.color.b], dtype=np.float32) * 200.0

        # 3. Optical Ghost Discs along line through center
        vec_x, vec_y = cx - fx, cy - fy
        for g in range(1, self.ghosts + 1):
            factor = 0.4 * g
            gx = int(fx + vec_x * factor)
            gy = int(fy + vec_y * factor)
            gr = max(4.0, 20.0 * (1.0 + 0.3 * g))
            g_dist = np.hypot(x - gx, y - gy)
            ghost_mask = np.clip(1.0 - (g_dist / gr), 0.0, 1.0) ** 2.0
            g_color = np.array([self.color.g, self.color.b, self.color.r], dtype=np.float32) * (50.0 / g)
            flare_acc += ghost_mask[:, :, np.newaxis] * g_color

        out[:, :, :3] = np.clip(rgb + flare_acc * self.intensity, 0, 255).astype(np.uint8)
        return out


class GodRays:
    """
    Volumetric radial light shafts (Crepuscular Rays) radiating from a light source.
    """

    def __init__(
        self,
        light_pos: Tuple[float, float] = (0.5, 0.1),
        decay: float = 0.95,
        density: float = 0.8,
        weight: float = 0.5,
        exposure: float = 0.3,
        samples: int = 32,
    ) -> None:
        self.light_pos = light_pos
        self.decay = max(0.5, min(0.99, float(decay)))
        self.density = max(0.1, min(1.0, float(density)))
        self.weight = max(0.05, min(1.0, float(weight)))
        self.exposure = max(0.01, min(1.0, float(exposure)))
        self.samples = max(8, min(64, int(samples)))

    def apply(self, rgba: np.ndarray, time: float = 0.0) -> np.ndarray:
        h, w, _ = rgba.shape
        lx = self.light_pos[0] * w
        ly = self.light_pos[1] * h

        # Downsample for volumetric blur pass
        scale = 0.25
        dw, dh = max(1, int(w * scale)), max(1, int(h * scale))
        pil_img = Image.fromarray(rgba[:, :, :3])
        small = pil_img.resize((dw, dh), Image.Resampling.BILINEAR)
        small_arr = np.array(small, dtype=np.float32) / 255.0

        # Radial ray marching
        accum = np.zeros_like(small_arr)
        cur_decay = 1.0
        dlx, dly = lx * scale, ly * scale

        for i in range(self.samples):
            step = float(i) / float(self.samples) * self.density
            # Affine scale towards light source
            t_scale = 1.0 - step * 0.5
            mat = (
                t_scale, 0, dlx * (1.0 - t_scale),
                0, t_scale, dly * (1.0 - t_scale)
            )
            sampled = small.transform((dw, dh), Image.Transform.AFFINE, mat, Image.Resampling.BILINEAR)
            accum += (np.array(sampled, dtype=np.float32) / 255.0) * cur_decay * self.weight
            cur_decay *= self.decay

        accum *= self.exposure
        # Upscale rays and screen blend
        rays_img = Image.fromarray(np.clip(accum * 255.0, 0, 255).astype(np.uint8)).resize((w, h), Image.Resampling.BILINEAR)
        rays_arr = np.array(rays_img, dtype=np.float32) / 255.0

        rgb = rgba[:, :, :3].astype(np.float32) / 255.0
        screened = 1.0 - (1.0 - rgb) * (1.0 - np.clip(rays_arr, 0.0, 1.0))

        out = rgba.copy()
        out[:, :, :3] = (np.clip(screened, 0.0, 1.0) * 255.0).astype(np.uint8)
        return out


class ThermalVision:
    """
    FLIR / Infrared thermal camera false color mapping.
    Maps image luminance to high-tech thermal color gradients (ironbow / rainbow).
    """

    def __init__(
        self,
        palette: Union[str, ThermalPalette] = ThermalPalette.IRONBOW,
        contrast: float = 1.2,
        gain: float = 1.0,
    ) -> None:
        self.palette = ThermalPalette(palette) if isinstance(palette, str) else palette
        self.contrast = float(contrast)
        self.gain = float(gain)

    def apply(self, rgba: np.ndarray, time: float = 0.0) -> np.ndarray:
        h, w, _ = rgba.shape
        rgb = rgba[:, :, :3].astype(np.float32) / 255.0

        luma = (0.299 * rgb[:, :, 0] + 0.587 * rgb[:, :, 1] + 0.114 * rgb[:, :, 2])
        luma = np.clip((luma - 0.5) * self.contrast + 0.5, 0.0, 1.0) * self.gain
        luma = np.clip(luma, 0.0, 1.0)

        out_rgb = np.zeros((h, w, 3), dtype=np.float32)

        if self.palette == ThermalPalette.IRONBOW:
            # Black -> Deep Purple -> Red -> Orange -> Yellow -> White
            out_rgb[:, :, 0] = np.clip(np.sin(luma * math.pi * 0.8) * 1.3, 0.0, 1.0)
            out_rgb[:, :, 1] = np.clip((luma - 0.35) * 1.6, 0.0, 1.0)
            out_rgb[:, :, 2] = np.clip(np.sin((1.0 - luma) * math.pi) * 0.7 + (luma > 0.8) * (luma - 0.8) * 5.0, 0.0, 1.0)
        elif self.palette == ThermalPalette.CYBERPUNK:
            out_rgb[:, :, 0] = np.clip(luma * 1.5, 0.0, 1.0)
            out_rgb[:, :, 1] = np.clip(np.sin(luma * math.pi) * 0.9, 0.0, 1.0)
            out_rgb[:, :, 2] = np.clip(1.0 - luma * 0.8, 0.0, 1.0)
        else:  # Rainbow
            out_rgb[:, :, 0] = np.clip(np.sin(luma * math.pi * 1.5 - 0.5) * 1.2, 0.0, 1.0)
            out_rgb[:, :, 1] = np.clip(np.sin(luma * math.pi * 1.5 - 1.5) * 1.2, 0.0, 1.0)
            out_rgb[:, :, 2] = np.clip(np.sin(luma * math.pi * 1.5 - 2.5) * 1.2, 0.0, 1.0)

        out = rgba.copy()
        out[:, :, :3] = (out_rgb * 255.0).astype(np.uint8)
        return out


# Convenience functions
def light_leak(intensity: float = 0.6, **kwargs: Any) -> LightLeak:
    return LightLeak(intensity=intensity, **kwargs)


def shine(progress: float = 0.0, angle: float = 35.0, **kwargs: Any) -> Shine:
    return Shine(progress=progress, angle=angle, **kwargs)


def lens_flare(position: Tuple[float, float] = (0.3, 0.3), intensity: float = 1.0, **kwargs: Any) -> LensFlare:
    return LensFlare(position=position, intensity=intensity, **kwargs)


def god_rays(light_pos: Tuple[float, float] = (0.5, 0.1), **kwargs: Any) -> GodRays:
    return GodRays(light_pos=light_pos, **kwargs)


def thermal_vision(palette: Union[str, ThermalPalette] = ThermalPalette.IRONBOW, **kwargs: Any) -> ThermalVision:
    return ThermalVision(palette=palette, **kwargs)
