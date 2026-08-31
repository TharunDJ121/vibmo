from __future__ import annotations
import math
from typing import Any, Optional, Tuple, Union

import cairo

from vibmo.core.color import Color
from vibmo.core.signal import Signal
from vibmo.scene.node import Node
from vibmo.layout.container import FlexContainer
from vibmo.spatial.shadows import DropShadow


def _rounded_rect(ctx: Any, x: float, y: float, w: float, h: float, r: float) -> None:
    r = min(r, w * 0.5, h * 0.5)
    if r <= 0:
        ctx.rectangle(x, y, w, h)
        return
    ctx.new_path()
    ctx.arc(x + w - r, y + r, r, -math.pi * 0.5, 0)
    ctx.arc(x + w - r, y + h - r, r, 0, math.pi * 0.5)
    ctx.arc(x + r, y + h - r, r, math.pi * 0.5, math.pi)
    ctx.arc(x + r, y + r, r, math.pi, math.pi * 1.5)
    ctx.close_path()


class FoldableDeviceFrame(Node):
    """
    Next-generation foldable smartphone chassis with dynamic folding angle,
    subtle crease shading, specular rim, and auto-clipped screen viewport.
    """
    def __init__(
        self,
        width: float = 600.0,
        height: float = 500.0,
        fold_angle: float = 0.0,
        bezel_width: float = 12.0,
        corner_radius: float = 32.0,
        bezel_color: Optional[Union[Color, str]] = None,
        shadow: Optional[Union[DropShadow, bool]] = True,
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)
        self.width_val = float(width)
        self.height_val = float(height)
        self.fold_angle = Signal(float(fold_angle), name=f"{self.name}.fold_angle")
        self.bezel_width = float(bezel_width)
        self.corner_radius = float(corner_radius)
        self.bezel_color = Color.from_any(bezel_color) if bezel_color else Color.hex("#1e293b")

        if shadow is True:
            self.shadow = DropShadow.elevated(blur=36.0, offset=(0, 18), color=Color.BLACK.with_alpha(0.50))
        elif isinstance(shadow, DropShadow):
            self.shadow = shadow
        else:
            self.shadow = None

        inner_w = self.width_val - self.bezel_width * 2
        inner_h = self.height_val - self.bezel_width * 2
        self.screen = FlexContainer(
            direction="row",
            gap=0.0,
            padding=0.0,
            width=inner_w,
            height=inner_h,
            position=(self.bezel_width, self.bezel_width),
            fill=Color.hex("#090d16"),
            stroke=Color.TRANSPARENT,
            corner_radius=max(0.0, self.corner_radius - 8.0),
        )
        self.add(self.screen)

    def add_screen(self, *nodes: Node) -> FoldableDeviceFrame:
        """Add child nodes to the auto-clipped screen viewport."""
        self.screen.add(*nodes)
        return self

    def add_screen_content(self, *nodes: Node) -> FoldableDeviceFrame:
        """Alias for add_screen."""
        return self.add_screen(*nodes)

    def local_bounds(self, time: float = 0.0) -> Tuple[float, float, float, float]:
        return (0.0, 0.0, self.width_val, self.height_val)

    def draw(self, ctx: Any, time: float = 0.0) -> None:
        w = self.width_val
        h = self.height_val
        cr = self.corner_radius
        angle = self.fold_angle.get(time)

        ctx.save()

        # 1. Subtle drop shadow
        if self.shadow is not None and hasattr(ctx, "set_source_surface"):
            self.shadow.render_shadow(ctx, (0, 0, w, h), cr)

        # 2. Outer chassis & bezel
        _rounded_rect(ctx, 0, 0, w, h, cr)
        ctx.set_source_rgba(self.bezel_color.r, self.bezel_color.g, self.bezel_color.b, self.bezel_color.a)
        ctx.fill_preserve()

        # 3. Specular rim highlight
        ctx.set_source_rgba(1.0, 1.0, 1.0, 0.18)
        ctx.set_line_width(2.0)
        ctx.stroke()

        # 4. Center crease gradient & fold perspective shadow
        crease_x = w * 0.5
        fold_intensity = min(1.0, 0.2 + (abs(angle) / 90.0) * 0.5)

        ctx.save()
        _rounded_rect(
            ctx,
            self.bezel_width,
            self.bezel_width,
            w - self.bezel_width * 2,
            h - self.bezel_width * 2,
            max(0.0, cr - 8.0),
        )
        ctx.clip()

        if hasattr(cairo, "LinearGradient") and hasattr(ctx, "set_source"):
            try:
                crease_w = 40.0 + (abs(angle) / 90.0) * 20.0
                pat = cairo.LinearGradient(crease_x - crease_w * 0.5, 0, crease_x + crease_w * 0.5, 0)
                pat.add_color_stop_rgba(0.0, 0, 0, 0, 0.0)
                pat.add_color_stop_rgba(0.48, 0, 0, 0, fold_intensity * 0.8)
                pat.add_color_stop_rgba(0.50, 1, 1, 1, 0.10)
                pat.add_color_stop_rgba(0.52, 0, 0, 0, fold_intensity * 0.8)
                pat.add_color_stop_rgba(1.0, 0, 0, 0, 0.0)

                ctx.set_source(pat)
                ctx.rectangle(crease_x - crease_w * 0.5, self.bezel_width, crease_w, h - self.bezel_width * 2)
                ctx.fill()
            except Exception:
                pass
        ctx.restore()

        ctx.restore()


# Semantic alias
FoldableBookPhone = FoldableDeviceFrame


class ClamshellFlipPhone(Node):
    """
    Vertical folding clamshell smartphone with top and bottom display zones.
    """
    def __init__(
        self,
        width: float = 380.0,
        height: float = 780.0,
        fold_angle: float = 0.0,
        bezel_width: float = 12.0,
        corner_radius: float = 48.0,
        bezel_color: Optional[Union[Color, str]] = None,
        shadow: Optional[Union[DropShadow, bool]] = True,
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)
        self.width_val = float(width)
        self.height_val = float(height)
        self.fold_angle = Signal(float(fold_angle), name=f"{self.name}.fold_angle")
        self.bezel_width = float(bezel_width)
        self.corner_radius = float(corner_radius)
        self.bezel_color = Color.from_any(bezel_color) if bezel_color else Color.hex("#1e293b")

        if shadow is True:
            self.shadow = DropShadow.elevated(blur=36.0, offset=(0, 18), color=Color.BLACK.with_alpha(0.50))
        elif isinstance(shadow, DropShadow):
            self.shadow = shadow
        else:
            self.shadow = None

        inner_w = self.width_val - self.bezel_width * 2
        inner_h = self.height_val - self.bezel_width * 2

        self.screen_top = FlexContainer(
            direction="column",
            gap=0.0,
            padding=0.0,
            width=inner_w,
            height=inner_h * 0.5,
            position=(self.bezel_width, self.bezel_width),
            fill=Color.hex("#090d16"),
            stroke=Color.TRANSPARENT,
            corner_radius=max(0.0, self.corner_radius - 8.0),
        )
        self.add(self.screen_top)

        self.screen_bottom = FlexContainer(
            direction="column",
            gap=0.0,
            padding=0.0,
            width=inner_w,
            height=inner_h * 0.5,
            position=(self.bezel_width, self.bezel_width + inner_h * 0.5),
            fill=Color.hex("#090d16"),
            stroke=Color.TRANSPARENT,
            corner_radius=max(0.0, self.corner_radius - 8.0),
        )
        self.add(self.screen_bottom)
        self.screen = self.screen_top

    def add_screen(self, *nodes: Node) -> ClamshellFlipPhone:
        """Add nodes to the top screen by default."""
        for node in nodes:
            self.screen_top.add(node)
        return self

    def add_screen_content(self, *nodes: Node) -> ClamshellFlipPhone:
        """Alias for add_screen."""
        return self.add_screen(*nodes)

    def local_bounds(self, time: float = 0.0) -> Tuple[float, float, float, float]:
        return (0.0, 0.0, self.width_val, self.height_val)

    def draw(self, ctx: Any, time: float = 0.0) -> None:
        w = self.width_val
        h = self.height_val
        cr = self.corner_radius
        angle = self.fold_angle.get(time)

        ctx.save()

        if self.shadow is not None and hasattr(ctx, "set_source_surface"):
            self.shadow.render_shadow(ctx, (0, 0, w, h), cr)

        _rounded_rect(ctx, 0, 0, w, h, cr)
        ctx.set_source_rgba(self.bezel_color.r, self.bezel_color.g, self.bezel_color.b, self.bezel_color.a)
        ctx.fill_preserve()
        ctx.set_source_rgba(1.0, 1.0, 1.0, 0.15)
        ctx.set_line_width(2.0)
        ctx.stroke()

        crease_y = h * 0.5

        ctx.save()
        _rounded_rect(
            ctx,
            self.bezel_width,
            self.bezel_width,
            w - self.bezel_width * 2,
            h - self.bezel_width * 2,
            max(0.0, cr - 8.0),
        )
        ctx.clip()

        if hasattr(cairo, "LinearGradient") and hasattr(ctx, "set_source"):
            try:
                fold_intensity = min(1.0, 0.2 + (abs(angle) / 90.0) * 0.5)
                crease_h = 40.0
                pat = cairo.LinearGradient(0, crease_y - crease_h * 0.5, 0, crease_y + crease_h * 0.5)
                pat.add_color_stop_rgba(0.0, 0, 0, 0, 0.0)
                pat.add_color_stop_rgba(0.48, 0, 0, 0, fold_intensity * 0.8)
                pat.add_color_stop_rgba(0.50, 1, 1, 1, 0.10)
                pat.add_color_stop_rgba(0.52, 0, 0, 0, fold_intensity * 0.8)
                pat.add_color_stop_rgba(1.0, 0, 0, 0, 0.0)

                ctx.set_source(pat)
                ctx.rectangle(self.bezel_width, crease_y - crease_h * 0.5, w - self.bezel_width * 2, crease_h)
                ctx.fill()
            except Exception:
                pass
        ctx.restore()

        ctx.restore()


class DualScreenBookDevice(Node):
    """
    Dual independent display folding tablet / book device connected with an engineered hinge.
    """
    def __init__(
        self,
        width: float = 800.0,
        height: float = 500.0,
        fold_angle: float = 0.0,
        bezel_width: float = 12.0,
        corner_radius: float = 24.0,
        bezel_color: Optional[Union[Color, str]] = None,
        shadow: Optional[Union[DropShadow, bool]] = True,
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)
        self.width_val = float(width)
        self.height_val = float(height)
        self.fold_angle = Signal(float(fold_angle), name=f"{self.name}.fold_angle")
        self.bezel_width = float(bezel_width)
        self.corner_radius = float(corner_radius)
        self.bezel_color = Color.from_any(bezel_color) if bezel_color else Color.hex("#1e293b")

        if shadow is True:
            self.shadow = DropShadow.elevated(blur=36.0, offset=(0, 18), color=Color.BLACK.with_alpha(0.50))
        elif isinstance(shadow, DropShadow):
            self.shadow = shadow
        else:
            self.shadow = None

        self.hinge_width = 16.0
        panel_w = (self.width_val - self.hinge_width) * 0.5

        inner_w = panel_w - self.bezel_width * 2
        inner_h = self.height_val - self.bezel_width * 2

        self.screen_left = FlexContainer(
            direction="column",
            gap=0.0,
            padding=0.0,
            width=inner_w,
            height=inner_h,
            position=(self.bezel_width, self.bezel_width),
            fill=Color.hex("#090d16"),
            stroke=Color.TRANSPARENT,
            corner_radius=max(0.0, self.corner_radius - 8.0),
        )
        self.add(self.screen_left)

        self.screen_right = FlexContainer(
            direction="column",
            gap=0.0,
            padding=0.0,
            width=inner_w,
            height=inner_h,
            position=(panel_w + self.hinge_width + self.bezel_width, self.bezel_width),
            fill=Color.hex("#090d16"),
            stroke=Color.TRANSPARENT,
            corner_radius=max(0.0, self.corner_radius - 8.0),
        )
        self.add(self.screen_right)
        self.screen = self.screen_left

    def add_screen(self, *nodes: Node) -> DualScreenBookDevice:
        """Add nodes to the left screen by default."""
        for node in nodes:
            self.screen_left.add(node)
        return self

    def add_screen_content(self, *nodes: Node) -> DualScreenBookDevice:
        """Alias for add_screen."""
        return self.add_screen(*nodes)

    def local_bounds(self, time: float = 0.0) -> Tuple[float, float, float, float]:
        return (0.0, 0.0, self.width_val, self.height_val)

    def draw(self, ctx: Any, time: float = 0.0) -> None:
        w = self.width_val
        h = self.height_val
        cr = self.corner_radius

        panel_w = (w - self.hinge_width) * 0.5

        ctx.save()

        if self.shadow is not None and hasattr(ctx, "set_source_surface"):
            self.shadow.render_shadow(ctx, (0, 0, panel_w, h), cr)
            self.shadow.render_shadow(ctx, (panel_w + self.hinge_width, 0, panel_w, h), cr)

        # Left panel
        _rounded_rect(ctx, 0, 0, panel_w, h, cr)
        ctx.set_source_rgba(self.bezel_color.r, self.bezel_color.g, self.bezel_color.b, self.bezel_color.a)
        ctx.fill_preserve()
        ctx.set_source_rgba(1.0, 1.0, 1.0, 0.15)
        ctx.set_line_width(2.0)
        ctx.stroke()

        # Right panel
        _rounded_rect(ctx, panel_w + self.hinge_width, 0, panel_w, h, cr)
        ctx.set_source_rgba(self.bezel_color.r, self.bezel_color.g, self.bezel_color.b, self.bezel_color.a)
        ctx.fill_preserve()
        ctx.set_source_rgba(1.0, 1.0, 1.0, 0.15)
        ctx.set_line_width(2.0)
        ctx.stroke()

        # Hinge mechanism
        if hasattr(cairo, "LinearGradient") and hasattr(ctx, "set_source"):
            try:
                hinge_pat = cairo.LinearGradient(panel_w, 0, panel_w + self.hinge_width, 0)
                hinge_pat.add_color_stop_rgba(0.0, 0.1, 0.1, 0.1, 1.0)
                hinge_pat.add_color_stop_rgba(0.5, 0.35, 0.35, 0.35, 1.0)
                hinge_pat.add_color_stop_rgba(1.0, 0.1, 0.1, 0.1, 1.0)
                ctx.set_source(hinge_pat)
                ctx.rectangle(panel_w, h * 0.1, self.hinge_width, h * 0.8)
                ctx.fill()
            except Exception:
                pass

        ctx.restore()


class HingeCreaseIndicator(Node):
    """
    Animated light sheen travelling along a foldable display crease axis.
    """
    def __init__(
        self,
        length: float = 500.0,
        direction: str = "vertical",
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)
        self.length = float(length)
        self.direction = direction.lower()
        self.progress = Signal(0.0, f"{self.name}.progress")

    def local_bounds(self, time: float = 0.0) -> Tuple[float, float, float, float]:
        if self.direction == "vertical":
            return (-20.0, 0.0, 40.0, self.length)
        else:
            return (0.0, -20.0, self.length, 40.0)

    def draw(self, ctx: Any, time: float = 0.0) -> None:
        prog = self.progress.get(time)
        if prog <= 0.0 or prog >= 1.0:
            return

        ctx.save()
        sheen_len = 100.0
        pos = (self.length + sheen_len) * prog - sheen_len

        if self.direction == "vertical":
            if hasattr(cairo, "LinearGradient") and hasattr(ctx, "set_source"):
                try:
                    pat = cairo.LinearGradient(0, pos, 0, pos + sheen_len)
                    pat.add_color_stop_rgba(0.0, 1.0, 1.0, 1.0, 0.0)
                    pat.add_color_stop_rgba(0.5, 1.0, 1.0, 1.0, 0.8)
                    pat.add_color_stop_rgba(1.0, 1.0, 1.0, 1.0, 0.0)
                    ctx.set_source(pat)
                except Exception:
                    ctx.set_source_rgba(1.0, 1.0, 1.0, 0.5)
            else:
                ctx.set_source_rgba(1.0, 1.0, 1.0, 0.5)
            ctx.rectangle(-2.0, pos, 4.0, sheen_len)
            ctx.fill()
        else:
            if hasattr(cairo, "LinearGradient") and hasattr(ctx, "set_source"):
                try:
                    pat = cairo.LinearGradient(pos, 0, pos + sheen_len, 0)
                    pat.add_color_stop_rgba(0.0, 1.0, 1.0, 1.0, 0.0)
                    pat.add_color_stop_rgba(0.5, 1.0, 1.0, 1.0, 0.8)
                    pat.add_color_stop_rgba(1.0, 1.0, 1.0, 1.0, 0.0)
                    ctx.set_source(pat)
                except Exception:
                    ctx.set_source_rgba(1.0, 1.0, 1.0, 0.5)
            else:
                ctx.set_source_rgba(1.0, 1.0, 1.0, 0.5)
            ctx.rectangle(pos, -2.0, sheen_len, 4.0)
            ctx.fill()

        ctx.restore()


class FoldableDeviceSuite:
    """
    Suite factory for creating foldable smartphone and book device mockups.
    """
    @staticmethod
    def phone(fold_angle: float = 0.0, **kwargs: Any) -> FoldableDeviceFrame:
        return FoldableDeviceFrame(fold_angle=fold_angle, **kwargs)

    @staticmethod
    def book_phone(fold_angle: float = 0.0, **kwargs: Any) -> FoldableBookPhone:
        return FoldableBookPhone(fold_angle=fold_angle, **kwargs)

    @staticmethod
    def flip_phone(fold_angle: float = 0.0, **kwargs: Any) -> ClamshellFlipPhone:
        return ClamshellFlipPhone(fold_angle=fold_angle, **kwargs)

    @staticmethod
    def dual_screen(fold_angle: float = 0.0, **kwargs: Any) -> DualScreenBookDevice:
        return DualScreenBookDevice(fold_angle=fold_angle, **kwargs)

    @staticmethod
    def crease_indicator(length: float = 500.0, direction: str = "vertical", **kwargs: Any) -> HingeCreaseIndicator:
        return HingeCreaseIndicator(length=length, direction=direction, **kwargs)
