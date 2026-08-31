"""
Deck Deal & Staging Motion Suites for Vibmo.
Inspired by video-shotcraft deck-deal-flyin, doc-park-left-pill-deal, and card-stack.
Implements non-linear spring physics metaphors for card dealing, fanning, and docking.
"""

from __future__ import annotations
import math
from typing import List, Optional, Tuple, Dict, Any, Union
import cairo
import numpy as np

from vibmo.core.color import Color, colors
from vibmo.core.signal import Signal, AnimationAction
from vibmo.core.easing import Ease, CubicBezier
from vibmo.scene.node import Node


class DeckDealFlyIn(Node):
    """
    Deals a cascade of feature cards onto the canvas from a deck origin.
    Applies physical acceleration metaphor with non-linear spring overshoot and hold rest.
    """

    def __init__(
        self,
        cards: Optional[List[Dict[str, Any]]] = None,
        origin: Tuple[float, float] = (960.0, 1200.0),
        spread_radius: float = 380.0,
        fan_angle_deg: float = 24.0,
        accent_color: Union[Color, str] = colors.CYAN,
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)
        self.cards_data = cards or [
            {"title": "Neural Engine", "metric": "99.4%", "icon": "cpu"},
            {"title": "GPU Pipeline", "metric": "60 FPS", "icon": "zap"},
            {"title": "Vector Index", "metric": "100k", "icon": "database"},
            {"title": "Auto-Reflow", "metric": "Zero Drift", "icon": "maximize"},
        ]
        self.origin = origin
        self.spread_radius = spread_radius
        self.fan_angle_deg = fan_angle_deg
        self.accent_color = Color.from_any(accent_color)
        
        # Signals
        self.progress = Signal(0.0, f"{self.id}.progress")
        self.spread_factor = Signal(0.0, f"{self.id}.spread_factor")
        self.rotation_tilt = Signal(0.0, f"{self.id}.rotation_tilt")

    def deal_cards(self, duration: float = 1.6, delay: float = 0.0) -> AnimationAction:
        """Deals cards with accelerating physics and spring overshoot."""
        return self.progress.to(1.0, duration=duration, delay=delay, ease=Ease.out_back)

    def fan_out(self, duration: float = 0.8, delay: float = 0.0) -> AnimationAction:
        """Spreads cards into a fanned arc deck."""
        return self.spread_factor.to(1.0, duration=duration, delay=delay, ease=Ease.out_expo)

    def draw(self, ctx: cairo.Context, time: float = 0.0) -> None:
        p = self.progress.evaluate_at(time)
        if p <= 0.001:
            return

        spread = self.spread_factor.evaluate_at(time)
        n = len(self.cards_data)
        cx, cy = self.position.evaluate_at(time)

        ctx.save()
        ctx.translate(cx, cy)

        for i, card_info in enumerate(self.cards_data):
            # Staggered entry progress
            card_delay = i * (0.4 / max(1, n))
            local_p = max(0.0, min(1.0, (p - card_delay) / max(0.001, 1.0 - card_delay)))
            
            if local_p <= 0.0:
                continue

            # Spring interpolation
            eased_p = 1.0 - math.pow(1.0 - local_p, 3)
            
            # Fan angle & position
            angle_norm = (i - (n - 1) / 2.0) / max(1.0, (n - 1) / 2.0) if n > 1 else 0.0
            angle_rad = math.radians(angle_norm * self.fan_angle_deg * spread)
            
            target_x = angle_norm * (self.spread_radius * spread + 80.0)
            target_y = math.sin(abs(angle_norm) * 0.5) * 40.0 * spread
            
            start_x, start_y = self.origin[0] - cx, self.origin[1] - cy
            
            curr_x = start_x + (target_x - start_x) * eased_p
            curr_y = start_y + (target_y - start_y) * eased_p
            curr_rot = angle_rad * eased_p

            # Draw card
            ctx.save()
            ctx.translate(curr_x, curr_y)
            ctx.rotate(curr_rot)

            card_w, card_h = 240.0, 150.0
            r = 16.0

            # Card Shadow
            ctx.save()
            ctx.set_source_rgba(0, 0, 0, 0.35 * eased_p)
            ctx.new_sub_path()
            ctx.arc(card_w / 2 - r, card_h / 2 - r + 8, r, 0, math.pi / 2)
            ctx.arc(-card_w / 2 + r, card_h / 2 - r + 8, r, math.pi / 2, math.pi)
            ctx.arc(-card_w / 2 + r, -card_h / 2 + r + 8, r, math.pi, 3 * math.pi / 2)
            ctx.arc(card_w / 2 - r, -card_h / 2 + r + 8, r, 3 * math.pi / 2, 2 * math.pi)
            ctx.close_path()
            ctx.fill()
            ctx.restore()

            # Glass Card Body
            ctx.new_sub_path()
            ctx.arc(card_w / 2 - r, card_h / 2 - r, r, 0, math.pi / 2)
            ctx.arc(-card_w / 2 + r, card_h / 2 - r, r, math.pi / 2, math.pi)
            ctx.arc(-card_w / 2 + r, -card_h / 2 + r, r, math.pi, 3 * math.pi / 2)
            ctx.arc(card_w / 2 - r, -card_h / 2 + r, r, 3 * math.pi / 2, 2 * math.pi)
            ctx.close_path()

            # Frosted Dark Surface
            ctx.set_source_rgba(0.08, 0.11, 0.18, 0.88)
            ctx.fill_preserve()

            # Card Border
            ctx.set_source_rgba(
                self.accent_color.r,
                self.accent_color.g,
                self.accent_color.b,
                0.3 + 0.5 * (1.0 - abs(angle_norm)),
            )
            ctx.set_line_width(1.5)
            ctx.stroke()

            # Top Specular Highlight
            ctx.move_to(-card_w / 2 + r, -card_h / 2 + 1)
            ctx.line_to(card_w / 2 - r, -card_h / 2 + 1)
            ctx.set_source_rgba(1, 1, 1, 0.25 * eased_p)
            ctx.set_line_width(1.0)
            ctx.stroke()

            # Text Labels
            ctx.select_font_face("Inter", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
            ctx.set_font_size(15.0)
            ctx.set_source_rgba(0.85, 0.90, 0.98, eased_p)
            ctx.move_to(-card_w / 2 + 20.0, -card_h / 2 + 38.0)
            ctx.show_text(str(card_info.get("title", "Feature")))

            # Metric Value
            ctx.select_font_face("Inter", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
            ctx.set_font_size(28.0)
            ctx.set_source_rgba(self.accent_color.r, self.accent_color.g, self.accent_color.b, eased_p)
            ctx.move_to(-card_w / 2 + 20.0, -card_h / 2 + 88.0)
            ctx.show_text(str(card_info.get("metric", "100%")))

            ctx.restore()

        ctx.restore()


class DocParkPillDeal(Node):
    """
    Docks a primary document panel to the left margin while dealing interactive
    feature pills along the right side with spring physics.
    """

    def __init__(
        self,
        doc_title: str = "Quarterly Research Synthesis",
        pills: Optional[List[str]] = None,
        accent_color: Union[Color, str] = colors.CYAN,
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)
        self.doc_title = doc_title
        self.pills = pills or [
            "Executive Summary",
            "Multi-Agent Benchmarks",
            "Latency Optimization",
            "Production Checklist",
        ]
        self.accent_color = Color.from_any(accent_color)
        
        self.doc_park_progress = Signal(0.0, f"{self.id}.doc_park")
        self.pill_deal_progress = Signal(0.0, f"{self.id}.pill_deal")

    def dock_left(self, duration: float = 1.0, delay: float = 0.0) -> AnimationAction:
        """Parks the document to the left margin."""
        return self.doc_park_progress.to(1.0, duration=duration, delay=delay, ease=Ease.out_expo)

    def deal_pills(self, duration: float = 1.2, delay: float = 0.0) -> AnimationAction:
        """Deals pills on the right side."""
        return self.pill_deal_progress.to(1.0, duration=duration, delay=delay, ease=Ease.out_back)

    def draw(self, ctx: cairo.Context, time: float = 0.0) -> None:
        dp = self.doc_park_progress.evaluate_at(time)
        pp = self.pill_deal_progress.evaluate_at(time)

        if dp <= 0.001 and pp <= 0.001:
            return

        cx, cy = self.position.evaluate_at(time)

        ctx.save()
        ctx.translate(cx, cy)

        # 1. Document Window on Left
        doc_x = -320.0 + (1.0 - dp) * 200.0
        doc_w, doc_h = 420.0, 480.0
        r = 16.0

        ctx.save()
        ctx.translate(doc_x, -doc_h / 2)

        # Shadow
        ctx.set_source_rgba(0, 0, 0, 0.4 * dp)
        ctx.new_sub_path()
        ctx.arc(doc_w - r, doc_h - r + 12, r, 0, math.pi / 2)
        ctx.arc(r, doc_h - r + 12, r, math.pi / 2, math.pi)
        ctx.arc(r, r + 12, r, math.pi, 3 * math.pi / 2)
        ctx.arc(doc_w - r, r + 12, r, 3 * math.pi / 2, 2 * math.pi)
        ctx.close_path()
        ctx.fill()

        # Doc Surface
        ctx.set_source_rgba(0.06, 0.09, 0.15, 0.95)
        ctx.new_sub_path()
        ctx.arc(doc_w - r, doc_h - r, r, 0, math.pi / 2)
        ctx.arc(r, doc_h - r, r, math.pi / 2, math.pi)
        ctx.arc(r, r, r, math.pi, 3 * math.pi / 2)
        ctx.arc(doc_w - r, r, r, 3 * math.pi / 2, 2 * math.pi)
        ctx.close_path()
        ctx.fill_preserve()

        ctx.set_source_rgba(0.2, 0.25, 0.35, 0.6)
        ctx.set_line_width(1.2)
        ctx.stroke()

        # Doc Header & Mock Lines
        ctx.select_font_face("Inter", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
        ctx.set_font_size(18.0)
        ctx.set_source_rgba(0.9, 0.95, 1.0, dp)
        ctx.move_to(24.0, 44.0)
        ctx.show_text(self.doc_title)

        # Mock paragraph skeleton lines
        for row in range(7):
            y_pos = 90.0 + row * 40.0
            width_frac = 0.85 if row % 3 != 2 else 0.55
            ctx.set_source_rgba(0.25, 0.32, 0.45, 0.45 * dp)
            ctx.rectangle(24.0, y_pos, (doc_w - 48.0) * width_frac, 12.0)
            ctx.fill()

        ctx.restore()

        # 2. Pills on Right
        if pp > 0.001:
            for idx, pill_text in enumerate(self.pills):
                stagger = idx * 0.15
                local_p = max(0.0, min(1.0, (pp - stagger) / max(0.001, 1.0 - stagger)))
                if local_p <= 0.0:
                    continue

                eased_p = 1.0 - math.pow(1.0 - local_p, 3)
                pill_y = -180.0 + idx * 75.0
                pill_x = 180.0 + (1.0 - eased_p) * 250.0

                ctx.save()
                ctx.translate(pill_x, pill_y)

                pw, ph = 320.0, 56.0
                pr = 14.0

                # Pill Surface
                ctx.set_source_rgba(0.09, 0.13, 0.22, 0.92 * eased_p)
                ctx.new_sub_path()
                ctx.arc(pw - pr, ph - pr, pr, 0, math.pi / 2)
                ctx.arc(pr, ph - pr, pr, math.pi / 2, math.pi)
                ctx.arc(pr, pr, pr, math.pi, 3 * math.pi / 2)
                ctx.arc(pw - pr, pr, pr, 3 * math.pi / 2, 2 * math.pi)
                ctx.close_path()
                ctx.fill_preserve()

                # Highlight Border
                ctx.set_source_rgba(
                    self.accent_color.r,
                    self.accent_color.g,
                    self.accent_color.b,
                    0.45 * eased_p,
                )
                ctx.set_line_width(1.4)
                ctx.stroke()

                # Index badge
                ctx.set_source_rgba(
                    self.accent_color.r,
                    self.accent_color.g,
                    self.accent_color.b,
                    0.25 * eased_p,
                )
                ctx.arc(28.0, ph / 2, 12.0, 0, 2 * math.pi)
                ctx.fill()

                ctx.select_font_face("Inter", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
                ctx.set_font_size(12.0)
                ctx.set_source_rgba(1, 1, 1, eased_p)
                ctx.move_to(24.0, ph / 2 + 4.0)
                ctx.show_text(str(idx + 1))

                # Pill text
                ctx.set_font_size(15.0)
                ctx.set_source_rgba(0.9, 0.95, 1.0, eased_p)
                ctx.move_to(52.0, ph / 2 + 5.0)
                ctx.show_text(pill_text)

                ctx.restore()

        ctx.restore()
