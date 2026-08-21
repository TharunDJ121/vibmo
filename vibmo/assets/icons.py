"""
Built-in SVG Icon Registry and Vector Icon Component.
Provides zero-network vector icons (Lucide / Heroicons inspired) with instant rendering.
"""

from __future__ import annotations
import math
from typing import Any, Dict, Optional, Sequence, Tuple, Union
import cairo

from vibmo.core.color import Color, colors
from vibmo.core.vector import Vector2D
from vibmo.core.signal import Signal, AnimationAction
from vibmo.core.easing import Ease, EasingFunc
from vibmo.scene.node import Node


# Built-in SVG-like path drawing routines normalized to a 24x24 viewBox
ICON_REGISTRY: Dict[str, Any] = {
    "sparkles": [
        ("move", 12, 3), ("line", 14, 8), ("line", 19, 10), ("line", 14, 12),
        ("line", 12, 17), ("line", 10, 12), ("line", 5, 10), ("line", 10, 8), ("close",)
    ],
    "check": [
        ("move", 20, 6), ("line", 9, 17), ("line", 4, 12)
    ],
    "alert": [
        ("move", 12, 2), ("line", 22, 20), ("line", 2, 20), ("close",),
        ("move", 12, 9), ("line", 12, 13),
        ("move", 12, 17), ("arc", 12, 17, 0.8)
    ],
    "user": [
        ("circle", 12, 8, 4),
        ("arc_path", 12, 14, 8, math.pi, 0)
    ],
    "gear": [
        ("circle", 12, 12, 3),
        ("circle", 12, 12, 7)
    ],
    "bell": [
        ("move", 18, 8), ("arc_path", 12, 8, 6, 0, math.pi),
        ("line", 6, 17), ("line", 18, 17), ("line", 18, 8),
        ("move", 10, 19), ("line", 14, 19)
    ],
    "chart": [
        ("move", 3, 3), ("line", 3, 21), ("line", 21, 21),
        ("move", 7, 16), ("line", 11, 10), ("line", 15, 14), ("line", 19, 6)
    ],
    "arrow": [
        ("move", 5, 12), ("line", 19, 12),
        ("move", 13, 6), ("line", 19, 12), ("line", 13, 18)
    ],
    "search": [
        ("circle", 11, 11, 6),
        ("move", 16, 16), ("line", 21, 21)
    ],
    "heart": [
        ("move", 12, 21), ("line", 4, 13),
        ("arc_path", 8, 9, 4, math.pi * 0.75, math.pi * 1.75),
        ("arc_path", 16, 9, 4, math.pi * 1.25, math.pi * 0.25),
        ("close",)
    ],
    "star": [
        ("move", 12, 2), ("line", 15, 9), ("line", 22, 9), ("line", 17, 14),
        ("line", 19, 21), ("line", 12, 17), ("line", 5, 21), ("line", 7, 14),
        ("line", 2, 9), ("line", 9, 9), ("close",)
    ],
    "shield": [
        ("move", 12, 2), ("line", 20, 5), ("line", 20, 12),
        ("line", 12, 22), ("line", 4, 12), ("line", 4, 5), ("close",)
    ],
    "lock": [
        ("rect", 5, 11, 14, 10),
        ("arc_path", 12, 11, 4, math.pi, 0)
    ],
    "play": [
        ("move", 6, 4), ("line", 20, 12), ("line", 6, 20), ("close",)
    ],
    "pause": [
        ("rect", 6, 4, 4, 16),
        ("rect", 14, 4, 4, 16)
    ],
    "cpu": [
        ("rect", 4, 4, 16, 16),
        ("rect", 9, 9, 6, 6),
        ("move", 9, 1), ("line", 9, 4),
        ("move", 15, 1), ("line", 15, 4),
        ("move", 9, 20), ("line", 9, 23),
        ("move", 15, 20), ("line", 15, 23)
    ],
    "zap": [
        ("move", 13, 2), ("line", 3, 14), ("line", 12, 14),
        ("line", 11, 22), ("line", 21, 10), ("line", 12, 10), ("close",)
    ],
}


class BuiltinIcon(Node):
    """
    High-performance vector icon component using the built-in icon registry.
    """

    def __init__(
        self,
        name: str = "sparkles",
        size: float = 32.0,
        color: Union[Color, str] = colors.INDIGO,
        stroke_width: float = 2.0,
        fill: bool = False,
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)
        # Handle "lucide:name" or "heroicons:name" prefixes
        clean_name = name.split(":")[-1].lower()
        self.icon_name = clean_name
        self.size_val = float(size)
        self.color = Color.from_any(color)
        self.stroke_width = float(stroke_width)
        self.fill_icon = fill
        self.scale_pulse = Signal(1.0, f"{self.name}.scale_pulse")

    def bounce(self, amplitude: float = 1.3, count: int = 2, duration: float = 0.8) -> AnimationAction:
        return self.scale_pulse.to(amplitude, duration=duration * 0.5, ease=Ease.out_back)

    def local_bounds(self, time: float = 0.0) -> Tuple[float, float, float, float]:
        return (0.0, 0.0, self.size_val, self.size_val)

    def draw(self, ctx: Any, time: float = 0.0) -> None:
        sz = self.size_val
        pulse = float(self.scale_pulse.get(time))

        ctx.save()
        if pulse != 1.0:
            ctx.translate(sz * 0.5, sz * 0.5)
            ctx.scale(pulse, pulse)
            ctx.translate(-sz * 0.5, -sz * 0.5)

        scale_factor = sz / 24.0
        ctx.scale(scale_factor, scale_factor)

        commands = ICON_REGISTRY.get(self.icon_name, ICON_REGISTRY["sparkles"])
        c = self.color
        ctx.set_source_rgba(c.r, c.g, c.b, c.a)
        ctx.set_line_width(self.stroke_width)
        ctx.set_line_cap(cairo.LINE_CAP_ROUND)
        ctx.set_line_join(cairo.LINE_JOIN_ROUND)

        for cmd in commands:
            op = cmd[0]
            if op == "move":
                ctx.move_to(cmd[1], cmd[2])
            elif op == "line":
                ctx.line_to(cmd[1], cmd[2])
            elif op == "close":
                ctx.close_path()
            elif op == "circle":
                ctx.arc(cmd[1], cmd[2], cmd[3], 0, math.pi * 2)
            elif op == "rect":
                ctx.rectangle(cmd[1], cmd[2], cmd[3], cmd[4])
            elif op == "arc_path":
                ctx.arc(cmd[1], cmd[2], cmd[3], cmd[4], cmd[5])

        if self.fill_icon:
            ctx.fill()
        else:
            ctx.stroke()

        ctx.restore()


# Short alias
Icon = BuiltinIcon
