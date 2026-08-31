"""
Unified Render Backend Abstraction for Vibmo.
Provides pluggable Hybrid GPU + CPU Vector Compositor and Deterministic Headless CPU Fallback.
"""

from __future__ import annotations
import abc
import math
import numpy as np
from PIL import Image
import cairo
from typing import Any, Dict, List, Optional, Sequence, Tuple, Union

from vibmo.core.color import Color
from vibmo.render.gpu.compositor import GPUCompositor


class RenderBackend(abc.ABC):
    """Abstract interface for all rendering and compositing backends."""

    def __init__(self, width: int, height: int) -> None:
        self.width = max(16, int(width))
        self.height = max(16, int(height))

    @property
    @abc.abstractmethod
    def name(self) -> str:
        """Name of the backend."""
        pass

    @property
    @abc.abstractmethod
    def is_gpu_accelerated(self) -> bool:
        """Whether this backend executes on hardware GPU."""
        pass

    @abc.abstractmethod
    def composite_layers(
        self,
        base_rgba: np.ndarray,
        layer_rgba: np.ndarray,
        blend_mode: str = "normal",
        opacity: float = 1.0,
    ) -> np.ndarray:
        """Blends two RGBA buffers together using the specified blend mode."""
        pass

    @abc.abstractmethod
    def apply_track_matte(
        self,
        target_rgba: np.ndarray,
        matte_rgba: np.ndarray,
        matte_type: str = "alpha",
        inverted: bool = False,
    ) -> np.ndarray:
        """Applies Alpha or Luma track matte to target layer."""
        pass

    @abc.abstractmethod
    def render_3d_quad(
        self,
        layer_rgba: np.ndarray,
        bounds: Tuple[float, float, float, float],
        position: Tuple[float, float],
        scale: Tuple[float, float],
        rot_z: float,
        rx: float,
        ry: float,
        anchor: Tuple[float, float] = (0.5, 0.5),
        opacity: float = 1.0,
        focal_dist: float = 1200.0,
    ) -> np.ndarray:
        """Projects a 2D layer quad in 3D perspective space."""
        pass

    @abc.abstractmethod
    def apply_post_fx(
        self,
        rgba: np.ndarray,
        time: float,
        post_fx: List[Any],
    ) -> np.ndarray:
        """Applies viewport post-processing shaders/filters."""
        pass

    @abc.abstractmethod
    def apply_lut3d(
        self,
        rgba: np.ndarray,
        lut_data: np.ndarray,
        intensity: float = 1.0,
    ) -> np.ndarray:
        """Applies a 3D LUT color grade."""
        pass


class CPURenderBackend(RenderBackend):
    """Deterministic Headless CPU Render Backend (Cairo + NumPy + PIL)."""

    @property
    def name(self) -> str:
        return "CPU Software Fallback"

    @property
    def is_gpu_accelerated(self) -> bool:
        return False

    def composite_layers(
        self,
        base_rgba: np.ndarray,
        layer_rgba: np.ndarray,
        blend_mode: str = "normal",
        opacity: float = 1.0,
    ) -> np.ndarray:
        # Software composite via Cairo ImageSurface
        h, w, _ = base_rgba.shape
        surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, w, h)
        ctx = cairo.Context(surf)

        # Draw Base
        base_bgra = np.ascontiguousarray(base_rgba[:, :, [2, 1, 0, 3]])
        surf_base = cairo.ImageSurface.create_for_data(base_bgra, cairo.FORMAT_ARGB32, w, h)
        ctx.set_source_surface(surf_base, 0, 0)
        ctx.paint()

        # Draw Layer with blend mode & opacity
        from vibmo.compositing.blend_modes import get_cairo_operator
        ctx.set_operator(get_cairo_operator(blend_mode))
        layer_bgra = np.ascontiguousarray(layer_rgba[:, :, [2, 1, 0, 3]])
        surf_layer = cairo.ImageSurface.create_for_data(layer_bgra, cairo.FORMAT_ARGB32, w, h)
        ctx.set_source_surface(surf_layer, 0, 0)
        ctx.paint_with_alpha(max(0.0, min(1.0, float(opacity))))

        surf.flush()
        out_buf = surf.get_data()
        out_bgra = np.ndarray(shape=(h, w, 4), dtype=np.uint8, buffer=out_buf)
        return out_bgra[:, :, [2, 1, 0, 3]].copy()

    def apply_track_matte(
        self,
        target_rgba: np.ndarray,
        matte_rgba: np.ndarray,
        matte_type: str = "alpha",
        inverted: bool = False,
    ) -> np.ndarray:
        out = target_rgba.copy()
        if matte_type.lower() == "alpha":
            factor = matte_rgba[:, :, 3].astype(np.float32) / 255.0
        else:
            factor = (
                0.299 * matte_rgba[:, :, 0] +
                0.587 * matte_rgba[:, :, 1] +
                0.114 * matte_rgba[:, :, 2]
            ).astype(np.float32) / 255.0

        if inverted:
            factor = 1.0 - factor

        out[:, :, 3] = (out[:, :, 3] * np.clip(factor, 0.0, 1.0)).astype(np.uint8)
        return out

    def render_3d_quad(
        self,
        layer_rgba: np.ndarray,
        bounds: Tuple[float, float, float, float],
        position: Tuple[float, float],
        scale: Tuple[float, float],
        rot_z: float,
        rx: float,
        ry: float,
        anchor: Tuple[float, float] = (0.5, 0.5),
        opacity: float = 1.0,
        focal_dist: float = 1200.0,
    ) -> np.ndarray:
        from vibmo.spatial.perspective import Projective3DWarp, find_perspective_coeffs
        lh, lw, _ = layer_rgba.shape
        img = Image.fromarray(layer_rgba, "RGBA")
        dst_quad = Projective3DWarp.project_quad(bounds, position, scale, rot_z, rx, ry, anchor, focal_dist=focal_dist)

        xs = [p[0] for p in dst_quad]
        ys = [p[1] for p in dst_quad]
        min_x, max_x = min(xs), max(xs)
        min_y, max_y = min(ys), max(ys)
        tw = max(4, int(math.ceil(max_x - min_x)))
        th = max(4, int(math.ceil(max_y - min_y)))

        dst_rel = [(px - min_x, py - min_y) for px, py in dst_quad]
        src_pts = [(0, 0), (lw, 0), (lw, lh), (0, lh)]
        coeffs = find_perspective_coeffs(src_points=src_pts, dst_points=dst_rel)

        warped_img = img.transform((tw, th), Image.Transform.PERSPECTIVE, coeffs, Image.Resampling.BICUBIC)
        warped_arr = np.array(warped_img)

        # Place onto canvas
        out = np.zeros((self.height, self.width, 4), dtype=np.uint8)
        # Compute bounding overlap
        ox0 = max(0, int(min_x))
        oy0 = max(0, int(min_y))
        ox1 = min(self.width, int(min_x + tw))
        oy1 = min(self.height, int(min_y + th))

        if ox1 > ox0 and oy1 > oy0:
            sx0 = ox0 - int(min_x)
            sy0 = oy0 - int(min_y)
            sx1 = sx0 + (ox1 - ox0)
            sy1 = sy0 + (oy1 - oy0)
            out[oy0:oy1, ox0:ox1] = (warped_arr[sy0:sy1, sx0:sx1].astype(np.float32) * opacity).astype(np.uint8)

        return out

    def apply_post_fx(
        self,
        rgba: np.ndarray,
        time: float,
        post_fx: List[Any],
    ) -> np.ndarray:
        out = rgba
        for fx in post_fx:
            out = fx.apply(out, time)
        return out

    def apply_lut3d(
        self,
        rgba: np.ndarray,
        lut_data: np.ndarray,
        intensity: float = 1.0,
    ) -> np.ndarray:
        # Software LUT interpolation fallback
        lut_dim = lut_data.shape[0]
        scale = (lut_dim - 1) / 255.0
        rgb = rgba[:, :, :3].astype(np.float32) * scale
        r0 = np.clip(np.floor(rgb[:, :, 0]).astype(np.int32), 0, lut_dim - 1)
        g0 = np.clip(np.floor(rgb[:, :, 1]).astype(np.int32), 0, lut_dim - 1)
        b0 = np.clip(np.floor(rgb[:, :, 2]).astype(np.int32), 0, lut_dim - 1)

        graded = (lut_data[r0, g0, b0] * 255.0).astype(np.uint8)
        final_rgb = ((1.0 - intensity) * rgba[:, :, :3] + intensity * graded).astype(np.uint8)
        out = rgba.copy()
        out[:, :, :3] = final_rgb
        return out


class HybridRenderBackend(RenderBackend):
    """
    Industry-Standard Hybrid Render Backend.
    Combines high-precision CPU Cairo vector rasterization with hardware ModernGL GPU multi-pass compositing.
    """

    def __init__(self, width: int, height: int) -> None:
        super().__init__(width, height)
        self.gpu = GPUCompositor(width, height)
        self.cpu = CPURenderBackend(width, height)

    @property
    def name(self) -> str:
        if self.gpu.is_available:
            return f"Hybrid Compositor (GPU: {self.gpu.device_name} + Cairo Vector)"
        return "Hybrid Compositor (CPU Fallback Mode)"

    @property
    def is_gpu_accelerated(self) -> bool:
        return self.gpu.is_available

    def composite_layers(
        self,
        base_rgba: np.ndarray,
        layer_rgba: np.ndarray,
        blend_mode: str = "normal",
        opacity: float = 1.0,
    ) -> np.ndarray:
        if self.gpu.is_available:
            try:
                return self.gpu.composite_layers(base_rgba, layer_rgba, blend_mode, opacity)
            except Exception:
                pass
        return self.cpu.composite_layers(base_rgba, layer_rgba, blend_mode, opacity)

    def apply_track_matte(
        self,
        target_rgba: np.ndarray,
        matte_rgba: np.ndarray,
        matte_type: str = "alpha",
        inverted: bool = False,
    ) -> np.ndarray:
        if self.gpu.is_available:
            try:
                return self.gpu.apply_track_matte(target_rgba, matte_rgba, matte_type, inverted)
            except Exception:
                pass
        return self.cpu.apply_track_matte(target_rgba, matte_rgba, matte_type, inverted)

    def render_3d_quad(
        self,
        layer_rgba: np.ndarray,
        bounds: Tuple[float, float, float, float],
        position: Tuple[float, float],
        scale: Tuple[float, float],
        rot_z: float,
        rx: float,
        ry: float,
        anchor: Tuple[float, float] = (0.5, 0.5),
        opacity: float = 1.0,
        focal_dist: float = 1200.0,
    ) -> np.ndarray:
        if self.gpu.is_available:
            try:
                return self.gpu.render_3d_quad(
                    layer_rgba=layer_rgba,
                    bounds=bounds,
                    position=position,
                    scale=scale,
                    rot_z=rot_z,
                    rx=rx,
                    ry=ry,
                    anchor=anchor,
                    opacity=opacity,
                    focal_dist=focal_dist,
                    scene_dim=(self.width, self.height),
                )
            except Exception:
                pass
        return self.cpu.render_3d_quad(
            layer_rgba, bounds, position, scale, rot_z, rx, ry, anchor, opacity, focal_dist
        )

    def apply_post_fx(
        self,
        rgba: np.ndarray,
        time: float,
        post_fx: List[Any],
    ) -> np.ndarray:
        if self.gpu.is_available and post_fx:
            try:
                return self.gpu.apply_post_fx(rgba, time, post_fx)
            except Exception:
                pass
        return self.cpu.apply_post_fx(rgba, time, post_fx)

    def apply_lut3d(
        self,
        rgba: np.ndarray,
        lut_data: np.ndarray,
        intensity: float = 1.0,
    ) -> np.ndarray:
        if self.gpu.is_available:
            try:
                return self.gpu.apply_lut3d(rgba, lut_data, intensity)
            except Exception:
                pass
        return self.cpu.apply_lut3d(rgba, lut_data, intensity)


def get_optimal_backend(width: int = 1920, height: int = 1080) -> RenderBackend:
    """Returns the optimal rendering backend for the current environment."""
    try:
        backend = HybridRenderBackend(width, height)
        if backend.is_gpu_accelerated:
            return backend
    except Exception:
        pass
    return CPURenderBackend(width, height)
