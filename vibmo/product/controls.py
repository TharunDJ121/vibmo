"""
Interactive Animated Form Controls: Toggle Switches, Checkboxes, Sliders, Progress Bars, and Rating Stars.
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


class ToggleSwitch(Node):
    """
    iOS / macOS Style Animated Toggle Switch with smooth spring thumb slider.
    """

    def __init__(
        self,
        checked: bool = True,
        width: float = 52.0,
        height: float = 30.0,
        active_color: Optional[Union[Color, str]] = colors.EMERALD,
        inactive_color: Optional[Union[Color, str]] = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)
        self.width_val = float(width)
        self.height_val = float(height)
        self.active_color = Color.from_any(active_color) if active_color else colors.EMERALD
        self.inactive_color = Color.from_any(inactive_color) if inactive_color else Color.hex("#334155")

        self.state_progress = Signal(1.0 if checked else 0.0, f"{self.name}.state")

    def toggle(
        self,
        on: bool = True,
        duration: float = 0.4,
        ease: Optional[EasingFunc] = None,
        delay: float = 0.0,
    ) -> AnimationAction:
        """Animates toggle thumb slide between on and off states."""
        target = 1.0 if on else 0.0
        return self.state_progress.to(target, duration=duration, ease=ease or Ease.spring(180, 14), delay=delay)

    def local_bounds(self, time: float = 0.0) -> Tuple[float, float, float, float]:
        return (0.0, 0.0, self.width_val, self.height_val)

    def draw(self, ctx: Any, time: float = 0.0) -> None:
        w, h = self.width_val, self.height_val
        r = h * 0.5
        prog = max(0.0, min(1.0, float(self.state_progress.get(time))))

        # Interpolate track background color
        c_on = self.active_color
        c_off = self.inactive_color
        tr = c_off.r + (c_on.r - c_off.r) * prog
        tg = c_off.g + (c_on.g - c_off.g) * prog
        tb = c_off.b + (c_on.b - c_off.b) * prog

        ctx.save()
        # 1. Capsule Track
        ctx.new_sub_path()
        ctx.arc(w - r, r, r, -math.pi / 2, math.pi / 2)
        ctx.arc(r, r, r, math.pi / 2, 3 * math.pi / 2)
        ctx.close_path()

        ctx.set_source_rgba(tr, tg, tb, 0.95)
        ctx.fill()

        # 2. Sliding Thumb Knob
        thumb_r = r - 3.0
        thumb_x = r + (w - 2.0 * r) * prog
        ctx.arc(thumb_x, r, thumb_r, 0, math.pi * 2)
        ctx.set_source_rgba(1.0, 1.0, 1.0, 1.0)
        ctx.fill_preserve()
        ctx.set_source_rgba(0.0, 0.0, 0.0, 0.15)
        ctx.set_line_width(1.0)
        ctx.stroke()

        ctx.restore()


class Checkbox(Node):
    """
    Animated Checkbox with spring border pulse and SVG checkmark draw.
    """

    def __init__(
        self,
        checked: bool = True,
        size: float = 28.0,
        color: Optional[Union[Color, str]] = colors.INDIGO,
        corner_radius: float = 6.0,
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)
        self.size_val = float(size)
        self.color = Color.from_any(color) if color else colors.INDIGO
        self.corner_radius = float(corner_radius)

        self.check_progress = Signal(1.0 if checked else 0.0, f"{self.name}.checked")

    def check(
        self,
        duration: float = 0.5,
        ease: Optional[EasingFunc] = None,
        delay: float = 0.0,
    ) -> AnimationAction:
        """Animates checkmark reveal."""
        return self.check_progress.to(1.0, duration=duration, ease=ease or Ease.spring(160, 12), delay=delay)

    def uncheck(
        self,
        duration: float = 0.3,
        ease: Optional[EasingFunc] = None,
        delay: float = 0.0,
    ) -> AnimationAction:
        """Animates checkmark removal."""
        return self.check_progress.to(0.0, duration=duration, ease=ease or Ease.out_quad, delay=delay)

    def local_bounds(self, time: float = 0.0) -> Tuple[float, float, float, float]:
        return (0.0, 0.0, self.size_val, self.size_val)

    def draw(self, ctx: Any, time: float = 0.0) -> None:
        sz = self.size_val
        r = self.corner_radius
        prog = max(0.0, min(1.0, float(self.check_progress.get(time))))
        c = self.color

        ctx.save()
        # Box background
        ctx.new_sub_path()
        ctx.arc(sz - r, r, r, -math.pi / 2, 0)
        ctx.arc(sz - r, sz - r, r, 0, math.pi / 2)
        ctx.arc(r, sz - r, r, math.pi / 2, math.pi)
        ctx.arc(r, r, r, math.pi, 3 * math.pi / 2)
        ctx.close_path()

        if prog > 0.01:
            ctx.set_source_rgba(c.r, c.g, c.b, prog)
            ctx.fill_preserve()
        ctx.set_source_rgba(c.r, c.g, c.b, 0.8)
        ctx.set_line_width(2.0)
        ctx.stroke()

        # Checkmark trace
        if prog > 0.05:
            ctx.set_source_rgba(1.0, 1.0, 1.0, prog)
            ctx.set_line_width(2.5)
            ctx.set_line_cap(cairo.LINE_CAP_ROUND)
            ctx.set_line_join(cairo.LINE_JOIN_ROUND)

            # (0.28, 0.52) -> (0.45, 0.70) -> (0.75, 0.32)
            p1 = (sz * 0.26, sz * 0.52)
            p2 = (sz * 0.44, sz * 0.70)
            p3 = (sz * 0.76, sz * 0.32)

            ctx.move_to(p1[0], p1[1])
            ctx.line_to(p2[0], p2[1])
            ctx.line_to(p3[0], p3[1])
            ctx.stroke()

        ctx.restore()


class ProgressBar(Node):
    """
    Linear Progress Bar with glowing gradient fill and animated percentage ticker.
    """

    def __init__(
        self,
        progress: float = 0.65,
        width: float = 380.0,
        height: float = 12.0,
        color: Optional[Union[Color, str]] = colors.CYAN,
        corner_radius: float = 6.0,
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)
        self.width_val = float(width)
        self.height_val = float(height)
        self.color = Color.from_any(color) if color else colors.CYAN
        self.corner_radius = float(corner_radius)

        self.progress_signal = Signal(float(progress), f"{self.name}.progress")

    def progress_to(
        self,
        target: float,
        duration: float = 1.2,
        ease: Optional[EasingFunc] = None,
        delay: float = 0.0,
    ) -> AnimationAction:
        """Animates progress track filling to target fraction (0.0 to 1.0)."""
        return self.progress_signal.to(float(target), duration=duration, ease=ease or Ease.out_expo, delay=delay)

    def local_bounds(self, time: float = 0.0) -> Tuple[float, float, float, float]:
        return (0.0, 0.0, self.width_val, self.height_val)

    def draw(self, ctx: Any, time: float = 0.0) -> None:
        w, h = self.width_val, self.height_val
        r = min(self.corner_radius, h * 0.5)
        prog = max(0.0, min(1.0, float(self.progress_signal.get(time))))
        c = self.color

        ctx.save()
        # 1. Background Track
        ctx.new_sub_path()
        ctx.arc(w - r, r, r, -math.pi / 2, math.pi / 2)
        ctx.arc(r, r, r, math.pi / 2, 3 * math.pi / 2)
        ctx.close_path()
        ctx.set_source_rgba(0.15, 0.2, 0.3, 0.6)
        ctx.fill()

        # 2. Active Progress Fill
        fill_w = max(h, w * prog)
        if prog > 0.01:
            ctx.new_sub_path()
            ctx.arc(fill_w - r, r, r, -math.pi / 2, math.pi / 2)
            ctx.arc(r, r, r, math.pi / 2, 3 * math.pi / 2)
            ctx.close_path()

            pat = cairo.LinearGradient(0, 0, fill_w, 0)
            pat.add_color_stop_rgba(0.0, c.r * 0.7, c.g * 0.7, c.b * 0.7, 0.95)
            pat.add_color_stop_rgba(1.0, c.r, c.g, c.b, 1.0)
            ctx.set_source(pat)
            ctx.fill()

        ctx.restore()


class RatingStars(Node):
    """
    5-Star Rating component with glowing gold stars and staggered pop animation.
    """

    def __init__(
        self,
        rating: float = 4.8,
        star_size: float = 24.0,
        gap: float = 8.0,
        color: Optional[Union[Color, str]] = colors.AMBER,
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)
        self.rating = float(rating)
        self.star_size = float(star_size)
        self.gap = float(gap)
        self.color = Color.from_any(color) if color else colors.AMBER

        self.reveal_progress = Signal(1.0, f"{self.name}.reveal")

    def local_bounds(self, time: float = 0.0) -> Tuple[float, float, float, float]:
        w = 5 * self.star_size + 4 * self.gap
        return (0.0, 0.0, w, self.star_size)

    def draw(self, ctx: Any, time: float = 0.0) -> None:
        sz = self.star_size
        c = self.color
        r_outer = sz * 0.5
        r_inner = r_outer * 0.45

        ctx.save()
        for i in range(5):
            cx = i * (sz + self.gap) + r_outer
            cy = r_outer
            star_fill = max(0.0, min(1.0, self.rating - i))

            ctx.new_path()
            for pt in range(10):
                ang = (pt * math.pi / 5.0) - math.pi * 0.5
                r = r_outer if pt % 2 == 0 else r_inner
                px = cx + math.cos(ang) * r
                py = cy + math.sin(ang) * r
                if pt == 0:
                    ctx.move_to(px, py)
                else:
                    ctx.line_to(px, py)
            ctx.close_path()

            if star_fill >= 0.8:
                ctx.set_source_rgba(c.r, c.g, c.b, 0.95)
                ctx.fill()
            else:
                ctx.set_source_rgba(0.3, 0.35, 0.45, 0.6)
                ctx.fill()

        ctx.restore()
