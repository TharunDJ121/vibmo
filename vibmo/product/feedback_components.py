"""
Social and feedback components (NotificationToast, AlertBanner, LoadingSpinner, SkeletonScreen, EmptyState, ErrorBoundary)
for notifications, alerts, and system state mockups.
"""

from __future__ import annotations
import math
from typing import Any, List, Optional, Sequence, Tuple, Union
import cairo

from vibmo.core.vector import Vector2D
from vibmo.core.color import Color, colors
from vibmo.core.signal import Signal, AnimationAction
from vibmo.core.easing import Ease, EasingFunc
from vibmo.scene.node import Node
from vibmo.spatial.shadows import DropShadow


class NotificationToast(Node):
    """
    Floating push notification bubble card with icon, title, description, and timestamp.
    """

    def __init__(
        self,
        title: str = "Payment Received",
        description: str = "$450.00 from Acme Corp",
        timestamp: str = "just now",
        width: float = 380.0,
        height: float = 76.0,
        icon_name: Optional[str] = None,
        icon_color: Union[Color, str] = colors.EMERALD,
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)
        self.icon_name = icon_name
        self.title_text = title
        self.description_text = description
        self.timestamp_text = timestamp
        self.width_val = float(width)
        self.height_val = float(height)
        self.icon_color = Color.from_any(icon_color)
        self.shadow = DropShadow.elevated(blur=32.0, offset=(0, 12), color=Color.BLACK.with_alpha(0.55))

    def local_bounds(self, time: float = 0.0) -> Tuple[float, float, float, float]:
        return (0.0, 0.0, self.width_val, self.height_val)

    def draw(self, ctx: Any, time: float = 0.0) -> None:
        w, h = self.width_val, self.height_val
        ctx.save()
        # Card Body
        self._rounded_rect(ctx, 0, 0, w, h, 16.0)
        ctx.set_source_rgba(0.08, 0.12, 0.22, 0.95)
        ctx.fill_preserve()
        ctx.set_source_rgba(1.0, 1.0, 1.0, 0.15)
        ctx.set_line_width(1.2)
        ctx.stroke()

        # Icon Circle
        ic_r = 18.0
        ic_x = 18.0 + ic_r
        ic_y = h * 0.5
        ctx.arc(ic_x, ic_y, ic_r, 0, math.pi * 2)
        c = self.icon_color
        ctx.set_source_rgba(c.r, c.g, c.b, 0.2)
        ctx.fill()

        # Icon Checkmark
        ctx.set_source_rgba(c.r, c.g, c.b, 1.0)
        ctx.set_line_width(2.5)
        ctx.set_line_cap(cairo.LINE_CAP_ROUND)
        ctx.set_line_join(cairo.LINE_JOIN_ROUND)
        ctx.move_to(ic_x - 6, ic_y)
        ctx.line_to(ic_x - 1, ic_y + 5)
        ctx.line_to(ic_x + 7, ic_y - 4)
        ctx.stroke()

        # Title
        ctx.set_source_rgba(1.0, 1.0, 1.0, 0.95)
        ctx.select_font_face("Segoe UI", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
        ctx.set_font_size(14.0)
        ctx.move_to(68.0, 32.0)
        ctx.show_text(self.title_text)

        # Description
        ctx.set_source_rgba(0.7, 0.75, 0.85, 0.85)
        ctx.select_font_face("Segoe UI", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)
        ctx.set_font_size(12.0)
        ctx.move_to(68.0, 52.0)
        ctx.show_text(self.description_text)

        # Timestamp
        ctx.set_source_rgba(0.45, 0.50, 0.60, 0.8)
        ctx.set_font_size(11.0)
        ext = ctx.text_extents(self.timestamp_text)
        ctx.move_to(w - 20.0 - ext.width, 30.0)
        ctx.show_text(self.timestamp_text)

        ctx.restore()

    def _rounded_rect(self, ctx: Any, x: float, y: float, w: float, h: float, r: float) -> None:
        r = min(r, w * 0.5, h * 0.5)
        ctx.new_path()
        ctx.arc(x + w - r, y + r, r, -math.pi * 0.5, 0)
        ctx.arc(x + w - r, y + h - r, r, 0, math.pi * 0.5)
        ctx.arc(x + r, y + h - r, r, math.pi * 0.5, math.pi)
        ctx.arc(x + r, y + r, r, math.pi, math.pi * 1.5)
        ctx.close_path()


class AlertBanner(Node):
    """
    Banner notification strip (info, success, warning, error).
    """

    def __init__(
        self,
        message: str = "Database maintenance scheduled for 02:00 UTC.",
        severity: str = "warning",  # "info", "success", "warning", "error"
        width: float = 620.0,
        height: float = 48.0,
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)
        self.message = message
        self.severity = severity
        self.width_val = float(width)
        self.height_val = float(height)

    def local_bounds(self, time: float = 0.0) -> Tuple[float, float, float, float]:
        return (0.0, 0.0, self.width_val, self.height_val)

    def draw(self, ctx: Any, time: float = 0.0) -> None:
        w, h = self.width_val, self.height_val
        ctx.save()
        color_map = {
            "info": colors.INDIGO,
            "success": colors.EMERALD,
            "warning": colors.AMBER,
            "error": colors.ROSE,
        }
        c = color_map.get(self.severity, colors.AMBER)

        self._rounded_rect(ctx, 0, 0, w, h, 10.0)
        ctx.set_source_rgba(c.r, c.g, c.b, 0.15)
        ctx.fill_preserve()
        ctx.set_source_rgba(c.r, c.g, c.b, 0.5)
        ctx.set_line_width(1.0)
        ctx.stroke()

        # Dot
        ctx.arc(24.0, h * 0.5, 4.0, 0, math.pi * 2)
        ctx.set_source_rgba(c.r, c.g, c.b, 1.0)
        ctx.fill()

        # Message
        ctx.set_source_rgba(1.0, 1.0, 1.0, 0.95)
        ctx.select_font_face("Segoe UI", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)
        ctx.set_font_size(13.0)
        ctx.move_to(40.0, h * 0.5 + 4.0)
        ctx.show_text(self.message)

        ctx.restore()

    def _rounded_rect(self, ctx: Any, x: float, y: float, w: float, h: float, r: float) -> None:
        r = min(r, w * 0.5, h * 0.5)
        ctx.new_path()
        ctx.arc(x + w - r, y + r, r, -math.pi * 0.5, 0)
        ctx.arc(x + w - r, y + h - r, r, 0, math.pi * 0.5)
        ctx.arc(x + r, y + h - r, r, math.pi * 0.5, math.pi)
        ctx.arc(x + r, y + r, r, math.pi, math.pi * 1.5)
        ctx.close_path()


class LoadingSpinner(Node):
    """
    Smooth rotating gradient arc loading spinner.
    """

    def __init__(
        self,
        radius: float = 24.0,
        line_width: float = 4.0,
        color: Union[Color, str] = colors.CYAN,
        speed: float = 1.5,
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)
        self.radius = float(radius)
        self.line_width = float(line_width)
        self.color = Color.from_any(color)
        self.speed = float(speed)

    def local_bounds(self, time: float = 0.0) -> Tuple[float, float, float, float]:
        r = self.radius + self.line_width
        return (-r, -r, r * 2, r * 2)

    def draw(self, ctx: Any, time: float = 0.0) -> None:
        r = self.radius
        rot = (time * self.speed * math.pi * 2) % (math.pi * 2)
        ctx.save()
        ctx.rotate(rot)

        # Draw arc with fading tail
        ctx.set_line_width(self.line_width)
        ctx.set_line_cap(cairo.LINE_CAP_ROUND)
        c = self.color
        ctx.set_source_rgba(c.r, c.g, c.b, 0.95)
        ctx.arc(0, 0, r, 0, math.pi * 1.4)
        ctx.stroke()

        ctx.restore()


class SkeletonScreen(Node):
    """
    Pulsing shimmer skeleton loading placeholder for cards, lines, and avatars.
    """

    def __init__(
        self,
        width: float = 360.0,
        height: float = 120.0,
        lines: int = 3,
        show_avatar: bool = True,
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)
        self.width_val = float(width)
        self.height_val = float(height)
        self.lines = max(1, int(lines))
        self.show_avatar = show_avatar

    def local_bounds(self, time: float = 0.0) -> Tuple[float, float, float, float]:
        return (0.0, 0.0, self.width_val, self.height_val)

    def draw(self, ctx: Any, time: float = 0.0) -> None:
        w, h = self.width_val, self.height_val
        shimmer = 0.12 + 0.08 * math.sin(time * 3.5)

        ctx.save()
        # Card outline
        self._rounded_rect(ctx, 0, 0, w, h, 14.0)
        ctx.set_source_rgba(0.08, 0.12, 0.20, 0.9)
        ctx.fill()

        # Avatar placeholder
        av_x = 20.0
        if self.show_avatar:
            ctx.arc(av_x + 20.0, 36.0, 20.0, 0, math.pi * 2)
            ctx.set_source_rgba(1.0, 1.0, 1.0, shimmer)
            ctx.fill()
            text_x = av_x + 54.0
        else:
            text_x = 20.0

        # Text lines
        line_w = w - text_x - 20.0
        line_h = 12.0
        for i in range(self.lines):
            cur_w = line_w * (1.0 if i == 0 else 0.7 - i * 0.1)
            ly = 24.0 + i * 22.0
            self._rounded_rect(ctx, text_x, ly, max(40.0, cur_w), line_h, 4.0)
            ctx.set_source_rgba(1.0, 1.0, 1.0, shimmer)
            ctx.fill()

        ctx.restore()

    def _rounded_rect(self, ctx: Any, x: float, y: float, w: float, h: float, r: float) -> None:
        r = min(r, w * 0.5, h * 0.5)
        ctx.new_path()
        ctx.arc(x + w - r, y + r, r, -math.pi * 0.5, 0)
        ctx.arc(x + w - r, y + h - r, r, 0, math.pi * 0.5)
        ctx.arc(x + r, y + h - r, r, math.pi * 0.5, math.pi)
        ctx.arc(x + r, y + r, r, math.pi, math.pi * 1.5)
        ctx.close_path()


class EmptyState(Node):
    """
    Aesthetic empty state illustration container with title, subtitle, and CTA button.
    """

    def __init__(
        self,
        title: str = "No Videos Yet",
        subtitle: str = "Generate your first motion graphic scene with Python.",
        button_label: str = "Create Project",
        width: float = 460.0,
        height: float = 240.0,
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)
        self.title_text = title
        self.subtitle_text = subtitle
        self.button_label = button_label
        self.width_val = float(width)
        self.height_val = float(height)

    def local_bounds(self, time: float = 0.0) -> Tuple[float, float, float, float]:
        return (0.0, 0.0, self.width_val, self.height_val)

    def draw(self, ctx: Any, time: float = 0.0) -> None:
        w, h = self.width_val, self.height_val
        ctx.save()
        # Dashed Border Container
        self._rounded_rect(ctx, 0, 0, w, h, 16.0)
        ctx.set_source_rgba(0.06, 0.09, 0.16, 0.9)
        ctx.fill_preserve()
        ctx.set_source_rgba(1.0, 1.0, 1.0, 0.15)
        ctx.set_dash([6.0, 6.0])
        ctx.set_line_width(1.5)
        ctx.stroke()
        ctx.set_dash([])

        # Title
        ctx.set_source_rgba(1.0, 1.0, 1.0, 0.95)
        ctx.select_font_face("Segoe UI", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
        ctx.set_font_size(18.0)
        ext = ctx.text_extents(self.title_text)
        ctx.move_to(w * 0.5 - ext.width * 0.5, 75.0)
        ctx.show_text(self.title_text)

        # Subtitle
        ctx.set_source_rgba(0.6, 0.65, 0.75, 0.8)
        ctx.select_font_face("Segoe UI", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)
        ctx.set_font_size(13.0)
        ext = ctx.text_extents(self.subtitle_text)
        ctx.move_to(w * 0.5 - ext.width * 0.5, 105.0)
        ctx.show_text(self.subtitle_text)

        # Button
        btn_w = 140.0
        btn_h = 36.0
        btn_x = (w - btn_w) * 0.5
        btn_y = 145.0
        self._rounded_rect(ctx, btn_x, btn_y, btn_w, btn_h, 8.0)
        ctx.set_source_rgba(0.39, 0.40, 0.95, 1.0)
        ctx.fill()

        ctx.set_source_rgba(1.0, 1.0, 1.0, 1.0)
        ctx.select_font_face("Segoe UI", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
        ctx.set_font_size(12.0)
        ext = ctx.text_extents(self.button_label)
        ctx.move_to(btn_x + (btn_w - ext.width) * 0.5, btn_y + (btn_h + ext.height) * 0.5 - 1.0)
        ctx.show_text(self.button_label)

        ctx.restore()

    def _rounded_rect(self, ctx: Any, x: float, y: float, w: float, h: float, r: float) -> None:
        r = min(r, w * 0.5, h * 0.5)
        ctx.new_path()
        ctx.arc(x + w - r, y + r, r, -math.pi * 0.5, 0)
        ctx.arc(x + w - r, y + h - r, r, 0, math.pi * 0.5)
        ctx.arc(x + r, y + h - r, r, math.pi * 0.5, math.pi)
        ctx.arc(x + r, y + r, r, math.pi, math.pi * 1.5)
        ctx.close_path()


class ErrorBoundary(Node):
    """
    Error fallback state display card with error badge and stack trace.
    """

    def __init__(
        self,
        error_name: str = "RuntimeError: Texture Allocation Failed",
        trace_summary: str = "at GPUContext.create_texture (wgpu_pipeline.py:142)\nat RenderPass.execute (compositor.py:88)",
        width: float = 520.0,
        height: float = 160.0,
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)
        self.error_name = error_name
        self.trace_summary = trace_summary
        self.width_val = float(width)
        self.height_val = float(height)

    def local_bounds(self, time: float = 0.0) -> Tuple[float, float, float, float]:
        return (0.0, 0.0, self.width_val, self.height_val)

    def draw(self, ctx: Any, time: float = 0.0) -> None:
        w, h = self.width_val, self.height_val
        ctx.save()
        # Error Card Body
        self._rounded_rect(ctx, 0, 0, w, h, 12.0)
        ctx.set_source_rgba(0.12, 0.04, 0.06, 0.95)
        ctx.fill_preserve()
        ctx.set_source_rgba(0.95, 0.25, 0.35, 0.5)
        ctx.set_line_width(1.5)
        ctx.stroke()

        # Error Title
        ctx.set_source_rgba(0.95, 0.35, 0.45, 1.0)
        ctx.select_font_face("Segoe UI", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
        ctx.set_font_size(15.0)
        ctx.move_to(20.0, 34.0)
        ctx.show_text(f"⚠️  {self.error_name}")

        # Stack Trace block
        lines = self.trace_summary.split("\n")
        ctx.set_source_rgba(0.75, 0.75, 0.85, 0.8)
        ctx.select_font_face("Consolas", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)
        ctx.set_font_size(12.0)
        for i, line in enumerate(lines):
            ctx.move_to(20.0, 68.0 + i * 20.0)
            ctx.show_text(line)

        ctx.restore()

    def _rounded_rect(self, ctx: Any, x: float, y: float, w: float, h: float, r: float) -> None:
        r = min(r, w * 0.5, h * 0.5)
        ctx.new_path()
        ctx.arc(x + w - r, y + r, r, -math.pi * 0.5, 0)
        ctx.arc(x + w - r, y + h - r, r, 0, math.pi * 0.5)
        ctx.arc(x + r, y + h - r, r, math.pi * 0.5, math.pi)
        ctx.arc(x + r, y + r, r, math.pi, math.pi * 1.5)
        ctx.close_path()
