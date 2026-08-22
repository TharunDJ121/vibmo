from __future__ import annotations
import math
from typing import Any, Optional, Union
import cairo

from vibmo.core.vector import Vector2D
from vibmo.core.color import Color, colors
from vibmo.core.signal import Signal, AnimationAction
from vibmo.core.easing import Ease, EasingFunc
from vibmo.scene.node import Node
from vibmo.components.glass import GlassCard
from vibmo.layout.container import FlexContainer

class MaskedTokenRevealField(Node):
    def __init__(
        self,
        masked_text: str = "sk-live-••••••••••••••••",
        clear_text: str = "sk-live-a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6",
        width: float = 380.0,
        height: float = 52.0,
        font_family: str = "Consolas",
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)
        self.masked_text = masked_text
        self.clear_text = clear_text
        self.width_val = float(width)
        self.height_val = float(height)
        self.font_family = font_family

        self.reveal_progress = Signal(0.0)

    def trigger_reveal(self, duration: float = 0.5, ease: EasingFunc = Ease.in_out_quad) -> AnimationAction:
        return self.reveal_progress.to(1.0, duration=duration, ease=ease)

    def trigger_hide(self, duration: float = 0.5, ease: EasingFunc = Ease.in_out_quad) -> AnimationAction:
        return self.reveal_progress.to(0.0, duration=duration, ease=ease)

    def draw(self, ctx: Any, time: float = 0.0) -> None:
        w, h = self.width_val, self.height_val
        ctx.save()

        # Draw rounded rect background
        r = 10.0
        ctx.new_path()
        ctx.arc(w - r, r, r, -math.pi * 0.5, 0)
        ctx.arc(w - r, h - r, r, 0, math.pi * 0.5)
        ctx.arc(r, h - r, r, math.pi * 0.5, math.pi)
        ctx.arc(r, r, r, math.pi, math.pi * 1.5)
        ctx.close_path()

        ctx.set_source_rgba(0.05, 0.07, 0.12, 0.9)
        ctx.fill_preserve()
        ctx.set_source_rgba(1.0, 1.0, 1.0, 0.1)
        ctx.set_line_width(1.0)
        ctx.stroke()

        progress = self.reveal_progress.get()

        ctx.select_font_face(self.font_family, cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)
        ctx.set_font_size(14.0)

        # Ensure smooth transition between masked and unmasked text.
        # Draw masked text fading out
        if progress < 1.0:
            ctx.set_source_rgba(0.7, 0.7, 0.7, 1.0 - progress)
            ctx.move_to(14.0, h / 2 + 5.0)
            ctx.show_text(self.masked_text)

        # Draw clear text fading in
        if progress > 0.0:
            ctx.set_source_rgba(0.9, 0.9, 0.9, progress)
            ctx.move_to(14.0, h / 2 + 5.0)
            ctx.show_text(self.clear_text)

        ctx.restore()

class CopyClipboardPill(Node):
    def __init__(
        self,
        width: float = 120.0,
        height: float = 40.0,
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)
        self.width_val = float(width)
        self.height_val = float(height)
        self.copy_progress = Signal(0.0)

    def trigger_copy(self, duration: float = 0.3, ease: EasingFunc = Ease.in_out_quad) -> AnimationAction:
        return self.copy_progress.to(1.0, duration=duration, ease=ease)

    def draw(self, ctx: Any, time: float = 0.0) -> None:
        w, h = self.width_val, self.height_val
        ctx.save()

        progress = self.copy_progress.get()

        # Pill Background
        r = h / 2.0
        ctx.new_path()
        ctx.arc(w - r, r, r, -math.pi * 0.5, 0)
        ctx.arc(w - r, h - r, r, 0, math.pi * 0.5)
        ctx.arc(r, h - r, r, math.pi * 0.5, math.pi)
        ctx.arc(r, r, r, math.pi, math.pi * 1.5)
        ctx.close_path()

        # Base color vs Emerald color interpolation
        base_color = Color.from_any(colors.SLATE_700)
        emerald_color = Color.from_any(colors.EMERALD)

        bg_r = base_color.r + (emerald_color.r - base_color.r) * progress
        bg_g = base_color.g + (emerald_color.g - base_color.g) * progress
        bg_b = base_color.b + (emerald_color.b - base_color.b) * progress

        ctx.set_source_rgba(bg_r, bg_g, bg_b, 0.8)
        ctx.fill_preserve()
        ctx.set_source_rgba(1.0, 1.0, 1.0, 0.15)
        ctx.set_line_width(1.0)
        ctx.stroke()

        # Text
        ctx.select_font_face("Segoe UI", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
        ctx.set_font_size(13.0)

        if progress < 0.5:
            text = "Copy Key"
            ctx.set_source_rgba(0.9, 0.9, 0.9, 1.0 - (progress * 2))
        else:
            text = "Copied! ✓"
            ctx.set_source_rgba(1.0, 1.0, 1.0, (progress - 0.5) * 2)

        extents = ctx.text_extents(text)
        ctx.move_to((w - extents.width) / 2.0 - extents.x_bearing, (h - extents.height) / 2.0 - extents.y_bearing)
        ctx.show_text(text)

        ctx.restore()

class ApiKeyVaultCard(GlassCard):
    def __init__(
        self,
        key_name: str = "Production AI Router",
        created_date: str = "Created: Oct 12, 2023",
        last_used: str = "Last used: 2 mins ago",
        width: float = 600.0,
        height: float = 240.0,
        **kwargs: Any,
    ) -> None:
        super().__init__(
            direction="column",
            width=width,
            height=height,
            padding=32.0,
            gap=20.0,
            corner_radius=24.0,
            fill=Color(0.02, 0.03, 0.08, 0.6),
            **kwargs,
        )
        self.key_name = key_name
        self.created_date = created_date
        self.last_used = last_used

        # Add masked field
        self.token_field = MaskedTokenRevealField(width=400.0)
        # Add copy pill
        self.copy_pill = CopyClipboardPill()

        # Wrap them in a row container
        row = FlexContainer(
            direction="row",
            gap=16.0,
            width=width - 64.0, # width - 2*padding
            height=60.0,
            fill=None,
            stroke=None
        )
        row.add(self.token_field)
        row.add(self.copy_pill)

        self.add(row)

    def draw(self, ctx: Any, time: float = 0.0) -> None:
        # Draw background and children
        super().draw(ctx, time)

        # We need to draw the text info at the top. Since GlassCard draws background and its flex children,
        # let's just overlay the text.
        # Actually a better approach is to add text elements if they existed, or just draw them directly.
        ctx.save()
        pos = self.position.get()
        # GlassCard origin is pos

        ctx.select_font_face("Segoe UI", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
        ctx.set_font_size(18.0)
        ctx.set_source_rgba(1.0, 1.0, 1.0, 0.95)
        ctx.move_to(pos.x + 32.0, pos.y + 32.0 + 18.0)
        ctx.show_text(self.key_name)

        ctx.select_font_face("Segoe UI", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)
        ctx.set_font_size(12.0)
        ctx.set_source_rgba(0.6, 0.65, 0.7, 1.0)
        ctx.move_to(pos.x + 32.0, pos.y + 32.0 + 40.0)
        ctx.show_text(f"{self.created_date} • {self.last_used}")

        ctx.restore()

class RevokeConfirmModal(GlassCard):
    def __init__(
        self,
        width: float = 480.0,
        height: float = 260.0,
        **kwargs: Any,
    ) -> None:
        super().__init__(
            direction="column",
            width=width,
            height=height,
            padding=32.0,
            gap=16.0,
            corner_radius=20.0,
            fill=Color(0.04, 0.02, 0.02, 0.8),
            stroke=colors.RED,
            **kwargs,
        )

    def draw(self, ctx: Any, time: float = 0.0) -> None:
        super().draw(ctx, time)

        ctx.save()
        pos = self.position.get()
        w, h = self.width.get(), self.height.get()

        # Warning badge
        badge_x, badge_y = pos.x + 32.0, pos.y + 32.0
        badge_r = 24.0
        ctx.new_path()
        ctx.arc(badge_x + badge_r, badge_y + badge_r, badge_r, 0, 2*math.pi)
        ctx.set_source_rgba(1.0, 0.2, 0.2, 0.2)
        ctx.fill_preserve()
        ctx.set_source_rgba(1.0, 0.2, 0.2, 0.8)
        ctx.set_line_width(2.0)
        ctx.stroke()

        # Exclamation mark
        ctx.select_font_face("Segoe UI", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
        ctx.set_font_size(24.0)
        ctx.set_source_rgba(1.0, 0.2, 0.2, 1.0)
        ext = ctx.text_extents("!")
        ctx.move_to(badge_x + badge_r - ext.width/2 - ext.x_bearing, badge_y + badge_r - ext.height/2 - ext.y_bearing)
        ctx.show_text("!")

        # Title
        ctx.set_font_size(20.0)
        ctx.set_source_rgba(1.0, 1.0, 1.0, 0.95)
        ctx.move_to(pos.x + 32.0 + badge_r*2 + 16.0, pos.y + 32.0 + 20.0)
        ctx.show_text("Revoke API Key")

        # Text
        ctx.set_font_size(14.0)
        ctx.set_source_rgba(0.7, 0.7, 0.7, 1.0)

        text = "This action cannot be undone. All current integrations"
        ctx.move_to(pos.x + 32.0, pos.y + 110.0)
        ctx.show_text(text)
        text2 = "using this key will immediately fail."
        ctx.move_to(pos.x + 32.0, pos.y + 130.0)
        ctx.show_text(text2)

        # Buttons (mockup)
        # Cancel Button
        btn_y = pos.y + h - 32.0 - 40.0
        ctx.new_path()
        ctx.rectangle(pos.x + 32.0, btn_y, 140.0, 40.0)
        ctx.set_source_rgba(1.0, 1.0, 1.0, 0.1)
        ctx.fill()

        ctx.set_font_size(14.0)
        ctx.set_source_rgba(1.0, 1.0, 1.0, 0.9)
        ctx.move_to(pos.x + 32.0 + 46.0, btn_y + 25.0)
        ctx.show_text("Cancel")

        # Revoke Button
        ctx.new_path()
        ctx.rectangle(pos.x + w - 32.0 - 140.0, btn_y, 140.0, 40.0)
        ctx.set_source_rgba(0.9, 0.2, 0.2, 0.9)
        ctx.fill()

        ctx.set_source_rgba(1.0, 1.0, 1.0, 1.0)
        ctx.move_to(pos.x + w - 32.0 - 140.0 + 20.0, btn_y + 25.0)
        ctx.show_text("Yes, revoke key")

        ctx.restore()
