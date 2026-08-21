"""
High-performance Cairo Vector Rasterizer with Compositing, Glassmorphism, and Motion Blur.
"""

from __future__ import annotations
import math
import numpy as np
from PIL import Image
import cairo
from typing import Any, List, Optional, Tuple, Union
from vibmo.core.color import Color, colors
from vibmo.scene.node import Node


class Rasterizer:
    """Renders a scene node hierarchy to raw RGBA pixel buffers using PyCairo."""

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

        # Create Cairo surface
        surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, render_w, render_h)
        ctx = cairo.Context(surface)
        if scale != 1.0:
            ctx.scale(scale, scale)

        # 1. Background
        if background is not None and background.a > 0:
            ctx.set_source_rgba(background.r, background.g, background.b, background.a)
            ctx.paint()
        else:
            ctx.set_operator(cairo.OPERATOR_CLEAR)
            ctx.paint()
            ctx.set_operator(cairo.OPERATOR_OVER)

        # 2. Camera Transform
        if camera is not None:
            cam_mat = camera.view_matrix(self.width, self.height, time)
            cairo_mat = cairo.Matrix(*cam_mat.to_cairo_tuple())
            ctx.transform(cairo_mat)

        # 3. Sort & Render Nodes
        sorted_nodes = sorted(root_nodes, key=lambda n: n.z_index)
        for node in sorted_nodes:
            self._render_node_recursive(ctx, node, time, surface)

        # 4. Extract pixel buffer
        surface.flush()
        buf = surface.get_data()
        # Cairo ARGB32 in memory is BGRA on little-endian machines
        arr = np.ndarray(shape=(render_h, render_w, 4), dtype=np.uint8, buffer=buf)
        # Convert BGRA to RGBA
        rgba = np.zeros_like(arr)
        rgba[:, :, 0] = arr[:, :, 2]  # R
        rgba[:, :, 1] = arr[:, :, 1]  # G
        rgba[:, :, 2] = arr[:, :, 0]  # B
        rgba[:, :, 3] = arr[:, :, 3]  # A

        # 5. Apply Post FX (Hardware GPU Shaders with CPU fallback)
        if post_fx:
            import threading
            if not hasattr(self, "_thread_local"):
                self._thread_local = threading.local()
                
            if not hasattr(self._thread_local, "gpu_proc"):
                try:
                    from vibmo.render.gpu.pipeline import GPUPostProcessor
                    self._thread_local.gpu_proc = GPUPostProcessor(self.width, self.height)
                except Exception:
                    self._thread_local.gpu_proc = None
                    
            gpu_proc = self._thread_local.gpu_proc

            if gpu_proc and gpu_proc.is_available:
                try:
                    rgba = gpu_proc.apply_post_fx(rgba, time, post_fx)
                except Exception:
                    for fx in post_fx:
                        rgba = fx.apply(rgba, time)
            else:
                for fx in post_fx:
                    rgba = fx.apply(rgba, time)



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
            for fx in post_fx:
                blurred = fx.apply(blurred, time)

        return blurred

    def _render_node_recursive(self, ctx: cairo.Context, node: Node, time: float, surface: cairo.ImageSurface) -> None:
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
                from vibmo.spatial.perspective import Projective3DWarp, find_perspective_coeffs
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
                        self._render_node_recursive(off_ctx, child, time, off_surf)

                off_surf.flush()
                buf = off_surf.get_data()
                arr = np.ndarray(shape=(off_h, off_w, 4), dtype=np.uint8, buffer=buf)
                rgba_local = np.zeros_like(arr)
                rgba_local[:, :, 0] = arr[:, :, 2]  # R
                rgba_local[:, :, 1] = arr[:, :, 1]  # G
                rgba_local[:, :, 2] = arr[:, :, 0]  # B
                rgba_local[:, :, 3] = arr[:, :, 3]  # A
                img_local = Image.fromarray(rgba_local, "RGBA")

                # Project 3D quad corners with perspective foreshortening
                pos = node.position.get(time)
                scale = node.scale.get(time)
                rot_z = float(node.rotation.get(time))
                anchor = node.anchor.get(time)
                padded_bounds = (lx - pad, ly - pad, off_w, off_h)
                dst_quad = Projective3DWarp.project_quad(padded_bounds, pos, scale, rot_z, rx, ry, anchor, focal_dist=1200.0)

                xs = [p[0] for p in dst_quad]
                ys = [p[1] for p in dst_quad]
                min_x, max_x = min(xs), max(xs)
                min_y, max_y = min(ys), max(ys)
                target_w = max(4, int(math.ceil(max_x - min_x)))
                target_h = max(4, int(math.ceil(max_y - min_y)))

                dst_rel = [(px - min_x, py - min_y) for px, py in dst_quad]
                src_pts = [(0, 0), (off_w, 0), (off_w, off_h), (0, off_h)]
                coeffs = find_perspective_coeffs(src_points=src_pts, dst_points=dst_rel)

                warped_img = img_local.transform((target_w, target_h), Image.Transform.PERSPECTIVE, coeffs, Image.Resampling.BICUBIC)
                warped_rgba = np.array(warped_img)

                # Convert to Cairo BGRA
                warped_bgra = np.zeros_like(warped_rgba)
                warped_bgra[:, :, 0] = warped_rgba[:, :, 2]  # B
                warped_bgra[:, :, 1] = warped_rgba[:, :, 1]  # G
                warped_bgra[:, :, 2] = warped_rgba[:, :, 0]  # R
                warped_bgra[:, :, 3] = warped_rgba[:, :, 3]  # A
                warped_bgra = np.ascontiguousarray(warped_bgra)

                warped_surf = cairo.ImageSurface.create_for_data(warped_bgra, cairo.FORMAT_ARGB32, target_w, target_h)
                ctx.set_source_surface(warped_surf, min_x, min_y)
                ctx.paint_with_alpha(op)
                ctx.restore()
                return

        # 2D Fast Direct Render Path
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
                self._render_node_recursive(ctx, child, time, surface)

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


