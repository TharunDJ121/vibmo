"""
Streaming LLM Token UI Suite for Vibmo / Motio.
Components:
- StreamingTokenOutput (TokenStreamerSuite)
- TokenStreamerBox
- ShimmeringCaretIndicator
- TokenSpeedVelocityCounter
- StopGenerationButton
"""

from __future__ import annotations
import math
from typing import Any, List, Optional, Sequence, Tuple, Union
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


class ShimmeringCaretIndicator(Rect):
    """Glowing cyan terminal cursor block that pulses at the insertion point."""

    def __init__(self, color: Union[str, Color] = "#06b6d4", **kwargs: Any) -> None:
        c = Color.from_any(color)
        super().__init__(
            width=12.0,
            height=24.0,
            corner_radius=3.0,
            fill=c,
            **kwargs,
        )
        self.pulse_speed = 5.0

    def draw(self, ctx: Any, time: float = 0.0) -> None:
        base_opacity = 0.4 + 0.6 * (0.5 * (1.0 + math.sin(time * self.pulse_speed)))
        w = self.width.get(time)
        h = self.height.get(time)
        c = self.fill.get(time)

        ctx.save()
        # Glow halo
        ctx.new_path()
        r = 4.0
        ctx.rectangle(-3, -3, w + 6, h + 6)
        ctx.set_source_rgba(c.r, c.g, c.b, 0.25 * base_opacity)
        ctx.fill()

        # Core caret
        ctx.new_path()
        ctx.arc(w - r, r, r, -math.pi * 0.5, 0)
        ctx.arc(w - r, h - r, r, 0, math.pi * 0.5)
        ctx.arc(r, h - r, r, math.pi * 0.5, math.pi)
        ctx.arc(r, r, r, math.pi, math.pi * 1.5)
        ctx.close_path()
        ctx.set_source_rgba(c.r, c.g, c.b, c.a * base_opacity)
        ctx.fill()
        ctx.restore()


class TokenSpeedVelocityCounter(FlexContainer):
    """Live metric badge calculating real-time tokens/second ticker (`118.4 tok/s`)."""

    def __init__(self, speed: float = 30.0, **kwargs: Any) -> None:
        super().__init__(
            direction="row",
            padding=(6, 12),
            gap=8,
            corner_radius=12.0,
            fill=Color(0.08, 0.1, 0.15, 0.8),
            stroke=Color(0.2, 0.3, 0.4, 0.8),
            stroke_width=1.0,
            align_items="center",
            **kwargs,
        )
        self.target_speed = Signal(float(speed), f"{self.name}.target_speed")
        self.tokens_count = Signal(0.0, f"{self.name}.tokens_count")

        self.text_node = Text(
            text="0.0 tok/s",
            font_size=13.0,
            font_family="Inter",
            color=colors.CYAN,
            bold=True,
        )
        self.add(self.text_node)
        self._last_time = 0.0
        self._last_tokens = 0.0
        self._velocity = 0.0

    def draw(self, ctx: Any, time: float = 0.0) -> None:
        current_tokens = self.tokens_count.get(time)
        dt = time - self._last_time
        if time == 0.0 or current_tokens == 0.0:
            self._velocity = 0.0
            self._last_time = time
            self._last_tokens = current_tokens
            self.text_node.text.set("0.0 tok/s")
        elif dt > 0.08:
            d_tok = current_tokens - self._last_tokens
            if d_tok > 0:
                instant_vel = d_tok / dt
                self._velocity = self._velocity * 0.6 + instant_vel * 0.4
            else:
                self._velocity = self.target_speed.get(time)
            self._last_time = time
            self._last_tokens = current_tokens
            self.text_node.text.set(f"{self._velocity:.1f} tok/s")

        super().draw(ctx, time)


class StopGenerationButton(FlexContainer):
    """Compact square pill button with pulsating red stop icon and subtle hover glow."""

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(
            direction="row",
            padding=(8, 14),
            gap=6,
            corner_radius=8.0,
            fill=Color(0.18, 0.06, 0.08, 0.85),
            stroke=colors.ROSE_500.with_alpha(0.6),
            stroke_width=1.0,
            align_items="center",
            justify_content="center",
            **kwargs,
        )
        self.icon = Rect(
            width=10.0,
            height=10.0,
            corner_radius=2.0,
            fill=colors.ROSE_500,
        )
        self.btn_text = Text("Stop", font_size=12.0, color=colors.ROSE, bold=True)
        self.add(self.icon, self.btn_text)

    def draw(self, ctx: Any, time: float = 0.0) -> None:
        pulse = 0.85 + 0.15 * math.sin(time * 6.0)
        self.icon.scale.set(Vector2D(pulse, pulse))
        super().draw(ctx, time)


class StreamingTokenOutput(Node):
    """
    Streaming LLM Token Output Suite.
    Renders token-by-token text generation with real-time velocity metrics,
    glowing insertion caret, and stop action button.
    """

    def __init__(
        self,
        text: str = "Analyzing model weights... Multi-head attention matrices initialized. Generating response tokens in real-time.",
        speed: float = 30.0,
        width: float = 650.0,
        height: float = 360.0,
        font_size: float = 16.0,
        bg_color: Union[Color, str] = "#0b101b",
        border_color: Union[Color, str] = "#1e293b",
        text_color: Optional[Union[Color, str]] = None,
        show_cursor: bool = True,
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)
        self.full_text = text
        self._current_text = text
        self.width_val = float(width)
        self.height_val = float(height)
        self.font_size = float(font_size)
        self.bg_color = Color.from_any(bg_color)
        self.border_color = Color.from_any(border_color)
        self.text_color = Color.from_any(text_color) if text_color is not None else Color(0.9, 0.94, 0.98, 0.95)
        self.show_cursor = show_cursor
        self.shadow = DropShadow(color=Color(0.0, 0.0, 0.0, 0.5), blur=32.0, offset=(0.0, 16.0))

        class _StreamingTextHelper:
            def __init__(self, total_chars: int, speed: float) -> None:
                self.total_chars = total_chars
                self.speed = speed

        self.streaming_text = _StreamingTextHelper(len(text), speed)

        # Signals
        self.stream_progress = Signal(0.0, f"{self.name}.stream_progress")
        self.char_count = Signal(0.0, f"{self.name}.char_count")
        self.speed = Signal(float(speed), f"{self.name}.speed")

        # Subcomponents
        self.velocity_counter = TokenSpeedVelocityCounter(speed=speed)
        self.velocity_counter.position.set(Vector2D(self.width_val - 210.0, 16.0))

        self.stop_btn = StopGenerationButton()
        self.stop_btn.position.set(Vector2D(self.width_val - 90.0, 16.0))

        self.caret = ShimmeringCaretIndicator()
        self.add(self.velocity_counter, self.stop_btn, self.caret)

    def stream_tokens(
        self,
        speed: Optional[float] = None,
        text: Optional[str] = None,
        duration: Optional[float] = None,
        ease: EasingFunc = Ease.linear,
    ) -> AnimationAction:
        """
        Fluent generator animation verb to stream tokens sequentially.
        """
        if text is not None:
            self.full_text = text
            self._current_text = text
            self.streaming_text.total_chars = len(text)
        if speed is not None:
            self.speed.set(float(speed))
            self.velocity_counter.target_speed.set(float(speed))
            self.streaming_text.speed = float(speed)

        total_chars = max(1, len(self.full_text))
        effective_speed = self.speed.get(0.0) if speed is None else float(speed)
        dur = float(duration) if duration is not None else max(0.5, (total_chars / 4.0) / max(1.0, effective_speed))

        self.velocity_counter.tokens_count.to(total_chars / 4.0, duration=dur, ease=ease)
        self.char_count.to(float(total_chars), duration=dur, ease=ease)
        return self.stream_progress.to(1.0, duration=dur, ease=ease)

    def stream_text(
        self,
        text: Optional[str] = None,
        duration: Optional[float] = None,
        speed: Optional[float] = None,
        ease: EasingFunc = Ease.linear,
    ) -> List[AnimationAction]:
        if text is not None:
            self.full_text = text
            self._current_text = text
            self.streaming_text.total_chars = len(text)
            dur = duration if duration is not None else 2.0
            self.streaming_text.speed = len(text) / dur
        action = self.stream_tokens(speed=speed, text=text, duration=duration, ease=ease)
        return [action]

    def local_bounds(self, time: float = 0.0) -> Tuple[float, float, float, float]:
        return (0.0, 0.0, self.width_val, self.height_val)

    def draw(self, ctx: Any, time: float = 0.0) -> None:
        w, h = self.width_val, self.height_val
        ctx.save()

        # Draw container card
        r = 16.0
        ctx.new_path()
        ctx.arc(w - r, r, r, -math.pi * 0.5, 0)
        ctx.arc(w - r, h - r, r, 0, math.pi * 0.5)
        ctx.arc(r, h - r, r, math.pi * 0.5, math.pi)
        ctx.arc(r, r, r, math.pi, math.pi * 1.5)
        ctx.close_path()

        # Background fill
        ctx.set_source_rgba(*self.bg_color.to_cairo())
        ctx.fill_preserve()

        # Specular rim
        ctx.set_source_rgba(*self.border_color.to_cairo())
        ctx.set_line_width(1.5)
        ctx.stroke()

        # Header title
        ctx.select_font_face("Inter", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
        ctx.set_font_size(14.0)
        ctx.set_source_rgba(0.9, 0.95, 1.0, 0.9)
        ctx.move_to(24.0, 36.0)
        ctx.show_text("LLM Response Stream")

        # Divider line
        ctx.set_source_rgba(0.2, 0.25, 0.35, 0.4)
        ctx.set_line_width(1.0)
        ctx.move_to(20.0, 60.0)
        ctx.line_to(w - 20.0, 60.0)
        ctx.stroke()

        # Streamed text rendering
        prog = max(0.0, min(1.0, self.stream_progress.get(time)))
        chars_to_show = int(prog * len(self.full_text))
        visible_text = self.full_text[:chars_to_show]

        # Draw text with line wrapping
        ctx.select_font_face("Consolas", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)
        ctx.set_font_size(self.font_size)
        line_height = self.font_size * 1.6
        max_text_w = w - 48.0
        start_x = 24.0
        start_y = 92.0

        words = visible_text.split(" ")
        lines: List[str] = []
        cur_line = ""

        for word in words:
            test_line = cur_line + (" " if cur_line else "") + word
            ext = ctx.text_extents(test_line)
            if ext.width > max_text_w and cur_line:
                lines.append(cur_line)
                cur_line = word
            else:
                cur_line = test_line
        if cur_line:
            lines.append(cur_line)

        # Draw lines
        last_x = start_x
        last_y = start_y
        for i, line in enumerate(lines):
            y = start_y + i * line_height
            ctx.set_source_rgba(0.9, 0.94, 0.98, 0.95)
            ctx.move_to(start_x, y)
            ctx.show_text(line)
            ext = ctx.text_extents(line)
            last_x = start_x + ext.width + 4.0
            last_y = y - self.font_size + 2.0

        if not lines:
            last_x = start_x
            last_y = start_y - self.font_size + 2.0

        # Update Caret position
        self.caret.position.set(Vector2D(last_x, last_y))

        # Draw children (metrics, buttons, caret)
        super().draw(ctx, time)
        ctx.restore()


# Aliases
TokenStreamerSuite = StreamingTokenOutput
TokenStreamerBox = StreamingTokenOutput
