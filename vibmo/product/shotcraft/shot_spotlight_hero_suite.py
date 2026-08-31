"""
Spotlight Hero Card & Dark Metallic Surface Suites for Vibmo.
Inspired by video-shotcraft spotlight-hero-card (aesthetic rules Q5, Q7).
Provides volumetric spotlight lighting, brushed metallic reflection floor, and hero glass card staging.
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


class DarkMetallicFloor(Node):
    """
    Procedural dark brushed-metal ground texture with an elliptical specular light pool.
    """

    def __init__(
        self,
        floor_y: float = 620.0,
        light_color: Union[Color, str] = colors.CYAN,
        intensity: float = 0.8,
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)
        self.floor_y = floor_y
        self.light_color = Color.from_any(light_color)
        self.intensity = Signal(intensity, f"{self.id}.intensity")

    def draw(self, ctx: cairo.Context, time: float = 0.0) -> None:
        inte = self.intensity.evaluate_at(time)
        if inte <= 0.001:
            return

        ctx.save()
        # Elliptical Ground Light Pool
        pat = cairo.RadialGradient(960.0, self.floor_y + 120.0, 10.0, 960.0, self.floor_y + 120.0, 480.0)
        pat.add_color_stop_rgba(
            0.0,
            self.light_color.r,
            self.light_color.g,
            self.light_color.b,
            0.35 * inte,
        )
        pat.add_color_stop_rgba(
            0.5,
            self.light_color.r * 0.4,
            self.light_color.g * 0.4,
            self.light_color.b * 0.4,
            0.12 * inte,
        )
        pat.add_color_stop_rgba(1.0, 0.02, 0.03, 0.06, 0.0)

        ctx.save()
        ctx.translate(960.0, self.floor_y + 120.0)
        ctx.scale(1.0, 0.35)  # Elliptical floor projection
        ctx.translate(-960.0, -(self.floor_y + 120.0))
        ctx.set_source(pat)
        ctx.paint()
        ctx.restore()

        # Brushed horizontal reflection lines
        ctx.set_line_width(1.0)
        for offset_y in range(int(self.floor_y), 1080, 8):
            alpha = (1.0 - (offset_y - self.floor_y) / (1080 - self.floor_y)) * 0.06 * inte
            ctx.set_source_rgba(0.7, 0.8, 1.0, alpha)
            ctx.move_to(360.0, float(offset_y))
            ctx.line_to(1560.0, float(offset_y))
            ctx.stroke()

        ctx.restore()


class SpotlightHeroCard(Node):
    """
    Volumetric cone spotlight focused on a hero glass card with 3D tilt and edge sheen.
    Adheres strictly to Case Law Q4 (single specular gleam clipped to border radius) and Q5 (single hero).
    """

    def __init__(
        self,
        title: str = "Enterprise Engine",
        subtitle: str = "Sub-millisecond Vector Processing",
        metric_value: str = "0.42 ms",
        metric_label: str = "Global Latency P99",
        accent_color: Union[Color, str] = colors.CYAN,
        card_size: Tuple[float, float] = (580.0, 360.0),
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)
        self.title = title
        self.subtitle = subtitle
        self.metric_value = metric_value
        self.metric_label = metric_label
        self.accent_color = Color.from_any(accent_color)
        self.card_size = card_size

        # Signals
        self.spotlight_progress = Signal(0.0, f"{self.id}.spotlight")
        self.card_lift = Signal(0.0, f"{self.id}.card_lift")
        self.sheen_progress = Signal(0.0, f"{self.id}.sheen")

    def ignite_spotlight(self, duration: float = 1.0, delay: float = 0.0) -> AnimationAction:
        """Fires the volumetric cone spotlight down to the hero card."""
        return self.spotlight_progress.to(1.0, duration=duration, delay=delay, ease=Ease.out_expo)

    def lift_card(self, duration: float = 1.2, delay: float = 0.0) -> AnimationAction:
        """Lifts the card with spring physics into hover position."""
        return self.card_lift.to(1.0, duration=duration, delay=delay, ease=Ease.out_back)

    def sweep_sheen(self, duration: float = 0.8, delay: float = 0.0) -> AnimationAction:
        """Sweeps a single specular glint across the card (Case Law Q4)."""
        return self.sheen_progress.to(1.0, duration=duration, delay=delay, ease=Ease.in_out_sine)

    def draw(self, ctx: cairo.Context, time: float = 0.0) -> None:
        sp = self.spotlight_progress.evaluate_at(time)
        lift = self.card_lift.evaluate_at(time)
        sheen = self.sheen_progress.evaluate_at(time)

        if sp <= 0.001 and lift <= 0.001:
            return

        cx, cy = self.position.evaluate_at(time)

        # 1. Volumetric Overhead Cone Spotlight
        if sp > 0.001:
            ctx.save()
            cone_pat = cairo.LinearGradient(960.0, 0.0, 960.0, cy + 180.0)
            cone_pat.add_color_stop_rgba(
                0.0,
                self.accent_color.r,
                self.accent_color.g,
                self.accent_color.b,
                0.22 * sp,
            )
            cone_pat.add_color_stop_rgba(
                0.7,
                self.accent_color.r * 0.3,
                self.accent_color.g * 0.3,
                self.accent_color.b * 0.3,
                0.08 * sp,
            )
            cone_pat.add_color_stop_rgba(1.0, 0.0, 0.0, 0.0, 0.0)

            ctx.set_source(cone_pat)
            ctx.move_to(960.0, 0.0)
            ctx.line_to(960.0 - 380.0 * sp, cy + 180.0)
            ctx.line_to(960.0 + 380.0 * sp, cy + 180.0)
            ctx.close_path()
            ctx.fill()
            ctx.restore()

        # 2. Hero Glass Card
        if lift > 0.001:
            cw, ch = self.card_size
            r = 20.0

            card_y = cy - lift * 30.0

            ctx.save()
            ctx.translate(cx, card_y)

            # Card Ambient Glow & Drop Shadow
            ctx.set_source_rgba(0, 0, 0, 0.5 * lift)
            ctx.new_sub_path()
            ctx.arc(cw / 2 - r, ch / 2 - r + 18, r, 0, math.pi / 2)
            ctx.arc(-cw / 2 + r, ch / 2 - r + 18, r, math.pi / 2, math.pi)
            ctx.arc(-cw / 2 + r, -ch / 2 + r + 18, r, math.pi, 3 * math.pi / 2)
            ctx.arc(cw / 2 - r, -ch / 2 + r + 18, r, 3 * math.pi / 2, 2 * math.pi)
            ctx.close_path()
            ctx.fill()

            # Frosted Dark Glass Surface (Clipped for Q4 specular glint containment)
            ctx.new_sub_path()
            ctx.arc(cw / 2 - r, ch / 2 - r, r, 0, math.pi / 2)
            ctx.arc(-cw / 2 + r, ch / 2 - r, r, math.pi / 2, math.pi)
            ctx.arc(-cw / 2 + r, -ch / 2 + r, r, math.pi, 3 * math.pi / 2)
            ctx.arc(cw / 2 - r, -ch / 2 + r, r, 3 * math.pi / 2, 2 * math.pi)
            ctx.close_path()

            ctx.set_source_rgba(0.05, 0.08, 0.14, 0.94)
            ctx.fill_preserve()

            # Specular Sheen (Strictly Clipped inside rounded border path)
            if 0.0 < sheen < 1.0:
                ctx.save()
                ctx.clip_preserve()
                sheen_x = -cw / 2 - 100.0 + sheen * (cw + 200.0)
                sheen_grad = cairo.LinearGradient(sheen_x - 60, -ch / 2, sheen_x + 60, ch / 2)
                sheen_grad.add_color_stop_rgba(0.0, 1, 1, 1, 0.0)
                sheen_grad.add_color_stop_rgba(0.5, 1, 1, 1, 0.35)
                sheen_grad.add_color_stop_rgba(1.0, 1, 1, 1, 0.0)
                ctx.set_source(sheen_grad)
                ctx.paint()
                ctx.restore()

            # Border Rim
            ctx.set_source_rgba(
                self.accent_color.r,
                self.accent_color.g,
                self.accent_color.b,
                0.4 + 0.3 * lift,
            )
            ctx.set_line_width(1.8)
            ctx.stroke()

            # Card Content
            # Badge
            badge_w, badge_h = 130.0, 30.0
            ctx.set_source_rgba(
                self.accent_color.r,
                self.accent_color.g,
                self.accent_color.b,
                0.2,
            )
            ctx.rectangle(-cw / 2 + 36.0, -ch / 2 + 36.0, badge_w, badge_h)
            ctx.fill()

            ctx.select_font_face("Inter", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
            ctx.set_font_size(12.0)
            ctx.set_source_rgba(self.accent_color.r, self.accent_color.g, self.accent_color.b, 1.0)
            ctx.move_to(-cw / 2 + 48.0, -ch / 2 + 56.0)
            ctx.show_text("LIVE SYSTEM")

            # Title
            ctx.set_font_size(24.0)
            ctx.set_source_rgba(0.95, 0.98, 1.0, lift)
            ctx.move_to(-cw / 2 + 36.0, -ch / 2 + 110.0)
            ctx.show_text(self.title)

            # Subtitle
            ctx.select_font_face("Inter", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)
            ctx.set_font_size(14.0)
            ctx.set_source_rgba(0.65, 0.72, 0.84, lift)
            ctx.move_to(-cw / 2 + 36.0, -ch / 2 + 140.0)
            ctx.show_text(self.subtitle)

            # Metric Box
            ctx.select_font_face("Inter", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
            ctx.set_font_size(52.0)
            ctx.set_source_rgba(self.accent_color.r, self.accent_color.g, self.accent_color.b, lift)
            ctx.move_to(-cw / 2 + 36.0, ch / 2 - 60.0)
            ctx.show_text(self.metric_value)

            ctx.select_font_face("Inter", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)
            ctx.set_font_size(14.0)
            ctx.set_source_rgba(0.55, 0.62, 0.75, lift)
            ctx.move_to(-cw / 2 + 36.0, ch / 2 - 28.0)
            ctx.show_text(self.metric_label)

            ctx.restore()
