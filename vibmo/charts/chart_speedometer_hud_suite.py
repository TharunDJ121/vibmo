import math
from typing import Any, Optional, Tuple

from vibmo.scene.node import Node
from vibmo.core.signal import Signal
from vibmo.core.color import Color, colors
from vibmo.core.vector import Vector2D
from vibmo.core.easing import Ease

class SpeedometerNeedleGauge(Node):
    """
    A 270-degree radial speedometer gauge with animated needle and numeric tick marks.
    Features an animated needle spring sweep and numeric tick marks.
    """
    def __init__(self, min_val: float = 0, max_val: float = 100, radius: float = 100, **kwargs):
        super().__init__(**kwargs)
        self.min_val = min_val
        self.max_val = max_val
        self.radius = radius
        self.value = Signal(min_val)
        self.needle_color = colors.RED
        self.tick_color = colors.WHITE
        self.start_angle = math.pi * 0.75
        self.end_angle = math.pi * 2.25

        # Damped display value for spring sweep
        self.display_value = Signal(min_val)

    def sweep_to(self, target: float, duration: float = 1.0, delay: float = 0.0):
        """Animates the needle to the target value with a spring sweep."""
        # Set the logical value instantly
        self.value.set(target)
        # Animate the visual display value
        return self.display_value.to(target, duration=duration, delay=delay, ease=Ease.spring(stiffness=120, damping=12))

    def _val_to_angle(self, val: float) -> float:
        clamped = max(self.min_val, min(self.max_val, val))
        progress = (clamped - self.min_val) / (self.max_val - self.min_val) if self.max_val != self.min_val else 0
        return self.start_angle + progress * (self.end_angle - self.start_angle)

    def draw(self, ctx: Any, time: float = 0.0) -> None:
        # Use display_value for smooth drawing
        val = self.display_value.get(time)
        angle = self._val_to_angle(val)

        # Draw outer arc
        ctx.set_line_width(2.0)
        ctx.set_source_rgba(*self.tick_color.to_tuple_rgba())
        ctx.arc(0, 0, self.radius, self.start_angle, self.end_angle)
        ctx.stroke()

        # Draw ticks (example: 10 major ticks)
        num_ticks = 10
        for i in range(num_ticks + 1):
            tick_angle = self.start_angle + (i / num_ticks) * (self.end_angle - self.start_angle)
            ctx.move_to(math.cos(tick_angle) * (self.radius - 10), math.sin(tick_angle) * (self.radius - 10))
            ctx.line_to(math.cos(tick_angle) * self.radius, math.sin(tick_angle) * self.radius)
            ctx.stroke()

        # Draw needle
        ctx.set_source_rgba(*self.needle_color.to_tuple_rgba())
        ctx.move_to(0, 0)
        ctx.line_to(math.cos(angle) * (self.radius - 15), math.sin(angle) * (self.radius - 15))
        ctx.set_line_width(4.0)
        ctx.stroke()

        super().draw(ctx, time)


class RedlineRpmArc(Node):
    """
    Glowing redline zone with warning pulse.
    """
    def __init__(self, radius: float = 100, redline_start: float = 80, redline_end: float = 100, min_val: float = 0, max_val: float = 100, **kwargs):
        super().__init__(**kwargs)
        self.radius = radius
        self.redline_start = redline_start
        self.redline_end = redline_end
        self.min_val = min_val
        self.max_val = max_val
        self.value = Signal(min_val)
        self.base_color = colors.RED

        self.start_angle = math.pi * 0.75
        self.end_angle = math.pi * 2.25

    def _val_to_angle(self, val: float) -> float:
        clamped = max(self.min_val, min(self.max_val, val))
        progress = (clamped - self.min_val) / (self.max_val - self.min_val) if self.max_val != self.min_val else 0
        return self.start_angle + progress * (self.end_angle - self.start_angle)

    def draw(self, ctx: Any, time: float = 0.0) -> None:
        val = self.value.get(time)
        start_a = self._val_to_angle(self.redline_start)
        end_a = self._val_to_angle(self.redline_end)

        # Pulse effect
        intensity = 1.0
        if val >= self.redline_start:
            intensity = 0.5 + 0.5 * math.sin(time * 10) # Fast pulse

        color = self.base_color.with_alpha(intensity)
        ctx.set_source_rgba(*color.to_tuple_rgba())
        ctx.set_line_width(8.0)
        ctx.arc(0, 0, self.radius, start_a, end_a)
        ctx.stroke()

        super().draw(ctx, time)


class DigitalSpeedNumberTicker(Node):
    """
    Large central digital speed counter with 3-digit rolling wheel.
    """
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.value = Signal(0)
        self.color = colors.WHITE
        self.digit_width = 30
        self.digit_height = 40
        self.font_size = 36
        self.display_value = Signal(0)

    def roll_to(self, target: float, duration: float = 1.0, delay: float = 0.0):
        """Animates the rolling ticker to the target value."""
        self.value.set(target)
        return self.display_value.to(target, duration=duration, delay=delay, ease=Ease.out_expo)

    def draw(self, ctx: Any, time: float = 0.0) -> None:
        val = self.display_value.get(time)

        ctx.set_source_rgba(*self.color.to_tuple_rgba())
        ctx.select_font_face("monospace", 0, 1) # Normal, Bold
        ctx.set_font_size(self.font_size)

        # For a 3-digit rolling wheel, we draw 3 columns.
        # We calculate the continuous value for each column to simulate rolling.
        val = max(0, min(999, val))

        # Calculate digit places based on continuous value
        units = val % 10
        tens = (val / 10) % 10
        hundreds = (val / 100) % 10

        digits = [hundreds, tens, units]

        for i, place_val in enumerate(digits):
            x = (i - 1.5) * self.digit_width
            ctx.save()
            # Clip for the digit
            ctx.rectangle(x, -self.digit_height/2, self.digit_width, self.digit_height)
            ctx.clip()

            # The integer part is the primary digit, the fractional part is how far it has rolled
            current_digit = int(place_val) % 10
            next_digit = (current_digit + 1) % 10

            # We only roll when the next lower place is rolling over (between 9 and 10),
            # but for a smooth counter effect as requested "rolling wheel",
            # we can just use the fractional part of the place value directly.
            fraction = place_val - int(place_val)

            # Draw current digit moving up
            y_offset = -fraction * self.digit_height

            ctx.move_to(x + 5, self.digit_height/3 + y_offset)
            ctx.show_text(str(current_digit))

            # Draw next digit coming from below
            ctx.move_to(x + 5, self.digit_height/3 + y_offset + self.digit_height)
            ctx.show_text(str(next_digit))

            ctx.restore()

        super().draw(ctx, time)

class TurboBoostBar(Node):
    """
    Curved auxiliary boost pressure meter bar with needle.
    """
    def __init__(self, radius: float = 60, min_val: float = -1.0, max_val: float = 2.0, **kwargs):
        super().__init__(**kwargs)
        self.radius = radius
        self.min_val = min_val
        self.max_val = max_val
        self.value = Signal(0.0)
        self.display_value = Signal(0.0)
        self.color = colors.CYAN

        # Arc from bottom left to top left
        self.start_angle = math.pi * 0.8
        self.end_angle = math.pi * 1.2

    def fill_to(self, target: float, duration: float = 1.0, delay: float = 0.0):
        self.value.set(target)
        return self.display_value.to(target, duration=duration, delay=delay, ease=Ease.out_cubic)

    def _val_to_angle(self, val: float) -> float:
        clamped = max(self.min_val, min(self.max_val, val))
        progress = (clamped - self.min_val) / (self.max_val - self.min_val) if self.max_val != self.min_val else 0
        return self.start_angle + progress * (self.end_angle - self.start_angle)

    def draw(self, ctx: Any, time: float = 0.0) -> None:
        val = self.display_value.get(time)
        angle = self._val_to_angle(val)

        # Draw base arc
        ctx.set_source_rgba(*colors.SLATE_800.to_tuple_rgba())
        ctx.set_line_width(6.0)
        ctx.arc(0, 0, self.radius, self.start_angle, self.end_angle)
        ctx.stroke()

        # Draw fill arc
        if angle > self.start_angle:
            ctx.set_source_rgba(*self.color.to_tuple_rgba())
            ctx.arc(0, 0, self.radius, self.start_angle, angle)
            ctx.stroke()

        # Draw small needle
        ctx.set_source_rgba(*colors.WHITE.to_tuple_rgba())
        ctx.move_to(math.cos(angle) * (self.radius - 8), math.sin(angle) * (self.radius - 8))
        ctx.line_to(math.cos(angle) * (self.radius + 8), math.sin(angle) * (self.radius + 8))
        ctx.set_line_width(2.0)
        ctx.stroke()

        super().draw(ctx, time)
