"""
Cinematic NLE Scene Transitions Suite.
Includes Whip Pan, Zoom Punch, Glitch, Light Leak, Film Burn, Shape Wipe, and Dip-to-Color.
"""

from __future__ import annotations
import math
import numpy as np
from PIL import Image, ImageFilter
from typing import Any, Optional, Tuple, Union

from vibmo.core.color import Color, colors
from vibmo.core.easing import Ease, EasingFunc
from vibmo.composition.sequence import Transition


class CrossDissolve(Transition):
    """Smooth cross-dissolve opacity blend between two scenes."""

    def blend(self, img_a: np.ndarray, img_b: np.ndarray, progress: float) -> np.ndarray:
        p = max(0.0, min(1.0, float(progress)))
        return (img_a.astype(np.float32) * (1.0 - p) + img_b.astype(np.float32) * p).astype(np.uint8)


class WhipPan(Transition):
    """High-speed kinetic camera whip pan with dynamic motion blur."""

    def __init__(self, direction: str = "right", blur: bool = True, duration: float = 0.45) -> None:
        super().__init__(duration=duration)
        self.direction = direction.lower()
        self.blur = blur

    def blend(self, img_a: np.ndarray, img_b: np.ndarray, progress: float) -> np.ndarray:
        p = Ease.in_out_cubic(max(0.0, min(1.0, float(progress))))
        h, w, _ = img_a.shape
        out = np.zeros_like(img_a)

        shift = int(w * p)
        if self.direction == "right":
            if shift < w:
                out[:, shift:] = img_a[:, : w - shift]
            if shift > 0:
                out[:, :shift] = img_b[:, w - shift :]
        else:  # left
            if shift < w:
                out[:, : w - shift] = img_a[:, shift:]
            if shift > 0:
                out[:, w - shift :] = img_b[:, :shift]

        # Apply directional blur during mid-transition peak velocity
        if self.blur and 0.15 < p < 0.85:
            blur_radius = int(math.sin(p * math.pi) * 12.0)
            if blur_radius > 1:
                pil_img = Image.fromarray(out, "RGBA").filter(ImageFilter.BoxBlur(blur_radius))
                out = np.array(pil_img)

        return out


class ZoomPunch(Transition):
    """Fast optical crash-zoom in and out pushing into scene B."""

    def __init__(self, max_scale: float = 2.2, duration: float = 0.4) -> None:
        super().__init__(duration=duration)
        self.max_scale = max_scale

    def blend(self, img_a: np.ndarray, img_b: np.ndarray, progress: float) -> np.ndarray:
        p = max(0.0, min(1.0, float(progress)))
        h, w, _ = img_a.shape

        if p < 0.5:
            # Zoom in A
            scale = 1.0 + (self.max_scale - 1.0) * Ease.in_expo(p * 2.0)
            pil_a = Image.fromarray(img_a, "RGBA")
            nw, nh = int(w * scale), int(h * scale)
            zoomed = pil_a.resize((nw, nh), Image.Resampling.BILINEAR)
            x0 = (nw - w) // 2
            y0 = (nh - h) // 2
            return np.array(zoomed.crop((x0, y0, x0 + w, y0 + h)))
        else:
            # Zoom out B
            scale = self.max_scale - (self.max_scale - 1.0) * Ease.out_expo((p - 0.5) * 2.0)
            pil_b = Image.fromarray(img_b, "RGBA")
            nw, nh = int(w * scale), int(h * scale)
            zoomed = pil_b.resize((nw, nh), Image.Resampling.BILINEAR)
            x0 = (nw - w) // 2
            y0 = (nh - h) // 2
            return np.array(zoomed.crop((x0, y0, x0 + w, y0 + h)))


class GlitchTransition(Transition):
    """Digital glitch displacement with chromatic aberration slicing."""

    def __init__(self, slices: int = 14, duration: float = 0.35) -> None:
        super().__init__(duration=duration)
        self.slices = slices

    def blend(self, img_a: np.ndarray, img_b: np.ndarray, progress: float) -> np.ndarray:
        p = max(0.0, min(1.0, float(progress)))
        h, w, _ = img_a.shape
        out = img_b.copy() if p >= 0.5 else img_a.copy()

        # Random horizontal slice shifts
        slice_h = max(4, h // self.slices)
        for i in range(self.slices):
            if (i * 7 + int(p * 100)) % 3 == 0:
                y0 = i * slice_h
                y1 = min(h, y0 + slice_h)
                shift = int(math.sin(i * 1.5 + p * 10) * 35.0)
                out[y0:y1] = np.roll(out[y0:y1], shift, axis=1)

        # Cross-fade alpha
        return (img_a.astype(np.float32) * (1.0 - p) + out.astype(np.float32) * p).astype(np.uint8)


class LightLeak(Transition):
    """Warm anamorphic optical light flare wash."""

    def __init__(self, color: Union[Color, str] = Color.hex("#ff9933"), duration: float = 0.5) -> None:
        super().__init__(duration=duration)
        self.color = Color.from_any(color) if isinstance(color, (str, Color)) else Color.hex("#ff9933")

    def blend(self, img_a: np.ndarray, img_b: np.ndarray, progress: float) -> np.ndarray:
        p = max(0.0, min(1.0, float(progress)))
        h, w, _ = img_a.shape

        # Base crossfade
        base = (img_a.astype(np.float32) * (1.0 - p) + img_b.astype(np.float32) * p)

        # Light flare intensity peaking at center
        flare_int = math.sin(p * math.pi) * 1.2
        flare = np.zeros((h, w, 3), dtype=np.float32)
        flare[:, :, 0] = self.color.r * 255.0 * flare_int
        flare[:, :, 1] = self.color.g * 255.0 * flare_int
        flare[:, :, 2] = self.color.b * 255.0 * flare_int

        base[:, :, :3] = np.clip(base[:, :, :3] + flare, 0.0, 255.0)
        return base.astype(np.uint8)


class ShapeWipe(Transition):
    """Radial circular or diamond geometric iris wipe."""

    def __init__(self, shape: str = "circle", duration: float = 0.5) -> None:
        super().__init__(duration=duration)
        self.shape = shape.lower()

    def blend(self, img_a: np.ndarray, img_b: np.ndarray, progress: float) -> np.ndarray:
        p = Ease.in_out_cubic(max(0.0, min(1.0, float(progress))))
        h, w, _ = img_a.shape

        y, x = np.ogrid[:h, :w]
        cx, cy = w * 0.5, h * 0.5

        if self.shape == "circle":
            max_r = math.hypot(cx, cy)
            r = np.sqrt((x - cx) ** 2 + (y - cy) ** 2)
            mask = (r <= max_r * p)
        else:  # diamond
            max_d = cx + cy
            d = np.abs(x - cx) + np.abs(y - cy)
            mask = (d <= max_d * p)

        out = img_a.copy()
        out[mask] = img_b[mask]
        return out


class DipToColor(Transition):
    """Fades out to solid color (black, white) and fades up into scene B."""

    def __init__(self, color: Union[Color, str] = colors.BLACK, duration: float = 0.5) -> None:
        super().__init__(duration=duration)
        self.color = Color.from_any(color) if isinstance(color, (str, Color)) else colors.BLACK

    def blend(self, img_a: np.ndarray, img_b: np.ndarray, progress: float) -> np.ndarray:
        p = max(0.0, min(1.0, float(progress)))
        h, w, _ = img_a.shape
        c_arr = np.zeros_like(img_a)
        c_arr[:, :, 0] = int(self.color.r * 255)
        c_arr[:, :, 1] = int(self.color.g * 255)
        c_arr[:, :, 2] = int(self.color.b * 255)
        c_arr[:, :, 3] = 255

        if p < 0.5:
            fade = p * 2.0
            return (img_a.astype(np.float32) * (1.0 - fade) + c_arr.astype(np.float32) * fade).astype(np.uint8)
        else:
            fade = (p - 0.5) * 2.0
            return (c_arr.astype(np.float32) * (1.0 - fade) + img_b.astype(np.float32) * fade).astype(np.uint8)
