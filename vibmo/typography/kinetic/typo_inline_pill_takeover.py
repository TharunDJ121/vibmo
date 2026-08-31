"""
✦ Vibmo Typography: Inline Pill Takeover & Strikethrough Replace
Inspired by Remocn inline-pill-takeover & strikethrough-replace.
"""

from __future__ import annotations

import math
from typing import Any, List, Optional, Tuple, Union
import cairo

from vibmo.core.color import Color, colors
from vibmo.core.signal import Signal, AnimationAction
from vibmo.core.easing import Ease
from vibmo.scene.node import Node
from vibmo.timeline.scheduler import all as sched_all, sequence as sched_seq


class InlinePillTakeoverText(Node):
    """
    Renders a sentence where a highlighted focal word is dynamically wrapped in an animated accent pill.
    """
    def __init__(
        self,
        before_text: str = "Build videos with ",
        pill_text: str = "zero boilerplate",
        after_text: str = " in seconds.",
        font_size: float = 36.0,
        font_family: str = "Inter",
        text_color: Color = colors.WHITE,
        pill_color: Color = colors.CYAN,
        pill_text_color: Color = colors.DARK_NAVY,
        **kwargs: Any,
    ):
        super().__init__(**kwargs)
        self.before_text = before_text
        self.pill_text = pill_text
        self.after_text = after_text
        self.font_size = Signal(float(font_size), f"{self.name}.font_size")
        self.font_family = font_family
        self.text_color = Signal(text_color, f"{self.name}.text_color")
        self.pill_color = Signal(pill_color, f"{self.name}.pill_color")
        self.pill_text_color = Signal(pill_text_color, f"{self.name}.pill_text_color")
        self.pill_progress = Signal(0.0, f"{self.name}.pill_progress")

    def expand_pill(self, duration: float = 0.8, ease: Any = Ease.out_expo) -> AnimationAction:
        """Expands the accent pill container around the keyword."""
        return self.pill_progress.to(1.0, duration=duration, ease=ease)

    def draw(self, ctx: Any, time: float = 0.0) -> None:
        prog = self.pill_progress.get(time)
        fs = self.font_size.get(time)
        tc = self.text_color.get(time)
        pc = self.pill_color.get(time)
        ptc = self.pill_text_color.get(time)

        ctx.save()
        ctx.select_font_face(self.font_family, cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
        ctx.set_font_size(fs)

        # 1. Measure text parts
        ext_before = ctx.text_extents(self.before_text)
        ext_pill = ctx.text_extents(self.pill_text)
        ext_after = ctx.text_extents(self.after_text)

        before_w = ext_before.x_advance
        pill_w = ext_pill.x_advance
        after_w = ext_after.x_advance

        # 2. Draw 'before' text
        ctx.set_source_rgba(tc.r, tc.g, tc.b, tc.a)
        ctx.move_to(0, fs * 0.95)
        ctx.show_text(self.before_text)

        # 3. Draw Pill background
        pill_pad_x = 16.0 * prog
        pill_pad_y = 8.0 * prog
        pill_x = before_w - (pill_pad_x * 0.5)
        pill_y = (fs * 0.95) - ext_pill.height - (pill_pad_y * 0.5) - 4.0
        pill_total_w = pill_w + pill_pad_x
        pill_total_h = ext_pill.height + pill_pad_y + 8.0
        radius = pill_total_h * 0.5

        if prog > 0.01:
            ctx.set_source_rgba(pc.r, pc.g, pc.b, pc.a * prog)
            # Rounded pill rectangle
            ctx.new_sub_path()
            ctx.arc(pill_x + pill_total_w - radius, pill_y + radius, radius, -math.pi / 2, math.pi / 2)
            ctx.arc(pill_x + radius, pill_y + radius, radius, math.pi / 2, 3 * math.pi / 2)
            ctx.close_path()
            ctx.fill()

        # 4. Draw Pill text
        cur_pill_text_color = Color.lerp(tc, ptc, prog) if hasattr(Color, 'lerp') else (ptc if prog > 0.5 else tc)
        ctx.set_source_rgba(cur_pill_text_color.r, cur_pill_text_color.g, cur_pill_text_color.b, tc.a)
        ctx.move_to(before_w, fs * 0.95)
        ctx.show_text(self.pill_text)

        # 5. Draw 'after' text
        ctx.set_source_rgba(tc.r, tc.g, tc.b, tc.a)
        ctx.move_to(before_w + pill_w + (pill_pad_x * 0.5), fs * 0.95)
        ctx.show_text(self.after_text)

        ctx.restore()
        super().draw(ctx, time)


class StrikethroughReplaceText(Node):
    """
    Shows an obsolete phrase struck through with a red line and replaced with the new capability.
    """
    def __init__(
        self,
        old_text: str = "Manual video editing",
        new_text: str = "Automated AI code",
        font_size: float = 38.0,
        font_family: str = "Inter",
        text_color: Color = colors.WHITE,
        strike_color: Color = colors.ROSE,
        new_color: Color = colors.EMERALD,
        **kwargs: Any,
    ):
        super().__init__(**kwargs)
        self.old_text = old_text
        self.new_text = new_text
        self.font_size = Signal(float(font_size), f"{self.name}.font_size")
        self.font_family = font_family
        self.text_color = Signal(text_color, f"{self.name}.text_color")
        self.strike_color = Signal(strike_color, f"{self.name}.strike_color")
        self.new_color = Signal(new_color, f"{self.name}.new_color")

        self.strike_progress = Signal(0.0, f"{self.name}.strike_progress")
        self.replace_progress = Signal(0.0, f"{self.name}.replace_progress")

    def animate_replacement(self, duration: float = 1.2) -> AnimationAction:
        """Strikes through the old text and fades in the new replacement."""
        return sched_seq(
            self.strike_progress.to(1.0, duration=duration * 0.45, ease=Ease.out_expo),
            self.replace_progress.to(1.0, duration=duration * 0.55, ease=Ease.out_back),
        )

    def draw(self, ctx: Any, time: float = 0.0) -> None:
        sp = self.strike_progress.get(time)
        rp = self.replace_progress.get(time)
        fs = self.font_size.get(time)
        tc = self.text_color.get(time)
        sc = self.strike_color.get(time)
        nc = self.new_color.get(time)

        ctx.save()
        ctx.select_font_face(self.font_family, cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
        ctx.set_font_size(fs)

        ext_old = ctx.text_extents(self.old_text)
        old_w = ext_old.x_advance

        # 1. Old text (dimmed as replaced)
        old_alpha = tc.a * (1.0 - rp * 0.6)
        ctx.set_source_rgba(tc.r, tc.g, tc.b, old_alpha)
        ctx.move_to(0, fs * 0.95)
        ctx.show_text(self.old_text)

        # 2. Strike line
        if sp > 0.01:
            ctx.set_source_rgba(sc.r, sc.g, sc.b, sc.a)
            ctx.set_line_width(3.5)
            mid_y = (fs * 0.95) - (ext_old.height * 0.4)
            ctx.move_to(0, mid_y)
            ctx.line_to(old_w * sp, mid_y)
            ctx.stroke()

        # 3. New replacement text (appears below or adjacent)
        if rp > 0.01:
            ctx.set_source_rgba(nc.r, nc.g, nc.b, nc.a * rp)
            new_y = (fs * 0.95) + (fs * 1.3 * rp)
            ctx.move_to(0, new_y)
            ctx.show_text(self.new_text)

        ctx.restore()
        super().draw(ctx, time)
