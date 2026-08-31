"""
High-performance Hybrid Vector Rasterizer and GPU Compositor Pipeline.
Combines subpixel CPU Cairo vector rasterization with hardware GPU ModernGL compositing.
"""

from __future__ import annotations
import math
import numpy as np
from PIL import Image
import cairo
import threading
from typing import Any, List, Optional, Tuple, Union

from vibmo.core.color import Color, colors
from vibmo.scene.node import Node
from vibmo.render.backend import RenderBackend, get_optimal_backend

_THREAD_LOCAL = threading.local()


def _get_thread_backend(width: int, height: int) -> RenderBackend:
    if not hasattr(_THREAD_LOCAL, "backend") or _THREAD_LOCAL.backend.width != width or _THREAD_LOCAL.backend.height != height:
        _THREAD_LOCAL.backend = get_optimal_backend(width, height)
    return _THREAD_LOCAL.backend


class Rasterizer:
    """Renders a scene node hierarchy using the Hybrid Vector & GPU Compositor Pipeline."""

    def __init__(self, width: int, height: int) -> None:
        self.width = int(width)
        self.height = int(height)

    def render_frame(
        self,
        root_nodes: List[Node],
        time: float,
        background: Optional[Color] = None,
        camera: Optional[Any] = None,
        post_fx: Optional[List[Any]] = None,
        scale: float = 1.0,
    ) -> np.ndarray:
        """Renders a single frame at time t, returning uint8 RGBA numpy array."""
        scale = max(0.1, min(2.0, float(scale)))
        render_w = max(16, int(self.width * scale))
        render_h = max(16, int(self.height * scale))

        backend = _get_thread_backend(render_w, render_h)

        # 1. Create Cairo surface for pixel-perfect vector rasterization
        surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, render_w, render_h)
        ctx = cairo.Context(surface)
        if scale != 1.0:
            ctx.scale(scale, scale)

        # 2. Background
        if background is not None and background.a > 0:
            ctx.set_source_rgba(background.r, background.g, background.b, background.a)
            ctx.paint()
        else:
            ctx.set_operator(cairo.OPERATOR_CLEAR)
            ctx.paint()
            ctx.set_operator(cairo.OPERATOR_OVER)

        # 3. Camera Transform
        if camera is not None:
            cam_mat = camera.view_matrix(self.width, self.height, time)
            cairo_mat = cairo.Matrix(*cam_mat.to_cairo_tuple())
            ctx.transform(cairo_mat)

        # 4. Sort & Render Nodes
        sorted_nodes = sorted(root_nodes, key=lambda n: n.z_index)
        for node in sorted_nodes:
            self._render_node_recursive(ctx, node, time, surface, backend)

        # 5. Extract pixel buffer (Cairo BGRA -> RGBA)
        surface.flush()
        buf = surface.get_data()
        arr = np.ndarray(shape=(render_h, render_w, 4), dtype=np.uint8, buffer=buf)
        rgba = arr[:, :, [2, 1, 0, 3]].copy()

        # 6. Apply GPU Hardware Post FX Shaders (Bloom, Vignette, Grain, Aberration)
        if post_fx:
            rgba = backend.apply_post_fx(rgba, time, post_fx)

        return rgba

    def render_frame_with_motion_blur(
        self,
        root_nodes: List[Node],
        time: float,
        fps: float,
        shutter_angle: float = 180.0,
        samples: int = 6,
        background: Optional[Color] = None,
        camera: Optional[Any] = None,
        post_fx: Optional[List[Any]] = None,
    ) -> np.ndarray:
        """Sub-frame temporal motion blur supersampling."""
        dt_frame = 1.0 / fps
        shutter_duration = dt_frame * (shutter_angle / 360.0)
        accum = np.zeros((self.height, self.width, 4), dtype=np.float32)

        sample_offsets = np.linspace(-shutter_duration * 0.5, shutter_duration * 0.5, samples)
        for offset in sample_offsets:
            sample_time = max(0.0, time + offset)
            sample_rgba = self.render_frame(root_nodes, sample_time, background, camera)
            accum += sample_rgba.astype(np.float32)

        accum /= float(samples)
        blurred = np.clip(accum, 0, 255).astype(np.uint8)

        if post_fx:
            backend = _get_thread_backend(self.width, self.height)
            blurred = backend.apply_post_fx(blurred, time, post_fx)

        return blurred

    def _render_node_recursive(
        self,
        ctx: cairo.Context,
        node: Node,
        time: float,
        surface: cairo.ImageSurface,
        backend: RenderBackend,
    ) -> None:
        if not node.visible:
            return
        op = max(0.0, min(1.0, float(node.opacity.get(time))))
        if op <= 0.001:
            return

        if hasattr(node, "apply_constraints"):
            node.apply_constraints(time)

        ctx.save()

        # Check for 3D Perspective Rotation
        rx = float(node.rotate_x.get(time))
        ry = float(node.rotate_y.get(time))
        is_3d = (abs(rx) > 1e-4 or abs(ry) > 1e-4)

        if is_3d:
            lx, ly, lw, lh = node.local_bounds(time)
            if lw > 4.0 and lh > 4.0:
                pad = 48
                off_w = int(math.ceil(lw + pad * 2))
                off_h = int(math.ceil(lh + pad * 2))
                off_surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, off_w, off_h)
                off_ctx = cairo.Context(off_surf)
                off_ctx.translate(pad - lx, pad - ly)

                # Render node and children into offscreen buffer
                node.draw(off_ctx, time)
                if node.children:
                    sorted_children = sorted(node.children, key=lambda c: c.z_index)
                    for child in sorted_children:
                        self._render_node_recursive(off_ctx, child, time, off_surf, backend)

                off_surf.flush()
                buf = off_surf.get_data()
                arr = np.ndarray(shape=(off_h, off_w, 4), dtype=np.uint8, buffer=buf)
                rgba_local = arr[:, :, [2, 1, 0, 3]].copy()

                # Hardware / Projective 3D Quad Projection
                pos = node.position.get(time)
                scale = node.scale.get(time)
                rot_z = float(node.rotation.get(time))
                anchor = node.anchor.get(time)
                padded_bounds = (lx - pad, ly - pad, off_w, off_h)

                warped_full_rgba = backend.render_3d_quad(
                    layer_rgba=rgba_local,
                    bounds=padded_bounds,
                    position=pos,
                    scale=scale,
                    rot_z=rot_z,
                    rx=rx,
                    ry=ry,
                    anchor=anchor,
                    opacity=op,
                    focal_dist=1200.0,
                )

                # Paint warped quad onto main Cairo canvas
                warped_bgra = np.ascontiguousarray(warped_full_rgba[:, :, [2, 1, 0, 3]])
                qh, qw = warped_bgra.shape[:2]
                stride = cairo.ImageSurface.format_stride_for_width(cairo.FORMAT_ARGB32, qw)
                warped_surf = cairo.ImageSurface.create_for_data(
                    warped_bgra, cairo.FORMAT_ARGB32, qw, qh, stride
                )
                ctx.identity_matrix()
                ctx.set_source_surface(warped_surf, 0, 0)
                ctx.paint()
                ctx.restore()
                return

        # 2D Fast Direct Vector Render Path
        local_mat = node.local_matrix(time)
        cairo_mat = cairo.Matrix(*local_mat.to_cairo_tuple())
        ctx.transform(cairo_mat)

        # Blend mode
        from vibmo.compositing.blend_modes import get_cairo_operator
        ctx.set_operator(get_cairo_operator(node.blend_mode))

        use_alpha_group = (op < 0.999 or node.mask is not None)
        if use_alpha_group:
            ctx.push_group()

        # Draw Node
        node.draw(ctx, time)

        # Draw Children sorted by z_index
        if node.children:
            sorted_children = sorted(node.children, key=lambda c: c.z_index)
            for child in sorted_children:
                self._render_node_recursive(ctx, child, time, surface, backend)

        if use_alpha_group:
            ctx.pop_group_to_source()
            # If node has a vector mask, apply it
            if node.mask is not None and hasattr(node.mask, "shape") and node.mask.shape is not None:
                ctx.save()
                if hasattr(node.mask.shape, "draw"):
                    node.mask.shape.draw(ctx, time)
                ctx.clip()
                ctx.paint_with_alpha(op)
                ctx.restore()
            else:
                ctx.paint_with_alpha(op)

        ctx.restore()
