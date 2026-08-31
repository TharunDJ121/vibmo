from __future__ import annotations
import math
from typing import Any, Optional, Tuple, Union

import cairo

from vibmo.core.color import Color
from vibmo.scene.node import Node
from vibmo.layout.container import FlexContainer
from vibmo.spatial.shadows import DropShadow


class SmartHomeHubFrame(Node):
    """
    Google Nest Hub style angled touchscreen mounted on a woven fabric acoustic speaker base,
    with configurable stand tilt, subtle drop shadow, and auto-clipped screen viewport.
    """
    def __init__(
        self,
        width: float = 800.0,
        height: float = 600.0,
        stand_tilt: float = 20.0,
        base_color: Optional[Union[Color, str]] = None,
        screen_bg_color: Optional[Union[Color, str]] = None,
        shadow: Optional[Union[DropShadow, bool]] = True,
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)
        self.width_val = float(width)
        self.height_val = float(height)
        self.stand_tilt = float(stand_tilt)
        self.base_color = Color.from_any(base_color) if base_color else Color(0.9, 0.9, 0.92, 1.0)
        self.screen_bg_color = Color.from_any(screen_bg_color) if screen_bg_color else Color(0.1, 0.1, 0.1, 1.0)

        if shadow is True:
            self.shadow = DropShadow.elevated(blur=36.0, offset=(0, 18), color=Color.BLACK.with_alpha(0.40))
        elif isinstance(shadow, DropShadow):
            self.shadow = shadow
        else:
            self.shadow = None

        screen_w = self.width_val
        screen_h = self.height_val * 0.70
        inner_m = 16.0
        self.screen = FlexContainer(
            direction="column",
            gap=12.0,
            padding=16.0,
            width=screen_w - inner_m * 2,
            height=screen_h - inner_m * 2,
            position=(inner_m, inner_m),
            fill=self.screen_bg_color,
            stroke=Color.TRANSPARENT,
            corner_radius=8.0,
        )
        self.screen_content = self.screen
        self.add(self.screen)

    def add_screen(self, *nodes: Node) -> SmartHomeHubFrame:
        """Add child nodes to the smart hub screen viewport."""
        self.screen.add(*nodes)
        return self

    def add_screen_content(self, node: Node) -> SmartHomeHubFrame:
        """Alias for add_screen."""
        self.screen_content.add(node)
        return self

    def local_bounds(self, time: float = 0.0) -> Tuple[float, float, float, float]:
        return (0.0, 0.0, self.width_val, self.height_val)

    def draw(self, ctx: Any, time: float = 0.0) -> None:
        w = self.width_val
        h = self.height_val

        ctx.save()

        # Drop shadow (only when real surface is available)
        if self.shadow is not None and hasattr(ctx, "set_source_surface"):
            self.shadow.render_shadow(ctx, (0, 0, w, h), 24.0)

        # 1. Draw fabric base (angled elliptical speaker stand)
        ctx.save()
        ctx.translate(w * 0.1, h * 0.6)

        ctx.move_to(0, 0)
        ctx.line_to(w * 0.8, 0)
        ctx.curve_to(w * 0.85, h * 0.2, w * 0.7, h * 0.4, w * 0.4, h * 0.4)
        ctx.curve_to(w * 0.1, h * 0.4, -w * 0.05, h * 0.2, 0, 0)
        ctx.close_path()

        ctx.set_source_rgba(self.base_color.r, self.base_color.g, self.base_color.b, self.base_color.a)
        ctx.fill_preserve()
        ctx.set_source_rgba(0.0, 0.0, 0.0, 0.1)
        ctx.set_line_width(2.0)
        ctx.stroke()

        # Fabric woven crosshatch texture
        ctx.set_line_width(0.5)
        ctx.set_source_rgba(0.0, 0.0, 0.0, 0.05)
        for i in range(10, int(w * 0.8), 20):
            ctx.move_to(i, 0)
            ctx.line_to(i - 20, h * 0.3)
            ctx.stroke()
        ctx.restore()

        # 2. Draw screen outer white bezel
        screen_w = w
        screen_h = h * 0.70
        cr = 24.0

        ctx.save()
        ctx.move_to(cr, 0)
        ctx.line_to(screen_w - cr, 0)
        ctx.arc(screen_w - cr, cr, cr, -math.pi / 2, 0)
        ctx.line_to(screen_w, screen_h - cr)
        ctx.arc(screen_w - cr, screen_h - cr, cr, 0, math.pi / 2)
        ctx.line_to(cr, screen_h)
        ctx.arc(cr, screen_h - cr, cr, math.pi / 2, math.pi)
        ctx.line_to(0, cr)
        ctx.arc(cr, cr, cr, math.pi, -math.pi / 2)
        ctx.close_path()

        ctx.set_source_rgba(1.0, 1.0, 1.0, 1.0)
        ctx.fill_preserve()
        ctx.set_source_rgba(0.8, 0.8, 0.8, 1.0)
        ctx.set_line_width(4.0)
        ctx.stroke()

        # Inner screen underlay
        inner_m = 16.0
        inner_w = screen_w - inner_m * 2
        inner_h = screen_h - inner_m * 2
        inner_cr = 8.0

        ctx.translate(inner_m, inner_m)
        ctx.move_to(inner_cr, 0)
        ctx.line_to(inner_w - inner_cr, 0)
        ctx.arc(inner_w - inner_cr, inner_cr, inner_cr, -math.pi / 2, 0)
        ctx.line_to(inner_w, inner_h - inner_cr)
        ctx.arc(inner_w - inner_cr, inner_h - inner_cr, inner_cr, 0, math.pi / 2)
        ctx.line_to(inner_cr, inner_h)
        ctx.arc(inner_cr, inner_h - inner_cr, inner_cr, math.pi / 2, math.pi)
        ctx.line_to(0, inner_cr)
        ctx.arc(inner_cr, inner_cr, inner_cr, math.pi, -math.pi / 2)
        ctx.close_path()

        ctx.set_source_rgba(self.screen_bg_color.r, self.screen_bg_color.g, self.screen_bg_color.b, self.screen_bg_color.a)
        ctx.fill()

        ctx.restore()
        ctx.restore()


# Semantic alias
FabricAcousticSmartHub = SmartHomeHubFrame


class RoundThermostatDial(Node):
    """
    Nest style circular glass smart thermostat with rotating temperature ring and temperature status display.
    """
    def __init__(
        self,
        radius: float = 150.0,
        temperature: float = 72.0,
        ring_color: Optional[Union[Color, str]] = None,
        screen_color: Optional[Union[Color, str]] = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)
        self.radius = float(radius)
        self.temperature = float(temperature)
        self.ring_color = Color.from_any(ring_color) if ring_color else Color(0.2, 0.2, 0.2, 1.0)
        self.screen_color = Color.from_any(screen_color) if screen_color else Color(0.05, 0.05, 0.05, 1.0)

        # Content slot
        self.screen_content = Node(name="screen_content")
        self.screen = self.screen_content
        self.add(self.screen_content)

    def add_screen(self, *nodes: Node) -> RoundThermostatDial:
        self.screen_content.add(*nodes)
        return self

    def add_screen_content(self, node: Node) -> RoundThermostatDial:
        self.screen_content.add(node)
        return self

    def local_bounds(self, time: float = 0.0) -> Tuple[float, float, float, float]:
        return (0.0, 0.0, self.radius * 2, self.radius * 2)

    def draw(self, ctx: Any, time: float = 0.0) -> None:
        r = self.radius
        cx = r
        cy = r

        ctx.save()

        # Outer ring
        ctx.arc(cx, cy, r, 0, math.pi * 2)
        ctx.set_source_rgba(self.ring_color.r, self.ring_color.g, self.ring_color.b, self.ring_color.a)
        ctx.fill_preserve()

        # Inner screen
        screen_r = r * 0.85
        ctx.arc(cx, cy, screen_r, 0, math.pi * 2)
        ctx.set_source_rgba(self.screen_color.r, self.screen_color.g, self.screen_color.b, self.screen_color.a)
        ctx.fill()

        # Glass reflection
        ctx.arc(cx, cy - r * 0.3, r * 0.6, 0, math.pi * 2)
        if hasattr(ctx, "set_source"):
            try:
                pat = cairo.LinearGradient(cx, cy - r, cx, cy)
                pat.add_color_stop_rgba(0, 1, 1, 1, 0.1)
                pat.add_color_stop_rgba(1, 1, 1, 1, 0.0)
                ctx.set_source(pat)
            except Exception:
                ctx.set_source_rgba(1, 1, 1, 0.05)
        else:
            ctx.set_source_rgba(1, 1, 1, 0.05)
        ctx.fill()

        ctx.restore()


class WallMountSecurityKeypad(Node):
    """
    Smart home alarm panel with numerical keypad and status LED icons.
    """
    def __init__(
        self,
        width: float = 300.0,
        height: float = 400.0,
        bg_color: Optional[Union[Color, str]] = None,
        status_led: Optional[Union[Color, str]] = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)
        self.width_val = float(width)
        self.height_val = float(height)
        self.bg_color = Color.from_any(bg_color) if bg_color else Color(0.95, 0.95, 0.95, 1.0)
        self.status_led = Color.from_any(status_led) if status_led else Color(0.1, 0.8, 0.2, 1.0)

        screen_m = 20.0
        screen_w = self.width_val - screen_m * 2
        screen_h = 80.0
        screen_y = 50.0
        self.screen = FlexContainer(
            direction="row",
            align_items="center",
            padding=8.0,
            width=screen_w,
            height=screen_h,
            position=(screen_m, screen_y),
            fill=Color.hex("#090d16"),
            stroke=Color.TRANSPARENT,
            corner_radius=4.0,
        )
        self.add(self.screen)

    def add_screen(self, *nodes: Node) -> WallMountSecurityKeypad:
        self.screen.add(*nodes)
        return self

    def local_bounds(self, time: float = 0.0) -> Tuple[float, float, float, float]:
        return (0.0, 0.0, self.width_val, self.height_val)

    def draw(self, ctx: Any, time: float = 0.0) -> None:
        w = self.width_val
        h = self.height_val
        cr = 16.0

        ctx.save()

        # Body
        ctx.move_to(cr, 0)
        ctx.line_to(w - cr, 0)
        ctx.arc(w - cr, cr, cr, -math.pi / 2, 0)
        ctx.line_to(w, h - cr)
        ctx.arc(w - cr, h - cr, cr, 0, math.pi / 2)
        ctx.line_to(cr, h)
        ctx.arc(cr, h - cr, cr, math.pi / 2, math.pi)
        ctx.line_to(0, cr)
        ctx.arc(cr, cr, cr, math.pi, -math.pi / 2)
        ctx.close_path()

        ctx.set_source_rgba(self.bg_color.r, self.bg_color.g, self.bg_color.b, self.bg_color.a)
        ctx.fill_preserve()
        ctx.set_source_rgba(0.8, 0.8, 0.8, 1.0)
        ctx.set_line_width(2.0)
        ctx.stroke()

        # Status LED indicator at top right
        ctx.arc(w - 30.0, 30.0, 8.0, 0, math.pi * 2)
        ctx.set_source_rgba(self.status_led.r, self.status_led.g, self.status_led.b, self.status_led.a)
        ctx.fill()

        # Screen underlay
        screen_m = 20.0
        screen_w = w - screen_m * 2
        screen_h = 80.0
        screen_y = 50.0

        ctx.rectangle(screen_m, screen_y, screen_w, screen_h)
        ctx.set_source_rgba(0.1, 0.1, 0.15, 1.0)
        ctx.fill()

        # Keypad Grid
        grid_cols = 3
        grid_rows = 4
        btn_w = 60.0
        btn_h = 40.0
        gap_x = (screen_w - (grid_cols * btn_w)) / (grid_cols - 1)
        gap_y = 15.0

        start_y = screen_y + screen_h + 30.0

        for row in range(grid_rows):
            for col in range(grid_cols):
                if row == 3 and (col == 0 or col == 2):
                    continue

                btn_x = screen_m + col * (btn_w + gap_x)
                btn_y = start_y + row * (btn_h + gap_y)

                bcr = 8.0
                ctx.move_to(btn_x + bcr, btn_y)
                ctx.line_to(btn_x + btn_w - bcr, btn_y)
                ctx.arc(btn_x + btn_w - bcr, btn_y + bcr, bcr, -math.pi / 2, 0)
                ctx.line_to(btn_x + btn_w, btn_y + btn_h - bcr)
                ctx.arc(btn_x + btn_w - bcr, btn_y + btn_h - bcr, bcr, 0, math.pi / 2)
                ctx.line_to(btn_x + bcr, btn_y + btn_h)
                ctx.arc(btn_x + bcr, btn_y + btn_h - bcr, bcr, math.pi / 2, math.pi)
                ctx.line_to(btn_x, btn_y + bcr)
                ctx.arc(btn_x + bcr, btn_y + bcr, bcr, math.pi, -math.pi / 2)
                ctx.close_path()

                ctx.set_source_rgba(0.98, 0.98, 0.98, 1.0)
                ctx.fill_preserve()
                ctx.set_source_rgba(0.85, 0.85, 0.85, 1.0)
                ctx.set_line_width(1.0)
                ctx.stroke()

        ctx.restore()


class SmartHomeHubSuite:
    """
    Suite factory for smart home hubs, thermostats, and wall-mounted security panels.
    """
    @staticmethod
    def hub(stand_tilt: float = 20.0, **kwargs: Any) -> SmartHomeHubFrame:
        return SmartHomeHubFrame(stand_tilt=stand_tilt, **kwargs)

    @staticmethod
    def thermostat(**kwargs: Any) -> RoundThermostatDial:
        return RoundThermostatDial(**kwargs)

    @staticmethod
    def security_keypad(**kwargs: Any) -> WallMountSecurityKeypad:
        return WallMountSecurityKeypad(**kwargs)
