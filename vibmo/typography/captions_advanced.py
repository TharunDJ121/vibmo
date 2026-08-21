"""
Advanced Subtitle & Kinetic Caption System with word-level sync, bouncing highlight pills, and social video presets.
"""

from __future__ import annotations
import math
from typing import Any, Dict, List, Optional, Sequence, Tuple, Union
from dataclasses import dataclass
import cairo

from vibmo.core.color import Color, colors
from vibmo.core.vector import Vector2D
from vibmo.core.signal import Signal, AnimationAction
from vibmo.scene.node import Node
from vibmo.typography.captions import CaptionWord, KineticCaptions


@dataclass
class TimedWord:
    word: str
    start: float
    end: float
    confidence: float = 1.0


class AdvancedKaraokeCaptions(Node):
    """
    TikTok / Instagram Reels / YouTube Shorts style animated kinetic captions
    with glowing bouncing background pill indicator that follows each spoken word in real-time.
    """

    def __init__(
        self,
        words: Optional[Sequence[TimedWord]] = None,
        font_size: float = 44.0,
        font_family: str = "Segoe UI",
        active_color: Union[Color, str] = colors.YELLOW,
        inactive_color: Union[Color, str] = colors.WHITE,
        pill_color: Union[Color, str] = colors.INDIGO,
        max_words_per_line: int = 4,
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)
        self.words = list(words or [
            TimedWord("Automated", 0.0, 0.5),
            TimedWord("motion", 0.5, 0.9),
            TimedWord("graphics", 0.9, 1.4),
            TimedWord("in", 1.4, 1.6),
            TimedWord("Python", 1.6, 2.2),
        ])
        self.font_size = float(font_size)
        self.font_family = font_family
        self.active_color = Color.from_any(active_color)
        self.inactive_color = Color.from_any(inactive_color)
        self.pill_color = Color.from_any(pill_color)
        self.max_words_per_line = max_words_per_line

    def local_bounds(self, time: float = 0.0) -> Tuple[float, float, float, float]:
        return (-300.0, -50.0, 600.0, 100.0)

    def draw(self, ctx: Any, time: float = 0.0) -> None:
        if not self.words:
            return

        ctx.save()
        ctx.select_font_face(self.font_family, cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
        ctx.set_font_size(self.font_size)

        # Find active word at timestamp
        active_idx = -1
        for i, tw in enumerate(self.words):
            if tw.start <= time <= tw.end:
                active_idx = i
                break
            elif time > tw.end and (i == len(self.words) - 1 or time < self.words[i + 1].start):
                active_idx = i

        # Measure words to center line
        extents = [ctx.text_extents(tw.word) for tw in self.words]
        space_ext = ctx.text_extents(" ")
        total_w = sum(e.width for e in extents) + space_ext.width * (len(self.words) - 1)

        start_x = -total_w * 0.5
        cur_x = start_x

        # 1. Draw Active Pill behind active word
        if 0 <= active_idx < len(self.words):
            # Calculate active word position
            ax = start_x + sum(extents[j].width + space_ext.width for j in range(active_idx))
            aw = extents[active_idx].width + 20.0
            ah = self.font_size * 1.3
            ay = -self.font_size * 0.95

            # Pill bounce spring
            tw = self.words[active_idx]
            prog = max(0.0, min(1.0, (time - tw.start) / max(0.01, tw.end - tw.start)))
            bounce = 1.0 + 0.15 * math.sin(prog * math.pi)

            ctx.save()
            ctx.translate(ax + aw * 0.5 - 10.0, ay + ah * 0.5)
            ctx.scale(bounce, bounce)
            ctx.translate(-(ax + aw * 0.5 - 10.0), -(ay + ah * 0.5))

            self._rounded_rect(ctx, ax - 10.0, ay, aw, ah, 10.0)
            pc = self.pill_color
            ctx.set_source_rgba(pc.r, pc.g, pc.b, 0.95)
            ctx.fill()
            ctx.restore()

        # 2. Render Text Glyphs
        for i, tw in enumerate(self.words):
            is_active = (i == active_idx)
            c = self.active_color if is_active else self.inactive_color

            ctx.set_source_rgba(c.r, c.g, c.b, c.a)
            ctx.move_to(cur_x, 0.0)
            ctx.show_text(tw.word)

            cur_x += extents[i].width + space_ext.width

        ctx.restore()

    def _rounded_rect(self, ctx: Any, x: float, y: float, w: float, h: float, r: float) -> None:
        r = min(r, w * 0.5, h * 0.5)
        ctx.new_path()
        ctx.arc(x + w - r, y + r, r, -math.pi * 0.5, 0)
        ctx.arc(x + w - r, y + h - r, r, 0, math.pi * 0.5)
        ctx.arc(x + r, y + h - r, r, math.pi * 0.5, math.pi)
        ctx.arc(x + r, y + r, r, math.pi, math.pi * 1.5)
        ctx.close_path()
