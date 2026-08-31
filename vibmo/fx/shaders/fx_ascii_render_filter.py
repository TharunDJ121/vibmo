"""
✦ Vibmo Shaders: ASCII Render Filter & Dynamic Glyph Atlas
Inspired by Remocn ascii-render with high-performance NumPy & Cairo rendering.
"""

from __future__ import annotations

import numpy as np
import cairo
from PIL import Image
from typing import Any, Optional, Tuple, Union

try:
    from vibmo.fx.filters import Filter
except ImportError:
    class Filter:
        def apply(self, rgba: np.ndarray, time: float = 0.0) -> np.ndarray:
            raise NotImplementedError


class AsciiRenderFilter(Filter):
    """
    Renders the scene as an ASCII character glyph matrix with full color or monochrome ink.
    """
    def __init__(
        self,
        glyph_size: int = 24,
        charset: str = " .:-=+*#%@",
        colored: bool = False,
        ink: str = "#9dff9d",
        intensity: float = 1.0,
        **kwargs: Any,
    ):
        self.glyph_size = max(6, int(glyph_size))
        self.charset = charset if charset else " .:-=+*#%@"
        self.colored = bool(colored)
        self.ink = ink
        self.intensity = float(np.clip(intensity, 0.0, 1.0))
        self.ink_rgb = self._parse_hex(ink)
        self.num_glyphs = len(self.charset)

    def _parse_hex(self, hex_code: str) -> Tuple[float, float, float]:
        hex_clean = hex_code.lstrip("#")
        if len(hex_clean) == 3:
            hex_clean = "".join(c * 2 for c in hex_clean)
        if len(hex_clean) != 6:
            return (0.6, 1.0, 0.6)
        r = int(hex_clean[0:2], 16) / 255.0
        g = int(hex_clean[2:4], 16) / 255.0
        b = int(hex_clean[4:6], 16) / 255.0
        return (r, g, b)

    def apply(self, rgba: np.ndarray, time: float = 0.0) -> np.ndarray:
        if self.intensity <= 0.0:
            return rgba

        h, w, _ = rgba.shape
        cols = max(1, w // self.glyph_size)
        rows = max(1, h // self.glyph_size)

        # Downsample image to grid size to compute average cell luminance and color
        src_rgb = rgba[:, :, :3]
        pil_img = Image.fromarray(src_rgb)
        small_img = pil_img.resize((cols, rows), Image.Resampling.BILINEAR)
        small_arr = np.array(small_img, dtype=np.float32)

        # Luminance per block
        luma = (
            0.299 * small_arr[:, :, 0] +
            0.587 * small_arr[:, :, 1] +
            0.114 * small_arr[:, :, 2]
        ) / 255.0

        glyph_indices = np.clip((luma * self.num_glyphs).astype(int), 0, self.num_glyphs - 1)

        # Create output Cairo surface
        surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, w, h)
        ctx = cairo.Context(surface)

        ctx.set_source_rgba(0, 0, 0, 1.0)
        ctx.paint()

        ctx.select_font_face("monospace", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
        ctx.set_font_size(float(self.glyph_size))

        for r in range(rows):
            y_pos = (r + 1) * self.glyph_size - (self.glyph_size * 0.15)
            for c in range(cols):
                idx = glyph_indices[r, c]
                char = self.charset[idx]
                if char.isspace():
                    continue

                if self.colored:
                    cell_color = small_arr[r, c] / 255.0
                    ctx.set_source_rgba(cell_color[0], cell_color[1], cell_color[2], 1.0)
                else:
                    ctx.set_source_rgba(self.ink_rgb[0], self.ink_rgb[1], self.ink_rgb[2], 1.0)

                x_pos = c * self.glyph_size + (self.glyph_size * 0.1)
                ctx.move_to(x_pos, y_pos)
                ctx.show_text(char)

        buf = surface.get_data()
        ascii_out = np.ndarray(shape=(h, w, 4), dtype=np.uint8, buffer=buf)
        # Cairo is BGRA -> convert to RGBA
        ascii_rgba = ascii_out[:, :, [2, 1, 0, 3]].copy()

        if self.intensity >= 1.0:
            return ascii_rgba

        blended = (rgba.astype(np.float32) * (1.0 - self.intensity) +
                   ascii_rgba.astype(np.float32) * self.intensity)
        return np.clip(blended, 0, 255).astype(np.uint8)


class AsciiRenderShader(AsciiRenderFilter):
    """Alias for AsciiRenderFilter."""
    pass
