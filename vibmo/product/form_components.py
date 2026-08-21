"""
Form components (InputField, SelectBox, RadioButton, Checkbox, ToggleButton, Switch, RangeSlider)
for interactive form UI mockups and SaaS input workflows.
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


class InputField(Node):
    """
    Modern form input field with floating label, text value / placeholder, and focus glow ring.
    """

    def __init__(
        self,
        label: str = "API Key",
        value: str = "sk_live_948fbc294a...",
        placeholder: str = "Enter your key...",
        width: float = 380.0,
        height: float = 52.0,
        is_focused: bool = True,
        focus_color: Union[Color, str] = colors.INDIGO,
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)
        self.label = label
        self.value = value
        self.placeholder = placeholder
        self.width_val = float(width)
        self.height_val = float(height)
        self.is_focused = is_focused
        self.focus_color = Color.from_any(focus_color)

    def local_bounds(self, time: float = 0.0) -> Tuple[float, float, float, float]:
        return (0.0, 0.0, self.width_val, self.height_val)

    def draw(self, ctx: Any, time: float = 0.0) -> None:
        w, h = self.width_val, self.height_val
        ctx.save()
        # Input Box Background
        self._rounded_rect(ctx, 0, 0, w, h, 10.0)
        ctx.set_source_rgba(0.06, 0.09, 0.16, 0.95)
        ctx.fill_preserve()

        if self.is_focused:
            c = self.focus_color
            ctx.set_source_rgba(c.r, c.g, c.b, 0.85)
            ctx.set_line_width(2.0)
        else:
            ctx.set_source_rgba(1.0, 1.0, 1.0, 0.12)
            ctx.set_line_width(1.0)
        ctx.stroke()

        # Small Floating Label
        ctx.set_source_rgba(0.6, 0.65, 0.75, 0.8)
        ctx.select_font_face("Segoe UI", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)
        ctx.set_font_size(11.0)
        ctx.move_to(14.0, 18.0)
        ctx.show_text(self.label)

        # Input Value
        ctx.set_source_rgba(1.0, 1.0, 1.0, 0.95 if self.value else 0.4)
        ctx.select_font_face("Segoe UI", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)
        ctx.set_font_size(14.0)
        ctx.move_to(14.0, 38.0)
        ctx.show_text(self.value or self.placeholder)

        ctx.restore()

    def _rounded_rect(self, ctx: Any, x: float, y: float, w: float, h: float, r: float) -> None:
        r = min(r, w * 0.5, h * 0.5)
        ctx.new_path()
        ctx.arc(x + w - r, y + r, r, -math.pi * 0.5, 0)
        ctx.arc(x + w - r, y + h - r, r, 0, math.pi * 0.5)
        ctx.arc(x + r, y + h - r, r, math.pi * 0.5, math.pi)
        ctx.arc(x + r, y + r, r, math.pi, math.pi * 1.5)
        ctx.close_path()


class SelectBox(Node):
    """
    Rich Select / Multi-Tag picker box.
    """

    def __init__(
        self,
        tags: Sequence[str] = ("TypeScript", "Python", "Rust"),
        width: float = 340.0,
        height: float = 48.0,
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)
        self.tags = list(tags)
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
        ctx.set_source_rgba(1.0, 1.0, 1.0, 0.12)
        ctx.set_line_width(1.0)
        ctx.stroke()

        # Render Pill Badges
        cur_x = 10.0
        ctx.select_font_face("Segoe UI", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
        ctx.set_font_size(11.0)

        for tag in self.tags:
            ext = ctx.text_extents(tag)
            pill_w = ext.width + 18.0
            pill_h = 26.0
            pill_y = (h - pill_h) * 0.5

            self._rounded_rect(ctx, cur_x, pill_y, pill_w, pill_h, 6.0)
            ctx.set_source_rgba(0.2, 0.3, 0.5, 0.8)
            ctx.fill()

            ctx.set_source_rgba(1.0, 1.0, 1.0, 0.95)
            ctx.move_to(cur_x + 9.0, pill_y + (pill_h + ext.height) * 0.5 - 1.0)
            ctx.show_text(tag)

            cur_x += pill_w + 8.0

        ctx.restore()

    def _rounded_rect(self, ctx: Any, x: float, y: float, w: float, h: float, r: float) -> None:
        r = min(r, w * 0.5, h * 0.5)
        ctx.new_path()
        ctx.arc(x + w - r, y + r, r, -math.pi * 0.5, 0)
        ctx.arc(x + w - r, y + h - r, r, 0, math.pi * 0.5)
        ctx.arc(x + r, y + h - r, r, math.pi * 0.5, math.pi)
        ctx.arc(x + r, y + r, r, math.pi, math.pi * 1.5)
        ctx.close_path()


class RadioButton(Node):
    """
    Radio Button with animated selection dot and text label.
    """

    def __init__(
        self,
        label: str = "Enterprise Plan",
        is_selected: bool = True,
        color: Union[Color, str] = colors.INDIGO,
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)
        self.label = label
        self.color = Color.from_any(color)
        self.select_progress = Signal(1.0 if is_selected else 0.0, f"{self.name}.select_progress")

    def local_bounds(self, time: float = 0.0) -> Tuple[float, float, float, float]:
        return (0.0, 0.0, 240.0, 32.0)

    def draw(self, ctx: Any, time: float = 0.0) -> None:
        p = float(self.select_progress.get(time))
        ctx.save()
        # Outer Radio Circle
        ctx.arc(14.0, 16.0, 10.0, 0, math.pi * 2)
        ctx.set_source_rgba(0.12, 0.16, 0.24, 0.9)
        ctx.fill_preserve()

        if p > 0.01:
            c = self.color
            ctx.set_source_rgba(c.r, c.g, c.b, 1.0)
            ctx.set_line_width(2.0)
            ctx.stroke()
            # Inner Dot
            ctx.arc(14.0, 16.0, 5.0 * p, 0, math.pi * 2)
            ctx.set_source_rgba(c.r, c.g, c.b, 1.0)
            ctx.fill()
        else:
            ctx.set_source_rgba(1.0, 1.0, 1.0, 0.2)
            ctx.set_line_width(1.5)
            ctx.stroke()

        # Label
        ctx.set_source_rgba(1.0, 1.0, 1.0, 0.9)
        ctx.select_font_face("Segoe UI", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)
        ctx.set_font_size(14.0)
        ctx.move_to(34.0, 21.0)
        ctx.show_text(self.label)

        ctx.restore()


class Checkbox(Node):
    """
    Checkbox component with animated checkmark draw.
    """

    def __init__(
        self,
        label: str = "Enable Cloud Sync",
        is_checked: bool = True,
        color: Union[Color, str] = colors.EMERALD,
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)
        self.label = label
        self.color = Color.from_any(color)
        self.check_progress = Signal(1.0 if is_checked else 0.0, f"{self.name}.check_progress")

    def toggle(self, duration: float = 0.5) -> AnimationAction:
        target = 0.0 if float(self.check_progress.get()) > 0.5 else 1.0
        return self.check_progress.to(target, duration=duration, ease=Ease.out_back)

    def local_bounds(self, time: float = 0.0) -> Tuple[float, float, float, float]:
        return (0.0, 0.0, 240.0, 32.0)

    def draw(self, ctx: Any, time: float = 0.0) -> None:
        p = float(self.check_progress.get(time))
        ctx.save()
        # Checkbox Box
        self._rounded_rect(ctx, 4.0, 6.0, 20.0, 20.0, 6.0)
        c = self.color
        if p > 0.01:
            ctx.set_source_rgba(c.r, c.g, c.b, p)
            ctx.fill()

            # Checkmark path
            ctx.set_source_rgba(1.0, 1.0, 1.0, 1.0)
            ctx.set_line_width(2.2)
            ctx.set_line_cap(cairo.LINE_CAP_ROUND)
            ctx.set_line_join(cairo.LINE_JOIN_ROUND)
            ctx.move_to(9.0, 16.0)
            ctx.line_to(13.0, 20.0)
            ctx.line_to(19.0, 12.0)
            ctx.stroke()
        else:
            ctx.set_source_rgba(0.12, 0.16, 0.24, 0.8)
            ctx.fill_preserve()
            ctx.set_source_rgba(1.0, 1.0, 1.0, 0.2)
            ctx.set_line_width(1.5)
            ctx.stroke()

        # Label
        ctx.set_source_rgba(1.0, 1.0, 1.0, 0.9)
        ctx.select_font_face("Segoe UI", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)
        ctx.set_font_size(14.0)
        ctx.move_to(34.0, 21.0)
        ctx.show_text(self.label)

        ctx.restore()

    def _rounded_rect(self, ctx: Any, x: float, y: float, w: float, h: float, r: float) -> None:
        r = min(r, w * 0.5, h * 0.5)
        ctx.new_path()
        ctx.arc(x + w - r, y + r, r, -math.pi * 0.5, 0)
        ctx.arc(x + w - r, y + h - r, r, 0, math.pi * 0.5)
        ctx.arc(x + r, y + h - r, r, math.pi * 0.5, math.pi)
        ctx.arc(x + r, y + r, r, math.pi, math.pi * 1.5)
        ctx.close_path()


class ToggleButton(Node):
    """
    Multi-state segmented toggle button group.
    """

    def __init__(
        self,
        options: Sequence[str] = ("Day", "Week", "Month", "Year"),
        selected_index: int = 1,
        width: float = 280.0,
        height: float = 38.0,
        color: Union[Color, str] = colors.INDIGO,
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)
        self.options = list(options)
        self.selected_index = selected_index
        self.width_val = float(width)
        self.height_val = float(height)
        self.color = Color.from_any(color)

    def local_bounds(self, time: float = 0.0) -> Tuple[float, float, float, float]:
        return (0.0, 0.0, self.width_val, self.height_val)

    def draw(self, ctx: Any, time: float = 0.0) -> None:
        n = len(self.options)
        if n == 0:
            return
        w, h = self.width_val, self.height_val
        opt_w = w / n

        ctx.save()
        self._rounded_rect(ctx, 0, 0, w, h, 8.0)
        ctx.set_source_rgba(0.08, 0.12, 0.20, 0.95)
        ctx.fill()

        # Active Option
        sel_x = self.selected_index * opt_w
        self._rounded_rect(ctx, sel_x + 2.0, 2.0, opt_w - 4.0, h - 4.0, 6.0)
        c = self.color
        ctx.set_source_rgba(c.r, c.g, c.b, 1.0)
        ctx.fill()

        # Option text
        ctx.select_font_face("Segoe UI", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
        ctx.set_font_size(12.0)
        for i, opt in enumerate(self.options):
            ext = ctx.text_extents(opt)
            tx = i * opt_w + opt_w * 0.5 - ext.width * 0.5
            ty = (h + ext.height) * 0.5 - 1.0
            ctx.set_source_rgba(1.0, 1.0, 1.0, 1.0 if i == self.selected_index else 0.7)
            ctx.move_to(tx, ty)
            ctx.show_text(opt)

        ctx.restore()

    def _rounded_rect(self, ctx: Any, x: float, y: float, w: float, h: float, r: float) -> None:
        r = min(r, w * 0.5, h * 0.5)
        ctx.new_path()
        ctx.arc(x + w - r, y + r, r, -math.pi * 0.5, 0)
        ctx.arc(x + w - r, y + h - r, r, 0, math.pi * 0.5)
        ctx.arc(x + r, y + h - r, r, math.pi * 0.5, math.pi)
        ctx.arc(x + r, y + r, r, math.pi, math.pi * 1.5)
        ctx.close_path()


class Switch(Node):
    """
    iOS-style sleek pill switch with smooth spring toggle knob animation.
    """

    def __init__(
        self,
        is_on: bool = True,
        width: float = 56.0,
        height: float = 32.0,
        active_color: Union[Color, str] = colors.EMERALD,
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)
        self.width_val = float(width)
        self.height_val = float(height)
        self.active_color = Color.from_any(active_color)
        self.state_progress = Signal(1.0 if is_on else 0.0, f"{self.name}.state_progress")

    def toggle(self, duration: float = 0.5) -> AnimationAction:
        target = 0.0 if float(self.state_progress.get()) > 0.5 else 1.0
        return self.state_progress.to(target, duration=duration, ease=Ease.out_back)

    def local_bounds(self, time: float = 0.0) -> Tuple[float, float, float, float]:
        return (0.0, 0.0, self.width_val, self.height_val)

    def draw(self, ctx: Any, time: float = 0.0) -> None:
        w, h = self.width_val, self.height_val
        p = max(0.0, min(1.0, float(self.state_progress.get(time))))

        ctx.save()
        # Track capsule
        self._rounded_rect(ctx, 0, 0, w, h, h * 0.5)
        c = self.active_color
        # Interpolate track color
        tr = 0.15 * (1.0 - p) + c.r * p
        tg = 0.20 * (1.0 - p) + c.g * p
        tb = 0.30 * (1.0 - p) + c.b * p
        ctx.set_source_rgba(tr, tg, tb, 1.0)
        ctx.fill()

        # Sliding Knob
        knob_r = (h - 6.0) * 0.5
        knob_x = 3.0 + knob_r + p * (w - 6.0 - knob_r * 2)
        ctx.arc(knob_x, h * 0.5, knob_r, 0, math.pi * 2)
        ctx.set_source_rgba(1.0, 1.0, 1.0, 1.0)
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


class RangeSlider(Node):
    """
    Dual-handle min-max range slider.
    """

    def __init__(
        self,
        min_val: float = 0.2,
        max_val: float = 0.8,
        width: float = 320.0,
        height: float = 36.0,
        color: Union[Color, str] = colors.INDIGO,
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)
        self.min_val = min_val
        self.max_val = max_val
        self.width_val = float(width)
        self.height_val = float(height)
        self.color = Color.from_any(color)

    def local_bounds(self, time: float = 0.0) -> Tuple[float, float, float, float]:
        return (0.0, 0.0, self.width_val, self.height_val)

    def draw(self, ctx: Any, time: float = 0.0) -> None:
        w, h = self.width_val, self.height_val
        track_h = 6.0
        track_y = (h - track_h) * 0.5
        thumb_r = 9.0

        ctx.save()
        # Track base
        ctx.set_source_rgba(0.18, 0.22, 0.32, 1.0)
        ctx.rectangle(0, track_y, w, track_h)
        ctx.fill()

        # Active Range
        x1 = thumb_r + self.min_val * (w - thumb_r * 2)
        x2 = thumb_r + self.max_val * (w - thumb_r * 2)
        c = self.color
        ctx.set_source_rgba(c.r, c.g, c.b, 1.0)
        ctx.rectangle(x1, track_y, x2 - x1, track_h)
        ctx.fill()

        # Thumbs
        for tx in (x1, x2):
            ctx.arc(tx, h * 0.5, thumb_r, 0, math.pi * 2)
            ctx.set_source_rgba(1.0, 1.0, 1.0, 1.0)
            ctx.fill()
            ctx.set_source_rgba(c.r, c.g, c.b, 1.0)
            ctx.set_line_width(2.0)
            ctx.stroke()

        ctx.restore()
