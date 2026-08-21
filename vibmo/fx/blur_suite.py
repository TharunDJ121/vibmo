"""
Comprehensive Blur Effects Suite inspired by Remotion's blur & defocus filters.
Includes LinearProgressiveBlur, RadialProgressiveBlur, RegionBlur, ZoomBlur, and MotionBlur.
"""

from __future__ import annotations
import math
import numpy as np
from PIL import Image, ImageFilter
from typing import Any, Optional, Tuple, Union, List
from enum import Enum
from dataclasses import dataclass

from vibmo.core.color import Color, colors


class BlurQuality(Enum):
    FAST = "fast"
    BALANCED = "balanced"
    HIGH = "high"


class LinearProgressiveBlur:
    """
    Linear progressive gradient blur along an arbitrary angle.
    Blurs the frame with a smooth variable blur radius ramp.
    """

    def __init__(
        self,
        angle: float = 90.0,  # 90 degrees = top to bottom
        start_blur: float = 0.0,
        end_blur: float = 24.0,
        start_pos: float = 0.2,  # Normalized 0-1
        end_pos: float = 0.8,
        steps: int = 5,
    ) -> None:
        self.angle = float(angle)
        self.start_blur = max(0.0, float(start_blur))
        self.end_blur = max(0.0, float(end_blur))
        self.start_pos = float(start_pos)
        self.end_pos = float(end_pos)
        self.steps = max(2, min(10, int(steps)))

    def apply(self, rgba: np.ndarray, time: float = 0.0) -> np.ndarray:
        if self.end_blur <= 0.1 and self.start_blur <= 0.1:
            return rgba

        h, w, _ = rgba.shape
        rad = math.radians(self.angle)
        cos_a, sin_a = math.cos(rad), math.sin(rad)

        y, x = np.ogrid[:h, :w]
        proj = (x * cos_a + y * sin_a)
        min_p = min(0, w * cos_a, h * sin_a, w * cos_a + h * sin_a)
        max_p = max(0, w * cos_a, h * sin_a, w * cos_a + h * sin_a)
        total_span = max(1.0, max_p - min_p)

        norm_pos = (proj - min_p) / total_span
        # Calculate blur weight per pixel
        t = np.clip((norm_pos - self.start_pos) / max(1e-4, self.end_pos - self.start_pos), 0.0, 1.0)

        # Multi-step blur blending
        pil_img = Image.fromarray(rgba)
        out = rgba.copy().astype(np.float32)

        # Base and blurred layers
        blurred_layers = []
        blur_radii = np.linspace(self.start_blur, self.end_blur, self.steps)
        for r in blur_radii:
            r_val = float(r)
            if r_val > 0.1:
                blurred = pil_img.filter(ImageFilter.GaussianBlur(radius=r_val))
                blurred_layers.append((r_val, np.array(blurred, dtype=np.float32)))
            else:
                blurred_layers.append((r_val, rgba.astype(np.float32)))

        # Weighted blend across steps
        final_accum = np.zeros_like(out)
        target_blur = self.start_blur + t * (self.end_blur - self.start_blur)

        for i in range(len(blurred_layers) - 1):
            r0, l0 = blurred_layers[i]
            r1, l1 = blurred_layers[i + 1]
            step_t = np.clip((target_blur - r0) / max(1e-4, r1 - r0), 0.0, 1.0)[:, :, np.newaxis]
            active_mask = ((target_blur >= r0) & (target_blur <= r1))[:, :, np.newaxis]
            interpolated = l0 * (1.0 - step_t) + l1 * step_t
            final_accum += interpolated * active_mask

        # Catch bounds
        min_mask = (target_blur < blur_radii[0])[:, :, np.newaxis]
        max_mask = (target_blur > blur_radii[-1])[:, :, np.newaxis]
        final_accum += blurred_layers[0][1] * min_mask
        final_accum += blurred_layers[-1][1] * max_mask

        return np.clip(final_accum, 0, 255).astype(np.uint8)


class RadialProgressiveBlur:
    """
    Center-out or edge-in circular progressive blur (Defocus / Lens falloff).
    """

    def __init__(
        self,
        center: Tuple[float, float] = (0.5, 0.5),
        inner_radius: float = 0.25,
        outer_radius: float = 0.75,
        max_blur: float = 24.0,
        invert: bool = False,
    ) -> None:
        self.center = center
        self.inner_radius = float(inner_radius)
        self.outer_radius = float(outer_radius)
        self.max_blur = max(0.0, float(max_blur))
        self.invert = invert

    def apply(self, rgba: np.ndarray, time: float = 0.0) -> np.ndarray:
        if self.max_blur <= 0.1:
            return rgba

        h, w, _ = rgba.shape
        cx = int(self.center[0] * w)
        cy = int(self.center[1] * h)
        diag = math.hypot(w, h)

        y, x = np.ogrid[:h, :w]
        dist = np.hypot(x - cx, y - cy) / diag

        r_in = self.inner_radius
        r_out = self.outer_radius
        blur_factor = np.clip((dist - r_in) / max(1e-4, r_out - r_in), 0.0, 1.0)
        if self.invert:
            blur_factor = 1.0 - blur_factor

        pil_img = Image.fromarray(rgba)
        blurred = np.array(pil_img.filter(ImageFilter.GaussianBlur(radius=self.max_blur)), dtype=np.float32)
        base = rgba.astype(np.float32)

        mask = blur_factor[:, :, np.newaxis]
        out = base * (1.0 - mask) + blurred * mask
        return np.clip(out, 0, 255).astype(np.uint8)


class RegionBlur:
    """
    Selective blur on a rectangular or elliptical bounding box with soft feathering.
    Useful for anonymizing UI areas or focusing depth of field.
    """

    def __init__(
        self,
        bounds: Tuple[float, float, float, float] = (0.2, 0.2, 0.6, 0.6),  # (x, y, w, h)
        radius: float = 18.0,
        feather: float = 20.0,
        shape: str = "rect",  # "rect" or "ellipse"
        blur_inside: bool = True,
    ) -> None:
        self.bounds = bounds
        self.radius = max(0.1, float(radius))
        self.feather = max(0.0, float(feather))
        self.shape = shape
        self.blur_inside = blur_inside

    def apply(self, rgba: np.ndarray, time: float = 0.0) -> np.ndarray:
        h, w, _ = rgba.shape
        bx, by, bw, bh = self.bounds
        px, py, pw, ph = int(bx * w), int(by * h), int(bw * w), int(bh * h)

        y, x = np.ogrid[:h, :w]
        if self.shape == "ellipse":
            cx, cy = px + pw // 2, py + ph // 2
            rx, ry = max(1, pw // 2), max(1, ph // 2)
            dist = np.hypot((x - cx) / rx, (y - cy) / ry)
            mask = np.clip((1.0 - dist) * (min(rx, ry) / max(1.0, self.feather)), 0.0, 1.0)
        else:
            dx = np.maximum(0, np.maximum(px - x, x - (px + pw)))
            dy = np.maximum(0, np.maximum(py - y, y - (py + ph)))
            dist = np.hypot(dx, dy)
            inside = (x >= px) & (x <= px + pw) & (y >= py) & (y <= py + ph)
            dist_inside = np.minimum(np.minimum(x - px, px + pw - x), np.minimum(y - py, py + ph - y))
            mask = np.where(inside, np.clip(dist_inside / max(1.0, self.feather), 0.0, 1.0), 0.0)

        if not self.blur_inside:
            mask = 1.0 - mask

        pil_img = Image.fromarray(rgba)
        blurred = np.array(pil_img.filter(ImageFilter.GaussianBlur(radius=self.radius)), dtype=np.float32)
        base = rgba.astype(np.float32)

        m = mask[:, :, np.newaxis]
        out = base * (1.0 - m) + blurred * m
        return np.clip(out, 0, 255).astype(np.uint8)


class ZoomBlur:
    """
    Explosive radial zoom blur radiating from a center point.
    """

    def __init__(
        self,
        center: Tuple[float, float] = (0.5, 0.5),
        strength: float = 0.3,
        samples: int = 16,
    ) -> None:
        self.center = center
        self.strength = max(0.0, min(1.0, float(strength)))
        self.samples = max(4, min(32, int(samples)))

    def apply(self, rgba: np.ndarray, time: float = 0.0) -> np.ndarray:
        if self.strength <= 1e-4:
            return rgba

        h, w, _ = rgba.shape
        cx = self.center[0] * w
        cy = self.center[1] * h

        pil_img = Image.fromarray(rgba)
        accum = np.zeros((h, w, rgba.shape[2]), dtype=np.float32)

        for i in range(self.samples):
            scale = 1.0 + (float(i) / max(1, self.samples - 1)) * self.strength
            mat = (
                scale, 0, cx * (1.0 - scale),
                0, scale, cy * (1.0 - scale)
            )
            transformed = pil_img.transform((w, h), Image.Transform.AFFINE, mat, Image.Resampling.BILINEAR)
            accum += np.array(transformed, dtype=np.float32)

        accum /= float(self.samples)
        return np.clip(accum, 0, 255).astype(np.uint8)


class MotionBlur:
    """
    Directional linear velocity motion blur along an angle.
    """

    def __init__(
        self,
        angle: float = 0.0,  # Degrees
        distance: float = 20.0,
        samples: int = 12,
    ) -> None:
        self.angle = float(angle)
        self.distance = max(0.0, float(distance))
        self.samples = max(2, min(32, int(samples)))

    def apply(self, rgba: np.ndarray, time: float = 0.0) -> np.ndarray:
        if self.distance <= 0.5:
            return rgba

        h, w, _ = rgba.shape
        rad = math.radians(self.angle)
        dx = math.cos(rad) * self.distance
        dy = math.sin(rad) * self.distance

        pil_img = Image.fromarray(rgba)
        accum = np.zeros((h, w, rgba.shape[2]), dtype=np.float32)

        offsets = np.linspace(-0.5, 0.5, self.samples)
        for off in offsets:
            mat = (1, 0, dx * off, 0, 1, dy * off)
            sampled = pil_img.transform((w, h), Image.Transform.AFFINE, mat, Image.Resampling.BILINEAR)
            accum += np.array(sampled, dtype=np.float32)

        accum /= float(self.samples)
        return np.clip(accum, 0, 255).astype(np.uint8)


# Convenience functions
def linear_progressive_blur(angle: float = 90.0, start_blur: float = 0.0, end_blur: float = 24.0, **kwargs: Any) -> LinearProgressiveBlur:
    return LinearProgressiveBlur(angle=angle, start_blur=start_blur, end_blur=end_blur, **kwargs)


def radial_progressive_blur(center: Tuple[float, float] = (0.5, 0.5), max_blur: float = 24.0, **kwargs: Any) -> RadialProgressiveBlur:
    return RadialProgressiveBlur(center=center, max_blur=max_blur, **kwargs)


def region_blur(bounds: Tuple[float, float, float, float] = (0.2, 0.2, 0.6, 0.6), radius: float = 18.0, **kwargs: Any) -> RegionBlur:
    return RegionBlur(bounds=bounds, radius=radius, **kwargs)


def zoom_blur(center: Tuple[float, float] = (0.5, 0.5), strength: float = 0.3, **kwargs: Any) -> ZoomBlur:
    return ZoomBlur(center=center, strength=strength, **kwargs)


def motion_blur(angle: float = 0.0, distance: float = 20.0, **kwargs: Any) -> MotionBlur:
    return MotionBlur(angle=angle, distance=distance, **kwargs)
