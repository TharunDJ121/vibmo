"""
Layer Masking, Vector Clipping, and Alpha Mattes.
"""

from __future__ import annotations
import math
from typing import Any, Optional, Tuple, Union
import cairo
import numpy as np
from PIL import Image, ImageFilter

from vibmo.core.vector import Vector2D
from vibmo.core.color import Color
from vibmo.scene.node import Node


class Mask:
    """
    A vector shape or raster mask applied to a Node to clip or alpha-stencil its rendering.
    Supports add, subtract, and intersect modes with optional edge feathering and inversion.
    """

    def __init__(
        self,
        shape: Any,
        mode: str = "add",  # "add", "subtract", "intersect"
        invert: bool = False,
        feather: float = 0.0,
        opacity: float = 1.0,
    ) -> None:
        self.shape = shape
        self.mode = mode.lower()
        self.invert = invert
        self.feather = float(feather)
        self.opacity = float(opacity)

    def apply_to_surface(
        self,
        target_surface: cairo.ImageSurface,
        time: float,
        width: int,
        height: int,
    ) -> None:
        """Applies mask stencil and feathering to the target Cairo surface in-place."""
        if self.shape is None:
            return

        # Render mask shape into offscreen grayscale surface
        mask_surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, width, height)
        mask_ctx = cairo.Context(mask_surf)

        # Draw mask shape in pure white
        if hasattr(self.shape, "draw"):
            self.shape.draw(mask_ctx, time)
        elif hasattr(self.shape, "render"):
            self.shape.render(mask_ctx, time)

        mask_surf.flush()
        m_buf = mask_surf.get_data()
        m_arr = np.ndarray(shape=(height, width, 4), dtype=np.uint8, buffer=m_buf)
        alpha_mask = m_arr[:, :, 3].astype(np.float32) / 255.0

        if self.invert:
            alpha_mask = 1.0 - alpha_mask

        # Feathering using Gaussian blur
        if self.feather > 0.5:
            m_img = Image.fromarray((alpha_mask * 255.0).astype(np.uint8), mode="L")
            m_img = m_img.filter(ImageFilter.GaussianBlur(radius=self.feather))
            alpha_mask = np.array(m_img, dtype=np.float32) / 255.0

        alpha_mask *= self.opacity

        # Apply stencil onto target surface
        target_surface.flush()
        t_buf = target_surface.get_data()
        t_arr = np.ndarray(shape=(height, width, 4), dtype=np.uint8, buffer=t_buf)

        # In Cairo ARGB32, channel 3 is Alpha
        t_arr[:, :, 3] = (t_arr[:, :, 3].astype(np.float32) * alpha_mask).astype(np.uint8)
        # Pre-multiply color channels
        t_arr[:, :, 0] = (t_arr[:, :, 0].astype(np.float32) * alpha_mask).astype(np.uint8)
        t_arr[:, :, 1] = (t_arr[:, :, 1].astype(np.float32) * alpha_mask).astype(np.uint8)
        t_arr[:, :, 2] = (t_arr[:, :, 2].astype(np.float32) * alpha_mask).astype(np.uint8)
        target_surface.mark_dirty()
