"""
Mechanical Odometer Tumbler Typography suite.
"""

from __future__ import annotations
import math
from typing import Any, Optional
import cairo

from vibmo.scene.node import Node
from vibmo.core.signal import Signal
from vibmo.core.color import Color, colors, LinearGradient
from vibmo.typography.text import Text
from vibmo.core.easing import Ease

class VerticalRollingGlyphs(Node):
    """Continuous vertical strip of digits (0-9) transitioning with exponential ease-out deceleration."""
    def __init__(
        self,
        font_size: float = 32.0,
        font_family: str = "Inter",
        color: Any = colors.WHITE,
        radius: float = 40.0,
        **kwargs: Any
    ):
        super().__init__(**kwargs)
        self.value = Signal(0.0)
        self.font_size = font_size
        self.font_family = font_family
        self.color = Color.from_any(color)
        self.radius = radius

    def roll_to(self, target_value: float, duration: float = 2.0):
        self.value.to(target_value, duration=duration, ease=Ease.out_expo)

    def draw(self, ctx: cairo.Context, time: float) -> None:
        super().draw(ctx, time)
        current_value = self.value.get()
        ctx.select_font_face(self.font_family, cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
        ctx.set_font_size(self.font_size)
        rgba = self.color.to_cairo()

        for d in range(10):
            diff = (d - current_value) % 10
            if diff > 5:
                diff -= 10

            theta = diff * (math.pi / 5.0)
            if math.cos(theta) <= 0.01:
                continue

            y_offset = self.radius * math.sin(theta)
            scale_y = math.cos(theta)
            brightness = math.cos(theta)

            ctx.save()
            ctx.translate(0, y_offset)
            ctx.scale(1.0, scale_y)
            ctx.set_source_rgba(rgba[0] * brightness, rgba[1] * brightness, rgba[2] * brightness, rgba[3] * brightness)

            text = str(d)
            extents = ctx.text_extents(text)
            ctx.move_to(-extents.width / 2 - extents.x_bearing, -extents.height / 2 - extents.y_bearing)
            ctx.show_text(text)
            ctx.restore()

class MechanicalSeparatorCommas(Node):
    """Fixed punctuation separators ($, commas, decimals, %) aligning with rolling wheels."""
    def __init__(
        self,
        text: str = ",",
        font_size: float = 32.0,
        font_family: str = "Inter",
        color: Any = colors.WHITE,
        **kwargs: Any
    ):
        super().__init__(**kwargs)
        self.text = text
        self.font_size = font_size
        self.font_family = font_family
        self.color = Color.from_any(color)

    def draw(self, ctx: cairo.Context, time: float) -> None:
        super().draw(ctx, time)
        ctx.save()
        ctx.select_font_face(self.font_family, cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
        ctx.set_font_size(self.font_size)
        rgba = self.color.to_cairo()
        ctx.set_source_rgba(*rgba)

        extents = ctx.text_extents(self.text)
        ctx.move_to(-extents.width / 2 - extents.x_bearing, -extents.height / 2 - extents.y_bearing)
        ctx.show_text(self.text)
        ctx.restore()

class TumblerBezelSlot(Node):
    """Recessed metal dashboard frame with top/bottom shadow gradients masking wheel edges."""
    def __init__(self, width: float = 100.0, height: float = 100.0, **kwargs: Any):
        super().__init__(**kwargs)
        self.width = width
        self.height = height

    def draw(self, ctx: cairo.Context, time: float) -> None:
        super().draw(ctx, time)
        w, h = self.width, self.height
        ctx.save()

        pat_top = cairo.LinearGradient(0, -h/2, 0, -h/2 + h*0.3)
        pat_top.add_color_stop_rgba(0, 0, 0, 0, 0.8)
        pat_top.add_color_stop_rgba(1, 0, 0, 0, 0.0)
        ctx.rectangle(-w/2, -h/2, w, h*0.3)
        ctx.set_source(pat_top)
        ctx.fill()

        pat_bot = cairo.LinearGradient(0, h/2, 0, h/2 - h*0.3)
        pat_bot.add_color_stop_rgba(0, 0, 0, 0, 0.8)
        pat_bot.add_color_stop_rgba(1, 0, 0, 0, 0.0)
        ctx.rectangle(-w/2, h/2 - h*0.3, w, h*0.3)
        ctx.set_source(pat_bot)
        ctx.fill()

        # Metal frame outline
        ctx.set_source_rgba(0.2, 0.2, 0.2, 1.0)
        ctx.set_line_width(4)
        # Inset the rectangle to ensure the 4px stroke is not clipped by parent bounding boxes
        ctx.rectangle(-w/2 + 2, -h/2 + 2, w - 4, h - 4)
        ctx.stroke()
        ctx.restore()

class OdometerTumblerCounter(Node):
    """High-precision rolling numeric odometer where digit wheels roll vertically with realistic cylindrical perspective."""
    def __init__(
        self,
        num_digits: int = 5,
        font_size: float = 32.0,
        font_family: str = "Inter",
        color: Any = colors.WHITE,
        radius: float = 40.0,
        digit_spacing: float = 25.0,
        decimals: int = 0,
        prefix: str = "",
        **kwargs: Any
    ):
        super().__init__(**kwargs)
        self.value = Signal(0.0)
        self.num_digits = num_digits
        self.digit_spacing = digit_spacing
        self.radius = radius
        self.decimals = decimals

        self.digits = []
        self.separators = []

        total_slots = num_digits
        if decimals > 0:
            total_slots += 1 # for decimal point
        if prefix:
            total_slots += 1

        current_x = - (total_slots - 1) * digit_spacing / 2

        if prefix:
            sep = MechanicalSeparatorCommas(text=prefix, font_size=font_size, font_family=font_family, color=color)
            sep.position.set((current_x, 0))
            self.add(sep)
            self.separators.append(sep)
            current_x += digit_spacing

        # Integer part digits
        for i in range(num_digits - decimals):
            d = VerticalRollingGlyphs(font_size=font_size, font_family=font_family, color=color, radius=radius)
            d.position.set((current_x, 0))
            self.digits.append(d)
            self.add(d)
            current_x += digit_spacing

        # Decimal separator
        if decimals > 0:
            sep = MechanicalSeparatorCommas(text=".", font_size=font_size, font_family=font_family, color=color)
            sep.position.set((current_x, 0))
            self.add(sep)
            self.separators.append(sep)
            current_x += digit_spacing

        # Fractional part digits
        for i in range(decimals):
            d = VerticalRollingGlyphs(font_size=font_size, font_family=font_family, color=color, radius=radius)
            d.position.set((current_x, 0))
            self.digits.append(d)
            self.add(d)
            current_x += digit_spacing

        bezel_w = total_slots * digit_spacing + 10
        self.bezel = TumblerBezelSlot(width=bezel_w, height=radius * 2.2)
        self.add(self.bezel)

    def roll_to(self, target_value: float, duration: float = 2.0):
        self.value.to(target_value, duration=duration, ease=Ease.out_expo)

    def draw(self, ctx: cairo.Context, time: float) -> None:
        val = self.value.get()

        # Distribute value across digits
        # self.digits contains integer digits then decimal digits (left to right)
        # So index 0 is most significant digit

        val_scaled = val * (10 ** self.decimals)

        for i, d in enumerate(reversed(self.digits)):
            # From least significant to most significant
            divisor = 10 ** i
            if i == 0:
                d_val = val_scaled
            else:
                lower_val = val_scaled % divisor
                base = math.floor(val_scaled / divisor)
                # Apply easing/carry over when lower digits wrap 9->0
                if lower_val > divisor - 1:
                    d_val = base + (lower_val - (divisor - 1))
                else:
                    d_val = base

            d.value.set(d_val)

        # Visual clipping for the odometer window
        total_slots = self.num_digits + (1 if self.decimals > 0 else 0) + (1 if self.separators and len(self.separators) > (1 if self.decimals > 0 else 0) else 0)
        w = total_slots * self.digit_spacing + 10
        h = self.radius * 2.2
        ctx.save()
        ctx.rectangle(-w/2, -h/2, w, h)
        ctx.clip()

        super().draw(ctx, time)

        ctx.restore()
