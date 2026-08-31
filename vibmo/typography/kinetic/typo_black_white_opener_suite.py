"""
Black & White Foley Typing Opener Suite for Vibmo.
Inspired by video-production-skills black-white-text-opener.
Pure black stage + crisp white kinetic type + 14 chars/sec cadence + word replacement + velocity wipe.
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


class BlackWhiteTypingOpener(Node):
    """
    High-impact Black & White Typing Opener:
    - Pitch black background hold.
    - Deterministic 14 cps character typewriter reveal.
    - Seamless word replacement states.
    - Final velocity wipe transition into main scene.
    """

    def __init__(
        self,
        title_prefix: str = "AI workflow engine",
        replace_phrases: Optional[List[str]] = None,
        final_hold_text: str = "Build in minutes.",
        typing_cps: float = 14.0,
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)
        self.title_prefix = title_prefix
        self.replace_phrases = replace_phrases or ["from raw idea", "to shipped video"]
        self.final_hold_text = final_hold_text
        self.typing_cps = typing_cps

        # Signals
        self.type_progress = Signal(0.0, f"{self.id}.type")
        self.replace_index = Signal(0.0, f"{self.id}.replace")
        self.wipe_progress = Signal(0.0, f"{self.id}.wipe")

    def type_intro(self, duration: float = 1.2, delay: float = 0.0) -> AnimationAction:
        """Types the initial main phrase."""
        return self.type_progress.to(1.0, duration=duration, delay=delay, ease=Ease.linear)

    def cycle_replace(self, target_idx: float, duration: float = 0.6, delay: float = 0.0) -> AnimationAction:
        """Cycles to the next replacement phrase with horizontal blur."""
        return self.replace_index.to(target_idx, duration=duration, delay=delay, ease=Ease.out_expo)

    def velocity_wipe(self, duration: float = 0.5, delay: float = 0.0) -> AnimationAction:
        """Sweeps a high-velocity white wipe transition across the frame."""
        return self.wipe_progress.to(1.0, duration=duration, delay=delay, ease=Ease.in_out_cubic)

    def draw(self, ctx: cairo.Context, time: float = 0.0) -> None:
        tp = self.type_progress.evaluate_at(time)
        rep = self.replace_index.evaluate_at(time)
        wipe = self.wipe_progress.evaluate_at(time)

        cx, cy = self.position.evaluate_at(time)

        ctx.save()

        # 1. Pitch Black Background
        ctx.set_source_rgb(0.0, 0.0, 0.0)
        ctx.paint()

        # 2. Main Typing Text
        if tp > 0.001:
            char_count = int(len(self.title_prefix) * tp)
            visible_prefix = self.title_prefix[:char_count]

            ctx.save()
            ctx.translate(cx, cy - 30.0)

            ctx.select_font_face("Space Grotesk", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
            ctx.set_font_size(52.0)
            ctx.set_source_rgb(1.0, 1.0, 1.0)
            
            ext = ctx.text_extents(visible_prefix)
            ctx.move_to(-ext.width / 2, 0.0)
            ctx.show_text(visible_prefix)

            # Blinking Square Caret
            if tp < 1.0 or int(time * 3.0) % 2 == 0:
                ctx.rectangle(ext.width / 2 + 10.0, -42.0, 6.0, 48.0)
                ctx.fill()

            ctx.restore()

        # 3. Subtitle Word Replacement Sequence
        if rep > 0.01:
            ctx.save()
            ctx.translate(cx, cy + 50.0)

            n_phrases = len(self.replace_phrases)
            curr_idx = min(n_phrases - 1, int(rep))
            phrase = self.replace_phrases[curr_idx]
            
            # Phrase fade / slide
            local_p = rep - curr_idx
            alpha = min(1.0, 1.0 - abs(local_p - 0.5) * 0.5)

            ctx.select_font_face("Inter", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)
            ctx.set_font_size(24.0)
            ctx.set_source_rgba(0.75, 0.82, 0.94, alpha)
            ext_rep = ctx.text_extents(phrase)
            ctx.move_to(-ext_rep.width / 2, 0.0)
            ctx.show_text(phrase)

            ctx.restore()

        # 4. White Velocity Wipe Transition
        if 0.0 < wipe < 1.0:
            wipe_x = -100.0 + wipe * 2200.0
            wipe_w = 400.0

            grad = cairo.LinearGradient(wipe_x - wipe_w / 2, 0, wipe_x + wipe_w / 2, 0)
            grad.add_color_stop_rgba(0.0, 1, 1, 1, 0.0)
            grad.add_color_stop_rgba(0.5, 1, 1, 1, 0.95)
            grad.add_color_stop_rgba(1.0, 1, 1, 1, 0.0)

            ctx.set_source(grad)
            ctx.rectangle(0, 0, 1920, 1080)
            ctx.fill()

        ctx.restore()
