"""
✦ Vibmo Transitions: Remocn-Inspired Cinematic Scene Transitions
Includes Push-Through, Focus-Pull, Whip-Pan, Ascii-Dissolve, and Dither-Dissolve.
"""

from __future__ import annotations

import math
import numpy as np
from PIL import Image, ImageFilter
from typing import Any, Optional, Tuple, Union

from vibmo.core.color import Color, colors
from vibmo.core.easing import Ease
from vibmo.composition.sequence import Transition


class PushThroughTransition(Transition):
    """
    Forward camera plunge transition pushing into the scene plane with radial blur pass-through.
    """
    def __init__(self, max_scale: float = 3.0, blur: bool = True, duration: float = 0.55) -> None:
        super().__init__(duration=duration)
        self.max_scale = max_scale
        self.blur = blur

    def blend(self, img_a: np.ndarray, img_b: np.ndarray, progress: float) -> np.ndarray:
        p = max(0.0, min(1.0, float(progress)))
        h, w, _ = img_a.shape

        if p < 0.5:
            # Scale up A dramatically and fade opacity
            norm_p = p * 2.0
            scale = 1.0 + (self.max_scale - 1.0) * Ease.in_expo(norm_p)
            alpha_a = 1.0 - norm_p

            pil_a = Image.fromarray(img_a, "RGBA")
            nw, nh = max(1, int(w * scale)), max(1, int(h * scale))
            zoomed = pil_a.resize((nw, nh), Image.Resampling.BILINEAR)
            x0 = (nw - w) // 2
            y0 = (nh - h) // 2
            cropped = np.array(zoomed.crop((x0, y0, x0 + w, y0 + h)), dtype=np.float32)

            if self.blur and norm_p > 0.3:
                blur_r = int(norm_p * 14.0)
                if blur_r > 1:
                    pil_blur = Image.fromarray(cropped.astype(np.uint8)).filter(ImageFilter.BoxBlur(blur_r))
                    cropped = np.array(pil_blur, dtype=np.float32)

            cropped[:, :, 3] *= alpha_a
            return np.clip(cropped, 0, 255).astype(np.uint8)
        else:
            # Scale down B from slight zoom (1.3 -> 1.0) with ease-out
            norm_p = (p - 0.5) * 2.0
            scale = 1.3 - 0.3 * Ease.out_expo(norm_p)
            alpha_b = norm_p

            pil_b = Image.fromarray(img_b, "RGBA")
            nw, nh = max(1, int(w * scale)), max(1, int(h * scale))
            zoomed = pil_b.resize((nw, nh), Image.Resampling.BILINEAR)
            x0 = (nw - w) // 2
            y0 = (nh - h) // 2
            cropped = np.array(zoomed.crop((x0, y0, x0 + w, y0 + h)), dtype=np.float32)

            cropped[:, :, 3] *= alpha_b
            return np.clip(cropped, 0, 255).astype(np.uint8)


class FocusPullTransition(Transition):
    """
    Cinematic rack-focus depth transition where outgoing scene blurs out while incoming scene resolves.
    """
    def __init__(self, max_blur: float = 24.0, duration: float = 0.6) -> None:
        super().__init__(duration=duration)
        self.max_blur = max_blur

    def blend(self, img_a: np.ndarray, img_b: np.ndarray, progress: float) -> np.ndarray:
        p = max(0.0, min(1.0, float(progress)))

        blur_a = int(math.sin(min(p, 0.5) * math.pi) * self.max_blur)
        blur_b = int(math.sin(max(0.0, 1.0 - p) * math.pi) * self.max_blur)

        pil_a = Image.fromarray(img_a, "RGBA")
        if blur_a > 1:
            pil_a = pil_a.filter(ImageFilter.BoxBlur(blur_a))

        pil_b = Image.fromarray(img_b, "RGBA")
        if blur_b > 1:
            pil_b = pil_b.filter(ImageFilter.BoxBlur(blur_b))

        arr_a = np.array(pil_a, dtype=np.float32)
        arr_b = np.array(pil_b, dtype=np.float32)

        crossfade = Ease.in_out_cubic(p)
        out = arr_a * (1.0 - crossfade) + arr_b * crossfade
        return np.clip(out, 0, 255).astype(np.uint8)


class WhipPanTransition(Transition):
    """
    High-velocity directional streak camera whip pan with chromatic displacement.
    """
    def __init__(self, direction: str = "right", blur: bool = True, duration: float = 0.4) -> None:
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
        else:
            if shift < w:
                out[:, : w - shift] = img_a[:, shift:]
            if shift > 0:
                out[:, w - shift :] = img_b[:, :shift]

        if self.blur and 0.15 < p < 0.85:
            blur_r = int(math.sin(p * math.pi) * 16.0)
            if blur_r > 1:
                pil_img = Image.fromarray(out, "RGBA").filter(ImageFilter.BoxBlur(blur_r))
                out = np.array(pil_img)

        return out


class DitherDissolveTransition(Transition):
    """
    Retro 1-bit / 8-bit Bayer matrix dither dissolve between two scenes.
    """
    def __init__(self, block_size: int = 8, duration: float = 0.5) -> None:
        super().__init__(duration=duration)
        self.block_size = block_size

    def blend(self, img_a: np.ndarray, img_b: np.ndarray, progress: float) -> np.ndarray:
        p = max(0.0, min(1.0, float(progress)))
        h, w, _ = img_a.shape

        # 4x4 Bayer Dither Matrix threshold
        bayer = np.array([
            [ 0,  8,  2, 10],
            [12,  4, 14,  6],
            [ 3, 11,  1,  9],
            [15,  7, 13,  5]
        ], dtype=np.float32) / 16.0

        tiled = np.tile(bayer, (h // 4 + 1, w // 4 + 1))[:h, :w]
        mask = (tiled < p)[:, :, None]

        out = np.where(mask, img_b, img_a)
        return out
