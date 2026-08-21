"""
UI Component Library (ProgressBar, Slider, Tabs, Accordion, Modal, Dropdown, Breadcrumbs, Pagination)
for modern web and mobile UI design mockups and product demos.
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
from vibmo.layout.container import FlexContainer
from vibmo.spatial.shadows import DropShadow


class ProgressBar(Node):
    """
    Linear animated progress bar with glowing fill, gradient, and percentage label.
    """

    def __init__(
        self,
        progress: float = 0.65,
        width: float = 340.0,
        height: float = 12.0,
        color: Union[Color, str] = colors.EMERALD,
        track_color: Optional[Union[Color, str]] = None,
        corner_radius: float = 6.0,
        show_label: bool = False,
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)
        self.width_val = float(width)
        self.height_val = float(height)
        self.fill_color = Color.from_any(color)
        self.track_color = Color.from_any(track_color) if track_color else Color.hex("#1e293b")
        self.corner_radius = float(corner_radius)
        self.show_label = show_label
        self.progress = Signal(float(progress), f"{self.name}.progress")

    def animate_to(self, target: float, duration: float = 1.2, ease: Optional[EasingFunc] = None) -> AnimationAction:
        return self.progress.to(target, duration=duration, ease=ease or Ease.out_expo)

    def local_bounds(self, time: float = 0.0) -> Tuple[float, float, float, float]:
        return (0.0, 0.0, self.width_val, self.height_val + (24.0 if self.show_label else 0.0))

    def draw(self, ctx: Any, time: float = 0.0) -> None:
        w = self.width_val
        h = self.height_val
        p = max(0.0, min(1.0, float(self.progress.get(time))))

        ctx.save()
        # Track background
        self._rounded_rect(ctx, 0, 0, w, h, self.corner_radius)
        ctx.set_source_rgba(self.track_color.r, self.track_color.g, self.track_color.b, self.track_color.a)
        ctx.fill()

        # Filled bar
        fill_w = max(h, w * p)
        if p > 0.01:
            self._rounded_rect(ctx, 0, 0, fill_w, h, self.corner_radius)
            c = self.fill_color
            ctx.set_source_rgba(c.r, c.g, c.b, c.a)
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


class Slider(Node):
    """
    Range slider component with filled active track and glowing thumb knob.
    """

    def __init__(
        self,
        value: float = 0.5,
        width: float = 300.0,
        height: float = 36.0,
        color: Union[Color, str] = colors.INDIGO,
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)
        self.width_val = float(width)
        self.height_val = float(height)
        self.color = Color.from_any(color)
        self.value = Signal(float(value), f"{self.name}.value")

    def slide_to(self, target: float, duration: float = 1.0) -> AnimationAction:
        return self.value.to(target, duration=duration, ease=Ease.out_back)

    def local_bounds(self, time: float = 0.0) -> Tuple[float, float, float, float]:
        return (0.0, 0.0, self.width_val, self.height_val)

    def draw(self, ctx: Any, time: float = 0.0) -> None:
        w = self.width_val
        h = self.height_val
        val = max(0.0, min(1.0, float(self.value.get(time))))
        track_h = 6.0
        track_y = (h - track_h) * 0.5
        thumb_r = 10.0
        thumb_x = thumb_r + val * (w - thumb_r * 2)

        ctx.save()
        # Track base
        ctx.set_source_rgba(0.2, 0.25, 0.35, 1.0)
        ctx.rectangle(0, track_y, w, track_h)
        ctx.fill()

        # Filled portion
        c = self.color
        ctx.set_source_rgba(c.r, c.g, c.b, 1.0)
        ctx.rectangle(0, track_y, thumb_x, track_h)
        ctx.fill()

        # Thumb Knob with glow
        ctx.set_source_rgba(c.r, c.g, c.b, 0.4)
        ctx.arc(thumb_x, h * 0.5, thumb_r * 1.5, 0, math.pi * 2)
        ctx.fill()

        ctx.set_source_rgba(1.0, 1.0, 1.0, 1.0)
        ctx.arc(thumb_x, h * 0.5, thumb_r, 0, math.pi * 2)
        ctx.fill()
        ctx.set_source_rgba(c.r, c.g, c.b, 1.0)
        ctx.set_line_width(2.0)
        ctx.stroke()

        ctx.restore()


class Tabs(Node):
    """
    Segmented Tab Bar control with animated sliding active pill indicator.
    """

    def __init__(
        self,
        items: Sequence[str] = ("Overview", "Analytics", "Settings", "Billing"),
        selected_index: int = 0,
        width: float = 460.0,
        height: float = 44.0,
        active_color: Union[Color, str] = colors.INDIGO,
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)
        self.items = list(items)
        self.width_val = float(width)
        self.height_val = float(height)
        self.active_color = Color.from_any(active_color)
        self.selected_index = Signal(float(selected_index), f"{self.name}.selected_index")

    def select(self, index: int, duration: float = 0.6) -> AnimationAction:
        return self.selected_index.to(float(index), duration=duration, ease=Ease.out_back)

    def local_bounds(self, time: float = 0.0) -> Tuple[float, float, float, float]:
        return (0.0, 0.0, self.width_val, self.height_val)

    def draw(self, ctx: Any, time: float = 0.0) -> None:
        n = len(self.items)
        if n == 0:
            return
        w = self.width_val
        h = self.height_val
        tab_w = (w - 8.0) / n
        idx = float(self.selected_index.get(time))
        pill_x = 4.0 + idx * tab_w

        ctx.save()
        # Outer bar container
        self._rounded_rect(ctx, 0, 0, w, h, 12.0)
        ctx.set_source_rgba(0.08, 0.12, 0.20, 0.9)
        ctx.fill_preserve()
        ctx.set_source_rgba(1.0, 1.0, 1.0, 0.1)
        ctx.set_line_width(1.0)
        ctx.stroke()

        # Active Sliding Pill
        self._rounded_rect(ctx, pill_x, 4.0, tab_w, h - 8.0, 8.0)
        c = self.active_color
        ctx.set_source_rgba(c.r, c.g, c.b, 0.95)
        ctx.fill()

        # Labels
        ctx.select_font_face("Segoe UI", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
        ctx.set_font_size(13.0)
        for i, item in enumerate(self.items):
            is_active = abs(i - idx) < 0.5
            tx = 4.0 + i * tab_w + tab_w * 0.5
            ext = ctx.text_extents(item)
            if is_active:
                ctx.set_source_rgba(1.0, 1.0, 1.0, 1.0)
            else:
                ctx.set_source_rgba(0.6, 0.65, 0.75, 0.8)
            ctx.move_to(tx - ext.width * 0.5, h * 0.5 + ext.height * 0.5 - 2.0)
            ctx.show_text(item)

        ctx.restore()

    def _rounded_rect(self, ctx: Any, x: float, y: float, w: float, h: float, r: float) -> None:
        r = min(r, w * 0.5, h * 0.5)
        ctx.new_path()
        ctx.arc(x + w - r, y + r, r, -math.pi * 0.5, 0)
        ctx.arc(x + w - r, y + h - r, r, 0, math.pi * 0.5)
        ctx.arc(x + r, y + h - r, r, math.pi * 0.5, math.pi)
        ctx.arc(x + r, y + r, r, math.pi, math.pi * 1.5)
        ctx.close_path()


class Accordion(Node):
    """
    Expandable accordion card with animated height transition and rotating chevron.
    """

    def __init__(
        self,
        title: str = "Frequently Asked Questions",
        content_text: str = "Vibmo renders broadcast-grade motion graphics with native GPU shaders and Python signals.",
        width: float = 480.0,
        collapsed_height: float = 54.0,
        expanded_height: float = 130.0,
        is_open: bool = False,
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)
        self.title_text = title
        self.content_text = content_text
        self.width_val = float(width)
        self.collapsed_h = float(collapsed_height)
        self.expanded_h = float(expanded_height)
        self.open_progress = Signal(1.0 if is_open else 0.0, f"{self.name}.open_progress")

    def toggle(self, duration: float = 0.8) -> AnimationAction:
        cur = float(self.open_progress.get())
        target = 0.0 if cur > 0.5 else 1.0
        return self.open_progress.to(target, duration=duration, ease=Ease.out_expo)

    def local_bounds(self, time: float = 0.0) -> Tuple[float, float, float, float]:
        p = float(self.open_progress.get(time))
        h = self.collapsed_h + p * (self.expanded_h - self.collapsed_h)
        return (0.0, 0.0, self.width_val, h)

    def draw(self, ctx: Any, time: float = 0.0) -> None:
        w = self.width_val
        p = float(self.open_progress.get(time))
        h = self.collapsed_h + p * (self.expanded_h - self.collapsed_h)

        ctx.save()
        # Card body
        self._rounded_rect(ctx, 0, 0, w, h, 12.0)
        ctx.set_source_rgba(0.08, 0.12, 0.20, 0.9)
        ctx.fill_preserve()
        ctx.set_source_rgba(1.0, 1.0, 1.0, 0.12)
        ctx.set_line_width(1.0)
        ctx.stroke()

        # Header Title
        ctx.set_source_rgba(1.0, 1.0, 1.0, 0.95)
        ctx.select_font_face("Segoe UI", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
        ctx.set_font_size(15.0)
        ctx.move_to(20.0, 32.0)
        ctx.show_text(self.title_text)

        # Rotating Chevron
        chev_x = w - 28.0
        chev_y = 28.0
        ctx.save()
        ctx.translate(chev_x, chev_y)
        ctx.rotate(p * math.pi)  # 0 to 180 deg
        ctx.set_source_rgba(0.7, 0.75, 0.85, 0.9)
        ctx.set_line_width(2.0)
        ctx.move_to(-5, -3)
        ctx.line_to(0, 3)
        ctx.line_to(5, -3)
        ctx.stroke()
        ctx.restore()

        # Expanded Content (clipped)
        if p > 0.05:
            ctx.set_source_rgba(0.7, 0.75, 0.85, p)
            ctx.select_font_face("Segoe UI", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)
            ctx.set_font_size(13.0)
            ctx.move_to(20.0, 68.0)
            ctx.show_text(self.content_text[:int(len(self.content_text) * min(1.0, p * 1.5))])

        ctx.restore()

    def _rounded_rect(self, ctx: Any, x: float, y: float, w: float, h: float, r: float) -> None:
        r = min(r, w * 0.5, h * 0.5)
        ctx.new_path()
        ctx.arc(x + w - r, y + r, r, -math.pi * 0.5, 0)
        ctx.arc(x + w - r, y + h - r, r, 0, math.pi * 0.5)
        ctx.arc(x + r, y + h - r, r, math.pi * 0.5, math.pi)
        ctx.arc(x + r, y + r, r, math.pi, math.pi * 1.5)
        ctx.close_path()


class Modal(Node):
    """
    Center Glassmorphism Modal Dialog with title, close button, and action buttons.
    """

    def __init__(
        self,
        title: str = "Confirm Deployment",
        description: str = "Are you sure you want to push production changes to 24 edge nodes?",
        width: float = 520.0,
        height: float = 260.0,
        confirm_label: str = "Deploy Now",
        cancel_label: str = "Cancel",
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)
        self.title_text = title
        self.description_text = description
        self.width_val = float(width)
        self.height_val = float(height)
        self.confirm_label = confirm_label
        self.cancel_label = cancel_label
        self.shadow = DropShadow.elevated(blur=48.0, offset=(0, 20), color=Color.BLACK.with_alpha(0.7))

    def local_bounds(self, time: float = 0.0) -> Tuple[float, float, float, float]:
        return (0.0, 0.0, self.width_val, self.height_val)

    def draw(self, ctx: Any, time: float = 0.0) -> None:
        w = self.width_val
        h = self.height_val

        ctx.save()
        # Card Body
        self._rounded_rect(ctx, 0, 0, w, h, 20.0)
        ctx.set_source_rgba(0.08, 0.12, 0.22, 0.95)
        ctx.fill_preserve()
        ctx.set_source_rgba(1.0, 1.0, 1.0, 0.15)
        ctx.set_line_width(1.5)
        ctx.stroke()

        # Title
        ctx.set_source_rgba(1.0, 1.0, 1.0, 0.95)
        ctx.select_font_face("Segoe UI", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
        ctx.set_font_size(18.0)
        ctx.move_to(28.0, 48.0)
        ctx.show_text(self.title_text)

        # Description
        ctx.set_source_rgba(0.7, 0.75, 0.85, 0.9)
        ctx.select_font_face("Segoe UI", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)
        ctx.set_font_size(14.0)
        ctx.move_to(28.0, 88.0)
        ctx.show_text(self.description_text)

        # Action Buttons
        btn_y = h - 64.0
        btn_h = 40.0
        
        # Confirm button (Indigo)
        conf_w = 120.0
        conf_x = w - 28.0 - conf_w
        self._rounded_rect(ctx, conf_x, btn_y, conf_w, btn_h, 8.0)
        ctx.set_source_rgba(0.39, 0.40, 0.95, 1.0)
        ctx.fill()
        ctx.set_source_rgba(1.0, 1.0, 1.0, 1.0)
        ctx.select_font_face("Segoe UI", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
        ctx.set_font_size(13.0)
        ext = ctx.text_extents(self.confirm_label)
        ctx.move_to(conf_x + (conf_w - ext.width) * 0.5, btn_y + (btn_h + ext.height) * 0.5 - 2.0)
        ctx.show_text(self.confirm_label)

        # Cancel button
        canc_w = 90.0
        canc_x = conf_x - 12.0 - canc_w
        self._rounded_rect(ctx, canc_x, btn_y, canc_w, btn_h, 8.0)
        ctx.set_source_rgba(0.18, 0.22, 0.32, 0.9)
        ctx.fill()
        ctx.set_source_rgba(0.8, 0.85, 0.95, 0.9)
        ext = ctx.text_extents(self.cancel_label)
        ctx.move_to(canc_x + (canc_w - ext.width) * 0.5, btn_y + (btn_h + ext.height) * 0.5 - 2.0)
        ctx.show_text(self.cancel_label)

        ctx.restore()

    def _rounded_rect(self, ctx: Any, x: float, y: float, w: float, h: float, r: float) -> None:
        r = min(r, w * 0.5, h * 0.5)
        ctx.new_path()
        ctx.arc(x + w - r, y + r, r, -math.pi * 0.5, 0)
        ctx.arc(x + w - r, y + h - r, r, 0, math.pi * 0.5)
        ctx.arc(x + r, y + h - r, r, math.pi * 0.5, math.pi)
        ctx.arc(x + r, y + r, r, math.pi, math.pi * 1.5)
        ctx.close_path()


class Dropdown(Node):
    """
    Select dropdown menu component with expandable options list.
    """

    def __init__(
        self,
        options: Sequence[str] = ("Production", "Staging", "Development"),
        selected_index: int = 0,
        width: float = 240.0,
        height: float = 42.0,
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)
        self.options = list(options)
        self.selected_index = selected_index
        self.width_val = float(width)
        self.height_val = float(height)

    def local_bounds(self, time: float = 0.0) -> Tuple[float, float, float, float]:
        return (0.0, 0.0, self.width_val, self.height_val)

    def draw(self, ctx: Any, time: float = 0.0) -> None:
        w, h = self.width_val, self.height_val
        ctx.save()
        self._rounded_rect(ctx, 0, 0, w, h, 8.0)
        ctx.set_source_rgba(0.08, 0.12, 0.20, 0.95)
        ctx.fill_preserve()
        ctx.set_source_rgba(1.0, 1.0, 1.0, 0.15)
        ctx.set_line_width(1.0)
        ctx.stroke()

        txt = self.options[self.selected_index] if self.options else ""
        ctx.set_source_rgba(1.0, 1.0, 1.0, 0.9)
        ctx.select_font_face("Segoe UI", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)
        ctx.set_font_size(13.0)
        ctx.move_to(16.0, h * 0.5 + 4.0)
        ctx.show_text(txt)

        # Chevron down
        ctx.set_source_rgba(0.6, 0.7, 0.8, 0.8)
        ctx.move_to(w - 24.0, h * 0.5 - 2.0)
        ctx.line_to(w - 18.0, h * 0.5 + 4.0)
        ctx.line_to(w - 12.0, h * 0.5 - 2.0)
        ctx.set_line_width(1.5)
        ctx.stroke()

        ctx.restore()

    def _rounded_rect(self, ctx: Any, x: float, y: float, w: float, h: float, r: float) -> None:
        r = min(r, w * 0.5, h * 0.5)
        ctx.new_path()
        ctx.arc(x + w - r, y + r, r, -math.pi * 0.5, 0)
        ctx.arc(x + w - r, y + h - r, r, 0, math.pi * 0.5)
        ctx.arc(x + r, y + h - r, r, math.pi * 0.5, math.pi)
        ctx.arc(x + r, y + r, r, math.pi, math.pi * 1.5)
        ctx.close_path()


class Breadcrumbs(Node):
    """
    Navigation breadcrumb trail with path segments and separator chevrons.
    """

    def __init__(
        self,
        paths: Sequence[str] = ("Home", "Projects", "Vibmo Studio", "Settings"),
        separator: str = "/",
        font_size: float = 14.0,
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)
        self.paths = list(paths)
        self.separator = separator
        self.font_size = float(font_size)

    def local_bounds(self, time: float = 0.0) -> Tuple[float, float, float, float]:
        return (0.0, 0.0, 400.0, 30.0)

    def draw(self, ctx: Any, time: float = 0.0) -> None:
        ctx.save()
        ctx.select_font_face("Segoe UI", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)
        ctx.set_font_size(self.font_size)

        cur_x = 0.0
        n = len(self.paths)
        for i, p in enumerate(self.paths):
            is_last = (i == n - 1)
            if is_last:
                ctx.set_source_rgba(1.0, 1.0, 1.0, 0.95)
                ctx.select_font_face("Segoe UI", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
            else:
                ctx.set_source_rgba(0.6, 0.65, 0.75, 0.8)
                ctx.select_font_face("Segoe UI", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)

            ext = ctx.text_extents(p)
            ctx.move_to(cur_x, 20.0)
            ctx.show_text(p)
            cur_x += ext.width + 10.0

            if not is_last:
                ctx.set_source_rgba(0.4, 0.45, 0.55, 0.6)
                ctx.move_to(cur_x, 20.0)
                ctx.show_text(self.separator)
                sep_ext = ctx.text_extents(self.separator)
                cur_x += sep_ext.width + 10.0

        ctx.restore()


class Pagination(Node):
    """
    Pagination controls with page buttons and active pill indicator.
    """

    def __init__(
        self,
        current_page: int = 1,
        total_pages: int = 5,
        button_size: float = 36.0,
        active_color: Union[Color, str] = colors.INDIGO,
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)
        self.current_page = current_page
        self.total_pages = total_pages
        self.button_size = float(button_size)
        self.active_color = Color.from_any(active_color)

    def local_bounds(self, time: float = 0.0) -> Tuple[float, float, float, float]:
        w = (self.total_pages + 2) * (self.button_size + 8.0)
        return (0.0, 0.0, w, self.button_size)

    def draw(self, ctx: Any, time: float = 0.0) -> None:
        bs = self.button_size
        gap = 8.0
        ctx.save()
        ctx.select_font_face("Segoe UI", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
        ctx.set_font_size(13.0)

        # Pages 1..N
        for p in range(1, self.total_pages + 1):
            bx = (p - 1) * (bs + gap)
            is_active = (p == self.current_page)

            # Button background
            self._rounded_rect(ctx, bx, 0, bs, bs, 8.0)
            if is_active:
                c = self.active_color
                ctx.set_source_rgba(c.r, c.g, c.b, 1.0)
            else:
                ctx.set_source_rgba(0.12, 0.16, 0.24, 0.8)
            ctx.fill()

            # Number text
            ctx.set_source_rgba(1.0, 1.0, 1.0, 1.0 if is_active else 0.7)
            txt = str(p)
            ext = ctx.text_extents(txt)
            ctx.move_to(bx + (bs - ext.width) * 0.5, (bs + ext.height) * 0.5 - 1.0)
            ctx.show_text(txt)

        ctx.restore()

    def _rounded_rect(self, ctx: Any, x: float, y: float, w: float, h: float, r: float) -> None:
        r = min(r, w * 0.5, h * 0.5)
        ctx.new_path()
        ctx.arc(x + w - r, y + r, r, -math.pi * 0.5, 0)
        ctx.arc(x + w - r, y + h - r, r, 0, math.pi * 0.5)
        ctx.arc(x + r, y + h - r, r, math.pi * 0.5, math.pi)
        ctx.arc(x + r, y + r, r, math.pi, math.pi * 1.5)
        ctx.close_path()
