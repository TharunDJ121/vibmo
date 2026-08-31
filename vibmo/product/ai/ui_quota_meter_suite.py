"""
Token Quota & Usage Ring UI Suite for Vibmo / Motio.
Components:
- TokenQuotaMeter
- UsageRingGauge (CircularTokenQuotaRing)
- OverLimitWarningBanner
- UsageThresholdPill
- UpgradeCtaButton
"""

from __future__ import annotations
import math
from typing import Any, Dict, List, Optional, Sequence, Tuple, Union
import cairo

from vibmo.core.color import Color, colors
from vibmo.core.vector import Vector2D
from vibmo.core.signal import Signal, AnimationAction
from vibmo.core.easing import Ease, EasingFunc
from vibmo.scene.node import Node
from vibmo.spatial.shadows import DropShadow


def _format_tokens(num: float) -> str:
    if num >= 1_000_000:
        return f"{num / 1_000_000:.2f}M"
    elif num >= 1_000:
        return f"{num / 1_000:.0f}k"
    return str(int(num))


class UsageRingGauge(Node):
    """Circular radial token gauge ring displaying consumption percentage and token count."""

    def __init__(
        self,
        used: float = 750000.0,
        total: float = 1000000.0,
        radius: float = 85.0,
        thickness: float = 16.0,
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)
        self.radius = float(radius)
        self.thickness = float(thickness)
        self.total = Signal(float(total), f"{self.name}.total")
        self.used = Signal(float(used), f"{self.name}.used")

    def draw(self, ctx: Any, time: float = 0.0) -> None:
        u = self.used.get(time)
        tot = max(1.0, self.total.get(time))
        ratio = max(0.0, min(1.0, u / tot))
        r = self.radius
        sw = self.thickness

        ctx.save()
        # Track circle
        ctx.arc(0, 0, r, 0, 2 * math.pi)
        ctx.set_source_rgba(0.12, 0.16, 0.24, 0.8)
        ctx.set_line_width(sw)
        ctx.stroke()

        # Gauge arc
        start_angle = -math.pi * 0.5
        end_angle = start_angle + ratio * (2.0 * math.pi)
        ctx.arc(0, 0, r, start_angle, end_angle)

        if ratio > 0.9:
            ctx.set_source_rgba(0.95, 0.25, 0.35, 0.95)
        elif ratio > 0.75:
            ctx.set_source_rgba(0.95, 0.7, 0.15, 0.95)
        else:
            ctx.set_source_rgba(0.2, 0.75, 1.0, 0.95)

        ctx.set_line_width(sw)
        ctx.set_line_cap(1)
        ctx.stroke()

        # Center readout
        ctx.select_font_face("Inter", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
        ctx.set_font_size(24.0)
        ctx.set_source_rgba(0.95, 0.98, 1.0, 0.95)
        text = f"{int(ratio * 100)}%"
        ext = ctx.text_extents(text)
        ctx.move_to(-ext.width * 0.5, 4.0)
        ctx.show_text(text)

        # Tokens readout below
        ctx.select_font_face("Inter", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)
        ctx.set_font_size(11.0)
        ctx.set_source_rgba(0.6, 0.7, 0.8, 0.8)
        sub_text = f"{_format_tokens(u)} / {_format_tokens(tot)}"
        sub_ext = ctx.text_extents(sub_text)
        ctx.move_to(-sub_ext.width * 0.5, 24.0)
        ctx.show_text(sub_text)

        ctx.restore()


CircularTokenQuotaRing = UsageRingGauge


class OverLimitWarningBanner(Node):
    """Banner alerting user when consumption passes 80% / 100% threshold."""

    def __init__(self, message: str = "Quota Threshold: 80% consumed this billing cycle", width: float = 460.0, height: float = 36.0, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.message = message
        self.width_val = float(width)
        self.height_val = float(height)

    def draw(self, ctx: Any, time: float = 0.0) -> None:
        w, h = self.width_val, self.height_val
        ctx.save()
        r = 8.0
        ctx.new_path()
        ctx.arc(w - r, r, r, -math.pi * 0.5, 0)
        ctx.arc(w - r, h - r, r, 0, math.pi * 0.5)
        ctx.arc(r, h - r, r, math.pi * 0.5, math.pi)
        ctx.arc(r, r, r, math.pi, math.pi * 1.5)
        ctx.close_path()

        ctx.set_source_rgba(0.2, 0.14, 0.04, 0.85)
        ctx.fill_preserve()
        ctx.set_source_rgba(0.95, 0.7, 0.15, 0.6)
        ctx.set_line_width(1.0)
        ctx.stroke()

        ctx.select_font_face("Inter", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
        ctx.set_font_size(11.0)
        ctx.set_source_rgba(1.0, 0.85, 0.3, 0.95)
        ctx.move_to(14.0, 22.0)
        ctx.show_text(f"⚠️ {self.message}")
        ctx.restore()


class UsageThresholdPill(Node):
    """Pill indicating tier quota limit."""

    def __init__(self, limit_str: str = "Pro Plan: 1,000,000 Tokens/mo", width: float = 240.0, height: float = 28.0, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.limit_str = limit_str
        self.width_val = float(width)
        self.height_val = float(height)

    def draw(self, ctx: Any, time: float = 0.0) -> None:
        w, h = self.width_val, self.height_val
        ctx.save()
        r = 6.0
        ctx.new_path()
        ctx.arc(w - r, r, r, -math.pi * 0.5, 0)
        ctx.arc(w - r, h - r, r, 0, math.pi * 0.5)
        ctx.arc(r, h - r, r, math.pi * 0.5, math.pi)
        ctx.arc(r, r, r, math.pi, math.pi * 1.5)
        ctx.close_path()

        ctx.set_source_rgba(0.08, 0.12, 0.18, 0.8)
        ctx.fill_preserve()
        ctx.set_source_rgba(0.2, 0.3, 0.45, 0.6)
        ctx.set_line_width(1.0)
        ctx.stroke()

        ctx.select_font_face("Inter", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)
        ctx.set_font_size(11.0)
        ctx.set_source_rgba(0.8, 0.9, 1.0, 0.9)
        ext = ctx.text_extents(self.limit_str)
        ctx.move_to((w - ext.width) * 0.5, h * 0.5 + ext.height * 0.35)
        ctx.show_text(self.limit_str)
        ctx.restore()


class UpgradeCtaButton(Node):
    """Button to add additional quota or upgrade tier."""

    def __init__(self, width: float = 160.0, height: float = 36.0, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.width_val = float(width)
        self.height_val = float(height)

    def draw(self, ctx: Any, time: float = 0.0) -> None:
        w, h = self.width_val, self.height_val
        ctx.save()
        r = 8.0
        ctx.new_path()
        ctx.arc(w - r, r, r, -math.pi * 0.5, 0)
        ctx.arc(w - r, h - r, r, 0, math.pi * 0.5)
        ctx.arc(r, h - r, r, math.pi * 0.5, math.pi)
        ctx.arc(r, r, r, math.pi, math.pi * 1.5)
        ctx.close_path()

        ctx.set_source_rgba(0.15, 0.5, 1.0, 0.95)
        ctx.fill()

        ctx.select_font_face("Inter", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
        ctx.set_font_size(12.0)
        ctx.set_source_rgba(1.0, 1.0, 1.0, 1.0)
        text = "Add Tokens"
        ext = ctx.text_extents(text)
        ctx.move_to((w - ext.width) * 0.5, h * 0.5 + ext.height * 0.35)
        ctx.show_text(text)
        ctx.restore()


class TokenQuotaMeter(Node):
    """
    Token Quota Meter Suite.
    Renders radial usage ring, warning banners, usage threshold breakdowns,
    and quota consumption animation verbs.
    """

    def __init__(
        self,
        total: float = 1000000.0,
        used: float = 500000.0,
        width: float = 540.0,
        height: float = 420.0,
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)
        self.width_val = float(width)
        self.height_val = float(height)
        self.shadow = DropShadow(color=Color(0.0, 0.0, 0.0, 0.5), blur=32.0, offset=(0.0, 16.0))

        # Ring Gauge in center
        self.ring_gauge = UsageRingGauge(used=used, total=total, radius=80.0, thickness=15.0)
        self.ring_gauge.position.set(Vector2D(self.width_val * 0.5, 175.0))
        self.add(self.ring_gauge)

        # Warning banner
        self.warning_banner = OverLimitWarningBanner(width=self.width_val - 48.0)
        self.warning_banner.position.set(Vector2D(24.0, 305.0))
        self.add(self.warning_banner)

        # Upgrade button
        self.upgrade_btn = UpgradeCtaButton(width=150.0, height=36.0)
        self.upgrade_btn.position.set(Vector2D((self.width_val - 150.0) * 0.5, 355.0))
        self.add(self.upgrade_btn)

    def consume(self, amount: float = 250000.0, duration: float = 1.2, ease: EasingFunc = Ease.out_quad) -> AnimationAction:
        """
        Fluent generator animation verb to consume quota tokens and advance the ring gauge.
        """
        curr = self.ring_gauge.used.get(0.0)
        target = curr + float(amount)
        return self.ring_gauge.used.to(target, duration=duration, ease=ease)

    def local_bounds(self, time: float = 0.0) -> Tuple[float, float, float, float]:
        return (0.0, 0.0, self.width_val, self.height_val)

    def draw(self, ctx: Any, time: float = 0.0) -> None:
        w, h = self.width_val, self.height_val
        ctx.save()

        # Card container
        r = 16.0
        ctx.new_path()
        ctx.arc(w - r, r, r, -math.pi * 0.5, 0)
        ctx.arc(w - r, h - r, r, 0, math.pi * 0.5)
        ctx.arc(r, h - r, r, math.pi * 0.5, math.pi)
        ctx.arc(r, r, r, math.pi, math.pi * 1.5)
        ctx.close_path()

        ctx.set_source_rgba(0.04, 0.06, 0.1, 0.95)
        ctx.fill_preserve()
        ctx.set_source_rgba(0.18, 0.25, 0.38, 0.8)
        ctx.set_line_width(1.5)
        ctx.stroke()

        # Title
        ctx.select_font_face("Inter", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
        ctx.set_font_size(15.0)
        ctx.set_source_rgba(0.95, 0.98, 1.0, 0.95)
        ctx.move_to(24.0, 42.0)
        ctx.show_text("Monthly LLM Token Quota")

        super().draw(ctx, time)
        ctx.restore()
