"""
✦ Vibmo Typography: Blur Out Up Kinetic Text Suite
Inspired by Remocn blur-out-up with upward character drift and gaussian blur dissipation.
"""

from __future__ import annotations

import math
from typing import Any, List, Optional, Tuple, Union
import cairo

from vibmo.core.color import Color, colors
from vibmo.core.signal import Signal, AnimationAction
from vibmo.core.easing import Ease
from vibmo.scene.node import Node
from vibmo.timeline.scheduler import all as sched_all


class BlurOutUpCharacterNode(Node):
    """
    Single character node that floats upward while fading out and expanding blur dissipation.
    """
    def __init__(
        self,
        char: str,
        font_size: float = 48.0,
        font_family: str = "Inter",
        color: Color = colors.WHITE,
        **kwargs: Any,
    ):
        super().__init__(**kwargs)
        self.char = char
        self.font_size = Signal(float(font_size), f"{self.name}.font_size")
        self.font_family = font_family
        self.color = Signal(color, f"{self.name}.color")
        self.progress = Signal(0.0, f"{self.name}.progress")  # 0: fully visible, 1: vanished upward

    def draw(self, ctx: Any, time: float = 0.0) -> None:
        prog = self.progress.get(time)
        if prog >= 1.0 or not self.char:
            return

        fs = self.font_size.get(time)
        col = self.color.get(time)

        # Upward drift offset: 0 -> -60px
        y_offset = -60.0 * (prog ** 1.4)
        alpha = col.a * (1.0 - (prog ** 0.8))
        scale = 1.0 + 0.15 * prog

        ctx.save()
        ctx.select_font_face(self.font_family, cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
        ctx.set_font_size(fs * scale)
        ctx.set_source_rgba(col.r, col.g, col.b, alpha)

        extents = ctx.text_extents(self.char)
        ctx.move_to(0, fs * 0.88 + y_offset)
        ctx.show_text(self.char)

        # Add soft faux-blur duplicate passes if in motion
        if 0.05 < prog < 0.95:
            ctx.set_source_rgba(col.r, col.g, col.b, alpha * 0.3)
            ctx.move_to(0, fs * 0.88 + y_offset - 3.0)
            ctx.show_text(self.char)
            ctx.move_to(0, fs * 0.88 + y_offset + 3.0)
            ctx.show_text(self.char)

        ctx.restore()
        super().draw(ctx, time)


class BlurOutUpText(Node):
    """
    Kinetic title where characters stagger and float upward with blur dissipation.
    """
    def __init__(
        self,
        text: str,
        font_size: float = 48.0,
        font_family: str = "Inter",
        color: Color = colors.WHITE,
        stagger: float = 0.04,
        **kwargs: Any,
    ):
        super().__init__(**kwargs)
        self.raw_text = text
        self.font_size = Signal(float(font_size), f"{self.name}.font_size")
        self.font_family = font_family
        self.color = Signal(color, f"{self.name}.color")
        self.stagger = stagger
        self.char_nodes: List[BlurOutUpCharacterNode] = []

        self._build_characters()

    def _build_characters(self) -> None:
        fs = self.font_size.get(0.0)
        c = self.color.get(0.0)
        cur_x = 0.0

        surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, 10, 10)
        ctx = cairo.Context(surface)
        ctx.select_font_face(self.font_family, cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
        ctx.set_font_size(fs)

        for i, ch in enumerate(self.raw_text):
            node = BlurOutUpCharacterNode(
                char=ch,
                font_size=fs,
                font_family=self.font_family,
                color=c,
                position=(cur_x, 0.0),
                name=f"{self.name}_ch_{i}",
            )
            self.add(node)
            self.char_nodes.append(node)

            ext = ctx.text_extents(ch)
            adv = ext.x_advance if ext.x_advance > 0 else fs * 0.4
            cur_x += adv

    def blur_out_up(self, duration: float = 0.8, ease: Any = Ease.out_expo) -> AnimationAction:
        """Triggers staggered upward blur dissipation of all characters."""
        actions = []
        for i, node in enumerate(self.char_nodes):
            delay = i * self.stagger
            actions.append(node.progress.to(1.0, duration=duration, delay=delay, ease=ease))
        return sched_all(*actions)

    def pop_in(self, duration: float = 0.6) -> AnimationAction:
        """Resets character progress to 0 (visible)."""
        actions = [node.progress.to(0.0, duration=duration) for node in self.char_nodes]
        return sched_all(*actions)
