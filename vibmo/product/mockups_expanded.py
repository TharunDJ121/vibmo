"""
Expanded hardware & device mockup frames (TabletFrame, LaptopFrame, WatchFrame, DesktopFrame) for product demos.
"""

from __future__ import annotations
import math
from typing import Any, Optional, Sequence, Tuple, Union
import cairo

from vibmo.core.color import Color, colors
from vibmo.core.vector import Vector2D
from vibmo.scene.node import Node
from vibmo.layout.container import FlexContainer
from vibmo.core.signal import Signal, AnimationAction
from vibmo.core.easing import Ease, EasingFunc
from vibmo.spatial.shadows import DropShadow


class TabletFrame(Node):
    """
    Modern Tablet device mockup (iPad / Surface Pro) with symmetrical slim bezels and screen slot.
    """

    def __init__(
        self,
        width: float = 720.0,
        height: float = 520.0,
        bezel_width: float = 16.0,
        corner_radius: float = 28.0,
        bezel_color: Optional[Union[Color, str]] = None,
        orientation: str = "landscape",
        shadow: Optional[Union[DropShadow, bool]] = True,
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)
        if orientation == "portrait" and width > height:
            width, height = height, width
        self.width_val = float(width)
        self.height_val = float(height)
        self.bezel_width = float(bezel_width)
        self.corner_radius = float(corner_radius)
        self.bezel_color = Color.from_any(bezel_color) if bezel_color else Color.hex("#111827")
        self.orientation = orientation

        if shadow is True:
            self.shadow = DropShadow.elevated(blur=40.0, offset=(0, 20), color=Color.BLACK.with_alpha(0.55))
        elif isinstance(shadow, DropShadow):
            self.shadow = shadow
        else:
            self.shadow = None

        inner_w = self.width_val - self.bezel_width * 2
        inner_h = self.height_val - self.bezel_width * 2
        self.screen = FlexContainer(
            direction="column",
            gap=16.0,
            padding=24.0,
            width=inner_w,
            height=inner_h,
            position=(self.bezel_width, self.bezel_width),
            fill=Color.hex("#090d16"),
            stroke=Color.TRANSPARENT,
            corner_radius=self.corner_radius - 8.0,
        )
        self.add(self.screen)

    def add_screen_content(self, *nodes: Node) -> TabletFrame:
        self.screen.add(*nodes)
        return self

    def local_bounds(self, time: float = 0.0) -> Tuple[float, float, float, float]:
        return (0.0, 0.0, self.width_val, self.height_val)

    def draw(self, ctx: Any, time: float = 0.0) -> None:
        w = self.width_val
        h = self.height_val
        cr = self.corner_radius

        ctx.save()
        # Outer body
        self._rounded_rect(ctx, 0, 0, w, h, cr)
        ctx.set_source_rgba(self.bezel_color.r, self.bezel_color.g, self.bezel_color.b, self.bezel_color.a)
        ctx.fill_preserve()
        ctx.set_source_rgba(1.0, 1.0, 1.0, 0.12)
        ctx.set_line_width(2.0)
        ctx.stroke()

        # Front Camera dot
        cam_x = w * 0.5 if self.orientation == "landscape" else self.bezel_width * 0.5
        cam_y = self.bezel_width * 0.5 if self.orientation == "landscape" else h * 0.5
        ctx.set_source_rgba(0.04, 0.06, 0.1, 1.0)
        ctx.arc(cam_x, cam_y, 4.0, 0, math.pi * 2)
        ctx.fill()
        ctx.set_source_rgba(0.2, 0.4, 0.8, 0.8)
        ctx.arc(cam_x, cam_y, 1.5, 0, math.pi * 2)
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


class LaptopFrame(Node):
    """
    MacBook / Modern Laptop device mockup with aluminum lid, notch/webcam, hinge, and bottom base deck.
    """

    def __init__(
        self,
        width: float = 960.0,
        height: float = 600.0,
        screen_ratio: float = 0.86,
        base_color: Optional[Union[Color, str]] = None,
        shadow: Optional[Union[DropShadow, bool]] = True,
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)
        self.width_val = float(width)
        self.height_val = float(height)
        self.screen_ratio = screen_ratio
        self.base_color = Color.from_any(base_color) if base_color else Color.hex("#1e293b")

        if shadow is True:
            self.shadow = DropShadow.elevated(blur=48.0, offset=(0, 24), color=Color.BLACK.with_alpha(0.6))
        elif isinstance(shadow, DropShadow):
            self.shadow = shadow
        else:
            self.shadow = None

        # Display lid dimensions
        self.lid_h = self.height_val * self.screen_ratio
        self.base_h = self.height_val - self.lid_h
        self.bezel = 14.0

        inner_w = self.width_val - self.bezel * 2
        inner_h = self.lid_h - self.bezel * 2
        self.screen = FlexContainer(
            direction="column",
            gap=16.0,
            padding=20.0,
            width=inner_w,
            height=inner_h,
            position=(self.bezel, self.bezel),
            fill=Color.hex("#090d16"),
            stroke=Color.TRANSPARENT,
            corner_radius=8.0,
        )
        self.add(self.screen)

    def add_screen_content(self, *nodes: Node) -> LaptopFrame:
        self.screen.add(*nodes)
        return self

    def local_bounds(self, time: float = 0.0) -> Tuple[float, float, float, float]:
        return (0.0, 0.0, self.width_val, self.height_val)

    def draw(self, ctx: Any, time: float = 0.0) -> None:
        w = self.width_val
        lid_h = self.lid_h
        base_h = self.base_h

        ctx.save()
        # 1. Screen Lid Frame
        self._rounded_rect(ctx, 0, 0, w, lid_h, 16.0)
        ctx.set_source_rgba(self.base_color.r, self.base_color.g, self.base_color.b, self.base_color.a)
        ctx.fill_preserve()
        ctx.set_source_rgba(1.0, 1.0, 1.0, 0.15)
        ctx.set_line_width(1.5)
        ctx.stroke()

        # Webcam dot
        ctx.set_source_rgba(0.04, 0.06, 0.1, 1.0)
        ctx.arc(w * 0.5, self.bezel * 0.5, 3.5, 0, math.pi * 2)
        ctx.fill()

        # 2. Bottom Laptop Base Deck & Hinge Lip
        base_y = lid_h
        base_w = w * 1.08
        base_x = (w - base_w) * 0.5

        # Aluminum base body
        self._rounded_rect(ctx, base_x, base_y, base_w, base_h, 6.0)
        base_grad = cairo.LinearGradient(0, base_y, 0, base_y + base_h)
        base_grad.add_color_stop_rgba(0.0, 0.25, 0.30, 0.40, 1.0)
        base_grad.add_color_stop_rgba(1.0, 0.12, 0.15, 0.22, 1.0)
        ctx.set_source(base_grad)
        ctx.fill_preserve()
        ctx.set_source_rgba(1.0, 1.0, 1.0, 0.2)
        ctx.set_line_width(1.0)
        ctx.stroke()

        # Center open notch thumb cut
        notch_w = 120.0
        notch_h = 6.0
        notch_x = (w - notch_w) * 0.5
        self._rounded_rect(ctx, notch_x, base_y, notch_w, notch_h, 3.0)
        ctx.set_source_rgba(0.08, 0.10, 0.15, 0.9)
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


class WatchFrame(Node):
    """
    Apple Watch / Smartwatch wearable mockup with squircle curved OLED display, Digital Crown, and side button.
    """

    def __init__(
        self,
        width: float = 320.0,
        height: float = 390.0,
        corner_radius: float = 64.0,
        case_color: Optional[Union[Color, str]] = None,
        shadow: Optional[Union[DropShadow, bool]] = True,
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)
        self.width_val = float(width)
        self.height_val = float(height)
        self.corner_radius = float(corner_radius)
        self.case_color = Color.from_any(case_color) if case_color else Color.hex("#18181b")

        if shadow is True:
            self.shadow = DropShadow.elevated(blur=36.0, offset=(0, 16), color=Color.BLACK.with_alpha(0.55))
        elif isinstance(shadow, DropShadow):
            self.shadow = shadow
        else:
            self.shadow = None

        bezel = 20.0
        inner_w = self.width_val - bezel * 2
        inner_h = self.height_val - bezel * 2
        self.screen = FlexContainer(
            direction="column",
            gap=10.0,
            padding=16.0,
            width=inner_w,
            height=inner_h,
            position=(bezel, bezel),
            fill=Color.BLACK,
            stroke=Color.TRANSPARENT,
            corner_radius=self.corner_radius - 14.0,
        )
        self.add(self.screen)

    def add_screen_content(self, *nodes: Node) -> WatchFrame:
        self.screen.add(*nodes)
        return self

    def local_bounds(self, time: float = 0.0) -> Tuple[float, float, float, float]:
        return (-14.0, 0.0, self.width_val + 24.0, self.height_val)

    def draw(self, ctx: Any, time: float = 0.0) -> None:
        w = self.width_val
        h = self.height_val
        cr = self.corner_radius

        ctx.save()
        # 1. Digital Crown on right
        crown_w = 10.0
        crown_h = 64.0
        crown_x = w
        crown_y = h * 0.28
        self._rounded_rect(ctx, crown_x, crown_y, crown_w, crown_h, 4.0)
        ctx.set_source_rgba(0.3, 0.35, 0.42, 1.0)
        ctx.fill()

        # Side button on right
        btn_w = 6.0
        btn_h = 48.0
        btn_x = w
        btn_y = h * 0.56
        self._rounded_rect(ctx, btn_x, btn_y, btn_w, btn_h, 3.0)
        ctx.set_source_rgba(0.2, 0.24, 0.30, 1.0)
        ctx.fill()

        # 2. Main Watch Case Body
        self._rounded_rect(ctx, 0, 0, w, h, cr)
        case_grad = cairo.LinearGradient(0, 0, w, h)
        case_grad.add_color_stop_rgba(0.0, 0.22, 0.25, 0.32, 1.0)
        case_grad.add_color_stop_rgba(1.0, 0.08, 0.10, 0.14, 1.0)
        ctx.set_source(case_grad)
        ctx.fill_preserve()
        ctx.set_source_rgba(1.0, 1.0, 1.0, 0.18)
        ctx.set_line_width(2.0)
        ctx.stroke()

        ctx.restore()

    def _rounded_rect(self, ctx: Any, x: float, y: float, w: float, h: float, r: float) -> None:
        r = min(r, w * 0.5, h * 0.5)
        ctx.new_path()
        ctx.arc(x + w - r, y + r, r, -math.pi * 0.5, 0)
        ctx.arc(x + w - r, y + h - r, r, 0, math.pi * 0.5)
        ctx.arc(x + r, y + h - r, r, math.pi * 0.5, math.pi)
        ctx.arc(x + r, y + r, r, math.pi, math.pi * 1.5)
        ctx.close_path()


class DesktopFrame(Node):
    """
    Studio Display / iMac desktop monitor mockup with ultra-thin bezels and aluminum stand.
    """

    def __init__(
        self,
        width: float = 1100.0,
        height: float = 720.0,
        stand_height: float = 120.0,
        bezel_color: Optional[Union[Color, str]] = None,
        shadow: Optional[Union[DropShadow, bool]] = True,
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)
        self.width_val = float(width)
        self.height_val = float(height)
        self.stand_h = float(stand_height)
        self.display_h = self.height_val - self.stand_h
        self.bezel_color = Color.from_any(bezel_color) if bezel_color else Color.hex("#0f172a")

        if shadow is True:
            self.shadow = DropShadow.elevated(blur=54.0, offset=(0, 28), color=Color.BLACK.with_alpha(0.65))
        elif isinstance(shadow, DropShadow):
            self.shadow = shadow
        else:
            self.shadow = None

        bezel = 14.0
        inner_w = self.width_val - bezel * 2
        inner_h = self.display_h - bezel * 2
        self.screen = FlexContainer(
            direction="column",
            gap=16.0,
            padding=24.0,
            width=inner_w,
            height=inner_h,
            position=(bezel, bezel),
            fill=Color.hex("#090d16"),
            stroke=Color.TRANSPARENT,
            corner_radius=12.0,
        )
        self.add(self.screen)

    def add_screen_content(self, *nodes: Node) -> DesktopFrame:
        self.screen.add(*nodes)
        return self

    def local_bounds(self, time: float = 0.0) -> Tuple[float, float, float, float]:
        return (0.0, 0.0, self.width_val, self.height_val)

    def draw(self, ctx: Any, time: float = 0.0) -> None:
        w = self.width_val
        dh = self.display_h

        ctx.save()
        # 1. Aluminum Stand Base & Neck
        stand_neck_w = 100.0
        stand_neck_x = (w - stand_neck_w) * 0.5
        stand_foot_w = 260.0
        stand_foot_h = 16.0
        stand_foot_x = (w - stand_foot_w) * 0.5
        stand_foot_y = self.height_val - stand_foot_h

        # Neck
        ctx.set_source_rgba(0.24, 0.28, 0.36, 1.0)
        ctx.rectangle(stand_neck_x, dh - 10.0, stand_neck_w, self.stand_h)
        ctx.fill()

        # Foot base
        self._rounded_rect(ctx, stand_foot_x, stand_foot_y, stand_foot_w, stand_foot_h, 8.0)
        ctx.set_source_rgba(0.32, 0.38, 0.48, 1.0)
        ctx.fill_preserve()
        ctx.set_source_rgba(1.0, 1.0, 1.0, 0.25)
        ctx.set_line_width(1.0)
        ctx.stroke()

        # 2. Main Monitor Body
        self._rounded_rect(ctx, 0, 0, w, dh, 20.0)
        ctx.set_source_rgba(self.bezel_color.r, self.bezel_color.g, self.bezel_color.b, self.bezel_color.a)
        ctx.fill_preserve()
        ctx.set_source_rgba(1.0, 1.0, 1.0, 0.15)
        ctx.set_line_width(2.0)
        ctx.stroke()

        # Center Studio Camera
        ctx.set_source_rgba(0.02, 0.03, 0.06, 1.0)
        ctx.arc(w * 0.5, 7.0, 3.5, 0, math.pi * 2)
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
