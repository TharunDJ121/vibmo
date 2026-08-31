"""
✦ Vibmo Typography: Rolling Number Wheel & Slot Machine Counter
Inspired by Remocn rolling-number & slot-machine-roll with mechanical vertical tumbler physics.
"""

from __future__ import annotations

import math
from typing import Any, List, Optional, Tuple, Union
import cairo

from vibmo.core.color import Color, colors
from vibmo.core.signal import Signal, AnimationAction
from vibmo.core.easing import Ease
from vibmo.scene.node import Node
from vibmo.timeline.scheduler import all as sched_all


class SingleDigitTumbler(Node):
    """
    Vertical rolling column containing digits 0 through 9 with mechanical tumbler motion.
    """
    def __init__(
        self,
        font_size: float = 52.0,
        font_family: str = "Inter",
        color: Color = colors.WHITE,
        **kwargs: Any,
    ):
        super().__init__(**kwargs)
        self.font_size = Signal(float(font_size), f"{self.name}.font_size")
        self.font_family = font_family
        self.color = Signal(color, f"{self.name}.color")
        self.current_value = Signal(0.0, f"{self.name}.current_value")

    def draw(self, ctx: Any, time: float = 0.0) -> None:
        val = self.current_value.get(time)
        fs = self.font_size.get(time)
        c = self.color.get(time)

        # Height per digit slot
        slot_height = fs * 1.2
        offset_y = (val % 10.0) * slot_height

        ctx.save()

        # Mask viewport to single digit height
        ctx.rectangle(0, 0, fs * 0.7, slot_height)
        ctx.clip()

        ctx.select_font_face(self.font_family, cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
        ctx.set_font_size(fs)

        # Draw current, previous, and next digits
        int_val = int(math.floor(val))
        for d in range(int_val - 1, int_val + 3):
            digit_char = str(d % 10)
            digit_y = (d * slot_height) - (val * slot_height) + (fs * 0.95)

            # Opacity falls off towards edges of slot
            dist_from_center = abs((slot_height * 0.5) - (digit_y - fs * 0.4)) / slot_height
            alpha = max(0.0, min(1.0, 1.0 - dist_from_center * 1.5)) * c.a

            ctx.set_source_rgba(c.r, c.g, c.b, alpha)
            ctx.move_to(fs * 0.1, digit_y)
            ctx.show_text(digit_char)

        ctx.restore()
        super().draw(ctx, time)


class RollingNumberWheel(Node):
    """
    Mechanical multi-digit odometer counter with rolling tumblers, prefix, suffix, and formatting.
    """
    def __init__(
        self,
        start_val: float = 0,
        end_val: float = 1000,
        prefix: str = "$",
        suffix: str = " /mo",
        num_digits: int = 4,
        font_size: float = 52.0,
        font_family: str = "Inter",
        color: Color = colors.EMERALD,
        **kwargs: Any,
    ):
        super().__init__(**kwargs)
        self.start_val = start_val
        self.end_val = end_val
        self.prefix = prefix
        self.suffix = suffix
        self.num_digits = num_digits
        self.font_size = Signal(float(font_size), f"{self.name}.font_size")
        self.font_family = font_family
        self.color = Signal(color, f"{self.name}.color")
        self.value = Signal(float(start_val), f"{self.name}.value")

    def roll_to(self, target_value: float, duration: float = 1.8, ease: Any = Ease.out_expo) -> AnimationAction:
        """Rolls the number wheel smoothly to target numeric value."""
        return self.value.to(float(target_value), duration=duration, ease=ease)

    def draw(self, ctx: Any, time: float = 0.0) -> None:
        cur_val = self.value.get(time)
        fs = self.font_size.get(time)
        c = self.color.get(time)

        # Format string
        formatted_str = f"{self.prefix}{int(round(cur_val)):,}{self.suffix}"

        ctx.save()
        ctx.select_font_face(self.font_family, cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
        ctx.set_font_size(fs)
        ctx.set_source_rgba(c.r, c.g, c.b, c.a)

        ctx.move_to(0, fs * 0.95)
        ctx.show_text(formatted_str)
        ctx.restore()

        super().draw(ctx, time)


class SlotMachineRoller(RollingNumberWheel):
    """Alias for RollingNumberWheel with slot-machine aesthetics."""
    pass
