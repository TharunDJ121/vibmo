from __future__ import annotations
import math
from typing import Any, Callable, List, Optional, Tuple, Union

from vibmo.core.vector import Vector2D
from vibmo.core.color import Color, colors
from vibmo.core.signal import Signal, AnimationAction
from vibmo.core.easing import Ease, EasingFunc
from vibmo.scene.node import Node
from vibmo.layout.container import FlexContainer
from vibmo.primitives.rect import Rect, RoundedRect
from vibmo.typography.text import Text
from vibmo.typography.typing import StreamingText, TypingVariant


class ShimmeringCaretIndicator(Rect):
    """
    Glowing cyan terminal cursor block that pulses at the insertion point.
    """
    def __init__(self, color: Union[str, Color] = "#06b6d4", **kwargs) -> None:
        c = Color.from_any(color)
        super().__init__(
            width=16.0,
            height=32.0,
            corner_radius=4.0,
            fill=c,
            **kwargs
        )
        self.pulse_speed = 4.0
        
    def draw(self, ctx: Any, time: float = 0.0) -> None:
        # Pulse opacity using sine wave based on time
        base_opacity = 0.4 + 0.6 * (0.5 * (1.0 + math.sin(time * self.pulse_speed)))
        
        ctx.save()
        # Scale locally based on bounds to give a breathing effect
        ctx.translate(self.width.get(time) * 0.5, self.height.get(time) * 0.5)
        # Apply glowing alpha locally
        ctx.set_source_rgba(self.fill.get(time).r, self.fill.get(time).g, self.fill.get(time).b, self.fill.get(time).a * base_opacity)
        ctx.translate(-self.width.get(time) * 0.5, -self.height.get(time) * 0.5)
        
        super().draw(ctx, time)
        
        # Add a glow ring
        ctx.new_path()
        r = self.corner_radius.get(time)
        w = self.width.get(time)
        h = self.height.get(time)
        ctx.rectangle(-4, -4, w+8, h+8)
        ctx.set_source_rgba(self.fill.get(time).r, self.fill.get(time).g, self.fill.get(time).b, 0.2 * base_opacity)
        ctx.fill()
        
        ctx.restore()


class TokenSpeedVelocityCounter(FlexContainer):
    """
    Live metric badge calculating real-time tokens/second ticker (`118.4 tok/s`).
    """
    def __init__(self, **kwargs) -> None:
        super().__init__(
            direction="row",
            padding=(6, 12),
            gap=8,
            corner_radius=12.0,
            fill=Color(0.1, 0.1, 0.1, 0.7),
            stroke=Color(0.2, 0.2, 0.2, 1.0),
            align_items="center",
            **kwargs
        )
        self.tokens_count = Signal(0.0)
        
        self.text_node = Text(
            text="0.0 tok/s",
            font_size=14.0,
            font_family="Inter",
            color=colors.CYAN_500,
            bold=True
        )
        self.add(self.text_node)
        
        # Metrics state
        self._last_time = 0.0
        self._last_tokens = 0.0
        self._velocity = 0.0
        
    def draw(self, ctx: Any, time: float = 0.0) -> None:
        # Update metrics logic
        current_tokens = self.tokens_count.get(time)
        dt = time - self._last_time
        if dt > 0.1: # Update rate
            d_tok = current_tokens - self._last_tokens
            if d_tok >= 0:
                self._velocity = self._velocity * 0.7 + (d_tok / dt) * 0.3 # Smoothing
            self._last_time = time
            self._last_tokens = current_tokens
            
            # Format text
            self.text_node.text.set(f"{self._velocity:.1f} tok/s")
            
        super().draw(ctx, time)


class StopGenerationButton(FlexContainer):
    """
    Compact square pill button with pulsating red stop icon and subtle hover glow.
    """
    def __init__(self, **kwargs) -> None:
        super().__init__(
            direction="row",
            padding=(10, 10),
            gap=0,
            corner_radius=8.0,
            fill=Color(0.15, 0.05, 0.05, 0.8),
            stroke=colors.RED_500.with_alpha(0.5),
            align_items="center",
            justify_content="center",
            **kwargs
        )
        # Red stop square
        self.icon = Rect(
            width=12.0,
            height=12.0,
            corner_radius=2.0,
            fill=colors.RED_500
        )
        self.add(self.icon)
        
    def draw(self, ctx: Any, time: float = 0.0) -> None:
        # Pulsating effect on the icon
        pulse = 0.8 + 0.2 * math.sin(time * 6.0)
        self.icon.scale.set(Vector2D(pulse, pulse))
        super().draw(ctx, time)


class TokenStreamerBox(FlexContainer):
    """
    Frosted glass container that renders markdown/code tokens as they stream in sequentially.
    """
    def __init__(self, width: float = 600.0, height: float = 400.0, **kwargs) -> None:
        super().__init__(
            direction="column",
            padding=24.0,
            gap=16.0,
            corner_radius=16.0,
            fill=Color(0.05, 0.05, 0.08, 0.85), # Frosted look (semi-transparent dark)
            stroke=Color(1.0, 1.0, 1.0, 0.1),
            width=width,
            height=height,
            align_items="start",
            **kwargs
        )
        
        # Internal layout
        self.header = FlexContainer(direction="row", justify_content="space_between", align_items="center", padding=0)
        self.header.width.set(width - 48.0) # padding compensation
        
        self.velocity_counter = TokenSpeedVelocityCounter()
        self.stop_btn = StopGenerationButton()
        
        self.header.add(self.velocity_counter, self.stop_btn)
        
        self.content_area = FlexContainer(direction="row", padding=0, gap=8)
        
        self.streaming_text = StreamingText(
            content="",
            variant=TypingVariant.STREAM,
            font_size=18.0,
            color=colors.SLATE_200,
            speed=0.0, # Controlled externally via stream_text
            show_cursor=False # Use custom cursor
        )
        
        self.cursor = ShimmeringCaretIndicator()
        
        self.content_area.add(self.streaming_text)
        
        # Cursor positioning is tricky since StreamingText calculates it internally.
        # But we can approximate or use a trick by making it a sibling and adjusting its position 
        # based on the text bounding box, or just having it next to it in a row container.
        self.content_area.add(self.cursor)
        
        self.add(self.header, self.content_area)
        
        self._current_text = ""
        self._is_streaming = False
        
    def stream_text(self, text: str, duration: float) -> List[AnimationAction]:
        """
        Animation generator that updates the text buffer over the duration.
        """
        self._current_text = text
        self.streaming_text.content = text
        self.streaming_text.total_chars = len(text)
        
        # Parse lines as StreamingText does internally so local_bounds work
        self.streaming_text.lines = []
        for raw_line in text.split("\n"):
            line = raw_line.strip()
            if not line:
                self.streaming_text.lines.append((False, 0.6, ""))
                continue
            if line.startswith("## "):
                self.streaming_text.lines.append((True, 1.25, line[3:]))
            elif line.startswith("# "):
                self.streaming_text.lines.append((True, 1.35, line[2:]))
            elif line.startswith("**") and line.endswith("**"):
                self.streaming_text.lines.append((True, 1.20, line[2:-2]))
            else:
                self.streaming_text.lines.append((False, 1.0, line))
                
        # Calculate speed needed to finish text in 'duration' seconds
        speed = len(text) / duration if duration > 0 else 0.0
        self.streaming_text.speed = speed
        self.streaming_text.start_delay = 0.0 # reset delay
        
        self._is_streaming = True
        
        # Animate the token counter
        from vibmo.timeline.scheduler import ParallelGroup
        return [self.velocity_counter.tokens_count.to(float(len(text)), duration=duration, ease=Ease.linear)]

    def draw(self, ctx: Any, time: float = 0.0) -> None:
        # Draw background and children
        super().draw(ctx, time)

