"""
Interactive Cursor and Click Ripple components for simulating mouse navigation in UI product demos.
"""

from __future__ import annotations
import math
from typing import Any, List, Optional, Sequence, Tuple, Union
import cairo

from vibmo.core.color import Color, colors
from vibmo.core.vector import Vector2D
from vibmo.core.easing import Ease, EasingFunc
from vibmo.core.signal import Signal, AnimationAction
from vibmo.scene.node import Node


class Cursor(Node):
    """
    Animated Vector Mouse Pointer for simulating realistic UI navigation and clicks.
    """

    def __init__(
        self,
        position: Union[Vector2D, Sequence[float]] = (960.0, 540.0),
        size: float = 24.0,
        style: str = "arrow",  # "arrow", "hand", "pointer"
        fill: Optional[Union[Color, str]] = None,
        stroke: Optional[Union[Color, str]] = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(position=position, **kwargs)
        self.size_val = float(size)
        self.style = style.lower()
        if self.style in ("hand", "pointer"):
            self.fill_color = Color.from_any(fill) if fill else Color.WHITE
            self.stroke_color = Color.from_any(stroke) if stroke else Color.hex("#111827")
        else:
            self.fill_color = Color.from_any(fill) if fill else Color.hex("#0f172a")
            self.stroke_color = Color.from_any(stroke) if stroke else Color.WHITE
        self._ripples: List[Tuple[float, float, Vector2D]] = []

    def move_to(
        self,
        target: Any,
        duration: float = 0.8,
        ease: EasingFunc = Ease.in_out_quad,
        delay: float = 0.0,
    ) -> AnimationAction:
        """
        Smoothly glides the cursor to a target Node or (x, y) coordinates.
        If a Node is passed, automatically resolves the node's world center!
        """
        if hasattr(target, "world_bounds"):
            bx, by, bw, bh = target.world_bounds(0.0)
            target_pos = Vector2D(bx + bw * 0.5, by + bh * 0.5)
        elif hasattr(target, "position"):
            target_pos = target.position.get(0.0)
        else:
            target_pos = Vector2D.from_any(target)

        return self.position.to(target_pos, duration=duration, ease=ease, delay=delay)

    glide_to = move_to

    def click(self, duration: float = 0.35, scale_dip: float = 0.82) -> List[AnimationAction]:
        """Simulates a mouse press with a spring bounce click animation."""
        curr_scale = self.scale.get()
        dip_scale = Vector2D(curr_scale.x * scale_dip, curr_scale.y * scale_dip)
        
        return [
            self.scale.to(dip_scale, duration=duration * 0.4, ease=Ease.out_quad),
            self.scale.to(curr_scale, duration=duration * 0.6, ease=Ease.spring(stiffness=180, damping=10), delay=duration * 0.4),
        ]

    def local_bounds(self, time: float = 0.0) -> Tuple[float, float, float, float]:
        return (0.0, 0.0, self.size_val, self.size_val * 1.4)

    def draw(self, ctx: Any, time: float = 0.0) -> None:
        s = self.size_val

        ctx.save()

        # 1. Subtle drop shadow
        ctx.save()
        ctx.translate(2.0, 3.0)
        self._trace_cursor_path(ctx, s)
        ctx.set_source_rgba(0.0, 0.0, 0.0, 0.35)
        ctx.fill()
        ctx.restore()

        # 2. Main Pointer Body
        self._trace_cursor_path(ctx, s)
        ctx.set_source_rgba(self.fill_color.r, self.fill_color.g, self.fill_color.b, self.fill_color.a)
        ctx.fill_preserve()

        # 3. Outer Stroke Outline
        ctx.set_source_rgba(self.stroke_color.r, self.stroke_color.g, self.stroke_color.b, self.stroke_color.a)
        ctx.set_line_width(2.5 if self.style in ("hand", "pointer") else 2.0)
        ctx.set_line_join(cairo.LINE_JOIN_ROUND)
        ctx.stroke()

        ctx.restore()

    def _trace_cursor_path(self, ctx: Any, s: float) -> None:
        if self.style in ("hand", "pointer"):
            # Clean vector pointing hand icon (Index finger pointing up)
            ctx.new_path()
            # Index fingertip
            ctx.move_to(s * 0.35, 0)
            ctx.arc(s * 0.45, s * 0.12, s * 0.10, -math.pi, 0)
            # Index finger right edge down
            ctx.line_to(s * 0.55, s * 0.60)
            # Middle finger
            ctx.arc(s * 0.65, s * 0.65, s * 0.10, -math.pi, 0)
            ctx.line_to(s * 0.75, s * 0.72)
            # Ring finger
            ctx.arc(s * 0.85, s * 0.75, s * 0.10, -math.pi, 0)
            ctx.line_to(s * 0.95, s * 0.85)
            # Pinky finger
            ctx.arc(s * 1.05, s * 0.90, s * 0.10, -math.pi, 0)
            ctx.line_to(s * 1.15, s * 1.35)
            # Palm base & wrist
            ctx.line_to(s * 0.25, s * 1.35)
            ctx.line_to(s * 0.10, s * 1.05)
            # Thumb
            ctx.arc(s * 0.10, s * 0.85, s * 0.12, math.pi * 0.5, math.pi * 1.5)
            ctx.line_to(s * 0.35, s * 0.60)
            ctx.line_to(s * 0.35, s * 0.12)
            ctx.close_path()
        else:
            ctx.new_path()
            ctx.move_to(0, 0)
            ctx.line_to(0, s * 1.3)
            ctx.line_to(s * 0.35, s * 0.95)
            ctx.line_to(s * 0.65, s * 1.5)
            ctx.line_to(s * 0.9, s * 1.38)
            ctx.line_to(s * 0.6, s * 0.85)
            ctx.line_to(s * 1.0, s * 0.85)
            ctx.close_path()


class ClickIndicator(Node):
    """Expanding neon shockwave ring indicating a mouse click point."""

    def __init__(
        self,
        position: Union[Vector2D, Sequence[float]] = (0.0, 0.0),
        color: Optional[Union[Color, str]] = None,
        max_radius: float = 45.0,
        **kwargs: Any,
    ) -> None:
        super().__init__(position=position, **kwargs)
        self.color = Color.from_any(color) if color else Color.hex("#6366f1")
        self.max_radius = float(max_radius)

    def trigger(self, duration: float = 0.5) -> List[AnimationAction]:
        self.scale.set(Vector2D(0.1, 0.1))
        self.opacity.set(1.0)
        return [
            self.scale.to(Vector2D(1.0, 1.0), duration=duration, ease=Ease.out_cubic),
            self.opacity.to(0.0, duration=duration, ease=Ease.out_cubic),
        ]

    def local_bounds(self, time: float = 0.0) -> Tuple[float, float, float, float]:
        r = self.max_radius
        return (-r, -r, r * 2, r * 2)

    def draw(self, ctx: Any, time: float = 0.0) -> None:
        ctx.save()
        ctx.set_source_rgba(self.color.r, self.color.g, self.color.b, self.color.a)
        ctx.set_line_width(3.0)
        ctx.arc(0, 0, self.max_radius, 0, math.pi * 2)
        ctx.stroke()
        ctx.restore()
