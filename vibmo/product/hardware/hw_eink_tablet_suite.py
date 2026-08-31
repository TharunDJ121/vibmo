from __future__ import annotations
import math
import random
from typing import Any, Optional, Tuple, Union

import numpy as np
import cairo

from vibmo.scene.node import Node
from vibmo.core.color import Color
from vibmo.core.signal import Signal
from vibmo.layout.container import FlexContainer
from vibmo.spatial.shadows import DropShadow


class MinimalistEInkTabletFrame(Node):
    """
    ReMarkable / Kindle Scribe style paper-like e-ink digital notepad.
    Features a wide left leather grip bezel, textured off-white screen,
    and auto-clipped screen viewport.
    """
    def __init__(
        self,
        width: float = 600.0,
        height: float = 800.0,
        corner_radius: float = 16.0,
        grip_width: float = 80.0,
        bezel_width: float = 12.0,
        shadow: Optional[Union[DropShadow, bool]] = True,
        **kwargs: Any
    ) -> None:
        super().__init__(**kwargs)
        self.width = float(width)
        self.height = float(height)

        self.corner_radius = float(corner_radius)
        self.grip_width = float(grip_width)
        self.bezel_width = float(bezel_width)

        self.screen_x = self.grip_width
        self.screen_y = self.bezel_width
        self.screen_width = self.width - self.grip_width - self.bezel_width
        self.screen_height = self.height - (2 * self.bezel_width)

        if shadow is True:
            self.shadow = DropShadow.elevated(blur=32.0, offset=(0, 16), color=Color.BLACK.with_alpha(0.40))
        elif isinstance(shadow, DropShadow):
            self.shadow = shadow
        else:
            self.shadow = None

        self.screen = FlexContainer(
            direction="column",
            gap=8.0,
            padding=16.0,
            width=self.screen_width,
            height=self.screen_height,
            position=(self.screen_x, self.screen_y),
            fill=Color.hex("#F2F2F2"),
            stroke=Color.TRANSPARENT,
            corner_radius=4.0,
        )
        self.add(self.screen)

    def add_screen(self, *nodes: Node) -> MinimalistEInkTabletFrame:
        """Add child nodes to the e-ink screen viewport."""
        self.screen.add(*nodes)
        return self

    def add_screen_content(self, *nodes: Node) -> MinimalistEInkTabletFrame:
        """Alias for add_screen."""
        return self.add_screen(*nodes)

    def draw(self, ctx: Any, time: float = 0.0) -> None:
        ctx.save()

        w, h = self.width, self.height
        r = self.corner_radius

        # Drop shadow (only with surface support)
        if self.shadow is not None and hasattr(ctx, "set_source_surface"):
            self.shadow.render_shadow(ctx, (0, 0, w, h), r)

        # 1. Outer Chassis / Bezel Background
        chassis_color = Color.hex("#2C2C2E")
        ctx.set_source_rgba(chassis_color.r, chassis_color.g, chassis_color.b, self.world_opacity(time))

        ctx.new_path()
        ctx.arc(r, r, r, math.pi, 1.5 * math.pi)
        ctx.arc(w - r, r, r, 1.5 * math.pi, 2 * math.pi)
        ctx.arc(w - r, h - r, r, 0, 0.5 * math.pi)
        ctx.arc(r, h - r, r, 0.5 * math.pi, math.pi)
        ctx.close_path()
        ctx.fill()

        # 2. Leather Grip detail (left side)
        ctx.set_source_rgba(0.0, 0.0, 0.0, 0.2 * self.world_opacity(time))
        for i in range(5):
            y_pos = (h / 6) * (i + 1)
            ctx.move_to(self.grip_width * 0.2, y_pos)
            ctx.line_to(self.grip_width * 0.8, y_pos)
            ctx.set_line_width(1.5)
            ctx.stroke()

        # 3. Inner Screen Area (Paper-like white)
        screen_bg = Color.hex("#F2F2F2")
        ctx.set_source_rgba(screen_bg.r, screen_bg.g, screen_bg.b, self.world_opacity(time))

        sx, sy, sw, sh = self.screen_x, self.screen_y, self.screen_width, self.screen_height
        sr = 4.0
        ctx.new_path()
        ctx.arc(sx + sr, sy + sr, sr, math.pi, 1.5 * math.pi)
        ctx.arc(sx + sw - sr, sy + sr, sr, 1.5 * math.pi, 2 * math.pi)
        ctx.arc(sx + sw - sr, sy + sh - sr, sr, 0, 0.5 * math.pi)
        ctx.arc(sx + sr, sy + sh - sr, sr, 0.5 * math.pi, math.pi)
        ctx.close_path()
        ctx.fill()

        # Screen inner shadow / depth
        ctx.set_source_rgba(0.0, 0.0, 0.0, 0.1 * self.world_opacity(time))
        ctx.set_line_width(2.0)
        ctx.stroke()

        ctx.restore()

    def local_bounds(self, time: float = 0.0) -> Tuple[float, float, float, float]:
        return (0.0, 0.0, self.width, self.height)


# Semantic alias
PaperEInkReaderFrame = MinimalistEInkTabletFrame


class StylusPenMockup(Node):
    """
    Precision digital stylus pen magnetically docked to side bezel.
    """
    def __init__(self, length: float = 140.0, radius: float = 4.0, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.length = float(length)
        self.radius = float(radius)
        self.body_color = Color.hex("#E5E5EA")
        self.tip_color = Color.hex("#3A3A3C")
        self.accent_color = Color.hex("#C7C7CC")

    def draw(self, ctx: Any, time: float = 0.0) -> None:
        ctx.save()
        l, r = self.length, self.radius
        op = self.world_opacity(time)

        # 1. Main cylindrical body
        ctx.set_source_rgba(self.body_color.r, self.body_color.g, self.body_color.b, op)
        ctx.new_path()
        ctx.arc(r, r, r, math.pi, 0)
        ctx.line_to(2 * r, l - 15.0)
        ctx.line_to(0, l - 15.0)
        ctx.close_path()
        ctx.fill()

        # Highlight
        ctx.set_source_rgba(1.0, 1.0, 1.0, 0.5 * op)
        ctx.move_to(r * 0.5, r)
        ctx.line_to(r * 0.5, l - 15.0)
        ctx.set_line_width(r * 0.8)
        ctx.stroke()

        # 2. Pen tip cone
        ctx.set_source_rgba(self.tip_color.r, self.tip_color.g, self.tip_color.b, op)
        ctx.move_to(0, l - 15.0)
        ctx.line_to(2 * r, l - 15.0)
        ctx.line_to(r + 0.5, l - 2.0)
        ctx.line_to(r - 0.5, l - 2.0)
        ctx.close_path()
        ctx.fill()

        # 3. Fine nib
        ctx.set_source_rgba(0.1, 0.1, 0.1, op)
        ctx.move_to(r - 0.5, l - 2.0)
        ctx.line_to(r + 0.5, l - 2.0)
        ctx.line_to(r + 0.2, l)
        ctx.line_to(r - 0.2, l)
        ctx.close_path()
        ctx.fill()

        # 4. Magnetic flat side / accent band
        ctx.set_source_rgba(self.accent_color.r, self.accent_color.g, self.accent_color.b, op)
        ctx.move_to(0, r * 3)
        ctx.line_to(2 * r, r * 3)
        ctx.set_line_width(2.0)
        ctx.stroke()

        ctx.restore()

    def local_bounds(self, time: float = 0.0) -> Tuple[float, float, float, float]:
        return (0.0, 0.0, self.radius * 2, self.length)


class TextureMatteScreenBezel(Node):
    """
    Subtle paper tooth grain texture and low-contrast e-ink refresh artifact simulator.
    """
    def __init__(self, width: float, height: float, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.width = float(width)
        self.height = float(height)
        self.refresh_progress = Signal(0.0, name=f"{self.name}.refresh_progress")
        self.base_color = Color.hex("#F2F2F2")

    def draw(self, ctx: Any, time: float = 0.0) -> None:
        ctx.save()
        op = self.world_opacity(time)

        rng = random.Random(42)

        ctx.set_source_rgba(self.base_color.r, self.base_color.g, self.base_color.b, op)
        ctx.rectangle(0, 0, self.width, self.height)
        ctx.fill()

        ctx.set_source_rgba(0.0, 0.0, 0.0, 0.02 * op)
        ctx.set_line_width(1.0)

        step = 4.0
        for y in np.arange(0, self.height, step):
            for x in np.arange(0, self.width, step):
                if rng.random() > 0.5:
                    ctx.rectangle(x, y, 1, 1)
        ctx.fill()

        refresh = self.refresh_progress.get(time)
        if refresh > 0.0 and refresh < 1.0:
            if refresh < 0.3:
                intensity = refresh / 0.3
                ctx.set_source_rgba(0.1, 0.1, 0.1, intensity * 0.8 * op)
                ctx.rectangle(0, 0, self.width, self.height)
                ctx.fill()
            elif refresh < 0.6:
                intensity = (refresh - 0.3) / 0.3
                ctx.set_source_rgba(0.95, 0.95, 0.95, intensity * 0.9 * op)
                ctx.rectangle(0, 0, self.width, self.height)
                ctx.fill()
            else:
                intensity = 1.0 - ((refresh - 0.6) / 0.4)
                ctx.set_source_rgba(0.0, 0.0, 0.0, intensity * 0.1 * op)

                dyn_rng = random.Random(int(time * 10))
                for _ in range(5):
                    gy = dyn_rng.uniform(0, self.height)
                    gh = dyn_rng.uniform(10, 50)
                    ctx.rectangle(0, gy, self.width, gh)
                ctx.fill()

        ctx.restore()

    def local_bounds(self, time: float = 0.0) -> Tuple[float, float, float, float]:
        return (0.0, 0.0, self.width, self.height)


class EInkTabletSuite:
    """
    Suite factory for paper-like e-ink tablets, styluses, and matte screen textures.
    """
    @staticmethod
    def tablet(**kwargs: Any) -> MinimalistEInkTabletFrame:
        return MinimalistEInkTabletFrame(**kwargs)

    @staticmethod
    def stylus(**kwargs: Any) -> StylusPenMockup:
        return StylusPenMockup(**kwargs)

    @staticmethod
    def matte_texture(width: float, height: float, **kwargs: Any) -> TextureMatteScreenBezel:
        return TextureMatteScreenBezel(width=width, height=height, **kwargs)
