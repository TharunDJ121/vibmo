"""
Compositing Graph, Precompositions, Track Mattes (Alpha & Luma), and Adjustment Layers.
"""

from __future__ import annotations
import math
from typing import Any, List, Optional, Sequence, Tuple, Union
import numpy as np
from PIL import Image, ImageFilter
import cairo

from vibmo.core.color import Color
from vibmo.core.vector import Vector2D
from vibmo.core.signal import Signal
from vibmo.scene.node import Node


class Precomp(Node):
    """
    Precomposition unit: Isolates a sub-tree of layers into its own offscreen render buffer.
    Allows treating complex layer hierarchies as a single animatable, transformable unit.
    """

    def __init__(
        self,
        *children: Node,
        width: float = 1920.0,
        height: float = 1080.0,
        background: Optional[Union[Color, str]] = None,
        position: Union[Vector2D, Sequence[float]] = (0.0, 0.0),
        **kwargs: Any,
    ) -> None:
        super().__init__(position=position, **kwargs)
        self.width_val = float(width)
        self.height_val = float(height)
        self.bg_color = Color.from_any(background) if background else None

        for child in children:
            self.add(child)

    def local_bounds(self, time: float = 0.0) -> Tuple[float, float, float, float]:
        return (0.0, 0.0, self.width_val, self.height_val)

    def draw(self, ctx: Any, time: float = 0.0) -> None:
        if not self.children and not self.bg_color:
            return

        w = int(self.width_val)
        h = int(self.height_val)

        # Create isolated offscreen surface
        surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, w, h)
        sub_ctx = cairo.Context(surf)

        # Background
        if self.bg_color is not None:
            sub_ctx.set_source_rgba(self.bg_color.r, self.bg_color.g, self.bg_color.b, self.bg_color.a)
            sub_ctx.paint()

        # Render children inside precomp coordinates
        sorted_children = sorted(self.children, key=lambda c: c.z_index)
        for child in sorted_children:
            self._render_child(sub_ctx, child, time, surf)

        # Paint offscreen result back to main context
        ctx.save()
        ctx.set_source_surface(surf, 0, 0)
        ctx.paint()
        ctx.restore()

    def _render_child(self, ctx: Any, node: Node, time: float, surface: Any) -> None:
        ctx.save()
        local_mat = node.local_matrix(time)
        ctx.transform(cairo.Matrix(*local_mat.to_cairo_tuple()))
        
        op = max(0.0, min(1.0, float(node.opacity.get(time))))
        if op <= 0.001:
            ctx.restore()
            return

        if op < 0.999:
            ctx.push_group()

        node.draw(ctx, time)

        if node.children:
            sorted_kids = sorted(node.children, key=lambda c: c.z_index)
            for k in sorted_kids:
                self._render_child(ctx, k, time, surface)

        if op < 0.999:
            ctx.pop_group_to_source()
            ctx.paint_with_alpha(op)

        ctx.restore()


class AlphaMatte(Node):
    """
    Alpha Matte Track: Uses the alpha channel of layer `matte` to stencil/cutout layer `target`.
    """

    def __init__(
        self,
        target: Node,
        matte: Node,
        inverted: bool = False,
        position: Union[Vector2D, Sequence[float]] = (0.0, 0.0),
        **kwargs: Any,
    ) -> None:
        super().__init__(position=position, **kwargs)
        self.target = target
        self.matte = matte
        self.target_node = target
        self.matte_node = matte
        self.inverted = inverted


    def local_bounds(self, time: float = 0.0) -> Tuple[float, float, float, float]:
        return self.target_node.local_bounds(time)

    def draw(self, ctx: Any, time: float = 0.0) -> None:
        ctx.save()

        # 1. Push group for compositing
        ctx.push_group()

        # 2. Draw Target Layer
        ctx.save()
        t_mat = self.target_node.local_matrix(time)
        ctx.transform(cairo.Matrix(*t_mat.to_cairo_tuple()))
        self.target_node.draw(ctx, time)
        ctx.restore()

        # 3. Apply Matte Operator (IN for normal, OUT for inverted)
        if self.inverted:
            ctx.set_operator(cairo.OPERATOR_DEST_OUT)
        else:
            ctx.set_operator(cairo.OPERATOR_DEST_IN)

        # 4. Draw Matte Layer
        ctx.save()
        m_mat = self.matte_node.local_matrix(time)
        ctx.transform(cairo.Matrix(*m_mat.to_cairo_tuple()))
        self.matte_node.draw(ctx, time)
        ctx.restore()

        # 5. Pop group to source and blend
        ctx.pop_group_to_source()
        ctx.set_operator(cairo.OPERATOR_OVER)
        ctx.paint()

        ctx.restore()


class LumaMatte(Node):
    """
    Luma Matte Track: Uses the grayscale luminosity of `matte` to modulate the alpha of `target`.
    """

    def __init__(
        self,
        target: Node,
        matte: Node,
        inverted: bool = False,
        position: Union[Vector2D, Sequence[float]] = (0.0, 0.0),
        **kwargs: Any,
    ) -> None:
        super().__init__(position=position, **kwargs)
        self.target = target
        self.matte = matte
        self.target_node = target
        self.matte_node = matte
        self.inverted = inverted


    def local_bounds(self, time: float = 0.0) -> Tuple[float, float, float, float]:
        return self.target_node.local_bounds(time)

    def draw(self, ctx: Any, time: float = 0.0) -> None:
        bx, by, bw, bh = self.target_node.local_bounds(time)
        w = max(1, int(bw))
        h = max(1, int(bh))

        # Render target to buffer
        target_surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, w, h)
        t_ctx = cairo.Context(target_surf)
        self.target_node.draw(t_ctx, time)

        # Render matte to buffer
        matte_surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, w, h)
        m_ctx = cairo.Context(matte_surf)
        self.matte_node.draw(m_ctx, time)

        # Convert to numpy arrays
        t_data = np.frombuffer(target_surf.get_data(), dtype=np.uint8).reshape((h, w, 4)).copy()
        m_data = np.frombuffer(matte_surf.get_data(), dtype=np.uint8).reshape((h, w, 4)).copy()

        # Calculate luminosity: 0.299*R + 0.587*G + 0.114*B (in BGRA Cairo byte layout)
        luma = (0.114 * m_data[:, :, 0] + 0.587 * m_data[:, :, 1] + 0.299 * m_data[:, :, 2]) / 255.0
        if self.inverted:
            luma = 1.0 - luma

        # Modulate alpha channel
        t_data[:, :, 3] = (t_data[:, :, 3] * luma).astype(np.uint8)

        # Paint result back
        res_surf = cairo.ImageSurface.create_for_data(t_data, cairo.FORMAT_ARGB32, w, h)
        ctx.save()
        ctx.set_source_surface(res_surf, 0, 0)
        ctx.paint()
        ctx.restore()


class AdjustmentLayer(Node):
    """
    Non-destructive Adjustment Layer: Captures underlying composite and applies post-fx filters.
    """

    def __init__(
        self,
        blur_radius: float = 0.0,
        tint: Optional[Union[Color, str]] = None,
        tint_strength: float = 0.5,
        width: float = 1920.0,
        height: float = 1080.0,
        position: Union[Vector2D, Sequence[float]] = (0.0, 0.0),
        **kwargs: Any,
    ) -> None:
        super().__init__(position=position, **kwargs)
        self.blur_radius = float(blur_radius)
        self.tint = Color.from_any(tint) if tint else None
        self.tint_strength = float(tint_strength)
        self.width_val = float(width)
        self.height_val = float(height)

    def local_bounds(self, time: float = 0.0) -> Tuple[float, float, float, float]:
        return (0.0, 0.0, self.width_val, self.height_val)

    def draw(self, ctx: Any, time: float = 0.0) -> None:
        # Adjustment layers are processed by rasterizer or surface sampling
        if self.tint is not None:
            ctx.save()
            ctx.set_source_rgba(self.tint.r, self.tint.g, self.tint.b, self.tint.a * self.tint_strength)
            ctx.rectangle(0, 0, self.width_val, self.height_val)
            ctx.fill()
            ctx.restore()


def precomp(*children: Node, name: str = "Precomp", **kwargs: Any) -> Precomp:
    """Helper factory to group multiple nodes into a single Precomp unit."""
    return Precomp(*children, name=name, **kwargs)
