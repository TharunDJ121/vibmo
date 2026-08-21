"""
AI & Modern SaaS Launch Components (ModelCard, ChatInputBar, KineticSnapText, FileAttachmentBadge, EditorialDoc, PillLaunchButton, GradientBackdrop).
Engineered for ultra-smooth morphs, fluid typing variants, specular shimmer reflections, and zero boilerplate.
"""

from __future__ import annotations
import math
from typing import Any, Dict, List, Optional, Sequence, Tuple, Union
import cairo

from vibmo.core.vector import Vector2D
from vibmo.core.color import Color, colors
from vibmo.core.signal import Signal, AnimationAction
from vibmo.core.easing import Ease, EasingFunc
from vibmo.spatial.shadows import DropShadow
from vibmo.scene.node import Node
from vibmo.typography.typing import StreamingText, TypingVariant


class GradientBackdrop(Node):
    """
    Multi-stop lush mesh/aurora gradient backdrop with ambient depth glow.
    Presets: 'sunset' (coral/violet), 'cerulean' (sky blue), 'aurora' (golden lavender).
    """

    def __init__(
        self,
        preset: str = "sunset",
        width: float = 720.0,
        height: float = 1280.0,
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)
        self.preset = preset
        self.w = float(width)
        self.h = float(height)

    @classmethod
    def sunset(cls, width: float = 720.0, height: float = 1280.0) -> GradientBackdrop:
        return cls(preset="sunset", width=width, height=height)

    @classmethod
    def cerulean(cls, width: float = 720.0, height: float = 1280.0) -> GradientBackdrop:
        return cls(preset="cerulean", width=width, height=height)

    @classmethod
    def aurora(cls, width: float = 720.0, height: float = 1280.0) -> GradientBackdrop:
        return cls(preset="aurora", width=width, height=height)

    def draw(self, ctx: Any, time: float = 0.0) -> None:
        w, h = self.w, self.h
        ctx.save()

        if self.preset == "cerulean":
            pat = cairo.LinearGradient(w * 0.5, 0, w * 0.5, h)
            pat.add_color_stop_rgba(0.0, 0.38, 0.64, 0.98, 1.0)
            pat.add_color_stop_rgba(0.5, 0.58, 0.78, 0.99, 1.0)
            pat.add_color_stop_rgba(1.0, 0.75, 0.88, 0.99, 1.0)
        elif self.preset == "aurora":
            pat = cairo.LinearGradient(0, 0, w, h)
            pat.add_color_stop_rgba(0.0, 0.72, 0.75, 0.94, 1.0)
            pat.add_color_stop_rgba(0.40, 0.94, 0.65, 0.60, 1.0)
            pat.add_color_stop_rgba(0.80, 0.98, 0.82, 0.64, 1.0)
            pat.add_color_stop_rgba(1.0, 0.95, 0.72, 0.58, 1.0)
        else:  # sunset
            pat = cairo.LinearGradient(0, 0, w, h)
            pat.add_color_stop_rgba(0.0, 0.96, 0.60, 0.46, 1.0)
            pat.add_color_stop_rgba(0.35, 0.90, 0.65, 0.70, 1.0)
            pat.add_color_stop_rgba(0.70, 0.75, 0.76, 0.94, 1.0)
            pat.add_color_stop_rgba(1.0, 0.88, 0.82, 0.92, 1.0)

        ctx.rectangle(0, 0, w, h)
        ctx.set_source(pat)
        ctx.fill()

        # Ambient soft glow
        glow = cairo.RadialGradient(w * 0.35, h * 0.35, 10.0, w * 0.35, h * 0.35, w * 0.85)
        glow.add_color_stop_rgba(0.0, 1.0, 1.0, 1.0, 0.20)
        glow.add_color_stop_rgba(1.0, 1.0, 1.0, 1.0, 0.0)
        ctx.rectangle(0, 0, w, h)
        ctx.set_source(glow)
        ctx.fill()

        ctx.restore()


class ModelCard(Node):
    """
    Sleek model selection dropdown card with smooth morphing from compact typing pill ('G  p')
    into confirmed model card ('GPT-5 | Flagship model') with specular shimmer reflection.
    """

    def __init__(
        self,
        title: str = "GPT-5",
        subtitle: str = "Flagship model",
        preview_text: str = "G  p",
        morph_start: float = 0.55,
        morph_duration: float = 0.45,
        width: float = 560.0,
        height: float = 150.0,
        shimmer: bool = True,
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)
        self.title = title
        self.subtitle = subtitle
        self.preview_text = preview_text
        self.morph_start = morph_start
        self.morph_duration = morph_duration
        self.target_w = float(width)
        self.target_h = float(height)
        self.initial_w = 360.0
        self.initial_h = 92.0
        self.shimmer = shimmer
        self.shadow = DropShadow.elevated(blur=36.0, offset=(0, 16), color=Color.hex("#1e293b").with_alpha(0.18))

    def local_bounds(self, time: float = 0.0) -> Tuple[float, float, float, float]:
        return (0.0, 0.0, self.target_w, self.target_h)

    def draw(self, ctx: Any, time: float = 0.0) -> None:
        # Calculate smooth morph progress between compact pill and expanded card
        if time < self.morph_start:
            morph_p = 0.0
        elif time > self.morph_start + self.morph_duration:
            morph_p = 1.0
        else:
            raw_p = (time - self.morph_start) / self.morph_duration
            morph_p = Ease.out_back(raw_p, s=1.2)

        curr_w = self.initial_w + (self.target_w - self.initial_w) * morph_p
        curr_h = self.initial_h + (self.target_h - self.initial_h) * morph_p
        curr_r = 30.0 + (34.0 - 30.0) * morph_p

        # Center card horizontally as it expands
        center_x = (self.target_w - curr_w) * 0.5
        center_y = (self.target_h - curr_h) * 0.5

        ctx.save()
        ctx.translate(center_x, center_y)

        # White Rounded Card Container
        self._rounded_rect(ctx, 0, 0, curr_w, curr_h, curr_r)
        ctx.set_source_rgba(1.0, 1.0, 1.0, 1.0)
        ctx.fill()

        # Specular Shimmer Sheen
        if self.shimmer and morph_p > 0.3:
            ctx.save()
            self._rounded_rect(ctx, 0, 0, curr_w, curr_h, curr_r)
            ctx.clip()
            sheen_x = -150.0 + ((time * 1.2) % 2.5) * (curr_w + 300.0)
            spat = cairo.LinearGradient(sheen_x - 70.0, 0, sheen_x + 70.0, curr_h)
            spat.add_color_stop_rgba(0.0, 1.0, 1.0, 1.0, 0.0)
            spat.add_color_stop_rgba(0.5, 1.0, 1.0, 1.0, 0.35)
            spat.add_color_stop_rgba(1.0, 1.0, 1.0, 1.0, 0.0)
            ctx.rectangle(0, 0, curr_w, curr_h)
            ctx.set_source(spat)
            ctx.fill()
            ctx.restore()

        if morph_p < 0.5:
            # Phase 1: Typing Preview "G  p" with blinking cursor
            fade_out = max(0.0, 1.0 - morph_p * 2.0)
            ctx.set_source_rgba(0.06, 0.09, 0.16, fade_out)
            ctx.select_font_face("Inter", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
            ctx.set_font_size(36.0)

            disp = "G" if time < self.morph_start * 0.45 else self.preview_text
            ctx.move_to(44.0, curr_h * 0.5 + 13.0)
            ctx.show_text(disp)

            te = ctx.text_extents(disp)
            cur_x = 44.0 + te.x_advance + 3.0
            if int(time * 4.0) % 2 == 0:
                ctx.set_line_width(2.6)
                ctx.set_source_rgba(0.06, 0.09, 0.16, fade_out)
                ctx.move_to(cur_x, curr_h * 0.5 - 18.0)
                ctx.line_to(cur_x, curr_h * 0.5 + 14.0)
                ctx.stroke()
        else:
            # Phase 2: Confirmed Model Selection with Smooth Alpha Fade-in
            fade_in = min(1.0, (morph_p - 0.5) * 2.0)
            ctx.set_source_rgba(0.06, 0.09, 0.16, fade_in)
            ctx.select_font_face("Inter", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
            ctx.set_font_size(36.0)
            ctx.move_to(48.0, 64.0)
            ctx.show_text(self.title)

            ctx.set_source_rgba(0.45, 0.50, 0.58, fade_in)
            ctx.select_font_face("Inter", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)
            ctx.set_font_size(24.0)
            ctx.move_to(48.0, 110.0)
            ctx.show_text(self.subtitle)

            # Checkmark badge with scale pop
            bx, by, br = curr_w - 64.0, curr_h * 0.5, 20.0 * fade_in
            if br > 1.0:
                ctx.set_source_rgba(0.05, 0.05, 0.07, fade_in)
                ctx.arc(bx, by, br, 0, math.pi * 2)
                ctx.fill()

                ctx.set_source_rgba(1.0, 1.0, 1.0, fade_in)
                ctx.set_line_width(3.4)
                ctx.set_line_cap(cairo.LINE_CAP_ROUND)
                ctx.set_line_join(cairo.LINE_JOIN_ROUND)
                ctx.move_to(bx - 8.0, by)
                ctx.line_to(bx - 2.0, by + 6.0)
                ctx.line_to(bx + 9.0, by - 6.0)
                ctx.stroke()

        ctx.restore()

    def _rounded_rect(self, ctx: Any, x: float, y: float, w: float, h: float, r: float) -> None:
        ctx.new_path()
        ctx.arc(x + w - r, y + r, r, -math.pi * 0.5, 0)
        ctx.arc(x + w - r, y + h - r, r, 0, math.pi * 0.5)
        ctx.arc(x + r, y + h - r, r, math.pi * 0.5, math.pi)
        ctx.arc(x + r, y + r, r, math.pi, math.pi * 1.5)
        ctx.close_path()


class ChatInputBar(Node):
    """
    Minimalist chat prompt search pill with smooth character streaming, glowing cursor, and mic/soundwave icons.
    """

    def __init__(
        self,
        text: str = "Our smartest, fastest model yet",
        typing_start: float = 0.2,
        typing_speed: float = 28.0,
        variant: str = "smooth",
        width: float = 640.0,
        height: float = 88.0,
        shimmer: bool = True,
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)
        self.text = text
        self.typing_start = typing_start
        self.typing_speed = typing_speed
        self.variant = variant
        self.w = float(width)
        self.h = float(height)
        self.shimmer = shimmer
        self.shadow = DropShadow.soft(blur=24.0, offset=(0, 8), color=Color.hex("#0f172a").with_alpha(0.08))

    def local_bounds(self, time: float = 0.0) -> Tuple[float, float, float, float]:
        return (0.0, 0.0, self.w, self.h)

    def draw(self, ctx: Any, time: float = 0.0) -> None:
        w, h, r = self.w, self.h, self.h * 0.5
        ctx.save()

        # White pill container with subtle border
        self._rounded_rect(ctx, 0, 0, w, h, r)
        ctx.set_source_rgba(1.0, 1.0, 1.0, 1.0)
        ctx.fill_preserve()
        ctx.set_source_rgba(0.88, 0.90, 0.94, 1.0)
        ctx.set_line_width(1.5)
        ctx.stroke()

        # Specular Shimmer Sheen
        if self.shimmer:
            ctx.save()
            self._rounded_rect(ctx, 0, 0, w, h, r)
            ctx.clip()
            sheen_x = -150.0 + ((time * 0.9) % 2.8) * (w + 300.0)
            spat = cairo.LinearGradient(sheen_x - 60.0, 0, sheen_x + 60.0, h)
            spat.add_color_stop_rgba(0.0, 1.0, 1.0, 1.0, 0.0)
            spat.add_color_stop_rgba(0.5, 1.0, 1.0, 1.0, 0.25)
            spat.add_color_stop_rgba(1.0, 1.0, 1.0, 1.0, 0.0)
            ctx.rectangle(0, 0, w, h)
            ctx.set_source(spat)
            ctx.fill()
            ctx.restore()

        # Plus '+' icon
        ctx.set_source_rgba(0.15, 0.18, 0.25, 1.0)
        ctx.set_line_width(2.6)
        ctx.set_line_cap(cairo.LINE_CAP_ROUND)
        ctx.move_to(36.0, h * 0.5)
        ctx.line_to(56.0, h * 0.5)
        ctx.move_to(46.0, h * 0.5 - 10.0)
        ctx.line_to(46.0, h * 0.5 + 10.0)
        ctx.stroke()

        # Streamed typing text with smooth per-character alpha ramp
        t_active = max(0.0, time - self.typing_start)
        char_count = min(len(self.text), t_active * self.typing_speed)

        ctx.select_font_face("Inter", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)
        ctx.set_font_size(26.0)

        cur_x = 80.0
        y_pos = h * 0.5 + 9.0

        for i, ch in enumerate(self.text):
            if i > char_count:
                break
            char_p = max(0.0, min(1.0, (char_count - i) * 2.0))
            if self.variant == "smooth":
                ctx.set_source_rgba(0.08, 0.10, 0.15, char_p)
                slide_y = (1.0 - char_p) * 3.0
                ctx.move_to(cur_x, y_pos + slide_y)
            else:
                ctx.set_source_rgba(0.08, 0.10, 0.15, 1.0)
                ctx.move_to(cur_x, y_pos)

            ctx.show_text(ch)
            te = ctx.text_extents(ch)
            cur_x += te.x_advance

        # Blinking cursor
        if char_count < len(self.text) or int(time * 3.5) % 2 == 0:
            ctx.set_line_width(2.2)
            ctx.set_source_rgba(0.12, 0.35, 0.85, 0.90)
            ctx.move_to(cur_x + 3.0, h * 0.5 - 15.0)
            ctx.line_to(cur_x + 3.0, h * 0.5 + 13.0)
            ctx.stroke()

        # Microphone icon
        mic_x = w - 100.0
        ctx.set_source_rgba(0.15, 0.18, 0.25, 1.0)
        ctx.set_line_width(2.2)
        ctx.move_to(mic_x, h * 0.5 - 7.0)
        ctx.line_to(mic_x, h * 0.5 + 4.0)
        ctx.arc(mic_x, h * 0.5 - 3.0, 5.0, 0, math.pi)
        ctx.stroke()

        # Audio waveform button
        wv_x = w - 46.0
        ctx.set_source_rgba(0.92, 0.94, 0.96, 1.0)
        ctx.arc(wv_x, h * 0.5, 20.0, 0, math.pi * 2)
        ctx.fill()

        ctx.set_source_rgba(0.12, 0.15, 0.22, 1.0)
        ctx.set_line_width(2.2)
        ctx.set_line_cap(cairo.LINE_CAP_ROUND)
        ctx.move_to(wv_x - 6.0, h * 0.5 - 4.0)
        ctx.line_to(wv_x - 6.0, h * 0.5 + 4.0)
        ctx.move_to(wv_x, h * 0.5 - 9.0)
        ctx.line_to(wv_x, h * 0.5 + 9.0)
        ctx.move_to(wv_x + 6.0, h * 0.5 - 5.0)
        ctx.line_to(wv_x + 6.0, h * 0.5 + 5.0)
        ctx.stroke()

        ctx.restore()

    def _rounded_rect(self, ctx: Any, x: float, y: float, w: float, h: float, r: float) -> None:
        ctx.new_path()
        ctx.arc(x + w - r, y + r, r, -math.pi * 0.5, 0)
        ctx.arc(x + w - r, y + h - r, r, 0, math.pi * 0.5)
        ctx.arc(x + r, y + h - r, r, math.pi * 0.5, math.pi)
        ctx.arc(x + r, y + r, r, math.pi, math.pi * 1.5)
        ctx.close_path()


class KineticSnapText(Node):
    """
    Bold kinetic typography that smoothly morphs from phrase A to phrase B with colored word accents.
    """

    def __init__(
        self,
        base_word: str = "Think",
        word_a: str = "deeper",
        word_b: str = "faster",
        color_a: Union[Color, str] = Color.hex("#8b5cf6"),
        color_b: Union[Color, str] = Color.hex("#f97316"),
        switch_time: float = 0.85,
        font_size: float = 56.0,
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)
        self.base_word = base_word
        self.word_a = word_a
        self.word_b = word_b
        self.color_a = Color.from_any(color_a)
        self.color_b = Color.from_any(color_b)
        self.switch_time = switch_time
        self.font_size = font_size

    def draw(self, ctx: Any, time: float = 0.0) -> None:
        ctx.save()
        ctx.select_font_face("Inter", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
        ctx.set_font_size(self.font_size)

        prefix = f"{self.base_word} "
        ctx.set_source_rgba(0.06, 0.08, 0.12, 1.0)
        ctx.move_to(160.0, 640.0)
        ctx.show_text(prefix)

        te = ctx.text_extents(prefix)
        x_accent = 160.0 + te.x_advance

        if time < self.switch_time:
            w = self.word_a
            c = self.color_a
            ctx.set_source_rgba(c.r, c.g, c.b, c.a)
            ctx.move_to(x_accent, 640.0)
            ctx.show_text(w)
        else:
            # Morph overshoot scale settle
            dt = time - self.switch_time
            settle_scale = 1.0 + 0.18 * math.exp(-dt * 6.0) * math.cos(dt * 18.0)
            w = self.word_b
            c = self.color_b

            ctx.save()
            ctx.translate(x_accent, 640.0)
            ctx.scale(settle_scale, settle_scale)
            ctx.set_source_rgba(c.r, c.g, c.b, c.a)
            ctx.move_to(0, 0)
            ctx.show_text(w)
            ctx.restore()

        ctx.restore()


class FileAttachmentBadge(Node):
    """
    3D floating file card with colored badge (PDF/XLSX/DOC), bold name, pulsing status,
    and active specular shimmer sweep.
    """

    def __init__(
        self,
        name: str = "sales_deck.pdf",
        file_type: str = "pdf",
        status: str = "Analyzing...",
        width: float = 460.0,
        height: float = 116.0,
        shimmer_offset: float = 0.0,
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)
        self.name = name
        self.file_type = file_type
        self.status = status
        self.w = float(width)
        self.h = float(height)
        self.shimmer_offset = shimmer_offset
        self.shadow = DropShadow.elevated(blur=28.0, offset=(0, 14), color=Color.hex("#0f172a").with_alpha(0.12))

    def local_bounds(self, time: float = 0.0) -> Tuple[float, float, float, float]:
        return (0.0, 0.0, self.w, self.h)

    def draw(self, ctx: Any, time: float = 0.0) -> None:
        w, h, r = self.w, self.h, 28.0
        ctx.save()

        # White rounded card
        self._rounded_rect(ctx, 0, 0, w, h, r)
        ctx.set_source_rgba(1.0, 1.0, 1.0, 1.0)
        ctx.fill()

        # Specular Shimmer Sheen Sweep
        ctx.save()
        self._rounded_rect(ctx, 0, 0, w, h, r)
        ctx.clip()
        sheen_x = -150.0 + (((time + self.shimmer_offset) * 1.1) % 2.4) * (w + 300.0)
        spat = cairo.LinearGradient(sheen_x - 60.0, 0, sheen_x + 60.0, h)
        spat.add_color_stop_rgba(0.0, 1.0, 1.0, 1.0, 0.0)
        spat.add_color_stop_rgba(0.5, 1.0, 1.0, 1.0, 0.35)
        spat.add_color_stop_rgba(1.0, 1.0, 1.0, 1.0, 0.0)
        ctx.rectangle(0, 0, w, h)
        ctx.set_source(spat)
        ctx.fill()
        ctx.restore()

        # Icon box
        ib_x, ib_y, ib_size, ib_r = 24.0, (h - 68.0) * 0.5, 68.0, 18.0
        if self.file_type.lower() == "pdf":
            color = (0.95, 0.32, 0.42, 1.0)
        elif self.file_type.lower() in ("xlsx", "excel", "csv"):
            color = (0.06, 0.60, 0.48, 1.0)
        else:
            color = (0.12, 0.50, 0.98, 1.0)

        self._rounded_rect(ctx, ib_x, ib_y, ib_size, ib_size, ib_r)
        ctx.set_source_rgba(*color)
        ctx.fill()

        # White glyph lines
        ctx.set_source_rgba(1.0, 1.0, 1.0, 1.0)
        ctx.set_line_width(2.6)
        ctx.set_line_cap(cairo.LINE_CAP_ROUND)
        self._rounded_rect(ctx, ib_x + 18.0, ib_y + 16.0, 32.0, 36.0, 6.0)
        ctx.stroke()
        ctx.move_to(ib_x + 24.0, ib_y + 30.0)
        ctx.line_to(ib_x + 44.0, ib_y + 30.0)
        ctx.move_to(ib_x + 24.0, ib_y + 38.0)
        ctx.line_to(ib_x + 38.0, ib_y + 38.0)
        ctx.stroke()

        # Filename
        ctx.set_source_rgba(0.08, 0.11, 0.18, 1.0)
        ctx.select_font_face("Inter", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
        ctx.set_font_size(24.0)
        ctx.move_to(110.0, h * 0.5 - 4.0)
        ctx.show_text(self.name)

        # Pulsing status
        pulse = 0.55 + 0.35 * math.sin(time * 6.0)
        ctx.set_source_rgba(0.50, 0.55, 0.65, pulse)
        ctx.select_font_face("Inter", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)
        ctx.set_font_size(18.0)
        ctx.move_to(110.0, h * 0.5 + 24.0)
        ctx.show_text(self.status)

        ctx.restore()

    def _rounded_rect(self, ctx: Any, x: float, y: float, w: float, h: float, r: float) -> None:
        ctx.new_path()
        ctx.arc(x + w - r, y + r, r, -math.pi * 0.5, 0)
        ctx.arc(x + w - r, y + h - r, r, 0, math.pi * 0.5)
        ctx.arc(x + r, y + h - r, r, math.pi * 0.5, math.pi)
        ctx.arc(x + r, y + r, r, math.pi, math.pi * 1.5)
        ctx.close_path()


class EditorialDoc(Node):
    """
    Clean AI editorial document view with fluid markdown streaming typing and moving cursor.
    """

    def __init__(
        self,
        content: Optional[str] = None,
        variant: str = "smooth",
        margin_x: float = 56.0,
        start_y: float = 360.0,
        speed: float = 65.0,  # chars per sec
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)
        default_content = (
            "Below is a concise summary of your business\ndocuments.\n\n"
            "**Bottom line**\n"
            "Overall momentum remains strong, with clear\nproduct-market fit.\n\n"
            "**Go-to-market (sales_deck)**\n"
            "The sales deck positions the product...\n"
            "lifts of 22–35% when snippets were added\n"
            "to developer onboarding flows."
        )
        self.streamer = StreamingText(
            content=content or default_content,
            variant=variant,
            font_size=28.0,
            speed=speed,
            start_delay=0.15,
            show_cursor=True,
            color=Color.hex("#0f172a"),
            cursor_color=Color.hex("#2563eb"),
        )
        self.margin_x = margin_x
        self.start_y = start_y

    def draw(self, ctx: Any, time: float = 0.0) -> None:
        ctx.save()
        ctx.translate(self.margin_x, self.start_y)
        self.streamer.draw(ctx, time)
        ctx.restore()


class PillLaunchButton(Node):
    """
    Floating pill call-to-action button with diagonal launch arrow (↗) and active specular shimmer.
    """

    def __init__(
        self,
        text: str = "Available now",
        width: float = 460.0,
        height: float = 96.0,
        shimmer: bool = True,
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)
        self.text = text
        self.w = float(width)
        self.h = float(height)
        self.shimmer = shimmer
        self.shadow = DropShadow.elevated(blur=36.0, offset=(0, 16), color=Color.hex("#1e293b").with_alpha(0.18))

    def local_bounds(self, time: float = 0.0) -> Tuple[float, float, float, float]:
        return (0.0, 0.0, self.w, self.h)

    def draw(self, ctx: Any, time: float = 0.0) -> None:
        w, h, r = self.w, self.h, self.h * 0.5
        ctx.save()

        # Pill Body
        self._rounded_rect(ctx, 0, 0, w, h, r)
        ctx.set_source_rgba(1.0, 1.0, 1.0, 1.0)
        ctx.fill()

        # Specular Shimmer Sheen
        if self.shimmer:
            ctx.save()
            self._rounded_rect(ctx, 0, 0, w, h, r)
            ctx.clip()
            sheen_x = -150.0 + ((time * 1.2) % 2.4) * (w + 300.0)
            spat = cairo.LinearGradient(sheen_x - 60.0, 0, sheen_x + 60.0, h)
            spat.add_color_stop_rgba(0.0, 1.0, 1.0, 1.0, 0.0)
            spat.add_color_stop_rgba(0.5, 1.0, 1.0, 1.0, 0.35)
            spat.add_color_stop_rgba(1.0, 1.0, 1.0, 1.0, 0.0)
            ctx.rectangle(0, 0, w, h)
            ctx.set_source(spat)
            ctx.fill()
            ctx.restore()

        # Text
        ctx.set_source_rgba(0.06, 0.08, 0.14, 1.0)
        ctx.select_font_face("Inter", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
        ctx.set_font_size(30.0)
        ctx.move_to(56.0, h * 0.5 + 10.0)
        ctx.show_text(self.text)

        # Diagonal Arrow (↗)
        arr_x, arr_y = w - 74.0, h * 0.5 + 2.0
        ctx.set_line_width(3.2)
        ctx.set_line_cap(cairo.LINE_CAP_ROUND)
        ctx.set_line_join(cairo.LINE_JOIN_ROUND)
        ctx.move_to(arr_x - 14.0, arr_y + 14.0)
        ctx.line_to(arr_x + 10.0, arr_y - 10.0)
        ctx.move_to(arr_x - 2.0, arr_y - 10.0)
        ctx.line_to(arr_x + 10.0, arr_y - 10.0)
        ctx.line_to(arr_x + 10.0, arr_y + 2.0)
        ctx.stroke()

        ctx.restore()

    def _rounded_rect(self, ctx: Any, x: float, y: float, w: float, h: float, r: float) -> None:
        ctx.new_path()
        ctx.arc(x + w - r, y + r, r, -math.pi * 0.5, 0)
        ctx.arc(x + w - r, y + h - r, r, 0, math.pi * 0.5)
        ctx.arc(x + r, y + h - r, r, math.pi * 0.5, math.pi)
        ctx.arc(x + r, y + r, r, math.pi, math.pi * 1.5)
        ctx.close_path()
