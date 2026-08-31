"""
✦ Vibmo Typography: Matrix Cipher Decode Typography Suite
Inspired by Remocn matrix-decode with high-velocity glyph cycling and chromatic lock-in.
"""

from __future__ import annotations

import random
from typing import Any, List, Optional, Tuple, Union
import cairo

from vibmo.core.color import Color, colors
from vibmo.core.signal import Signal, AnimationAction
from vibmo.core.easing import Ease
from vibmo.scene.node import Node
from vibmo.timeline.scheduler import all as sched_all


class MatrixGlyphScrambler(Node):
    """
    Renders an individual character that rapidly scrambles through a cipher pool
    before resolving and locking into the target character.
    """
    def __init__(
        self,
        target_char: str,
        pool: str = "0123456789ABCDEF$#@%&*!?",
        font_size: float = 36.0,
        font_family: str = "monospace",
        color: Color = colors.EMERALD,
        lock_color: Color = colors.WHITE,
        cycle_speed: float = 24.0,
        **kwargs: Any,
    ):
        super().__init__(**kwargs)
        self.target_char = target_char
        self.pool = pool if pool else "0123456789"
        self.font_size = Signal(float(font_size), f"{self.name}.font_size")
        self.font_family = font_family
        self.color = Signal(color, f"{self.name}.color")
        self.lock_color = Signal(lock_color, f"{self.name}.lock_color")
        self.cycle_speed = cycle_speed
        self.decode_progress = Signal(0.0, f"{self.name}.decode_progress")

        self._seed = hash(target_char) & 0xFFFFFF

    def draw(self, ctx: Any, time: float = 0.0) -> None:
        prog = self.decode_progress.get(time)
        fs = self.font_size.get(time)

        if prog >= 1.0 or not self.target_char:
            char_to_render = self.target_char
            c = self.lock_color.get(time)
        else:
            # Random scramble glyph based on time and local seed
            step = int(time * self.cycle_speed + self._seed)
            rng = random.Random(step)
            char_to_render = rng.choice(self.pool)
            c = self.color.get(time)

        ctx.save()
        ctx.select_font_face(self.font_family, cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
        ctx.set_font_size(fs)
        ctx.set_source_rgba(c.r, c.g, c.b, c.a)

        ctx.move_to(0, fs * 0.88)
        ctx.show_text(char_to_render)
        ctx.restore()

        super().draw(ctx, time)


class MatrixDecodeText(Node):
    """
    Headline component that decodes from an encrypted matrix glyph scramble into final legible text.
    """
    def __init__(
        self,
        text: str,
        font_size: float = 36.0,
        font_family: str = "monospace",
        color: Color = colors.EMERALD,
        lock_color: Color = colors.WHITE,
        stagger: float = 0.05,
        **kwargs: Any,
    ):
        super().__init__(**kwargs)
        self.raw_text = text
        self.font_size = Signal(float(font_size), f"{self.name}.font_size")
        self.font_family = font_family
        self.color = Signal(color, f"{self.name}.color")
        self.lock_color = Signal(lock_color, f"{self.name}.lock_color")
        self.stagger = stagger
        self.glyph_nodes: List[MatrixGlyphScrambler] = []

        self._build_scramblers()

    def _build_scramblers(self) -> None:
        fs = self.font_size.get(0.0)
        c = self.color.get(0.0)
        lc = self.lock_color.get(0.0)
        cur_x = 0.0

        surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, 10, 10)
        ctx = cairo.Context(surface)
        ctx.select_font_face(self.font_family, cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
        ctx.set_font_size(fs)

        for i, ch in enumerate(self.raw_text):
            node = MatrixGlyphScrambler(
                target_char=ch,
                font_size=fs,
                font_family=self.font_family,
                color=c,
                lock_color=lc,
                position=(cur_x, 0.0),
                name=f"{self.name}_glyph_{i}",
            )
            self.add(node)
            self.glyph_nodes.append(node)

            ext = ctx.text_extents(ch)
            adv = ext.x_advance if ext.x_advance > 0 else fs * 0.55
            cur_x += adv

    def decode(self, duration: float = 1.2, ease: Any = Ease.out_expo) -> AnimationAction:
        """Triggers the wave-staggered decode sequence."""
        actions = []
        for i, node in enumerate(self.glyph_nodes):
            delay = i * self.stagger
            actions.append(node.decode_progress.to(1.0, duration=duration, delay=delay, ease=ease))
        return sched_all(*actions)
