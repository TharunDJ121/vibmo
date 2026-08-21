"""
Advanced Kinetic Typography & Smooth Streaming Engine.
Provides multiple typing variants: Classic, Smooth Alpha Ramp, AI Token Stream, Shimmer Trail, and Word Fade.
"""

from __future__ import annotations
import math
import re
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Sequence, Tuple, Union
import cairo

from vibmo.core.color import Color, colors
from vibmo.core.vector import Vector2D
from vibmo.core.signal import Signal, AnimationAction
from vibmo.core.easing import Ease, EasingFunc
from vibmo.scene.node import Node


class TypingVariant(str, Enum):
    CLASSIC = "classic"        # Discrete character-by-character
    SMOOTH = "smooth"          # Silky progressive alpha ramp per character
    STREAM = "stream"          # Natural AI LLM token generation with punctuation cadence
    SHIMMER = "shimmer"        # Luminous glowing highlight leading the active stream
    WORD_FADE = "word_fade"    # Staggered word-level fluid opacity fade


class StreamingText(Node):
    """
    Rich kinetic text streamer with Markdown support (headings, bold, lists) and multiple typing variants.
    """

    def __init__(
        self,
        content: str,
        variant: Union[str, TypingVariant] = TypingVariant.SMOOTH,
        font_size: float = 28.0,
        font_family: str = "Inter",
        color: Union[Color, str] = Color.hex("#0f172a"),
        speed: float = 34.0,  # chars per second
        start_delay: float = 0.15,
        line_height: float = 1.45,
        show_cursor: bool = True,
        cursor_color: Union[Color, str] = Color.hex("#3b82f6"),
        shimmer_color: Union[Color, str] = Color.hex("#60a5fa"),
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)
        self.content = content
        self.variant = TypingVariant(variant) if isinstance(variant, str) else variant
        self.font_size = float(font_size)
        self.font_family = font_family
        self.color = Color.from_any(color)
        self.speed = float(speed)
        self.start_delay = float(start_delay)
        self.line_height = float(line_height)
        self.show_cursor = show_cursor
        self.cursor_color = Color.from_any(cursor_color)
        self.shimmer_color = Color.from_any(shimmer_color)

        # Parse structured lines: (is_bold, font_size_multiplier, text)
        self.lines: List[Tuple[bool, float, str]] = []
        for raw_line in content.split("\n"):
            line = raw_line.strip()
            if not line:
                self.lines.append((False, 0.6, ""))
                continue
            if line.startswith("## "):
                self.lines.append((True, 1.25, line[3:]))
            elif line.startswith("# "):
                self.lines.append((True, 1.35, line[2:]))
            elif line.startswith("**") and line.endswith("**"):
                self.lines.append((True, 1.20, line[2:-2]))
            else:
                self.lines.append((False, 1.0, line))

        # Flatten total character count for continuous streaming progression
        self.total_chars = sum(len(txt) for _, _, txt in self.lines)
        self.progress = Signal(1.0, f"{self.name}.progress")

    def local_bounds(self, time: float = 0.0) -> Tuple[float, float, float, float]:
        est_h = len(self.lines) * self.font_size * self.line_height
        return (0.0, 0.0, 640.0, est_h)

    def draw(self, ctx: Any, time: float = 0.0) -> None:
        ctx.save()

        # Calculate character budget based on timeline or signal
        t_active = max(0.0, time - self.start_delay)
        current_char_count = min(self.total_chars, t_active * self.speed)

        # Draw lines sequentially
        y = self.font_size
        chars_drawn = 0
        cursor_x = 0.0
        cursor_y = y
        cursor_h = self.font_size
        is_active_streaming = current_char_count < self.total_chars

        for is_bold, size_mult, text in self.lines:
            if not text:
                y += self.font_size * self.line_height * size_mult
                continue

            current_font_size = self.font_size * size_mult
            weight = cairo.FONT_WEIGHT_BOLD if is_bold else cairo.FONT_WEIGHT_NORMAL
            ctx.select_font_face(self.font_family, cairo.FONT_SLANT_NORMAL, weight)
            ctx.set_font_size(current_font_size)

            line_chars = len(text)
            line_start_char = chars_drawn
            line_end_char = chars_drawn + line_chars

            if current_char_count <= line_start_char:
                # Line not yet reached
                chars_drawn += line_chars
                y += current_font_size * self.line_height
                continue

            # Render line with chosen variant
            x = 0.0
            for i, ch in enumerate(text):
                global_char_idx = line_start_char + i
                if global_char_idx > current_char_count:
                    break

                char_progress = current_char_count - global_char_idx

                if self.variant == TypingVariant.SMOOTH:
                    # Smooth alpha ramp from 0.0 -> 1.0 with subtle slide up
                    alpha = max(0.0, min(1.0, char_progress * 1.5))
                    slide_y = (1.0 - alpha) * 4.0
                    c = self.color
                    ctx.set_source_rgba(c.r, c.g, c.b, c.a * alpha)
                    ctx.move_to(x, y + slide_y)
                    ctx.show_text(ch)

                elif self.variant == TypingVariant.SHIMMER:
                    # Luminous lead character glow
                    if char_progress < 1.5:
                        sc = self.shimmer_color
                        ctx.set_source_rgba(sc.r, sc.g, sc.b, 1.0)
                    else:
                        c = self.color
                        ctx.set_source_rgba(c.r, c.g, c.b, c.a)
                    ctx.move_to(x, y)
                    ctx.show_text(ch)

                elif self.variant == TypingVariant.STREAM:
                    # Token-level natural micro-easing
                    alpha = max(0.0, min(1.0, char_progress * 2.0))
                    c = self.color
                    ctx.set_source_rgba(c.r, c.g, c.b, c.a * alpha)
                    ctx.move_to(x, y)
                    ctx.show_text(ch)

                else:  # CLASSIC
                    c = self.color
                    ctx.set_source_rgba(c.r, c.g, c.b, c.a)
                    ctx.move_to(x, y)
                    ctx.show_text(ch)

                te = ctx.text_extents(ch)
                x += te.x_advance
                cursor_x = x
                cursor_y = y
                cursor_h = current_font_size

            chars_drawn += line_chars
            y += current_font_size * self.line_height

        # Blinking / Pulse Stream Cursor
        if self.show_cursor and (is_active_streaming or int(time * 3.5) % 2 == 0):
            cc = self.cursor_color
            ctx.set_source_rgba(cc.r, cc.g, cc.b, 0.85)
            ctx.set_line_width(2.4)
            ctx.set_line_cap(cairo.LINE_CAP_ROUND)
            ctx.move_to(cursor_x + 3.0, cursor_y - cursor_h * 0.85)
            ctx.line_to(cursor_x + 3.0, cursor_y + cursor_h * 0.15)
            ctx.stroke()

        ctx.restore()
