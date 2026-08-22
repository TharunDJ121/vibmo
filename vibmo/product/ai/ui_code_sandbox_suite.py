"""
Split Code Playground & Sandbox UI suite components for Vibmo.
"""

from __future__ import annotations
import math
from typing import Any, Dict, List, Optional, Sequence, Tuple, Union
import cairo

from vibmo.core.vector import Vector2D
from vibmo.core.color import Color, colors
from vibmo.core.signal import Signal, AnimationAction
from vibmo.core.easing import Ease, EasingFunc
from vibmo.scene.node import Node


def _rounded_rect(ctx: Any, x: float, y: float, w: float, h: float, r: float) -> None:
    """Helper for drawing rounded rectangles."""
    ctx.new_path()
    ctx.arc(x + w - r, y + r, r, -math.pi / 2, 0)
    ctx.arc(x + w - r, y + h - r, r, 0, math.pi / 2)
    ctx.arc(x + r, y + h - r, r, math.pi / 2, math.pi)
    ctx.arc(x + r, y + r, r, math.pi, 3 * math.pi / 2)
    ctx.close_path()


class SplitCodePlayground(Node):
    """
    Split-pane container with Code Editor on left and Interactive Preview / Output on right.
    """

    def __init__(
        self,
        width: float = 1200.0,
        height: float = 800.0,
        split_ratio: float = 0.5,
        left_color: Union[Color, str] = "#1e1e1e",
        right_color: Union[Color, str] = "#ffffff",
        divider_color: Union[Color, str] = "#333333",
        corner_radius: float = 12.0,
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)
        self.width_val = float(width)
        self.height_val = float(height)
        self.split_ratio = Signal(float(split_ratio), f"{self.name}.split_ratio")
        self.left_color = Color.from_any(left_color)
        self.right_color = Color.from_any(right_color)
        self.divider_color = Color.from_any(divider_color)
        self.corner_radius = float(corner_radius)

    def draw(self, ctx: Any, time: float = 0.0) -> None:
        ratio = max(0.0, min(1.0, float(self.split_ratio.get(time))))
        left_w = self.width_val * ratio
        right_w = self.width_val * (1.0 - ratio)

        ctx.save()

        # Clip container for rounded corners
        _rounded_rect(ctx, 0, 0, self.width_val, self.height_val, self.corner_radius)
        ctx.clip()

        # Left Pane (Code Editor)
        ctx.new_path()
        ctx.rectangle(0, 0, left_w, self.height_val)
        ctx.set_source_rgba(*self.left_color.to_tuple_rgba())
        ctx.fill()

        # Right Pane (Preview)
        ctx.new_path()
        ctx.rectangle(left_w, 0, right_w, self.height_val)
        ctx.set_source_rgba(*self.right_color.to_tuple_rgba())
        ctx.fill()

        # Divider
        ctx.new_path()
        ctx.move_to(left_w, 0)
        ctx.line_to(left_w, self.height_val)
        ctx.set_line_width(2.0)
        ctx.set_source_rgba(*self.divider_color.to_tuple_rgba())
        ctx.stroke()

        ctx.restore()


class InteractiveTerminalLogs(Node):
    """
    Bottom console output drawer with stdout logs and execution timer.
    """

    def __init__(
        self,
        logs: Sequence[str] = ("Starting server...", "Server running on port 3000"),
        execution_time: str = "0.45s",
        width: float = 600.0,
        height: float = 200.0,
        bg_color: Union[Color, str] = "#0d1117",
        text_color: Union[Color, str] = "#c9d1d9",
        corner_radius: float = 8.0,
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)
        self.logs = list(logs)
        self.execution_time = execution_time
        self.width_val = float(width)
        self.height_val = float(height)
        self.bg_color = Color.from_any(bg_color)
        self.text_color = Color.from_any(text_color)
        self.corner_radius = float(corner_radius)

    def draw(self, ctx: Any, time: float = 0.0) -> None:
        ctx.save()
        _rounded_rect(ctx, 0, 0, self.width_val, self.height_val, self.corner_radius)
        ctx.set_source_rgba(*self.bg_color.to_tuple_rgba())
        ctx.fill()

        ctx.set_source_rgba(*self.text_color.to_tuple_rgba())
        ctx.select_font_face("monospace", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)
        ctx.set_font_size(14)

        # Header with execution timer
        ctx.move_to(16, 24)
        ctx.show_text(f"Terminal Output — Execution time: {self.execution_time}")

        ctx.set_line_width(1.0)
        ctx.move_to(16, 32)
        ctx.line_to(self.width_val - 16, 32)
        ctx.set_source_rgba(*Color.from_any("#30363d").to_tuple_rgba())
        ctx.stroke()

        # Logs
        ctx.set_source_rgba(*self.text_color.to_tuple_rgba())
        y = 56
        for log in self.logs:
            ctx.move_to(16, y)
            ctx.show_text(log)
            y += 20

        ctx.restore()


class RunCodeSuccessIndicator(Node):
    """
    Pulsing green run button that transforms to checkmark upon completion.
    """

    def __init__(
        self,
        radius: float = 24.0,
        base_color: Union[Color, str] = colors.EMERALD,
        success: bool = False,
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)
        self.radius_val = float(radius)
        self.base_color = Color.from_any(base_color)
        self.success = Signal(1.0 if success else 0.0, f"{self.name}.success")

    def animate_success(self, duration: float = 0.5) -> AnimationAction:
        return self.success.to(1.0, duration=duration, ease=Ease.out_back)

    def draw(self, ctx: Any, time: float = 0.0) -> None:
        success_val = float(self.success.get(time))
        pulse = (math.sin(time * 5.0) * 0.1 + 1.0) if success_val < 0.5 else 1.0

        ctx.save()
        r = self.radius_val * pulse

        # Draw circular background
        ctx.new_path()
        ctx.arc(self.radius_val, self.radius_val, r, 0, 2 * math.pi)
        ctx.set_source_rgba(*self.base_color.to_tuple_rgba())
        ctx.fill()

        # Icon logic: Play button (triangle) morphed to Checkmark
        ctx.set_source_rgba(1, 1, 1, 1)  # White icon

        if success_val < 0.5:
            # Play Triangle
            ctx.new_path()
            ctx.move_to(self.radius_val - 4, self.radius_val - 8)
            ctx.line_to(self.radius_val + 8, self.radius_val)
            ctx.line_to(self.radius_val - 4, self.radius_val + 8)
            ctx.close_path()
            ctx.fill()
        else:
            # Checkmark
            ctx.new_path()
            ctx.move_to(self.radius_val - 6, self.radius_val)
            ctx.line_to(self.radius_val - 2, self.radius_val + 6)
            ctx.line_to(self.radius_val + 8, self.radius_val - 6)
            ctx.set_line_width(3.0)
            ctx.set_line_cap(cairo.LINE_CAP_ROUND)
            ctx.set_line_join(cairo.LINE_JOIN_ROUND)
            ctx.stroke()

        ctx.restore()


class DependencyInstallPill(Node):
    """
    Small pill badge displaying 'npm packages installed in 1.2s'.
    """

    def __init__(
        self,
        text: str = "npm packages installed in 1.2s",
        height: float = 28.0,
        bg_color: Union[Color, str] = "#f0fdf4",  # light green
        text_color: Union[Color, str] = "#166534", # dark green
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)
        self.text = text
        self.height_val = float(height)
        self.bg_color = Color.from_any(bg_color)
        self.text_color = Color.from_any(text_color)
        self.padding = 12.0

    def draw(self, ctx: Any, time: float = 0.0) -> None:
        ctx.save()

        ctx.select_font_face("sans-serif", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
        ctx.set_font_size(12)
        xbearing, ybearing, width, height, dx, dy = ctx.text_extents(self.text)

        w = width + self.padding * 2
        h = self.height_val
        r = h / 2.0

        _rounded_rect(ctx, 0, 0, w, h, r)
        ctx.set_source_rgba(*self.bg_color.to_tuple_rgba())
        ctx.fill()

        ctx.set_source_rgba(*self.text_color.to_tuple_rgba())
        ctx.move_to(self.padding, h / 2.0 - ybearing / 2.0)
        ctx.show_text(self.text)

        ctx.restore()
