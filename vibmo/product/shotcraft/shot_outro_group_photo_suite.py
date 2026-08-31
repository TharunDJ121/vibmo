"""
Outro Finale & Title Sequences for Vibmo.
Inspired by video-shotcraft:
- outro-group-photo-launch: Keynote Family Portrait (Case Law Q8) - all showcased feature cards
  fly in from 4 corners around the brand wordmark with crane sweep & stage lights.
- brand-ink-open: Fine ink crosshairs + stamped wordmark + typewriter subtitle.
- brace-expand: Curly braces { } expanding horizontally to unveil title text.
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


class OutroGroupPhotoLaunch(Node):
    """
    Keynote Group Photo / Family Portrait Outro (Case Law Q8).
    All product feature cards fly in from the 4 corners of the canvas to surround
    the central brand wordmark, elevating energy to the highest peak of the video.
    """

    def __init__(
        self,
        brand_name: str = "Vibmo",
        tagline: str = "The Autonomous Motion Design Engine",
        feature_cards: Optional[List[Dict[str, str]]] = None,
        accent_color: Union[Color, str] = colors.CYAN,
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)
        self.brand_name = brand_name
        self.tagline = tagline
        self.feature_cards = feature_cards or [
            {"title": "Neural Shaders", "corner": "top_left"},
            {"title": "Audio Beat-Sync", "corner": "top_right"},
            {"title": "2.5D Camera Rig", "corner": "bottom_left"},
            {"title": "CapCut Export", "corner": "bottom_right"},
        ]
        self.accent_color = Color.from_any(accent_color)

        self.converge_progress = Signal(0.0, f"{self.id}.converge")
        self.stage_light = Signal(0.0, f"{self.id}.stage_light")

    def launch_family_portrait(self, duration: float = 1.6, delay: float = 0.0) -> AnimationAction:
        """Launches the full keynote family portrait assemble."""
        return self.converge_progress.to(1.0, duration=duration, delay=delay, ease=Ease.out_back)

    def draw(self, ctx: cairo.Context, time: float = 0.0) -> None:
        p = self.converge_progress.evaluate_at(time)
        if p <= 0.001:
            return

        cx, cy = self.position.evaluate_at(time)

        ctx.save()
        ctx.translate(cx, cy)

        # 1. Central Ambient Stage Light
        ctx.save()
        stage_pat = cairo.RadialGradient(0.0, 0.0, 10.0, 0.0, 0.0, 600.0)
        stage_pat.add_color_stop_rgba(
            0.0,
            self.accent_color.r,
            self.accent_color.g,
            self.accent_color.b,
            0.35 * p,
        )
        stage_pat.add_color_stop_rgba(
            0.5,
            self.accent_color.r * 0.3,
            self.accent_color.g * 0.3,
            self.accent_color.b * 0.3,
            0.12 * p,
        )
        stage_pat.add_color_stop_rgba(1.0, 0.0, 0.0, 0.0, 0.0)
        ctx.set_source(stage_pat)
        ctx.arc(0.0, 0.0, 600.0, 0, 2 * math.pi)
        ctx.fill()
        ctx.restore()

        # 2. Central Brand Wordmark
        ctx.select_font_face("Space Grotesk", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
        ctx.set_font_size(68.0)
        ctx.set_source_rgba(0.95, 0.98, 1.0, p)
        
        # Measure brand text
        ext = ctx.text_extents(self.brand_name)
        ctx.move_to(-ext.width / 2, 10.0)
        ctx.show_text(self.brand_name)

        ctx.select_font_face("Inter", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)
        ctx.set_font_size(18.0)
        ctx.set_source_rgba(self.accent_color.r, self.accent_color.g, self.accent_color.b, p)
        ext_tag = ctx.text_extents(self.tagline)
        ctx.move_to(-ext_tag.width / 2, 50.0)
        ctx.show_text(self.tagline)

        # 3. Four Feature Cards Flying in from 4 Corners
        corner_offsets = {
            "top_left": ((-560.0, -1000.0), (-380.0, -180.0), -6.0),
            "top_right": ((560.0, -1000.0), (380.0, -180.0), 6.0),
            "bottom_left": ((-560.0, 1000.0), (-380.0, 180.0), 4.0),
            "bottom_right": ((560.0, 1000.0), (380.0, 180.0), -4.0),
        }

        card_w, card_h = 240.0, 120.0
        r = 14.0

        for idx, card in enumerate(self.feature_cards):
            corner = card.get("corner", list(corner_offsets.keys())[idx % 4])
            start_pos, end_pos, angle_deg = corner_offsets[corner]

            curr_x = start_pos[0] + (end_pos[0] - start_pos[0]) * p
            curr_y = start_pos[1] + (end_pos[1] - start_pos[1]) * p
            curr_rot = math.radians(angle_deg * p)

            ctx.save()
            ctx.translate(curr_x, curr_y)
            ctx.rotate(curr_rot)

            # Drop Shadow
            ctx.set_source_rgba(0, 0, 0, 0.4 * p)
            ctx.rectangle(-card_w / 2, -card_h / 2 + 10, card_w, card_h)
            ctx.fill()

            # Glass Surface
            ctx.new_sub_path()
            ctx.arc(card_w / 2 - r, card_h / 2 - r, r, 0, math.pi / 2)
            ctx.arc(-card_w / 2 + r, card_h / 2 - r, r, math.pi / 2, math.pi)
            ctx.arc(-card_w / 2 + r, -card_h / 2 + r, r, math.pi, 3 * math.pi / 2)
            ctx.arc(card_w / 2 - r, -card_h / 2 + r, r, 3 * math.pi / 2, 2 * math.pi)
            ctx.close_path()

            ctx.set_source_rgba(0.08, 0.11, 0.18, 0.9)
            ctx.fill_preserve()

            ctx.set_source_rgba(
                self.accent_color.r,
                self.accent_color.g,
                self.accent_color.b,
                0.5 * p,
            )
            ctx.set_line_width(1.4)
            ctx.stroke()

            # Card Title
            ctx.select_font_face("Inter", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
            ctx.set_font_size(15.0)
            ctx.set_source_rgba(0.9, 0.95, 1.0, p)
            ctx.move_to(-card_w / 2 + 20.0, -card_h / 2 + 40.0)
            ctx.show_text(card.get("title", "Feature"))

            # Dot indicator
            ctx.set_source_rgba(self.accent_color.r, self.accent_color.g, self.accent_color.b, p)
            ctx.arc(-card_w / 2 + 24.0, card_h / 2 - 28.0, 5.0, 0, 2 * math.pi)
            ctx.fill()

            ctx.set_font_size(12.0)
            ctx.set_source_rgba(0.65, 0.75, 0.9, p)
            ctx.move_to(-card_w / 2 + 36.0, card_h / 2 - 24.0)
            ctx.show_text("VERIFIED ACTIVE")

            ctx.restore()

        ctx.restore()


class BrandInkOpen(Node):
    """
    Fine ink reticle crosshairs + stamped wordmark + typewriter subtitle.
    """

    def __init__(
        self,
        brand_name: str = "VIBMO",
        subtitle: str = "AUTONOMOUS MOTION GRAPHICS",
        accent_color: Union[Color, str] = colors.CYAN,
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)
        self.brand_name = brand_name
        self.subtitle = subtitle
        self.accent_color = Color.from_any(accent_color)

        self.reticle_progress = Signal(0.0, f"{self.id}.reticle")
        self.stamp_progress = Signal(0.0, f"{self.id}.stamp")

    def animate_intro(self, duration: float = 1.5, delay: float = 0.0) -> AnimationAction:
        """Draws reticle crosshairs and stamps wordmark."""
        return self.stamp_progress.to(1.0, duration=duration, delay=delay, ease=Ease.out_expo)

    def draw(self, ctx: cairo.Context, time: float = 0.0) -> None:
        sp = self.stamp_progress.evaluate_at(time)
        if sp <= 0.001:
            return

        cx, cy = self.position.evaluate_at(time)

        ctx.save()
        ctx.translate(cx, cy)

        # 1. Fine Ink Reticle Crosshairs
        cross_len = 24.0
        ctx.set_source_rgba(
            self.accent_color.r,
            self.accent_color.g,
            self.accent_color.b,
            0.7 * sp,
        )
        ctx.set_line_width(1.0)
        
        # Center tick
        ctx.move_to(-cross_len, 0.0)
        ctx.line_to(cross_len, 0.0)
        ctx.move_to(0.0, -cross_len)
        ctx.line_to(0.0, cross_len)
        ctx.stroke()

        # 2. Stamped Brand Wordmark with slight scale slam
        scale = 1.0 + 0.25 * (1.0 - sp)
        ctx.save()
        ctx.scale(scale, scale)

        ctx.select_font_face("Space Grotesk", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
        ctx.set_font_size(52.0)
        ctx.set_source_rgba(0.95, 0.98, 1.0, sp)
        
        ext = ctx.text_extents(self.brand_name)
        ctx.move_to(-ext.width / 2, -18.0)
        ctx.show_text(self.brand_name)

        # 3. Typewriter Subtitle
        ctx.select_font_face("Inter", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
        ctx.set_font_size(13.0)
        ctx.set_source_rgba(self.accent_color.r, self.accent_color.g, self.accent_color.b, sp)
        
        ext_sub = ctx.text_extents(self.subtitle)
        ctx.move_to(-ext_sub.width / 2, 28.0)
        ctx.show_text(self.subtitle)

        ctx.restore()
        ctx.restore()


class BraceExpand(Node):
    """
    Curly braces { } expanding horizontally to unveil title text.
    """

    def __init__(
        self,
        title_text: str = "ZERO BOILERPLATE",
        accent_color: Union[Color, str] = colors.CYAN,
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)
        self.title_text = title_text
        self.accent_color = Color.from_any(accent_color)

        self.expand_progress = Signal(0.0, f"{self.id}.expand")

    def expand(self, duration: float = 1.0, delay: float = 0.0) -> AnimationAction:
        """Expands braces horizontally."""
        return self.expand_progress.to(1.0, duration=duration, delay=delay, ease=Ease.out_back)

    def draw(self, ctx: cairo.Context, time: float = 0.0) -> None:
        p = self.expand_progress.evaluate_at(time)
        if p <= 0.001:
            return

        cx, cy = self.position.evaluate_at(time)

        ctx.save()
        ctx.translate(cx, cy)

        # Measure text width
        ctx.select_font_face("Space Grotesk", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
        ctx.set_font_size(36.0)
        ext = ctx.text_extents(self.title_text)
        half_w = (ext.width / 2) + 20.0

        brace_offset = half_w * p

        # Left Brace "{"
        ctx.set_font_size(44.0)
        ctx.set_source_rgba(self.accent_color.r, self.accent_color.g, self.accent_color.b, 1.0)
        ctx.move_to(-brace_offset - 20.0, 10.0)
        ctx.show_text("{")

        # Revealed Text (Clipped between braces)
        ctx.save()
        ctx.rectangle(-brace_offset, -40.0, brace_offset * 2, 80.0)
        ctx.clip()

        ctx.set_font_size(36.0)
        ctx.set_source_rgba(0.95, 0.98, 1.0, p)
        ctx.move_to(-ext.width / 2, 10.0)
        ctx.show_text(self.title_text)
        ctx.restore()

        # Right Brace "}"
        ctx.set_font_size(44.0)
        ctx.set_source_rgba(self.accent_color.r, self.accent_color.g, self.accent_color.b, 1.0)
        ctx.move_to(brace_offset, 10.0)
        ctx.show_text("}")

        ctx.restore()
