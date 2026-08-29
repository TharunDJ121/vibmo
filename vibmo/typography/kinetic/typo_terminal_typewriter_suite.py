"""
Vintage Phosphor Terminal Typewriter Suite.
Contains nodes for rendering retro terminal typing effects.
"""

from __future__ import annotations
import math
import random
from typing import Any, Callable, List, Optional, Tuple, Union
import cairo

from vibmo.core.color import Color, colors
from vibmo.core.vector import Vector2D
from vibmo.core.signal import Signal, AnimationAction
from vibmo.core.easing import Ease
from vibmo.scene.node import Node


class TypingAudioSyncHook(Node):
    """Event hook firing on each keypress character reveal."""
    def __init__(self, on_type: Callable[[str, float], None], **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.on_type = on_type
        self._last_revealed_index = -1

    def trigger(self, char: str, time: float, index: int) -> None:
        if index > self._last_revealed_index:
            self.on_type(char, time)
            self._last_revealed_index = index

    def reset(self):
        self._last_revealed_index = -1


class BlinkingBlockCaret(Node):
    """Solid amber or green phosphor rectangular cursor blinking at 2 Hz."""
    def __init__(
        self,
        color: Union[Color, str] = Color.hex("#ffb000"), # Amber default
        blink_rate: float = 2.0, # Hz
        width: float = 12.0,
        height: float = 24.0,
        **kwargs: Any
    ) -> None:
        super().__init__(**kwargs)
        self.color = Signal(Color.from_any(color), f"{self.name}.color")
        self.blink_rate = blink_rate
        self.width = Signal(float(width), f"{self.name}.width")
        self.height = Signal(float(height), f"{self.name}.height")
        self.visible = Signal(True, f"{self.name}.visible")
        # Start time tracking for blinking relative to creation
        self._start_time: Optional[float] = None

    def draw(self, ctx: Any, time: float = 0.0) -> None:
        if not self.visible.get(time):
            return

        if self._start_time is None:
            self._start_time = time

        dt = time - self._start_time
        # 2 Hz -> 2 cycles per second -> frequency is 2, period is 0.5s
        # True half the time, False half the time
        is_visible = (math.floor(dt * self.blink_rate * 2) % 2) == 0

        if is_visible:
            c = self.color.get(time)
            w = self.width.get(time)
            h = self.height.get(time)

            ctx.save()
            ctx.set_source_rgba(c.r, c.g, c.b, c.a)
            ctx.rectangle(0, -h * 0.85, w, h)
            ctx.fill()
            ctx.restore()

        super().draw(ctx, time)


class CommandPromptPrefix(Node):
    """Monospace user prompt prefix in distinct accent color."""
    def __init__(
        self,
        prompt: str = "user@vibmo:~$ ",
        font_size: float = 24.0,
        font_family: str = "monospace",
        color: Union[Color, str] = colors.GREEN_500,
        **kwargs: Any
    ) -> None:
        super().__init__(**kwargs)
        self.prompt = prompt
        self.font_size = Signal(float(font_size), f"{self.name}.font_size")
        self.font_family = font_family
        self.color = Signal(Color.from_any(color), f"{self.name}.color")

    def _setup_cairo_font(self, ctx: cairo.Context, font_size: float) -> None:
        ctx.select_font_face(self.font_family, cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
        ctx.set_font_size(font_size)

    def draw(self, ctx: Any, time: float = 0.0) -> None:
        c = self.color.get(time)
        fs = self.font_size.get(time)

        ctx.save()
        self._setup_cairo_font(ctx, fs)
        ctx.set_source_rgba(c.r, c.g, c.b, c.a)

        ctx.move_to(0, fs * 0.88)
        ctx.show_text(self.prompt)
        ctx.restore()

        super().draw(ctx, time)

    def measure_width(self) -> float:
        surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, 1, 1)
        m_ctx = cairo.Context(surf)
        self._setup_cairo_font(m_ctx, self.font_size.get(0.0))
        return m_ctx.text_extents(self.prompt).x_advance


class PhosphorTerminalTypewriter(Node):
    """Monospace terminal typography that types sequentially with natural typing cadence variation."""
    def __init__(
        self,
        font_size: float = 24.0,
        font_family: str = "monospace",
        color: Union[Color, str] = Color.hex("#ffb000"), # Amber
        prompt_text: Optional[str] = "user@vibmo:~$ ",
        prompt_color: Union[Color, str] = colors.GREEN_500,
        audio_hook: Optional[Callable[[str, float], None]] = None,
        **kwargs: Any
    ) -> None:
        super().__init__(**kwargs)

        self.font_size = Signal(float(font_size), f"{self.name}.font_size")
        self.font_family = font_family
        self.color = Signal(Color.from_any(color), f"{self.name}.color")

        self.text_content = ""
        self.typing_progress = Signal(0.0, f"{self.name}.typing_progress")
        self.typing_speed = 35.0

        self.prompt_node: Optional[CommandPromptPrefix] = None
        self.prompt_width = 0.0
        if prompt_text:
            self.prompt_node = CommandPromptPrefix(
                prompt=prompt_text,
                font_size=font_size,
                font_family=font_family,
                color=prompt_color
            )
            self.prompt_width = self.prompt_node.measure_width()
            self.add(self.prompt_node)

        self.caret = BlinkingBlockCaret(
            color=color,
            width=font_size * 0.6,
            height=font_size,
            position=Vector2D(self.prompt_width, 0)
        )
        self.add(self.caret)

        self.audio_hook_node = None
        if audio_hook:
            self.audio_hook_node = TypingAudioSyncHook(on_type=audio_hook)
            self.add(self.audio_hook_node)

        # Precompute character timings
        self.char_times: List[float] = []
        self._rng = random.Random(42)

    def typewriter(self, text: str, speed: float = 35.0, delay: float = 0.0) -> AnimationAction:
        self.text_content = text
        self.typing_speed = speed

        if self.audio_hook_node:
            self.audio_hook_node.reset()

        # Generate varied cadence
        self.char_times = []
        current_time = 0.0
        for char in text:
            # We want to reveal characters exactly at or slightly after current_time
            # Using current_time as the start of the character's appearance
            self.char_times.append(current_time)

            # Natural variation
            base_dt = 1.0 / speed
            variation = self._rng.uniform(0.7, 1.3)

            # Pause slightly on punctuation or spaces
            if char in ".!?":
                variation *= 3.0
            elif char in ",;":
                variation *= 2.0
            elif char == " ":
                variation *= 1.2

            current_time += base_dt * variation

        total_duration = current_time if len(text) > 0 else 0.0

        return self.typing_progress.to(
            1.0,
            duration=total_duration,
            ease=Ease.linear,
            delay=delay
        )

    def _setup_cairo_font(self, ctx: cairo.Context, font_size: float) -> None:
        ctx.select_font_face(self.font_family, cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)
        ctx.set_font_size(font_size)

    def draw(self, ctx: Any, time: float = 0.0) -> None:
        if not self.text_content:
            super().draw(ctx, time)
            return

        prog = self.typing_progress.get(time)
        fs = self.font_size.get(time)
        c = self.color.get(time)

        total_duration = self.char_times[-1] + (1.0 / self.typing_speed) if self.char_times else 0.0
        current_elapsed = prog * total_duration

        chars_to_draw = 0
        if prog > 0.0:
            for t in self.char_times:
                if current_elapsed >= t:
                    chars_to_draw += 1
                else:
                    break

        text_to_draw = self.text_content[:chars_to_draw]

        ctx.save()
        self._setup_cairo_font(ctx, fs)
        ctx.set_source_rgba(c.r, c.g, c.b, c.a)

        current_x = self.prompt_width
        current_y = 0.0

        # Fire audio hook for every character drawn so far
        if self.audio_hook_node and chars_to_draw > 0:
            for i in range(self.audio_hook_node._last_revealed_index + 1, chars_to_draw):
                self.audio_hook_node.trigger(self.text_content[i], time, i)

        # Draw and layout text
        lines = text_to_draw.split("\n")

        for i, line in enumerate(lines):
            # Move to start of line
            x_start = self.prompt_width if i == 0 else 0.0
            ctx.move_to(x_start, current_y + fs * 0.88)

            if line:
                ctx.show_text(line)
                extents = ctx.text_extents(line)
                current_x = x_start + extents.x_advance
            else:
                current_x = x_start

            if i < len(lines) - 1:
                current_y += fs * 1.2

        ctx.restore()

        # Update caret position
        self.caret.position.set(Vector2D(current_x + fs * 0.1, current_y))

        super().draw(ctx, time)
