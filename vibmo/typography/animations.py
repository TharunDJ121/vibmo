"""
Typography Animation suite (WordReveal, TextScramble, TextTypewriter, TextCounter, TextPathFollower).
"""

from __future__ import annotations
import math
import random
from typing import Any, List, Optional, Sequence, Tuple, Union, Callable
import cairo

from vibmo.core.color import Color, colors
from vibmo.core.vector import Vector2D
from vibmo.core.signal import Signal, AnimationAction
from vibmo.core.easing import Ease, EasingFunc
from vibmo.scene.node import Node


class WordReveal(Node):
    """
    Staggered word-by-word motion reveal with smooth upward spring glide.
    """

    def __init__(
        self,
        text: str = "World-Class Motion Graphics in Python",
        font_size: float = 48.0,
        font_family: str = "Segoe UI",
        color: Union[Color, str] = colors.WHITE,
        stagger_delay: float = 0.08,
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)
        self.text_content = text
        self.words = text.split(" ")
        self.font_size = float(font_size)
        self.font_family = font_family
        self.color = Color.from_any(color)
        self.stagger_delay = float(stagger_delay)
        self.reveal_progress = Signal(1.0, f"{self.name}.reveal_progress")

    def reveal(self, duration: float = 1.2, delay: float = 0.0) -> AnimationAction:
        self.reveal_progress.set(0.0)
        return self.reveal_progress.to(1.0, duration=duration, ease=Ease.out_expo, delay=delay)

    def local_bounds(self, time: float = 0.0) -> Tuple[float, float, float, float]:
        return (0.0, 0.0, len(self.text_content) * self.font_size * 0.65, self.font_size * 1.5)

    def draw(self, ctx: Any, time: float = 0.0) -> None:
        p = float(self.reveal_progress.get(time))
        n = len(self.words)
        if n == 0:
            return

        ctx.save()
        ctx.select_font_face(self.font_family, cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
        ctx.set_font_size(self.font_size)
        c = self.color

        cur_x = 0.0
        for i, word in enumerate(self.words):
            word_start = i * (1.0 / (n + 2))
            word_p = np_clip = max(0.0, min(1.0, (p - word_start) * 3.0))
            ease_wp = Ease.out_cubic(word_p)

            y_offset = (1.0 - ease_wp) * (self.font_size * 0.8)
            alpha = ease_wp

            ctx.save()
            ctx.set_source_rgba(c.r, c.g, c.b, c.a * alpha)
            ctx.move_to(cur_x, self.font_size + y_offset)
            ctx.show_text(word)
            ext = ctx.text_extents(word + " ")
            ctx.restore()

            cur_x += ext.x_advance

        ctx.restore()


class TextScramble(Node):
    """
    Cyberpunk / Matrix hacker text decoding scramble animation.
    Characters cycle through randomized glyphs before settling into the final text.
    """

    GLYPHS = "!<>-_\\/[]{}—=+*^?#________010101"

    def __init__(
        self,
        target_text: str = "SYSTEM_INITIALIZED",
        font_size: float = 40.0,
        font_family: str = "Consolas",
        color: Union[Color, str] = colors.EMERALD,
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)
        self.target_text = target_text
        self.font_size = float(font_size)
        self.font_family = font_family
        self.color = Color.from_any(color)
        self.decode_progress = Signal(1.0, f"{self.name}.decode_progress")

    def decode(self, duration: float = 1.4, delay: float = 0.0) -> AnimationAction:
        self.decode_progress.set(0.0)
        return self.decode_progress.to(1.0, duration=duration, ease=Ease.out_expo, delay=delay)

    def local_bounds(self, time: float = 0.0) -> Tuple[float, float, float, float]:
        return (0.0, 0.0, len(self.target_text) * self.font_size * 0.65, self.font_size * 1.5)

    def draw(self, ctx: Any, time: float = 0.0) -> None:
        p = float(self.decode_progress.get(time))
        n = len(self.target_text)

        # Build scrambled display string
        chars = []
        rng = random.Random(int((time * 30.0) % 10000))
        for i, char in enumerate(self.target_text):
            char_threshold = float(i) / max(1, n)
            if p > char_threshold:
                chars.append(char)
            elif p > max(0.0, char_threshold - 0.25):
                chars.append(rng.choice(self.GLYPHS))
            else:
                chars.append(" ")

        display_str = "".join(chars)

        ctx.save()
        ctx.select_font_face(self.font_family, cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
        ctx.set_font_size(self.font_size)
        c = self.color
        ctx.set_source_rgba(c.r, c.g, c.b, c.a)
        ctx.move_to(0, self.font_size)
        ctx.show_text(display_str)
        ctx.restore()


class TextTypewriter(Node):
    """
    Sequential typewriter text animator with blinking cursor block/line.
    """

    def __init__(
        self,
        text: str = "import motio\nscene = Scene()",
        font_size: float = 24.0,
        font_family: str = "Consolas",
        color: Union[Color, str] = colors.CYAN,
        cursor_blink_speed: float = 4.0,
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)
        self.text_content = text
        self.font_size = float(font_size)
        self.font_family = font_family
        self.color = Color.from_any(color)
        self.cursor_blink_speed = float(cursor_blink_speed)
        self.type_progress = Signal(1.0, f"{self.name}.type_progress")

    def type_out(self, duration: float = 2.0, delay: float = 0.0) -> AnimationAction:
        self.type_progress.set(0.0)
        return self.type_progress.to(1.0, duration=duration, ease=Ease.linear, delay=delay)

    def local_bounds(self, time: float = 0.0) -> Tuple[float, float, float, float]:
        lines = self.text_content.split("\n")
        return (0.0, 0.0, 600.0, len(lines) * self.font_size * 1.5)

    def draw(self, ctx: Any, time: float = 0.0) -> None:
        p = float(self.type_progress.get(time))
        total_len = len(self.text_content)
        visible_len = int(p * total_len)
        typed_str = self.text_content[:visible_len]

        ctx.save()
        ctx.select_font_face(self.font_family, cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)
        ctx.set_font_size(self.font_size)
        c = self.color
        ctx.set_source_rgba(c.r, c.g, c.b, c.a)

        lines = typed_str.split("\n")
        line_h = self.font_size * 1.4
        last_ext_x = 0.0
        last_y = 0.0

        for i, line in enumerate(lines):
            y = (i + 1) * line_h
            ctx.move_to(0, y)
            ctx.show_text(line)
            ext = ctx.text_extents(line)
            last_ext_x = ext.x_advance
            last_y = y

        # Blinking Cursor
        blink = math.sin(time * self.cursor_blink_speed * math.pi) > 0.0
        if blink and p < 1.0:
            ctx.set_source_rgba(1.0, 1.0, 1.0, 0.9)
            ctx.rectangle(last_ext_x + 2.0, last_y - self.font_size * 0.85, 8.0, self.font_size)
            ctx.fill()

        ctx.restore()


class TextPathFollower(Node):
    """
    Animates characters along a parametric curved Bezier path.
    """

    def __init__(
        self,
        text: str = "FLOWING ALONG BEZIER CURVE",
        font_size: float = 32.0,
        color: Union[Color, str] = colors.WHITE,
        path_fn: Optional[Callable[[float], Tuple[float, float]]] = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)
        self.text_content = text
        self.font_size = float(font_size)
        self.color = Color.from_any(color)
        # Default S-curve path
        self.path_fn = path_fn or (lambda t: (t * 600.0, math.sin(t * math.pi * 2.0) * 80.0 + 100.0))
        self.offset = Signal(0.0, f"{self.name}.offset")

    def local_bounds(self, time: float = 0.0) -> Tuple[float, float, float, float]:
        return (0.0, 0.0, 700.0, 250.0)

    def draw(self, ctx: Any, time: float = 0.0) -> None:
        ctx.save()
        ctx.select_font_face("Segoe UI", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
        ctx.set_font_size(self.font_size)
        c = self.color
        ctx.set_source_rgba(c.r, c.g, c.b, c.a)

        off = float(self.offset.get(time))
        n = len(self.text_content)
        for i, char in enumerate(self.text_content):
            t = (off + i * 0.035) % 1.0
            x, y = self.path_fn(t)
            
            # Tangent
            dt = 0.01
            x2, y2 = self.path_fn(min(1.0, t + dt))
            angle = math.atan2(y2 - y, x2 - x)

            ctx.save()
            ctx.translate(x, y)
            ctx.rotate(angle)
            ctx.move_to(0, 0)
            ctx.show_text(char)
            ctx.restore()

        ctx.restore()
