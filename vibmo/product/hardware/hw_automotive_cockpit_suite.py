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


class AutomotiveCockpitDash(Node):
    """
    15-inch landscape floating center console touchscreen with minimal matte black bezels,
    optional digital HUD instrument gauges, and auto-clipped screen viewport.
    """
    def __init__(
        self,
        width: float = 1200.0,
        height: float = 750.0,
        hud_gauges: bool = False,
        bezel_width: float = 20.0,
        corner_radius: float = 24.0,
        bezel_color: Optional[Union[Color, str]] = None,
        bg_color: Optional[Union[Color, str]] = None,
        shadow: Optional[Union[DropShadow, bool]] = True,
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)
        self.width_val = float(width)
        self.height_val = float(height)
        self.hud_gauges = hud_gauges
        self.bezel_width = float(bezel_width)
        self.corner_radius = float(corner_radius)
        self.bezel_color = Color.from_any(bezel_color) if bezel_color else Color.hex("#111111")
        self.bg_color = Color.from_any(bg_color) if bg_color else Color.hex("#0d0d0d")

        if shadow is True:
            self.shadow = DropShadow.elevated(blur=40.0, offset=(0, 20), color=Color.BLACK.with_alpha(0.60))
        elif isinstance(shadow, DropShadow):
            self.shadow = shadow
        else:
            self.shadow = None

        inner_w = self.width_val - self.bezel_width * 2
        inner_h = self.height_val - self.bezel_width * 2

        self.screen = FlexContainer(
            direction="row",
            gap=16.0,
            padding=16.0,
            width=inner_w,
            height=inner_h,
            position=(self.bezel_width, self.bezel_width),
            fill=self.bg_color,
            stroke=Color.TRANSPARENT,
            corner_radius=max(0.0, self.corner_radius - 6.0),
        )
        self.add(self.screen)

    def add_screen(self, *nodes: Node) -> AutomotiveCockpitDash:
        """Add child nodes to the dashboard touchscreen viewport."""
        self.screen.add(*nodes)
        return self

    def add_screen_content(self, *nodes: Node) -> AutomotiveCockpitDash:
        """Alias for add_screen."""
        return self.add_screen(*nodes)

    def add_content(self, *nodes: Node) -> AutomotiveCockpitDash:
        """Alias for add_screen."""
        return self.add_screen(*nodes)

    def local_bounds(self, time: float = 0.0) -> Tuple[float, float, float, float]:
        return (0.0, 0.0, self.width_val, self.height_val)

    def draw(self, ctx: Any, time: float = 0.0) -> None:
        w = self.width_val
        h = self.height_val
        cr = self.corner_radius

        ctx.save()

        # Drop shadow
        if self.shadow is not None and hasattr(ctx, "set_source_surface"):
            self.shadow.render_shadow(ctx, (0, 0, w, h), cr)

        # Bezel body
        ctx.new_sub_path()
        ctx.arc(w - cr, h - cr, cr, 0, math.pi / 2)
        ctx.arc(cr, h - cr, cr, math.pi / 2, math.pi)
        ctx.arc(cr, cr, cr, math.pi, 3 * math.pi / 2)
        ctx.arc(w - cr, cr, cr, 3 * math.pi / 2, 2 * math.pi)
        ctx.close_path()

        r, g, b, a = self.bezel_color.to_tuple_rgba()
        ctx.set_source_rgba(r, g, b, a)
        ctx.fill_preserve()

        # Specular rim
        ctx.set_source_rgba(1.0, 1.0, 1.0, 0.12)
        ctx.set_line_width(2.0)
        ctx.stroke()

        # HUD Gauges Overlay (if enabled)
        if self.hud_gauges:
            ctx.save()
            bar_y = self.bezel_width + 12.0
            if hasattr(ctx, "select_font_face"):
                ctx.select_font_face("sans-serif", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
            if hasattr(ctx, "set_font_size"):
                ctx.set_font_size(18)
            ctx.set_source_rgba(1.0, 1.0, 1.0, 0.8)
            ctx.move_to(self.bezel_width + 20, bar_y + 16)
            if hasattr(ctx, "show_text"):
                ctx.show_text("PRND  |  68°F  |  12:45 PM")

            bx = w - self.bezel_width - 100
            ctx.rectangle(bx, bar_y, 40, 16)
            ctx.set_line_width(1.5)
            ctx.stroke()
            ctx.rectangle(bx + 40, bar_y + 4, 3, 8)
            ctx.fill()
            ctx.set_source_rgba(0.2, 0.8, 0.3, 0.9)
            ctx.rectangle(bx + 2, bar_y + 2, 32, 12)
            ctx.fill()
            ctx.move_to(bx + 50, bar_y + 14)
            if hasattr(ctx, "set_font_size"):
                ctx.set_font_size(14)
            ctx.set_source_rgba(1.0, 1.0, 1.0, 0.8)
            if hasattr(ctx, "show_text"):
                ctx.show_text("88%")
            ctx.restore()

        ctx.restore()


# Semantic alias
TeslaCenterTouchscreen = AutomotiveCockpitDash


class CarPlayDashboardPill(Node):
    """
    Rounded dashboard cluster with horizontal split widget layout (maps + music + navigation pill).
    """
    def __init__(
        self,
        width: float = 1400.0,
        height: float = 400.0,
        bezel_width: float = 16.0,
        corner_radius: float = 100.0,
        bezel_color: Optional[Union[Color, str]] = None,
        bg_color: Optional[Union[Color, str]] = None,
        shadow: Optional[Union[DropShadow, bool]] = True,
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)
        self.width_val = float(width)
        self.height_val = float(height)
        self.bezel_width = float(bezel_width)
        self.corner_radius = float(corner_radius)
        self.bezel_color = Color.from_any(bezel_color) if bezel_color else Color.hex("#111111")
        self.bg_color = Color.from_any(bg_color) if bg_color else Color.hex("#0d0d0d")

        if shadow is True:
            self.shadow = DropShadow.elevated(blur=30.0, offset=(0, 15), color=Color.BLACK.with_alpha(0.50))
        elif isinstance(shadow, DropShadow):
            self.shadow = shadow
        else:
            self.shadow = None

        inner_w = self.width_val - self.bezel_width * 2
        inner_h = self.height_val - self.bezel_width * 2

        self.screen = FlexContainer(
            direction="row",
            gap=24.0,
            padding=32.0,
            width=inner_w,
            height=inner_h,
            position=(self.bezel_width, self.bezel_width),
            fill=self.bg_color,
            stroke=Color.TRANSPARENT,
            corner_radius=max(0.0, self.corner_radius - 8.0),
        )
        self.add(self.screen)

    def add_screen(self, *nodes: Node) -> CarPlayDashboardPill:
        self.screen.add(*nodes)
        return self

    def add_screen_content(self, *nodes: Node) -> CarPlayDashboardPill:
        """Alias for add_screen."""
        return self.add_screen(*nodes)

    def add_widget(self, *nodes: Node) -> CarPlayDashboardPill:
        return self.add_screen(*nodes)

    def local_bounds(self, time: float = 0.0) -> Tuple[float, float, float, float]:
        return (0.0, 0.0, self.width_val, self.height_val)

    def draw(self, ctx: Any, time: float = 0.0) -> None:
        w = self.width_val
        h = self.height_val
        cr = self.corner_radius

        ctx.save()

        if self.shadow is not None and hasattr(ctx, "set_source_surface"):
            self.shadow.render_shadow(ctx, (0, 0, w, h), cr)

        ctx.new_sub_path()
        ctx.arc(w - cr, h - cr, cr, 0, math.pi / 2)
        ctx.arc(cr, h - cr, cr, math.pi / 2, math.pi)
        ctx.arc(cr, cr, cr, math.pi, 3 * math.pi / 2)
        ctx.arc(w - cr, cr, cr, 3 * math.pi / 2, 2 * math.pi)
        ctx.close_path()

        r, g, b, a = self.bezel_color.to_tuple_rgba()
        ctx.set_source_rgba(r, g, b, a)
        ctx.fill()

        ctx.restore()


class DigitalGaugeClusterHud(Node):
    """
    Driver instrument digital cluster with speed needle, battery percentage, and ADAS car lane visualization.
    """
    def __init__(
        self,
        width: float = 1000.0,
        height: float = 500.0,
        corner_radius: float = 20.0,
        bg_color: Optional[Union[Color, str]] = None,
        speed: float = 0.0,
        battery_percentage: float = 100.0,
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)
        self.width_val = float(width)
        self.height_val = float(height)
        self.corner_radius = float(corner_radius)
        self.bg_color = Color.from_any(bg_color) if bg_color else Color.hex("#0d0d0d")

        self.speed = Signal(float(speed), f"{self.name}.speed")
        self.battery = Signal(float(battery_percentage), f"{self.name}.battery")

        self.screen = FlexContainer(
            direction="row",
            gap=40.0,
            padding=40.0,
            width=self.width_val,
            height=self.height_val,
            fill=Color.TRANSPARENT,
            stroke=Color.TRANSPARENT,
        )
        self.content = self.screen
        self.add(self.screen)

    def add_screen(self, *nodes: Node) -> DigitalGaugeClusterHud:
        self.screen.add(*nodes)
        return self

    def add_screen_content(self, *nodes: Node) -> DigitalGaugeClusterHud:
        """Alias for add_screen."""
        return self.add_screen(*nodes)

    def set_speed(self, val: float, duration: float = 0.0, ease: Optional[EasingFunc] = None) -> AnimationAction:
        return self.speed.to(val, duration=duration, ease=ease or Ease.in_out_cubic)

    def local_bounds(self, time: float = 0.0) -> Tuple[float, float, float, float]:
        return (0.0, 0.0, self.width_val, self.height_val)

    def draw(self, ctx: Any, time: float = 0.0) -> None:
        w = self.width_val
        h = self.height_val
        cr = self.corner_radius

        ctx.save()

        ctx.new_sub_path()
        ctx.arc(w - cr, h - cr, cr, 0, math.pi / 2)
        ctx.arc(cr, h - cr, cr, math.pi / 2, math.pi)
        ctx.arc(cr, cr, cr, math.pi, 3 * math.pi / 2)
        ctx.arc(w - cr, cr, cr, 3 * math.pi / 2, 2 * math.pi)
        ctx.close_path()

        r, g, b, a = self.bg_color.to_tuple_rgba()
        ctx.set_source_rgba(r, g, b, a)
        ctx.fill()

        # Speed needle on left
        ctx.save()
        ctx.translate(w * 0.25, h * 0.5)
        ctx.arc(0, 0, h * 0.3, 0, 2 * math.pi)
        r, g, b, a = Color.WHITE.with_alpha(0.1).to_tuple_rgba()
        ctx.set_source_rgba(r, g, b, a)
        ctx.fill()

        ctx.set_line_width(4)
        r, g, b, a = Color.hex("#3b82f6").to_tuple_rgba()
        ctx.set_source_rgba(r, g, b, a)
        ctx.move_to(0, 0)
        speed_angle = (self.speed.get(time) / 120.0) * math.pi - math.pi
        ctx.line_to(math.cos(speed_angle) * (h * 0.25), math.sin(speed_angle) * (h * 0.25))
        ctx.stroke()
        ctx.restore()

        # Battery bar on right
        ctx.save()
        ctx.translate(w * 0.75, h * 0.5)
        bar_w = w * 0.1
        bar_h = h * 0.4
        ctx.rectangle(-bar_w / 2, -bar_h / 2, bar_w, bar_h)
        r, g, b, a = Color.WHITE.with_alpha(0.1).to_tuple_rgba()
        ctx.set_source_rgba(r, g, b, a)
        ctx.fill()

        fill_h = bar_h * (self.battery.get(time) / 100.0)
        ctx.rectangle(-bar_w / 2, bar_h / 2 - fill_h, bar_w, fill_h)
        r, g, b, a = Color.hex("#22c55e").to_tuple_rgba()
        ctx.set_source_rgba(r, g, b, a)
        ctx.fill()
        ctx.restore()

        # ADAS lane in center
        ctx.save()
        ctx.translate(w * 0.5, h * 0.5)
        ctx.set_line_width(2)
        r, g, b, a = Color.WHITE.with_alpha(0.5).to_tuple_rgba()
        ctx.set_source_rgba(r, g, b, a)
        ctx.move_to(-50, h * 0.4)
        ctx.line_to(-20, -h * 0.2)
        ctx.move_to(50, h * 0.4)
        ctx.line_to(20, -h * 0.2)
        ctx.stroke()

        ctx.rectangle(-15, -15, 30, 50)
        r, g, b, a = Color.WHITE.to_tuple_rgba()
        ctx.set_source_rgba(r, g, b, a)
        ctx.fill()
        ctx.restore()

        ctx.restore()


class AutomotiveCockpitSuite:
    """
    Suite factory for automotive digital cockpits, center consoles, and gauge clusters.
    """
    @staticmethod
    def dash(hud_gauges: bool = True, **kwargs: Any) -> AutomotiveCockpitDash:
        return AutomotiveCockpitDash(hud_gauges=hud_gauges, **kwargs)

    @staticmethod
    def touchscreen(**kwargs: Any) -> TeslaCenterTouchscreen:
        return TeslaCenterTouchscreen(**kwargs)

    @staticmethod
    def carplay_pill(**kwargs: Any) -> CarPlayDashboardPill:
        return CarPlayDashboardPill(**kwargs)

    @staticmethod
    def gauge_cluster(**kwargs: Any) -> DigitalGaugeClusterHud:
        return DigitalGaugeClusterHud(**kwargs)
