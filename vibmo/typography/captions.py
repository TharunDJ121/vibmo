"""
Kinetic Captions & Word-by-Word Subtitle Animation Engine (Remotion & Shorts inspired).
Features Whisper-compatible word-level timestamp animation, TikTok bounce, Karaoke sweep, and Auto-Chunking.
"""

from __future__ import annotations
import math
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple, Union, Sequence

from vibmo.core.color import Color, colors
from vibmo.core.vector import Vector2D
from vibmo.core.signal import Signal
from vibmo.scene.node import Node


@dataclass
class CaptionWord:
    """A single word with start/end timestamps and optional emoji / tag."""
    text: str
    start: float  # Start time in seconds
    end: float    # End time in seconds
    color: Optional[Color] = None
    emoji: Optional[str] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> CaptionWord:
        c = Color.from_any(data["color"]) if "color" in data and data["color"] else None
        return cls(
            text=str(data["text"]).strip(),
            start=float(data["start"]),
            end=float(data["end"]),
            color=c,
            emoji=data.get("emoji"),
        )


class KineticCaptions(Node):
    """
    Animated Kinetic Captions Node.
    Renders word-by-word dynamic subtitles with spring overshoot, active word highlighting,
    and automatic line paging.
    """

    def __init__(
        self,
        words: List[Union[CaptionWord, Dict[str, Any]]],
        font_size: float = 48.0,
        font_family: str = "Inter",
        style_preset: str = "tiktok_bounce",  # "tiktok_bounce", "karaoke_fill", "minimal_pop"
        active_color: Union[Color, str] = colors.AMBER,
        inactive_color: Union[Color, str] = colors.WHITE,
        stroke_color: Union[Color, str] = colors.SLATE_900,
        stroke_width: float = 8.0,
        background_pill: bool = True,
        pill_color: Union[Color, str] = Color.hex("#090D16").with_alpha(0.85),
        words_per_line: int = 5,
        max_duration_per_line: float = 2.5,
        position: Union[Vector2D, Sequence[float]] = (960.0, 850.0),
        **kwargs: Any,
    ) -> None:
        super().__init__(position=position, **kwargs)
        self.font_size = float(font_size)
        self.font_family = font_family
        self.style_preset = style_preset
        self.active_color = Color.from_any(active_color)
        self.inactive_color = Color.from_any(inactive_color)
        self.stroke_color = Color.from_any(stroke_color)
        self.stroke_width = float(stroke_width)
        self.background_pill = background_pill
        self.pill_color = Color.from_any(pill_color)
        self.words_per_line = words_per_line
        self.max_duration_per_line = max_duration_per_line

        # Parse word objects
        self.parsed_words: List[CaptionWord] = []
        for w in words:
            if isinstance(w, dict):
                self.parsed_words.append(CaptionWord.from_dict(w))
            else:
                self.parsed_words.append(w)

        # Build chunks / lines
        self.lines: List[List[CaptionWord]] = self._build_lines()

    def _build_lines(self) -> List[List[CaptionWord]]:
        """Groups words into short, rhythmic subtitle lines."""
        lines: List[List[CaptionWord]] = []
        current_line: List[CaptionWord] = []
        line_start = 0.0

        for word in self.parsed_words:
            if not current_line:
                line_start = word.start
                current_line.append(word)
            else:
                # Check line limits (word count or duration or long silence gap)
                gap = word.start - current_line[-1].end
                dur = word.end - line_start
                if len(current_line) >= self.words_per_line or dur > self.max_duration_per_line or gap > 0.6:
                    lines.append(current_line)
                    current_line = [word]
                    line_start = word.start
                else:
                    current_line.append(word)

        if current_line:
            lines.append(current_line)
        return lines

    def _get_active_line(self, time: float) -> Optional[List[CaptionWord]]:
        """Finds which line should be visible at timestamp `time`."""
        for line in self.lines:
            line_start = line[0].start - 0.1
            line_end = line[-1].end + 0.25
            if line_start <= time <= line_end:
                return line
        return None

    def local_bounds(self, time: float = 0.0) -> Tuple[float, float, float, float]:
        return (-500.0, -50.0, 1000.0, 100.0)

    def draw(self, ctx: Any, time: float = 0.0) -> None:
        import cairo

        line = self._get_active_line(time)
        if not line:
            return

        ctx.save()
        ctx.select_font_face(self.font_family, cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
        ctx.set_font_size(self.font_size)

        # Calculate word widths and total line width
        word_metrics = []
        total_width = 0.0
        space_width = ctx.text_extents(" ")[4]

        for w in line:
            ext = ctx.text_extents(w.text)
            word_metrics.append((ext[4], ext[2], ext[3]))  # x_advance, width, height
            total_width += ext[4] + space_width
        total_width -= space_width

        start_x = -total_width / 2.0
        current_x = start_x

        # 1. Background Pill (if enabled)
        if self.background_pill:
            pad_x = 24.0
            pad_y = 14.0
            pill_w = total_width + pad_x * 2.0
            pill_h = self.font_size * 1.5 + pad_y * 2.0
            pill_x = -pill_w / 2.0
            pill_y = -pill_h / 2.0 + 4.0

            ctx.save()
            ctx.set_source_rgba(self.pill_color.r, self.pill_color.g, self.pill_color.b, self.pill_color.a)
            # Draw rounded rect
            rad = 16.0
            ctx.new_sub_path()
            ctx.arc(pill_x + pill_w - rad, pill_y + rad, rad, -math.pi / 2, 0)
            ctx.arc(pill_x + pill_w - rad, pill_y + pill_h - rad, rad, 0, math.pi / 2)
            ctx.arc(pill_x + rad, pill_y + pill_h - rad, rad, math.pi / 2, math.pi)
            ctx.arc(pill_x + rad, pill_y + rad, rad, math.pi, 3 * math.pi / 2)
            ctx.close_path()
            ctx.fill()
            ctx.restore()

        # 2. Render each word in line
        for i, word in enumerate(line):
            is_active = word.start <= time <= word.end
            has_spoken = time > word.end

            # Calculate word scale and color based on preset
            scale = 1.0
            text_color = self.inactive_color

            if is_active:
                text_color = self.active_color
                if self.style_preset == "tiktok_bounce":
                    # Bouncy spring peak when word begins
                    elapsed = time - word.start
                    dur = max(0.01, word.end - word.start)
                    progress = min(1.0, elapsed / dur)
                    # Spring pop: 1.0 -> 1.25 -> 1.0
                    scale = 1.0 + 0.25 * math.sin(progress * math.pi)
            elif has_spoken:
                text_color = self.inactive_color.with_alpha(0.85)
            else:
                text_color = self.inactive_color.with_alpha(0.4)

            w_adv, w_w, w_h = word_metrics[i]
            center_word_x = current_x + w_adv / 2.0

            ctx.save()
            # Apply scale from center of word
            ctx.translate(center_word_x, 0.0)
            ctx.scale(scale, scale)
            ctx.translate(-center_word_x, 0.0)

            # Stroke (outline) for high readability
            if self.stroke_width > 0:
                ctx.set_source_rgba(self.stroke_color.r, self.stroke_color.g, self.stroke_color.b, self.stroke_color.a)
                ctx.set_line_width(self.stroke_width)
                ctx.set_line_join(cairo.LINE_JOIN_ROUND)
                ctx.move_to(current_x, self.font_size * 0.35)
                ctx.text_path(word.text)
                ctx.stroke()

            # Fill Text
            ctx.set_source_rgba(text_color.r, text_color.g, text_color.b, text_color.a)
            ctx.move_to(current_x, self.font_size * 0.35)
            ctx.show_text(word.text)

            ctx.restore()

            current_x += w_adv + space_width

        ctx.restore()
