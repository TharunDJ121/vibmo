"""
Hardware mockups for Handheld Gaming Consoles.
"""

from __future__ import annotations
import math
from typing import Any, Tuple, Optional, Union
import cairo

from vibmo.scene.node import Node
from vibmo.layout.container import FlexContainer
from vibmo.core.color import Color

class ClippedScreenContainer(FlexContainer):
    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)

    def draw(self, ctx: Any, time: float = 0.0) -> None:
        self.compute_layout(time)
        ctx.save()
        self._build_path(ctx, time)
        ctx.clip()
        super().draw(ctx, time)
        ctx.restore()

class HandheldBase(Node):
    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)

    def _rounded_rect(self, ctx: Any, x: float, y: float, w: float, h: float, r: float) -> None:
        r = min(r, w * 0.5, h * 0.5)
        ctx.new_path()
        ctx.arc(x + w - r, y + r, r, -math.pi * 0.5, 0)
        ctx.arc(x + w - r, y + h - r, r, 0, math.pi * 0.5)
        ctx.arc(x + r, y + h - r, r, math.pi * 0.5, math.pi)
        ctx.arc(x + r, y + r, r, math.pi, math.pi * 1.5)
        ctx.close_path()

    def _draw_dpad(self, ctx: Any, cx: float, cy: float, size: float, color: Color) -> None:
        w = size * 0.33
        ctx.set_source_rgba(color.r, color.g, color.b, color.a)
        # Vertical bar
        self._rounded_rect(ctx, cx - w/2, cy - size/2, w, size, 2.0)
        ctx.fill()
        # Horizontal bar
        self._rounded_rect(ctx, cx - size/2, cy - w/2, size, w, 2.0)
        ctx.fill()

    def _draw_abxy(self, ctx: Any, cx: float, cy: float, spacing: float, radius: float, color: Color) -> None:
        ctx.set_source_rgba(color.r, color.g, color.b, color.a)
        for dx, dy in [(0, -spacing), (spacing, 0), (0, spacing), (-spacing, 0)]:
            ctx.arc(cx + dx, cy + dy, radius, 0, math.pi * 2)
            ctx.fill()

    def _draw_thumbstick(self, ctx: Any, cx: float, cy: float, radius: float, color: Color, inner_color: Color) -> None:
        ctx.set_source_rgba(color.r, color.g, color.b, color.a)
        ctx.arc(cx, cy, radius, 0, math.pi * 2)
        ctx.fill()
        ctx.set_source_rgba(inner_color.r, inner_color.g, inner_color.b, inner_color.a)
        ctx.arc(cx, cy, radius * 0.7, 0, math.pi * 2)
        ctx.fill()


class SteamDeckHandheldChassis(HandheldBase):
    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.width_val = 800.0
        self.height_val = 360.0
        self.screen_w = 520.0
        self.screen_h = 320.0
        self.corner_radius = 40.0

        self.screen_x = (self.width_val - self.screen_w) / 2
        self.screen_y = (self.height_val - self.screen_h) / 2

        self.screen = ClippedScreenContainer(
            direction="column",
            width=self.screen_w,
            height=self.screen_h,
            position=(self.screen_x, self.screen_y),
            fill=Color.hex("#090d16"),
            stroke=Color.TRANSPARENT,
            corner_radius=4.0,
        )
        self.add(self.screen)

    def add_screen_content(self, *nodes: Node) -> SteamDeckHandheldChassis:
        self.screen.add(*nodes)
        return self

    def draw(self, ctx: Any, time: float = 0.0) -> None:
        # Body
        self._rounded_rect(ctx, 0, 0, self.width_val, self.height_val, self.corner_radius)
        ctx.set_source_rgb(0.15, 0.15, 0.15)
        ctx.fill()

        # Grips styling
        ctx.save()
        self._rounded_rect(ctx, 10, 10, 120, self.height_val - 20, 30)
        self._rounded_rect(ctx, self.width_val - 130, 10, 120, self.height_val - 20, 30)
        ctx.set_source_rgb(0.12, 0.12, 0.12)
        ctx.fill()
        ctx.restore()

        # Left controls
        # Thumbstick
        self._draw_thumbstick(ctx, 70, 80, 25, Color.hex("#333"), Color.hex("#222"))
        # D-pad
        self._draw_dpad(ctx, 70, 180, 45, Color.hex("#444"))
        # Trackpad
        self._rounded_rect(ctx, 45, 240, 50, 50, 10)
        ctx.set_source_rgb(0.2, 0.2, 0.2)
        ctx.fill()

        # Right controls
        # ABXY
        self._draw_abxy(ctx, self.width_val - 70, 80, 20, 8, Color.hex("#444"))
        # Thumbstick
        self._draw_thumbstick(ctx, self.width_val - 70, 180, 25, Color.hex("#333"), Color.hex("#222"))
        # Trackpad
        self._rounded_rect(ctx, self.width_val - 95, 240, 50, 50, 10)
        ctx.set_source_rgb(0.2, 0.2, 0.2)
        ctx.fill()

        super().draw(ctx, time)


class SwitchJoyConFrame(HandheldBase):
    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.center_w = 560.0
        self.center_h = 320.0
        self.joycon_w = 90.0
        self.joycon_h = self.center_h

        self.width_val = self.joycon_w * 2 + self.center_w
        self.height_val = self.center_h

        self.screen_w = self.center_w - 40.0
        self.screen_h = self.center_h - 40.0
        self.screen_x = self.joycon_w + 20.0
        self.screen_y = 20.0

        self.screen = ClippedScreenContainer(
            direction="column",
            width=self.screen_w,
            height=self.screen_h,
            position=(self.screen_x, self.screen_y),
            fill=Color.hex("#000000"),
            stroke=Color.TRANSPARENT,
            corner_radius=10.0,
        )
        self.add(self.screen)

    def add_screen_content(self, *nodes: Node) -> SwitchJoyConFrame:
        self.screen.add(*nodes)
        return self

    def draw(self, ctx: Any, time: float = 0.0) -> None:
        # Left Joy-Con (Neon Blue)
        self._rounded_rect(ctx, 0, 0, self.joycon_w, self.joycon_h, 30.0)
        ctx.set_source_rgb(0.0, 0.8, 1.0) # Neon blue
        ctx.fill()

        # Center Body
        self._rounded_rect(ctx, self.joycon_w, 0, self.center_w, self.center_h, 5.0)
        ctx.set_source_rgb(0.2, 0.2, 0.2)
        ctx.fill()

        # Right Joy-Con (Neon Red)
        self._rounded_rect(ctx, self.joycon_w + self.center_w, 0, self.joycon_w, self.joycon_h, 30.0)
        ctx.set_source_rgb(1.0, 0.2, 0.2) # Neon red
        ctx.fill()

        # Left Controls
        self._draw_thumbstick(ctx, self.joycon_w / 2, 80, 20, Color.hex("#333"), Color.hex("#222"))
        # D-pad (buttons style for Joy-Con)
        self._draw_abxy(ctx, self.joycon_w / 2, 170, 15, 6, Color.hex("#333"))

        # Right Controls
        self._draw_abxy(ctx, self.width_val - self.joycon_w / 2, 80, 15, 6, Color.hex("#333"))
        self._draw_thumbstick(ctx, self.width_val - self.joycon_w / 2, 170, 20, Color.hex("#333"), Color.hex("#222"))

        super().draw(ctx, time)


class RetroGameBoyEnclosure(HandheldBase):
    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.width_val = 300.0
        self.height_val = 500.0

        self.screen_w = 200.0
        self.screen_h = 180.0
        self.screen_x = (self.width_val - self.screen_w) / 2
        self.screen_y = 50.0

        self.screen = ClippedScreenContainer(
            direction="column",
            width=self.screen_w,
            height=self.screen_h,
            position=(self.screen_x, self.screen_y),
            fill=Color.hex("#8b956d"), # Classic dot-matrix green
            stroke=Color.TRANSPARENT,
            corner_radius=5.0,
        )
        self.add(self.screen)

    def add_screen_content(self, *nodes: Node) -> RetroGameBoyEnclosure:
        self.screen.add(*nodes)
        return self

    def draw(self, ctx: Any, time: float = 0.0) -> None:
        # Body
        self._rounded_rect(ctx, 0, 0, self.width_val, self.height_val, 15.0)
        ctx.set_source_rgb(0.85, 0.85, 0.85) # Off-white/gray
        ctx.fill()

        # Screen Bezel
        self._rounded_rect(ctx, 30, 30, self.width_val - 60, 230, 10.0)
        ctx.set_source_rgb(0.3, 0.3, 0.3)
        ctx.fill()

        # D-pad
        self._draw_dpad(ctx, 80, 350, 60, Color.hex("#111"))

        # A/B Buttons (Purple/Magenta)
        ctx.save()
        ctx.set_source_rgb(0.6, 0.1, 0.4) # Classic purple
        ctx.arc(220, 370, 15, 0, math.pi * 2)
        ctx.fill()
        ctx.arc(260, 340, 15, 0, math.pi * 2)
        ctx.fill()
        ctx.restore()

        # Select / Start
        ctx.save()
        ctx.translate(130, 430)
        ctx.rotate(-math.pi / 8)
        self._rounded_rect(ctx, 0, 0, 30, 10, 5)
        ctx.set_source_rgb(0.4, 0.4, 0.4)
        ctx.fill()
        ctx.restore()

        ctx.save()
        ctx.translate(170, 430)
        ctx.rotate(-math.pi / 8)
        self._rounded_rect(ctx, 0, 0, 30, 10, 5)
        ctx.set_source_rgb(0.4, 0.4, 0.4)
        ctx.fill()
        ctx.restore()

        super().draw(ctx, time)
