"""
Model Orbit, Export Burst & Ecosystem Integration Suites for Vibmo.
Inspired by video-production-skills dark-saas-magic-video (Blueprints 5, 6, 7).
Provides 3D orbital model badge rings, radiating export format bursts, and curved ecosystem nodes.
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


class ModelCapabilityOrbit(Node):
    """
    3D Orbital Badge Ring of AI models (Blueprint 6).
    Badges rotate in depth with dynamic 2.5D scale and opacity swapping.
    """

    def __init__(
        self,
        center_title: str = "MULTI-MODEL ORCHESTRATION",
        models: Optional[List[str]] = None,
        radius_x: float = 340.0,
        radius_y: float = 90.0,
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)
        self.center_title = center_title
        self.models = models or ["Claude 3.7", "GPT-4o", "DeepSeek R1", "Gemini 2.5", "Llama 3.3"]
        self.radius_x = radius_x
        self.radius_y = radius_y

        self.orbit_progress = Signal(0.0, f"{self.id}.orbit")
        self.ring_open = Signal(0.0, f"{self.id}.open")

    def open_ring(self, duration: float = 1.2, delay: float = 0.0) -> AnimationAction:
        """Expands the orbital ring into view."""
        return self.ring_open.to(1.0, duration=duration, delay=delay, ease=Ease.out_back)

    def rotate_orbit(self, revolutions: float = 1.0, duration: float = 3.0, delay: float = 0.0) -> AnimationAction:
        """Rotates badges along the 3D ellipse."""
        return self.orbit_progress.to(revolutions, duration=duration, delay=delay, ease=Ease.in_out_cubic)

    def draw(self, ctx: cairo.Context, time: float = 0.0) -> None:
        open_p = self.ring_open.evaluate_at(time)
        if open_p <= 0.001:
            return

        rot = self.orbit_progress.evaluate_at(time)
        cx, cy = self.position.evaluate_at(time)
        n = len(self.models)

        ctx.save()
        ctx.translate(cx, cy)

        # 1. Elliptical Orbital Track Path
        ctx.save()
        ctx.scale(1.0, self.radius_y / max(1.0, self.radius_x))
        ctx.set_source_rgba(0.2, 0.28, 0.45, 0.35 * open_p)
        ctx.set_line_width(1.5)
        ctx.arc(0, 0, self.radius_x * open_p, 0, 2 * math.pi)
        ctx.stroke()
        ctx.restore()

        # 2. Central Title Box
        ctx.select_font_face("Space Grotesk", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
        ctx.set_font_size(24.0)
        ctx.set_source_rgba(0.95, 0.98, 1.0, open_p)
        ext = ctx.text_extents(self.center_title)
        ctx.move_to(-ext.width / 2, 8.0)
        ctx.show_text(self.center_title)

        # 3. Compute 3D Positions of Badges and Sort by Depth (Z-index)
        badge_positions = []
        for i, name in enumerate(self.models):
            angle = (i * (2 * math.pi / n) + rot * 2 * math.pi) % (2 * math.pi)
            x = math.cos(angle) * self.radius_x * open_p
            y = math.sin(angle) * self.radius_y * open_p
            z = math.sin(angle)  # -1 (back) to +1 (front)
            badge_positions.append((z, x, y, name))

        badge_positions.sort(key=lambda item: item[0])  # Draw back items first

        # 4. Render Badges
        for z, x, y, name in badge_positions:
            scale = 0.75 + 0.25 * (z + 1.0) / 2.0
            alpha = (0.4 + 0.6 * (z + 1.0) / 2.0) * open_p
            bw, bh = 140.0, 40.0
            br = 10.0

            ctx.save()
            ctx.translate(x, y)
            ctx.scale(scale, scale)

            # Badge Body
            ctx.new_sub_path()
            ctx.arc(bw / 2 - br, bh / 2 - br, br, 0, math.pi / 2)
            ctx.arc(-bw / 2 + br, bh / 2 - br, br, math.pi / 2, math.pi)
            ctx.arc(-bw / 2 + br, -bh / 2 + br, br, math.pi, 3 * math.pi / 2)
            ctx.arc(bw / 2 - br, -bh / 2 + br, br, 3 * math.pi / 2, 2 * math.pi)
            ctx.close_path()

            ctx.set_source_rgba(0.08, 0.12, 0.20, 0.95 * alpha)
            ctx.fill_preserve()

            # Border
            ctx.set_source_rgba(0.06, 0.71, 0.83, 0.65 * alpha)
            ctx.set_line_width(1.4)
            ctx.stroke()

            # Name Text
            ctx.select_font_face("Inter", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
            ctx.set_font_size(13.0)
            ctx.set_source_rgba(1, 1, 1, alpha)
            ext_b = ctx.text_extents(name)
            ctx.move_to(-ext_b.width / 2, 4.0)
            ctx.show_text(name)

            ctx.restore()

        ctx.restore()


class ExportBurstContainer(Node):
    """
    Export Burst Container (Blueprint 7).
    Container opening with radiating output format pills: PDF, PPTX, Markdown, MP4, API.
    """

    def __init__(
        self,
        headline: str = "Instant Multi-Format Export",
        formats: Optional[List[str]] = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)
        self.headline = headline
        self.formats = formats or ["PDF", "PPTX", "Markdown", "MP4 60FPS", "REST API", "Live Web"]

        self.burst_progress = Signal(0.0, f"{self.id}.burst")

    def trigger_burst(self, duration: float = 1.2, delay: float = 0.0) -> AnimationAction:
        """Triggers the radiating burst of export pills."""
        return self.burst_progress.to(1.0, duration=duration, delay=delay, ease=Ease.out_back)

    def draw(self, ctx: cairo.Context, time: float = 0.0) -> None:
        bp = self.burst_progress.evaluate_at(time)
        if bp <= 0.001:
            return

        cx, cy = self.position.evaluate_at(time)
        n = len(self.formats)

        ctx.save()
        ctx.translate(cx, cy)

        # 1. Headline
        ctx.select_font_face("Space Grotesk", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
        ctx.set_font_size(36.0)
        ctx.set_source_rgba(0.95, 0.98, 1.0, bp)
        ext = ctx.text_extents(self.headline)
        ctx.move_to(-ext.width / 2, -180.0)
        ctx.show_text(self.headline)

        # 2. Central Hub Box
        box_w, box_h = 180.0, 90.0
        r = 16.0
        ctx.set_source_rgba(0.08, 0.11, 0.18, 0.95)
        ctx.rectangle(-box_w / 2, -box_h / 2, box_w, box_h)
        ctx.fill_preserve()
        ctx.set_source_rgba(0.93, 0.28, 0.60, 0.8)  # Magenta border
        ctx.set_line_width(2.0)
        ctx.stroke()

        ctx.select_font_face("Inter", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
        ctx.set_font_size(15.0)
        ctx.set_source_rgb(1, 1, 1)
        ctx.move_to(-52.0, 6.0)
        ctx.show_text("EXPORT ENGINE")

        # 3. Bursting Output Format Pills
        radius = 240.0 * bp
        for idx, fmt_name in enumerate(self.formats):
            ang = idx * (2 * math.pi / n) - (math.pi / 2)
            px = math.cos(ang) * radius
            py = math.sin(ang) * radius

            pw, ph = 120.0, 42.0
            pr = 12.0

            ctx.save()
            ctx.translate(px, py)

            # Connecting Line to Hub
            ctx.set_source_rgba(0.06, 0.71, 0.83, 0.4 * bp)
            ctx.set_line_width(1.2)
            ctx.move_to(-px * 0.4, -py * 0.4)
            ctx.line_to(0, 0)
            ctx.stroke()

            # Pill Surface
            ctx.set_source_rgba(0.09, 0.14, 0.22, 0.95 * bp)
            ctx.rectangle(-pw / 2, -ph / 2, pw, ph)
            ctx.fill_preserve()

            ctx.set_source_rgba(0.06, 0.71, 0.83, 0.75 * bp)
            ctx.set_line_width(1.5)
            ctx.stroke()

            # Label
            ctx.set_font_size(13.0)
            ctx.set_source_rgba(0.95, 0.98, 1.0, bp)
            ext_p = ctx.text_extents(fmt_name)
            ctx.move_to(-ext_p.width / 2, 5.0)
            ctx.show_text(fmt_name)

            ctx.restore()

        ctx.restore()


class ConnectEcosystemSlot(Node):
    """
    Connect Ecosystem Curved Slot Node (Blueprint 5).
    Large curved node with orbiting integration pills (GitHub, Slack, Stripe, Notion).
    """

    def __init__(
        self,
        hub_name: str = "Connected Cloud",
        integrations: Optional[List[str]] = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)
        self.hub_name = hub_name
        self.integrations = integrations or ["GitHub", "Slack", "Stripe", "PostgreSQL", "Notion"]

        self.expand_progress = Signal(0.0, f"{self.id}.expand")

    def animate_connect(self, duration: float = 1.2, delay: float = 0.0) -> AnimationAction:
        """Expands curved slot node and integration badges."""
        return self.expand_progress.to(1.0, duration=duration, delay=delay, ease=Ease.out_expo)

    def draw(self, ctx: cairo.Context, time: float = 0.0) -> None:
        p = self.expand_progress.evaluate_at(time)
        if p <= 0.001:
            return

        cx, cy = self.position.evaluate_at(time)
        ctx.save()
        ctx.translate(cx, cy)

        # Curved Arc Slot
        arc_r = 280.0
        ctx.set_source_rgba(0.18, 0.25, 0.38, 0.45 * p)
        ctx.set_line_width(2.0)
        ctx.arc(0, 0, arc_r, -math.pi * 0.7, math.pi * 0.7)
        ctx.stroke()

        # Integration Badges along arc
        n = len(self.integrations)
        for i, item in enumerate(self.integrations):
            ang = -math.pi * 0.6 + i * (math.pi * 1.2 / max(1, n - 1))
            ix = math.cos(ang) * arc_r * p
            iy = math.sin(ang) * arc_r * p

            ctx.save()
            ctx.translate(ix, iy)

            ctx.set_source_rgba(0.08, 0.12, 0.20, 0.95 * p)
            ctx.arc(0, 0, 32.0, 0, 2 * math.pi)
            ctx.fill_preserve()
            ctx.set_source_rgba(0.06, 0.71, 0.83, 0.7 * p)
            ctx.set_line_width(1.4)
            ctx.stroke()

            ctx.select_font_face("Inter", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
            ctx.set_font_size(11.0)
            ctx.set_source_rgba(1, 1, 1, p)
            ext_i = ctx.text_extents(item)
            ctx.move_to(-ext_i.width / 2, 4.0)
            ctx.show_text(item)

            ctx.restore()

        # Center Hub
        ctx.set_source_rgba(0.06, 0.08, 0.14, 0.95)
        ctx.arc(0, 0, 60.0, 0, 2 * math.pi)
        ctx.fill_preserve()
        ctx.set_source_rgba(0.93, 0.28, 0.60, 0.8 * p)
        ctx.set_line_width(2.0)
        ctx.stroke()

        ctx.select_font_face("Space Grotesk", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
        ctx.set_font_size(13.0)
        ctx.set_source_rgb(1, 1, 1)
        ext_h = ctx.text_extents(self.hub_name)
        ctx.move_to(-ext_h.width / 2, 5.0)
        ctx.show_text(self.hub_name)

        ctx.restore()
