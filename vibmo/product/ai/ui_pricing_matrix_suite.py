"""
SaaS Pricing Tier Matrix UI Suite for Vibmo / Motio.
Components:
- PricingTierMatrix (PricingTierGrid)
- PricingTierColumn
- FeatureChecklistRow
- AnnualBillingToggle
- PopularGlowBadge
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
from vibmo.layout.container import FlexContainer
from vibmo.primitives.rect import Rect, RoundedRect
from vibmo.typography.text import Text
from vibmo.spatial.shadows import DropShadow


class FeatureChecklistRow(Node):
    """Feature item row with checkmark indicator and feature title."""

    def __init__(self, text: str = "Feature included", active: bool = True, width: float = 220.0, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.text = text
        self.active = active
        self.width_val = float(width)
        self.height_val = 26.0

    def draw(self, ctx: Any, time: float = 0.0) -> None:
        ctx.save()
        # Checkmark icon
        if self.active:
            ctx.set_source_rgba(0.1, 0.85, 0.45, 0.95)
            ctx.arc(8.0, 12.0, 6.0, 0, 2 * math.pi)
            ctx.fill()

            ctx.set_source_rgba(1.0, 1.0, 1.0, 1.0)
            ctx.set_line_width(1.5)
            ctx.move_to(5.0, 12.0)
            ctx.line_to(7.5, 14.5)
            ctx.line_to(11.0, 9.5)
            ctx.stroke()
            text_col = (0.9, 0.95, 1.0, 0.9)
        else:
            ctx.set_source_rgba(0.3, 0.35, 0.45, 0.5)
            ctx.arc(8.0, 12.0, 6.0, 0, 2 * math.pi)
            ctx.fill()
            text_col = (0.45, 0.5, 0.6, 0.6)

        ctx.select_font_face("Inter", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)
        ctx.set_font_size(11.0)
        ctx.set_source_rgba(*text_col)
        ctx.move_to(22.0, 16.0)
        ctx.show_text(self.text)
        ctx.restore()


class AnnualBillingToggle(Node):
    """Toggle switch for Monthly vs Annual pricing with '-20% DISCOUNT' pill."""

    def __init__(self, is_annual: Union[bool, Signal] = False, width: float = 240.0, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.is_annual = is_annual if isinstance(is_annual, Signal) else Signal(bool(is_annual), f"{self.name}.is_annual")
        self.width_val = float(width)
        self.height_val = 36.0

    def draw(self, ctx: Any, time: float = 0.0) -> None:
        w, h = self.width_val, self.height_val
        ctx.save()
        annual = bool(self.is_annual.get(time))

        # Pill background
        r = h * 0.5
        ctx.new_path()
        ctx.arc(w - r, r, r, -math.pi * 0.5, math.pi * 0.5)
        ctx.arc(r, r, r, math.pi * 0.5, math.pi * 1.5)
        ctx.close_path()
        ctx.set_source_rgba(0.08, 0.12, 0.18, 0.9)
        ctx.fill_preserve()
        ctx.set_source_rgba(0.2, 0.3, 0.45, 0.6)
        ctx.set_line_width(1.0)
        ctx.stroke()

        # Labels
        ctx.select_font_face("Inter", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
        ctx.set_font_size(11.0)
        ctx.set_source_rgba(0.9, 0.95, 1.0, 0.9 if not annual else 0.5)
        ctx.move_to(16.0, 22.0)
        ctx.show_text("Monthly")

        ctx.set_source_rgba(0.1, 0.85, 0.5, 0.95 if annual else 0.6)
        ctx.move_to(80.0, 22.0)
        ctx.show_text("Annual (-20%)")
        ctx.restore()


class PopularGlowBadge(Node):
    """Glowing badge identifying the most popular tier ('MOST POPULAR')."""

    def __init__(self, text: str = "MOST POPULAR", **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.text = text
        self.width = 110.0
        self.height = 24.0

    def draw(self, ctx: Any, time: float = 0.0) -> None:
        w, h = self.width, self.height
        ctx.save()
        r = 12.0
        ctx.new_path()
        ctx.arc(w - r, r, r, -math.pi * 0.5, math.pi * 0.5)
        ctx.arc(r, r, r, math.pi * 0.5, math.pi * 1.5)
        ctx.close_path()

        ctx.set_source_rgba(0.2, 0.5, 1.0, 0.95)
        ctx.fill_preserve()
        ctx.set_source_rgba(0.4, 0.8, 1.0, 1.0)
        ctx.set_line_width(1.5)
        ctx.stroke()

        ctx.select_font_face("Inter", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
        ctx.set_font_size(9.0)
        ctx.set_source_rgba(1.0, 1.0, 1.0, 1.0)
        ext = ctx.text_extents(self.text)
        ctx.move_to((w - ext.width) * 0.5, h * 0.5 + ext.height * 0.35)
        ctx.show_text(self.text)
        ctx.restore()


class PricingTierColumn(Node):
    """Individual pricing tier column card (Free, Pro, Enterprise)."""

    def __init__(
        self,
        name: str = "Pro",
        price: str = "$49",
        interval: str = "/mo",
        description: str = "For scaling engineering teams",
        features: Optional[List[str]] = None,
        is_popular: bool = False,
        width: float = 260.0,
        height: float = 420.0,
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)
        self.tier_name = name
        self.price = price
        self.interval = interval
        self.description = description
        self.features = features or ["Unlimited GPU compute", "10 Team seats", "Dedicated VPC", "24/7 Priority SLA"]
        self.is_popular = is_popular
        self.width_val = float(width)
        self.height_val = float(height)

        # Signals
        self.scale_sig = Signal(1.0, f"{self.name}.scale_sig")
        self.highlight_glow = Signal(1.0 if is_popular else 0.0, f"{self.name}.highlight_glow")
        self.opacity = Signal(1.0, f"{self.name}.opacity")

        if is_popular:
            self.badge = PopularGlowBadge()
            self.badge.position.set(Vector2D((self.width_val - 110.0) * 0.5, -12.0))
            self.add(self.badge)

    def local_bounds(self, time: float = 0.0) -> Tuple[float, float, float, float]:
        return (0.0, 0.0, self.width_val, self.height_val)

    def draw(self, ctx: Any, time: float = 0.0) -> None:
        w, h = self.width_val, self.height_val
        sc = self.scale_sig.get(time)
        op = max(0.0, min(1.0, self.opacity.get(time)))
        glow = max(0.0, min(1.0, self.highlight_glow.get(time)))

        ctx.save()
        ctx.translate(w * 0.5, h * 0.5)
        ctx.scale(sc, sc)
        ctx.translate(-w * 0.5, -h * 0.5)

        # Card container
        r = 16.0
        ctx.new_path()
        ctx.arc(w - r, r, r, -math.pi * 0.5, 0)
        ctx.arc(w - r, h - r, r, 0, math.pi * 0.5)
        ctx.arc(r, h - r, r, math.pi * 0.5, math.pi)
        ctx.arc(r, r, r, math.pi, math.pi * 1.5)
        ctx.close_path()

        if glow > 0.1:
            ctx.set_source_rgba(0.06, 0.1, 0.2, 0.95 * op)
            ctx.fill_preserve()
            ctx.set_source_rgba(0.25, 0.65, 1.0, 0.9 * op)
            ctx.set_line_width(2.0)
            ctx.stroke()
        else:
            ctx.set_source_rgba(0.04, 0.06, 0.1, 0.9 * op)
            ctx.fill_preserve()
            ctx.set_source_rgba(0.18, 0.24, 0.35, 0.6 * op)
            ctx.set_line_width(1.0)
            ctx.stroke()

        # Tier title
        ctx.select_font_face("Inter", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
        ctx.set_font_size(16.0)
        ctx.set_source_rgba(0.95, 0.98, 1.0, op)
        ctx.move_to(20.0, 38.0)
        ctx.show_text(self.tier_name)

        # Price
        ctx.set_font_size(32.0)
        ctx.move_to(20.0, 82.0)
        ctx.show_text(self.price)

        # Interval
        ctx.select_font_face("Inter", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)
        ctx.set_font_size(13.0)
        ctx.set_source_rgba(0.6, 0.7, 0.8, 0.8 * op)
        price_ext = ctx.text_extents(self.price)
        ctx.move_to(24.0 + price_ext.width, 82.0)
        ctx.show_text(self.interval)

        # Description
        ctx.set_font_size(11.0)
        ctx.move_to(20.0, 106.0)
        ctx.show_text(self.description)

        # Divider
        ctx.set_source_rgba(0.2, 0.25, 0.35, 0.4 * op)
        ctx.set_line_width(1.0)
        ctx.move_to(20.0, 124.0)
        ctx.line_to(w - 20.0, 124.0)
        ctx.stroke()

        # Feature items
        for i, feat in enumerate(self.features):
            fy = 145.0 + i * 28.0
            # Draw check dot
            ctx.set_source_rgba(0.1, 0.85, 0.45, 0.9 * op)
            ctx.arc(28.0, fy, 4.0, 0, 2 * math.pi)
            ctx.fill()

            ctx.select_font_face("Inter", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)
            ctx.set_font_size(12.0)
            ctx.set_source_rgba(0.85, 0.9, 0.96, 0.9 * op)
            ctx.move_to(40.0, fy + 4.0)
            ctx.show_text(feat)

        # CTA Button at bottom
        btn_y = h - 60.0
        btn_w = w - 40.0
        btn_h = 38.0
        btn_r = 8.0

        ctx.new_path()
        ctx.arc(20.0 + btn_w - btn_r, btn_y + btn_r, btn_r, -math.pi * 0.5, 0)
        ctx.arc(20.0 + btn_w - btn_r, btn_y + btn_h - btn_r, btn_r, 0, math.pi * 0.5)
        ctx.arc(20.0 + btn_r, btn_y + btn_h - btn_r, btn_r, math.pi * 0.5, math.pi)
        ctx.arc(20.0 + btn_r, btn_y + btn_r, btn_r, math.pi, math.pi * 1.5)
        ctx.close_path()

        if glow > 0.1:
            ctx.set_source_rgba(0.15, 0.5, 1.0, 0.95 * op)
            ctx.fill()
            cta_text = "Upgrade to Pro"
        else:
            ctx.set_source_rgba(0.12, 0.18, 0.26, 0.9 * op)
            ctx.fill_preserve()
            ctx.set_source_rgba(0.25, 0.35, 0.5, 0.6 * op)
            ctx.stroke()
            cta_text = "Get Started"

        ctx.select_font_face("Inter", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
        ctx.set_font_size(12.0)
        ctx.set_source_rgba(1.0, 1.0, 1.0, op)
        btn_ext = ctx.text_extents(cta_text)
        ctx.move_to(20.0 + (btn_w - btn_ext.width) * 0.5, btn_y + btn_h * 0.5 + btn_ext.height * 0.35)
        ctx.show_text(cta_text)

        super().draw(ctx, time)
        ctx.restore()


class PricingTierMatrix(Node):
    """
    SaaS Pricing Matrix Suite.
    Renders multi-column pricing tiers (Starter, Pro, Enterprise) with interactive
    tier highlighting, billing discount toggles, and feature comparison badges.
    """

    def __init__(
        self,
        tiers: Optional[List[Dict[str, Any]]] = None,
        is_annual: bool = False,
        width: float = 920.0,
        height: float = 560.0,
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)
        self.width_val = float(width)
        self.height_val = float(height)
        self.shadow = DropShadow(color=Color(0.0, 0.0, 0.0, 0.5), blur=32.0, offset=(0.0, 16.0))

        # Billing toggle in top right
        self.toggle = AnnualBillingToggle(is_annual=is_annual)
        self.toggle.position.set(Vector2D(self.width_val - 280.0, 24.0))
        self.add(self.toggle)

        # Columns
        raw_tiers = tiers or [
            {"name": "Starter", "price": "$0", "interval": "/mo", "description": "For hobbyists & side projects", "is_popular": False},
            {"name": "Pro", "price": "$49", "interval": "/mo", "description": "For high-velocity AI engineering", "is_popular": True},
            {"name": "Enterprise", "price": "$249", "interval": "/mo", "description": "Custom SLAs & dedicated hardware", "is_popular": False},
        ]

        self.columns: Dict[str, PricingTierColumn] = {}
        col_w = 270.0
        gap = 20.0
        start_x = 30.0

        for i, t_data in enumerate(raw_tiers):
            t_name = t_data.get("name", f"Tier {i}")
            col = PricingTierColumn(
                name=t_name,
                price=t_data.get("price", "$0"),
                interval=t_data.get("interval", "/mo"),
                description=t_data.get("description", ""),
                is_popular=t_data.get("is_popular", False),
                width=col_w,
                height=440.0,
            )
            col.position.set(Vector2D(start_x + i * (col_w + gap), 80.0))
            self.add(col)
            self.columns[t_name] = col

    def highlight_tier(self, tier_name: str = "Pro", duration: float = 0.8) -> List[AnimationAction]:
        """
        Fluent generator animation verb to pop and illuminate a selected pricing tier.
        """
        actions: List[AnimationAction] = []
        for name, col in self.columns.items():
            if name.lower() == tier_name.lower():
                actions.append(col.scale_sig.to(1.05, duration=duration, ease=Ease.out_back))
                actions.append(col.highlight_glow.to(1.0, duration=duration, ease=Ease.out_quad))
                actions.append(col.opacity.to(1.0, duration=duration, ease=Ease.out_quad))
            else:
                actions.append(col.scale_sig.to(0.96, duration=duration, ease=Ease.out_quad))
                actions.append(col.highlight_glow.to(0.0, duration=duration, ease=Ease.out_quad))
                actions.append(col.opacity.to(0.7, duration=duration, ease=Ease.out_quad))
        return actions

    def local_bounds(self, time: float = 0.0) -> Tuple[float, float, float, float]:
        return (0.0, 0.0, self.width_val, self.height_val)

    def draw(self, ctx: Any, time: float = 0.0) -> None:
        w, h = self.width_val, self.height_val
        ctx.save()

        # Header Title
        ctx.select_font_face("Inter", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
        ctx.set_font_size(18.0)
        ctx.set_source_rgba(0.95, 0.98, 1.0, 0.95)
        ctx.move_to(30.0, 48.0)
        ctx.show_text("Flexible Plans for Autonomous Intelligence")

        # Draw columns & toggle
        super().draw(ctx, time)
        ctx.restore()


PricingTierGrid = PricingTierMatrix
