"""
Prompt Invocation Card Suite for Vibmo.
Inspired by video-production-skills dark-saas-magic-video (Blueprint 2).
Provides a 2.5D tilted prompt card, animated text typing, cyan-to-magenta gradient CTA, and sparkle burst.
"""

from __future__ import annotations
import math
from typing import List, Optional, Tuple, Dict, Any, Union
import cairo
import numpy as np

from vibmo.core.color import Color, colors
from vibmo.core.signal import Signal, AnimationAction
from vibmo.core.easing import Ease
from vibmo.scene.node import Node


class PromptInvocationCard(Node):
    """
    Presenton-style Prompt Invocation Card:
    Tilted frosted dark card with prompt typing, glowing cyan-to-magenta gradient CTA,
    and particle sparkle burst upon generation trigger.
    """

    def __init__(
        self,
        prompt_text: str = "Generate high-converting SaaS product demo in Python",
        cta_text: str = "Generate Video ✨",
        tilt_angle_deg: float = -3.5,
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)
        self.prompt_text = prompt_text
        self.cta_text = cta_text
        self.tilt_angle_deg = tilt_angle_deg

        # Signals
        self.card_progress = Signal(0.0, f"{self.id}.card")
        self.type_progress = Signal(0.0, f"{self.id}.type")
        self.click_progress = Signal(0.0, f"{self.id}.click")
        self.sparkle_progress = Signal(0.0, f"{self.id}.sparkle")

    def enter_card(self, duration: float = 1.0, delay: float = 0.0) -> AnimationAction:
        """Pops the card in with spring overshoot."""
        return self.card_progress.to(1.0, duration=duration, delay=delay, ease=Ease.out_back)

    def type_prompt(self, duration: float = 1.6, delay: float = 0.0) -> AnimationAction:
        """Types the prompt text character-by-character."""
        return self.type_progress.to(1.0, duration=duration, delay=delay, ease=Ease.linear)

    def click_cta(self, duration: float = 0.6, delay: float = 0.0) -> AnimationAction:
        """Triggers CTA button click pulse and sparkles."""
        return self.click_progress.to(1.0, duration=duration, delay=delay, ease=Ease.out_expo)

    def draw(self, ctx: cairo.Context, time: float = 0.0) -> None:
        cp = self.card_progress.evaluate_at(time)
        tp = self.type_progress.evaluate_at(time)
        clk = self.click_progress.evaluate_at(time)

        if cp <= 0.001:
            return

        cx, cy = self.position.evaluate_at(time)
        w, h = 640.0, 260.0
        r = 18.0

        ctx.save()
        ctx.translate(cx, cy)
        ctx.rotate(math.radians(self.tilt_angle_deg * cp))

        # 1. Card Shadow
        ctx.set_source_rgba(0, 0, 0, 0.5 * cp)
        ctx.rectangle(-w / 2, -h / 2 + 16, w, h)
        ctx.fill()

        # 2. Frosted Dark Surface
        ctx.new_sub_path()
        ctx.arc(w / 2 - r, h / 2 - r, r, 0, math.pi / 2)
        ctx.arc(-w / 2 + r, h / 2 - r, r, math.pi / 2, math.pi)
        ctx.arc(-w / 2 + r, -h / 2 + r, r, math.pi, 3 * math.pi / 2)
        ctx.arc(w / 2 - r, -h / 2 + r, r, 3 * math.pi / 2, 2 * math.pi)
        ctx.close_path()

        ctx.set_source_rgba(0.06, 0.08, 0.14, 0.94)
        ctx.fill_preserve()

        # Card Border with soft cyan/purple ambient rim
        border_grad = cairo.LinearGradient(-w / 2, -h / 2, w / 2, h / 2)
        border_grad.add_color_stop_rgba(0.0, 0.06, 0.71, 0.83, 0.7 * cp)  # Cyan #06b6d4
        border_grad.add_color_stop_rgba(1.0, 0.93, 0.28, 0.60, 0.7 * cp)  # Magenta #ec4899
        ctx.set_source(border_grad)
        ctx.set_line_width(1.6)
        ctx.stroke()

        # 3. Window Header Controls
        for i, dot_color in enumerate([(0.95, 0.35, 0.35), (0.95, 0.75, 0.25), (0.35, 0.85, 0.45)]):
            ctx.set_source_rgba(*dot_color, 0.85)
            ctx.arc(-w / 2 + 28.0 + i * 18.0, -h / 2 + 26.0, 5.0, 0, 2 * math.pi)
            ctx.fill()

        # 4. Prompt Input Field & Typing
        ctx.set_source_rgba(0.09, 0.12, 0.20, 0.9)
        ctx.rectangle(-w / 2 + 24.0, -h / 2 + 56.0, w - 48.0, 100.0)
        ctx.fill_preserve()
        ctx.set_source_rgba(0.2, 0.26, 0.38, 0.4)
        ctx.set_line_width(1.0)
        ctx.stroke()

        # Typed Text
        char_count = int(len(self.prompt_text) * tp)
        visible_text = self.prompt_text[:char_count]

        ctx.select_font_face("Inter", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)
        ctx.set_font_size(17.0)
        ctx.set_source_rgba(0.92, 0.96, 1.0, 1.0)
        ctx.move_to(-w / 2 + 40.0, -h / 2 + 96.0)
        ctx.show_text(visible_text)

        # Blinking Cursor
        if tp < 1.0 or int(time * 3.0) % 2 == 0:
            ext = ctx.text_extents(visible_text)
            ctx.set_source_rgba(0.06, 0.71, 0.83, 0.9)
            ctx.rectangle(-w / 2 + 42.0 + ext.x_advance, -h / 2 + 80.0, 2.0, 20.0)
            ctx.fill()

        # 5. Cyan-to-Magenta Gradient CTA Button
        cta_w, cta_h = 190.0, 44.0
        cta_x = w / 2 - 24.0 - cta_w
        cta_y = h / 2 - 24.0 - cta_h
        cta_r = 12.0

        ctx.save()
        ctx.translate(cta_x + cta_w / 2, cta_y + cta_h / 2)
        if clk > 0.01:
            scale_pulse = 1.0 - 0.12 * math.sin(clk * math.pi)
            ctx.scale(scale_pulse, scale_pulse)
        ctx.translate(-cta_w / 2, -cta_h / 2)

        # Button Gradient Body
        cta_grad = cairo.LinearGradient(0, 0, cta_w, cta_h)
        cta_grad.add_color_stop_rgb(0.0, 0.06, 0.71, 0.83)  # Cyan #06b6d4
        cta_grad.add_color_stop_rgb(1.0, 0.93, 0.28, 0.60)  # Magenta #ec4899

        ctx.new_sub_path()
        ctx.arc(cta_w - cta_r, cta_h - cta_r, cta_r, 0, math.pi / 2)
        ctx.arc(cta_r, cta_h - cta_r, cta_r, math.pi / 2, math.pi)
        ctx.arc(cta_r, cta_r, cta_r, math.pi, 3 * math.pi / 2)
        ctx.arc(cta_w - cta_r, cta_r, cta_r, 3 * math.pi / 2, 2 * math.pi)
        ctx.close_path()
        ctx.set_source(cta_grad)
        ctx.fill()

        # CTA Label
        ctx.select_font_face("Inter", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
        ctx.set_font_size(14.0)
        ctx.set_source_rgb(1, 1, 1)
        ext_btn = ctx.text_extents(self.cta_text)
        ctx.move_to((cta_w - ext_btn.width) / 2, cta_h / 2 + 5.0)
        ctx.show_text(self.cta_text)

        # Sparkles when clicked
        if clk > 0.05:
            for s_idx in range(6):
                s_ang = s_idx * (math.pi / 3.0)
                s_dist = 30.0 + 40.0 * clk
                sx = cta_w / 2 + math.cos(s_ang) * s_dist
                sy = cta_h / 2 + math.sin(s_ang) * s_dist
                s_alpha = max(0.0, 1.0 - clk)
                ctx.set_source_rgba(1, 1, 1, s_alpha)
                ctx.arc(sx, sy, 3.0 * s_alpha, 0, 2 * math.pi)
                ctx.fill()

        ctx.restore()
        ctx.restore()
