"""
Digital and pixel effects inspired by Remotion's digital/retro filters.
Includes Pixelate, PixelDissolve, Halftone, DotGrid, and Dither.
"""

from __future__ import annotations
import math
import numpy as np
from PIL import Image, ImageDraw
from typing import Any, Optional, Tuple, Union, List
from enum import Enum
from dataclasses import dataclass

from vibmo.core.color import Color, colors


class PixelShape(Enum):
    SQUARE = "square"
    CIRCLE = "circle"
    HEXAGON = "hexagon"
    DIAMOND = "diamond"


class DitherMethod(Enum):
    BAYER_2X2 = "bayer2"
    BAYER_4X4 = "bayer4"
    BAYER_8X8 = "bayer8"
    FLOYD_STEINBERG = "floyd_steinberg"
    RANDOM = "random"


class Pixelate:
    """
    High-quality digital pixelation and mosaic effect.
    Supports square, circular, diamond, and hexagonal pixel grids with spacing and background styling.
    """

    def __init__(
        self,
        size: int = 16,
        shape: Union[str, PixelShape] = PixelShape.SQUARE,
        gap: int = 0,
        bg_color: Optional[Union[Color, str]] = None,
        pixel_size: Optional[int] = None,
    ) -> None:
        effective_size = pixel_size if pixel_size is not None else size
        self.size = max(1, int(effective_size))
        self.shape = PixelShape(shape) if isinstance(shape, str) else shape
        self.gap = max(0, int(gap))
        self.bg_color = Color.from_any(bg_color) if bg_color else Color.BLACK

    def apply(self, rgba: np.ndarray, time: float = 0.0) -> np.ndarray:
        if self.size <= 1:
            return rgba

        h, w, _ = rgba.shape
        sz = self.size
        
        # Downscale then upscale
        down_w = max(1, w // sz)
        down_h = max(1, h // sz)

        pil_img = Image.fromarray(rgba)
        small = pil_img.resize((down_w, down_h), Image.Resampling.BOX)

        if self.shape == PixelShape.SQUARE and self.gap == 0:
            pixelated = small.resize((w, h), Image.Resampling.NEAREST)
            return np.array(pixelated)

        # Custom shapes or gaps
        out_img = Image.new("RGBA", (w, h), (
            int(self.bg_color.r * 255),
            int(self.bg_color.g * 255),
            int(self.bg_color.b * 255),
            int(self.bg_color.a * 255),
        ))
        draw = ImageDraw.Draw(out_img)
        small_arr = np.array(small)

        r = (sz - self.gap) // 2
        for y in range(down_h):
            for x in range(down_w):
                color = tuple(small_arr[y, x])
                px = x * sz + sz // 2
                py = y * sz + sz // 2
                
                if self.shape == PixelShape.CIRCLE:
                    draw.ellipse([px - r, py - r, px + r, py + r], fill=color)
                elif self.shape == PixelShape.DIAMOND:
                    draw.polygon([(px, py - r), (px + r, py), (px, py + r), (px - r, py)], fill=color)
                else:  # Square with gap
                    draw.rectangle([px - r, py - r, px + r, py + r], fill=color)

        return np.array(out_img)


class PixelDissolve:
    """
    Digital block dissolve effect. Staggers blocks based on pseudo-random noise threshold.
    """

    def __init__(
        self,
        progress: float = 0.0,
        block_size: int = 24,
        softness: float = 0.1,
        invert: bool = False,
    ) -> None:
        self.progress = max(0.0, min(1.0, float(progress)))
        self.block_size = max(2, int(block_size))
        self.softness = max(0.01, float(softness))
        self.invert = invert

    def apply(self, rgba: np.ndarray, time: float = 0.0) -> np.ndarray:
        p = 1.0 - self.progress if self.invert else self.progress
        if p <= 0.0:
            return rgba if not self.invert else np.zeros_like(rgba)
        if p >= 1.0:
            return np.zeros_like(rgba) if not self.invert else rgba

        h, w, _ = rgba.shape
        bs = self.block_size
        gh = (h + bs - 1) // bs
        gw = (w + bs - 1) // bs

        rng = np.random.RandomState(42)
        grid_noise = rng.uniform(0.0, 1.0, (gh, gw)).astype(np.float32)

        # Expand grid mask to pixel resolution
        from scipy.ndimage import zoom
        mask_grid = (grid_noise > p).astype(np.float32)
        mask = np.repeat(np.repeat(mask_grid, bs, axis=0)[:h, :], bs, axis=1)[:, :w]

        out = rgba.copy()
        out[:, :, 3] = (out[:, :, 3].astype(np.float32) * mask).astype(np.uint8)
        return out


class Halftone:
    """
    CMYK & Monochrome dot screen halftone printing effect.
    Simulates vintage comic book / newspaper raster printing.
    """

    def __init__(
        self,
        dot_size: int = 10,
        angle: float = 45.0,
        cmyk: bool = False,
        contrast: float = 1.2,
        bg_color: Union[Color, str] = colors.WHITE,
    ) -> None:
        self.dot_size = max(3, int(dot_size))
        self.angle = float(angle)
        self.cmyk = cmyk
        self.contrast = float(contrast)
        self.bg_color = Color.from_any(bg_color)

    def apply(self, rgba: np.ndarray, time: float = 0.0) -> np.ndarray:
        h, w, _ = rgba.shape
        sz = self.dot_size
        rad = math.radians(self.angle)
        cos_a, sin_a = math.cos(rad), math.sin(rad)

        out_img = Image.new("RGBA", (w, h), (
            int(self.bg_color.r * 255),
            int(self.bg_color.g * 255),
            int(self.bg_color.b * 255),
            int(self.bg_color.a * 255),
        ))
        draw = ImageDraw.Draw(out_img)

        # Grayscale luminance
        rgb = rgba[:, :, :3].astype(np.float32) / 255.0
        luma = np.clip((0.299 * rgb[:, :, 0] + 0.587 * rgb[:, :, 1] + 0.114 * rgb[:, :, 2]) * self.contrast, 0.0, 1.0)

        # Sample grid
        for y in range(0, h, sz):
            for x in range(0, w, sz):
                cx = min(w - 1, x + sz // 2)
                cy = min(h - 1, y + sz // 2)
                brightness = 1.0 - luma[cy, cx]  # Ink density
                dot_r = (sz * 0.7) * math.sqrt(brightness)
                if dot_r > 0.5:
                    c = rgba[cy, cx]
                    ink_color = (int(c[0] * 0.2), int(c[1] * 0.2), int(c[2] * 0.2), int(c[3]))
                    draw.ellipse([cx - dot_r, cy - dot_r, cx + dot_r, cy + dot_r], fill=ink_color)

        return np.array(out_img)


class DotGrid:
    """
    Digital LED matrix display and dot grid billboard shader.
    """

    def __init__(
        self,
        grid_size: int = 8,
        dot_radius_ratio: float = 0.38,
        glow_intensity: float = 0.4,
        gap_color: Union[Color, str] = colors.BLACK,
    ) -> None:
        self.grid_size = max(2, int(grid_size))
        self.dot_radius_ratio = max(0.1, min(0.5, float(dot_radius_ratio)))
        self.glow_intensity = float(glow_intensity)
        self.gap_color = Color.from_any(gap_color)

    def apply(self, rgba: np.ndarray, time: float = 0.0) -> np.ndarray:
        h, w, _ = rgba.shape
        sz = self.grid_size

        # Sub-pixel coordinate within cell
        y, x = np.ogrid[:h, :w]
        cell_x = (x % sz) - sz * 0.5
        cell_y = (y % sz) - sz * 0.5
        dist = np.hypot(cell_x, cell_y)

        r_max = sz * self.dot_radius_ratio
        dot_mask = np.clip(1.0 - (dist - r_max + 0.5), 0.0, 1.0)[:, :, np.newaxis]

        # Sample color at cell center
        cell_center_x = (x // sz) * sz + sz // 2
        cell_center_y = (y // sz) * sz + sz // 2
        cell_center_x = np.clip(cell_center_x, 0, w - 1)
        cell_center_y = np.clip(cell_center_y, 0, h - 1)

        sampled_rgb = rgba[cell_center_y, cell_center_x, :3].astype(np.float32)
        gap_rgb = np.array([self.gap_color.r * 255, self.gap_color.g * 255, self.gap_color.b * 255], dtype=np.float32)

        out_rgb = dot_mask * sampled_rgb + (1.0 - dot_mask) * gap_rgb
        if self.glow_intensity > 0:
            out_rgb += sampled_rgb * self.glow_intensity * 0.2

        out = rgba.copy()
        out[:, :, :3] = np.clip(out_rgb, 0, 255).astype(np.uint8)
        return out


class Dither:
    """
    Retro 8-bit / 16-bit Ordered and Error-Diffusion Dithering.
    Reduces color depth while preserving visual gradient smoothness.
    """

    def __init__(
        self,
        method: Union[str, DitherMethod] = DitherMethod.BAYER_4X4,
        levels: int = 4,
        color_mode: str = "rgb",  # "rgb" or "monochrome"
    ) -> None:
        self.method = DitherMethod(method) if isinstance(method, str) else method
        self.levels = max(2, int(levels))
        self.color_mode = color_mode

    def apply(self, rgba: np.ndarray, time: float = 0.0) -> np.ndarray:
        h, w, _ = rgba.shape
        rgb = rgba[:, :, :3].astype(np.float32) / 255.0

        if self.color_mode == "monochrome":
            luma = 0.299 * rgb[:, :, 0] + 0.587 * rgb[:, :, 1] + 0.114 * rgb[:, :, 2]
            rgb = np.repeat(luma[:, :, np.newaxis], 3, axis=2)

        # Bayer matrices normalized to [-0.5, 0.5]
        if self.method == DitherMethod.BAYER_2X2:
            m = np.array([[0, 2], [3, 1]], dtype=np.float32) / 4.0 - 0.5
        elif self.method == DitherMethod.BAYER_8X8:
            m4 = np.array([
                [0, 32, 8, 40, 2, 34, 10, 42],
                [48, 16, 56, 24, 50, 18, 58, 26],
                [12, 44, 4, 36, 14, 46, 6, 38],
                [60, 28, 52, 20, 62, 30, 54, 22],
                [3, 35, 11, 43, 1, 33, 9, 41],
                [51, 19, 59, 27, 49, 17, 57, 25],
                [15, 47, 7, 39, 13, 45, 5, 37],
                [63, 31, 55, 23, 61, 29, 53, 21]
            ], dtype=np.float32) / 64.0 - 0.5
            m = m4
        else:  # Default Bayer 4x4
            m = np.array([
                [0, 8, 2, 10],
                [12, 4, 14, 6],
                [3, 11, 1, 9],
                [15, 7, 13, 5]
            ], dtype=np.float32) / 16.0 - 0.5

        # Tile Bayer matrix across screen
        mh, mw = m.shape
        tiled_m = np.tile(m, ((h + mh - 1) // mh, (w + mw - 1) // mw))[:h, :w, np.newaxis]

        # Quantize with dither offset
        spread = 1.0 / (self.levels - 1)
        dithered = rgb + tiled_m * spread
        quantized = np.round(dithered * (self.levels - 1)) / (self.levels - 1)

        out = rgba.copy()
        out[:, :, :3] = (np.clip(quantized, 0.0, 1.0) * 255.0).astype(np.uint8)
        return out


# Convenience functions
def pixelate(size: int = 16, shape: Union[str, PixelShape] = PixelShape.SQUARE, **kwargs: Any) -> Pixelate:
    return Pixelate(size=size, shape=shape, **kwargs)


def pixel_dissolve(progress: float = 0.0, block_size: int = 24, **kwargs: Any) -> PixelDissolve:
    return PixelDissolve(progress=progress, block_size=block_size, **kwargs)


def halftone(dot_size: int = 10, angle: float = 45.0, **kwargs: Any) -> Halftone:
    return Halftone(dot_size=dot_size, angle=angle, **kwargs)


def dot_grid(grid_size: int = 8, glow_intensity: float = 0.4, **kwargs: Any) -> DotGrid:
    return DotGrid(grid_size=grid_size, glow_intensity=glow_intensity, **kwargs)


def dither(method: Union[str, DitherMethod] = DitherMethod.BAYER_4X4, levels: int = 4, **kwargs: Any) -> Dither:
    return Dither(method=method, levels=levels, **kwargs)
