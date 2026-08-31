"""
Rhythmic Cuts & Flash Sequencing Suites for Vibmo.
Inspired by video-shotcraft:
- beat-cut-accelerando: Progressively halved frame intervals (16f -> 12f -> 8f -> 4f) ending in a dead stop hold.
- paparazzi-flash: Triple camera flash snapping between macro detail crops.
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


class BeatCutAccelerando(Node):
    """
    Rhythmic rapid cutting sequence with exponentially decreasing interval steps:
    16f -> 12f -> 8f -> 4f cuts ending in a dead stop hold.
    """

    def __init__(
        self,
        cut_labels: Optional[List[str]] = None,
        accent_color: Union[Color, str] = colors.CYAN,
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)
        self.cut_labels = cut_labels or ["INITIATE", "GPU ACCELERATE", "VECTOR EMBED", "RENDER 60FPS", "VERIFIED"]
        self.accent_color = Color.from_any(accent_color)
        self.step_index = Signal(0.0, f"{self.id}.step")

    def step_cut(self, step: int, duration: float = 0.1, delay: float = 0.0) -> AnimationAction:
        """Instantly cuts to the specified sequence frame index."""
        return self.step_index.to(float(step), duration=duration, delay=delay, ease=Ease.linear)

    def draw(self, ctx: cairo.Context, time: float = 0.0) -> None:
        idx = int(self.step_index.evaluate_at(time)) % len(self.cut_labels)
        label = self.cut_labels[idx]
        cx, cy = self.position.evaluate_at(time)

        ctx.save()
        ctx.translate(cx, cy)

        # Full-width Cut Banner
        banner_w, banner_h = 720.0, 140.0
        r = 16.0

        ctx.set_source_rgba(0.06, 0.08, 0.14, 0.95)
        ctx.rectangle(-banner_w / 2, -banner_h / 2, banner_w, banner_h)
        ctx.fill_preserve()

        ctx.set_source_rgba(
            self.accent_color.r,
            self.accent_color.g,
            self.accent_color.b,
            0.8,
        )
        ctx.set_line_width(2.0)
        ctx.stroke()

        # Step index number
        ctx.select_font_face("Space Grotesk", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
        ctx.set_font_size(18.0)
        ctx.set_source_rgba(self.accent_color.r, self.accent_color.g, self.accent_color.b, 1.0)
        ctx.move_to(-banner_w / 2 + 40.0, -banner_h / 2 + 40.0)
        ctx.show_text(f"BEAT CUT // 0{idx + 1}")

        # Big Cut Headline
        ctx.set_font_size(44.0)
        ctx.set_source_rgba(0.95, 0.98, 1.0, 1.0)
        ctx.move_to(-banner_w / 2 + 40.0, banner_h / 2 - 35.0)
        ctx.show_text(label)

        ctx.restore()


class PaparazziFlash(Node):
    """
    Triple camera flash snapping between macro detail crops with shutter decay.
    """

    def __init__(
        self,
        flash_color: Union[Color, str] = colors.WHITE,
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)
        self.flash_color = Color.from_any(flash_color)
        self.flash_alpha = Signal(0.0, f"{self.id}.alpha")

    def trigger_flash(self, duration: float = 0.25, delay: float = 0.0) -> AnimationAction:
        """Triggers instantaneous camera strobe flash with rapid exponential decay."""
        return self.flash_alpha.to(1.0, duration=0.04, delay=delay, ease=Ease.linear)

    def draw(self, ctx: cairo.Context, time: float = 0.0) -> None:
        a = self.flash_alpha.evaluate_at(time)
        if a <= 0.001:
            return

        ctx.save()
        ctx.set_source_rgba(
            self.flash_color.r,
            self.flash_color.g,
            self.flash_color.b,
            a * 0.85,
        )
        ctx.paint()
        ctx.restore()
