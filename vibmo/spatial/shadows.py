"""
Realistic Gaussian Soft Drop Shadows and Emissive Glows for 2.5D Layer Depth.
"""

from __future__ import annotations
import math
from typing import Any, Dict, Optional, Sequence, Tuple, Union
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
import cairo

from collections import OrderedDict
from vibmo.core.color import Color, colors
from vibmo.core.vector import Vector2D


# Global LRU surface cache for instant 60 FPS replay without re-filtering
_SHADOW_CACHE: OrderedDict[Tuple, Tuple[cairo.ImageSurface, np.ndarray, int]] = OrderedDict()
_MAX_CACHE_ENTRIES = 512



class DropShadow:
    """
    True Gaussian-blurred multi-pass soft drop shadow and glow generator.
    """

    def __init__(
        self,
        color: Union[Color, str] = Color.hex("#000000").with_alpha(0.4),
        blur: float = 24.0,
        offset: Union[Vector2D, Sequence[float]] = (0.0, 12.0),
        spread: float = 0.0,
        ambient_blur: Optional[float] = None,
        ambient_alpha: Optional[float] = None,
    ) -> None:
        self.color = Color.from_any(color) if isinstance(color, (str, Color)) else Color.BLACK.with_alpha(0.4)
        self.blur = float(blur)
        self.offset = Vector2D.from_any(offset)
        self.spread = float(spread)
        self.ambient_blur = float(ambient_blur) if ambient_blur is not None else None
        self.ambient_alpha = float(ambient_alpha) if ambient_alpha is not None else None

    @classmethod
    def elevated(
        cls,
        blur: float = 28.0,
        offset: Union[Vector2D, Sequence[float]] = (0.0, 12.0),
        color: Union[Color, str] = Color.hex("#000000").with_alpha(0.45),
        spread: float = 0.0,
        ambient_blur: float = 8.0,
        ambient_alpha: float = 0.18,
    ) -> DropShadow:
        """Iconic Apple / Stripe elevated double-pass shadow (ambient contact + diffuse key)."""
        return cls(
            color=color,
            blur=blur,
            offset=offset,
            spread=spread,
            ambient_blur=ambient_blur,
            ambient_alpha=ambient_alpha,
        )

    @classmethod
    def soft(
        cls,
        blur: float = 24.0,
        offset: Union[Vector2D, Sequence[float]] = (0.0, 8.0),
        color: Union[Color, str] = Color.hex("#000000").with_alpha(0.15),
    ) -> DropShadow:
        """Gentle soft diffused drop shadow."""
        return cls(color=color, blur=blur, offset=offset)

    @classmethod
    def glow(
        cls,
        color: Union[Color, str] = colors.CYAN,
        blur: float = 32.0,
        spread: float = 2.0,
        intensity: float = 0.6,
    ) -> DropShadow:
        """Emissive neon glow shadow."""
        resolved = Color.from_any(color).with_alpha(intensity)
        return cls(color=resolved, blur=blur, offset=(0.0, 0.0), spread=spread)

    def render_shadow(
        self,
        ctx: Any,
        bounds: Tuple[float, float, float, float],
        corner_radius: float = 0.0,
    ) -> None:
        """Renders Gaussian blurred soft shadow beneath rectangular/card bounds."""
        bx, by, bw, bh = bounds
        if bw <= 1.0 or bh <= 1.0 or self.color.a <= 0.001:
            return

        # Render ambient contact shadow if specified
        if self.ambient_blur is not None and self.ambient_blur > 0.0:
            amb_alpha = self.ambient_alpha if self.ambient_alpha is not None else self.color.a * 0.5
            amb_color = self.color.with_alpha(amb_alpha)
            self._render_single_pass(ctx, bx, by, bw, bh, corner_radius, self.ambient_blur, 0.0, 0.0, 2.0, amb_color)

        # Render main directional shadow
        self._render_single_pass(
            ctx,
            bx,
            by,
            bw,
            bh,
            corner_radius,
            self.blur,
            self.spread,
            self.offset.x,
            self.offset.y,
            self.color,
        )

    def _render_single_pass(
        self,
        ctx: Any,
        bx: float,
        by: float,
        bw: float,
        bh: float,
        corner_radius: float,
        blur: float,
        spread: float,
        off_x: float,
        off_y: float,
        color: Color,
    ) -> None:
        if blur <= 0.0:
            return

        # Quantize cache key to avoid recomputing for tiny subpixel variations
        q_w = max(4, int(round(bw)))
        q_h = max(4, int(round(bh)))
        q_cr = max(0, int(round(corner_radius)))
        q_blur = max(1, int(round(blur)))
        q_spread = int(round(spread))
        q_color = (round(color.r, 2), round(color.g, 2), round(color.b, 2), round(color.a, 2))

        cache_key = (q_w, q_h, q_cr, q_blur, q_spread, q_color)

        if cache_key in _SHADOW_CACHE:
            surface, _, pad = _SHADOW_CACHE[cache_key]
            _SHADOW_CACHE.move_to_end(cache_key)
        else:
            surface, arr, pad = self._generate_shadow_surface(q_w, q_h, q_cr, q_blur, q_spread, color)
            if len(_SHADOW_CACHE) >= _MAX_CACHE_ENTRIES:
                _SHADOW_CACHE.popitem(last=False)
            _SHADOW_CACHE[cache_key] = (surface, arr, pad)


        ctx.save()
        # Position surface accurately accounting for padding and shadow offset
        dest_x = bx + off_x - pad
        dest_y = by + off_y - pad
        ctx.set_source_surface(surface, dest_x, dest_y)
        ctx.paint()
        ctx.restore()

    @staticmethod
    def _generate_shadow_surface(
        w: int,
        h: int,
        cr: int,
        blur: int,
        spread: int,
        color: Color,
    ) -> Tuple[cairo.ImageSurface, np.ndarray, int]:
        """Generates a premultiplied ARGB32 Cairo ImageSurface containing true Gaussian blur."""
        pad = int(math.ceil(blur * 2.8 + abs(spread) + 4))
        full_w = w + 2 * pad
        full_h = h + 2 * pad

        # 1. Draw crisp mask onto grayscale image
        mask_img = Image.new("L", (full_w, full_h), 0)
        draw = ImageDraw.Draw(mask_img)

        sx = pad - spread
        sy = pad - spread
        sw = w + 2 * spread
        sh = h + 2 * spread
        scr = max(0, cr + spread)

        if scr > 0:
            draw.rounded_rectangle([sx, sy, sx + sw, sy + sh], radius=scr, fill=255)
        else:
            draw.rectangle([sx, sy, sx + sw, sy + sh], fill=255)

        # 2. True Gaussian blur
        blurred_mask = mask_img.filter(ImageFilter.GaussianBlur(radius=blur))
        mask_arr = np.array(blurred_mask, dtype=np.float32) / 255.0

        # 3. Construct premultiplied BGRA numpy array for Cairo
        # alpha = mask * color.a
        alpha = mask_arr * color.a
        r = np.clip(alpha * color.r * 255.0, 0, 255).astype(np.uint8)
        g = np.clip(alpha * color.g * 255.0, 0, 255).astype(np.uint8)
        b = np.clip(alpha * color.b * 255.0, 0, 255).astype(np.uint8)
        a = np.clip(alpha * 255.0, 0, 255).astype(np.uint8)

        # In memory on little-endian: BGRA
        bgra = np.stack([b, g, r, a], axis=-1)

        # Ensure C-contiguous memory layout
        bgra_contiguous = np.ascontiguousarray(bgra)
        surf = cairo.ImageSurface.create_for_data(bgra_contiguous, cairo.FORMAT_ARGB32, full_w, full_h)

        return surf, bgra_contiguous, pad

