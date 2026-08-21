import math
from typing import Any, Tuple, Optional, Union
import cairo

from vibmo.scene.node import Node
from vibmo.layout.container import FlexContainer
from vibmo.core.color import Color
from vibmo.spatial.shadows import DropShadow

class WallMountedDisplayShadow(Node):
    """Deep soft ambient wall-cast drop shadow for wall-mounted TV demos."""
    def __init__(self, width: float, height: float, elevation: float = 30.0, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.width_val = float(width)
        self.height_val = float(height)
        self.elevation = float(elevation)

    def draw(self, ctx: Any, time: float = 0.0) -> None:
        # Drawing just an ambient shadow for the TV frame.
        # For Cairo, we typically use DropShadow if possible or draw manually
        # A simple fake shadow with a couple of rects
        w = self.width_val
        h = self.height_val

        ctx.save()

        shadow_y_offset = self.elevation
        blur_radius = self.elevation * 1.5
        shadow_spread = blur_radius * 0.5

        shadow = DropShadow(
            blur=blur_radius,
            offset=(0, shadow_y_offset),
            color=Color.BLACK.with_alpha(0.6)
        )

        # We can utilize DropShadow.render_shadow here.
        # It takes (x, y, w, h) bounds.
        shadow.render_shadow(ctx, (0, 0, w, h), 0)

        ctx.restore()

class FloatingTvStand(Node):
    """Minimalist metallic desktop pedestal stand."""
    def __init__(self, width: float = 300.0, height: float = 80.0, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.width_val = float(width)
        self.height_val = float(height)

    def draw(self, ctx: Any, time: float = 0.0) -> None:
        w = self.width_val
        h = self.height_val

        ctx.save()

        # Base plate
        base_h = 10.0
        base_w = w
        ctx.set_source_rgba(0.7, 0.7, 0.75, 1.0) # metallic silver
        self._rounded_rect(ctx, 0, h - base_h, base_w, base_h, 4.0)
        ctx.fill_preserve()
        ctx.set_source_rgba(0.9, 0.9, 0.95, 1.0)
        ctx.set_line_width(1.0)
        ctx.stroke()

        # Vertical pedestal
        ped_w = 80.0
        ped_h = h - base_h
        ped_x = (w - ped_w) * 0.5
        ctx.set_source_rgba(0.6, 0.6, 0.65, 1.0)
        ctx.rectangle(ped_x, 0, ped_w, ped_h)
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

class OledSmartTvFrame(Node):
    """65-inch ultra-thin razor bezel TV with aluminum bottom lip and status indicator LED."""

    def __init__(
        self,
        width: float = 1280.0,
        bezel_width: float = 6.0,
        bottom_lip_height: float = 24.0,
        **kwargs: Any
    ) -> None:
        super().__init__(**kwargs)

        self.width_val = float(width)
        # 16:9 aspect ratio enforced
        self.height_val = self.width_val * (9.0 / 16.0)

        self.bezel_width = float(bezel_width)
        self.bottom_lip_height = float(bottom_lip_height)

        inner_w = self.width_val - (self.bezel_width * 2)
        inner_h = self.height_val - self.bezel_width - self.bottom_lip_height

        # Content container
        self.screen = FlexContainer(
            direction="column",
            gap=0.0,
            padding=0.0,
            width=inner_w,
            height=inner_h,
            position=(self.bezel_width, self.bezel_width),
            fill=Color.hex("#000000"),
            stroke=Color.TRANSPARENT,
        )
        self.add(self.screen)

    def add_screen_content(self, *nodes: Node) -> 'OledSmartTvFrame':
        self.screen.add(*nodes)
        return self

    def draw(self, ctx: Any, time: float = 0.0) -> None:
        w = self.width_val
        h = self.height_val

        ctx.save()

        # Outer bezel
        ctx.set_source_rgba(0.05, 0.05, 0.05, 1.0)
        ctx.rectangle(0, 0, w, h)
        ctx.fill()

        # Bottom aluminum lip
        ctx.set_source_rgba(0.5, 0.5, 0.55, 1.0)
        lip_y = h - self.bottom_lip_height
        ctx.rectangle(0, lip_y, w, self.bottom_lip_height)
        ctx.fill()

        # LED indicator on the bottom lip
        led_x = w * 0.5
        led_y = lip_y + (self.bottom_lip_height * 0.5)

        # White glowing LED
        ctx.set_source_rgba(1.0, 1.0, 1.0, 0.8)
        ctx.arc(led_x, led_y, 2.0, 0, math.pi * 2)
        ctx.fill()

        ctx.restore()

class CurvedCinemaDisplay(Node):
    """Wide curved display with subtle panoramic edge compression."""

    def __init__(
        self,
        width: float = 1440.0,
        height: float = 600.0,
        bezel_width: float = 12.0,
        curve_depth: float = 30.0,
        **kwargs: Any
    ) -> None:
        super().__init__(**kwargs)
        self.width_val = float(width)
        self.height_val = float(height)
        self.bezel_width = float(bezel_width)
        self.curve_depth = float(curve_depth)

        # Screen area
        inner_w = self.width_val - (self.bezel_width * 2)
        inner_h = self.height_val - (self.bezel_width * 2)

        self.screen = FlexContainer(
            direction="column",
            gap=0.0,
            padding=0.0,
            width=inner_w,
            height=inner_h,
            position=(self.bezel_width, self.bezel_width),
            fill=Color.hex("#050505"),
            stroke=Color.TRANSPARENT,
        )
        self.add(self.screen)

    def add_screen_content(self, *nodes: Node) -> 'CurvedCinemaDisplay':
        self.screen.add(*nodes)
        return self

    def draw(self, ctx: Any, time: float = 0.0) -> None:
        w = self.width_val
        h = self.height_val

        ctx.save()

        # Top curve and bottom curve paths
        # Curved display has subtle panoramic edge compression
        # We can draw it as a curved polygon

        ctx.set_source_rgba(0.1, 0.1, 0.1, 1.0)

        # Top curve
        ctx.move_to(0, 0)
        ctx.curve_to(w * 0.33, self.curve_depth, w * 0.66, self.curve_depth, w, 0)

        # Right edge
        ctx.line_to(w, h)

        # Bottom curve
        ctx.curve_to(w * 0.66, h + self.curve_depth, w * 0.33, h + self.curve_depth, 0, h)

        # Left edge
        ctx.line_to(0, 0)

        ctx.fill()

        # Optional: gradient/gleam simulating curvature
        gleam = cairo.LinearGradient(0, 0, w, 0)
        gleam.add_color_stop_rgba(0.0, 1.0, 1.0, 1.0, 0.05)
        gleam.add_color_stop_rgba(0.1, 1.0, 1.0, 1.0, 0.15)
        gleam.add_color_stop_rgba(0.5, 1.0, 1.0, 1.0, 0.0)
        gleam.add_color_stop_rgba(0.9, 1.0, 1.0, 1.0, 0.15)
        gleam.add_color_stop_rgba(1.0, 1.0, 1.0, 1.0, 0.05)

        # Clip to the curved shape to apply the gradient
        ctx.move_to(0, 0)
        ctx.curve_to(w * 0.33, self.curve_depth, w * 0.66, self.curve_depth, w, 0)
        ctx.line_to(w, h)
        ctx.curve_to(w * 0.66, h + self.curve_depth, w * 0.33, h + self.curve_depth, 0, h)
        ctx.line_to(0, 0)

        ctx.clip()

        ctx.set_source(gleam)
        ctx.paint()

        ctx.restore()
