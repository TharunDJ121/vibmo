"""
Audio visualizer components (SpectrumVisualizer, CircularEqualizer, WaveformRibbon, AudioReactivePulse).
"""

from __future__ import annotations
import math
from typing import Any, List, Optional, Sequence, Tuple, Union
import cairo
import numpy as np

from vibmo.core.color import Color, colors
from vibmo.core.vector import Vector2D
from vibmo.scene.node import Node


class SpectrumVisualizer(Node):
    """
    Animated FFT Frequency Spectrum Bars visualizer with glowing caps.
    """

    def __init__(
        self,
        bars: int = 24,
        width: float = 480.0,
        height: float = 140.0,
        color: Union[Color, str] = colors.CYAN,
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)
        self.bar_count = max(4, int(bars))
        self.width_val = float(width)
        self.height_val = float(height)
        self.color = Color.from_any(color)

    def local_bounds(self, time: float = 0.0) -> Tuple[float, float, float, float]:
        return (0.0, 0.0, self.width_val, self.height_val)

    def draw(self, ctx: Any, time: float = 0.0) -> None:
        w, h = self.width_val, self.height_val
        n = self.bar_count
        slot_w = w / n
        bar_w = max(4.0, slot_w - 4.0)

        ctx.save()
        c = self.color

        for i in range(n):
            # Harmonic procedural audio frequency spectrum simulator
            freq_band = (i + 1) * 1.5
            val = (
                0.5 * math.sin(time * 6.0 + freq_band) +
                0.3 * math.sin(time * 14.0 + freq_band * 2.1) +
                0.2 * math.cos(time * 22.0 + freq_band * 3.7)
            )
            norm_val = max(0.08, min(1.0, (val + 1.0) * 0.5))
            bar_h = norm_val * h

            bx = i * slot_w + (slot_w - bar_w) * 0.5
            by = h - bar_h

            # Bar body
            ctx.set_source_rgba(c.r, c.g, c.b, 0.75)
            self._rounded_rect(ctx, bx, by, bar_w, bar_h, 4.0)
            ctx.fill()

            # Glowing peak cap
            ctx.set_source_rgba(1.0, 1.0, 1.0, 0.95)
            ctx.rectangle(bx, by, bar_w, 3.0)
            ctx.fill()

        ctx.restore()

    def _rounded_rect(self, ctx: Any, x: float, y: float, w: float, h: float, r: float) -> None:
        r = min(r, w * 0.5, h * 0.5)
        ctx.new_path()
        ctx.arc(x + w - r, y + r, r, -math.pi * 0.5, 0)
        ctx.arc(x + w - r, y + h - r, r, 0, math.pi * 0.5)
        ctx.arc(x + r, y + h - r, r, math.pi * 0.5, math.pi)
        ctx.arc(x + r, y + r, r, math.pi, math.pi * 1.5)
        ctx.close_path()


class CircularEqualizer(Node):
    """
    360-degree radial circular audio visualizer.
    """

    def __init__(
        self,
        radius: float = 90.0,
        bars: int = 36,
        color: Union[Color, str] = colors.INDIGO,
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)
        self.radius = float(radius)
        self.bars = max(8, int(bars))
        self.color = Color.from_any(color)

    def local_bounds(self, time: float = 0.0) -> Tuple[float, float, float, float]:
        r = self.radius + 80.0
        return (-r, -r, r * 2, r * 2)

    def draw(self, ctx: Any, time: float = 0.0) -> None:
        r0 = self.radius
        n = self.bars
        angle_step = (math.pi * 2) / n
        c = self.color

        ctx.save()
        ctx.set_line_width(4.0)
        ctx.set_line_cap(cairo.LINE_CAP_ROUND)

        for i in range(n):
            a = i * angle_step
            # Simulated audio intensity
            norm_val = 0.3 + 0.7 * abs(math.sin(time * 8.0 + i * 0.4))
            r1 = r0 + norm_val * 40.0

            x0 = math.cos(a) * r0
            y0 = math.sin(a) * r0
            x1 = math.cos(a) * r1
            y1 = math.sin(a) * r1

            ctx.set_source_rgba(c.r, c.g, c.b, 0.85)
            ctx.move_to(x0, y0)
            ctx.line_to(x1, y1)
            ctx.stroke()

        ctx.restore()


class AudioReactivePulse(Node):
    """
    Pulse container that organically scales / blooms child nodes with audio beat energy.
    """

    def __init__(
        self,
        bpm: float = 120.0,
        intensity: float = 0.25,
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)
        self.bpm = float(bpm)
        self.intensity = float(intensity)

    def draw(self, ctx: Any, time: float = 0.0) -> None:
        # Beat interval in seconds
        beat_interval = 60.0 / self.bpm
        beat_phase = (time % beat_interval) / beat_interval
        # Fast kick attack with exponential decay
        scale = 1.0 + self.intensity * math.exp(-beat_phase * 6.0)

        ctx.save()
        ctx.scale(scale, scale)
        super().draw(ctx, time)
        ctx.restore()
