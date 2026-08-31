from __future__ import annotations
import math
from typing import Any, Optional, Tuple, Union

import cairo

from vibmo.core.color import Color
from vibmo.scene.node import Node
from vibmo.layout.container import FlexContainer
from vibmo.spatial.shadows import DropShadow


class _VintageNode(Node):
    def _rounded_rect(self, ctx: Any, x: float, y: float, w: float, h: float, r: float) -> None:
        """Helper to draw a rounded rectangle."""
        r = min(r, w * 0.5, h * 0.5)
        if r <= 0:
            ctx.rectangle(x, y, w, h)
            return
        ctx.new_path()
        ctx.arc(x + w - r, y + r, r, -math.pi / 2, 0)
        ctx.arc(x + w - r, y + h - r, r, 0, math.pi / 2)
        ctx.arc(x + r, y + h - r, r, math.pi / 2, math.pi)
        ctx.arc(x + r, y + r, r, math.pi, 3 * math.pi / 2)
        ctx.close_path()

    def _draw_screen_clipping(self, ctx: Any, x: float, y: float, w: float, h: float, r: float) -> None:
        """Sets up the screen clipping area."""
        self._rounded_rect(ctx, x, y, w, h, r)
        ctx.clip()


class RetroArcadeCrtCabinet(_VintageNode):
    """
    Retro arcade machine wooden cabinet side art, illuminated marquee,
    CRT curvature mask, and auto-clipped screen viewport.
    """
    def __init__(
        self,
        width: float = 600.0,
        height: float = 800.0,
        cabinet_color: Optional[Union[Color, str]] = "#3a2010",
        screen_color: Optional[Union[Color, str]] = "#000000",
        shadow: Optional[Union[DropShadow, bool]] = True,
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)
        self.width_val = float(width)
        self.height_val = float(height)
        self.cabinet_color = Color.from_any(cabinet_color)
        self.screen_color = Color.from_any(screen_color)

        if shadow is True:
            self.shadow = DropShadow.elevated(blur=36.0, offset=(0, 18), color=Color.BLACK.with_alpha(0.50))
        elif isinstance(shadow, DropShadow):
            self.shadow = shadow
        else:
            self.shadow = None

        screen_x = 60.0
        screen_y = 150.0
        screen_w = self.width_val - 120.0
        screen_h = self.height_val - 200.0

        self.screen = FlexContainer(
            direction="column",
            gap=0.0,
            padding=0.0,
            width=screen_w,
            height=screen_h,
            position=(screen_x, screen_y),
            fill=self.screen_color,
            stroke=Color.TRANSPARENT,
            corner_radius=15.0,
        )
        self.add(self.screen)

    def add_screen(self, *nodes: Node) -> RetroArcadeCrtCabinet:
        """Add child nodes to the arcade CRT screen viewport."""
        self.screen.add(*nodes)
        return self

    def add_screen_content(self, *nodes: Node) -> RetroArcadeCrtCabinet:
        """Alias for add_screen."""
        return self.add_screen(*nodes)

    def local_bounds(self, time: float = 0.0) -> Tuple[float, float, float, float]:
        return (0.0, 0.0, self.width_val, self.height_val)

    def draw(self, ctx: Any, time: float = 0.0) -> None:
        w = self.width_val
        h = self.height_val
        ctx.save()

        # Shadow (only with real surface)
        if self.shadow is not None and hasattr(ctx, "set_source_surface"):
            self.shadow.render_shadow(ctx, (0, 0, w, h), 10.0)

        # Cabinet Body
        self._rounded_rect(ctx, 0, 0, w, h, 10.0)
        ctx.set_source_rgba(self.cabinet_color.r, self.cabinet_color.g, self.cabinet_color.b, self.cabinet_color.a)
        ctx.fill()

        # Side art / panels
        ctx.set_source_rgba(0, 0, 0, 0.3)
        self._rounded_rect(ctx, 10, 10, 40, h - 20, 5)
        ctx.fill()
        self._rounded_rect(ctx, w - 50, 10, 40, h - 20, 5)
        ctx.fill()

        # Marquee area
        ctx.set_source_rgba(1, 1, 1, 0.85)
        self._rounded_rect(ctx, 60, 20, w - 120, 100, 5)
        ctx.fill()
        # "ARCADE" Text mock
        ctx.set_source_rgba(1, 0, 0, 1)
        if hasattr(ctx, "select_font_face"):
            ctx.select_font_face("sans-serif", cairo.FONT_SLANT_NORMAL if hasattr(cairo, "FONT_SLANT_NORMAL") else None, cairo.FONT_WEIGHT_BOLD if hasattr(cairo, "FONT_WEIGHT_BOLD") else None)
        if hasattr(ctx, "set_font_size"):
            ctx.set_font_size(40)
        if hasattr(ctx, "move_to"):
            ctx.move_to(w / 2 - 80, 85)
        if hasattr(ctx, "show_text"):
            ctx.show_text("ARCADE")

        # Screen Bezel
        screen_x, screen_y = 60.0, 150.0
        screen_w, screen_h = w - 120.0, h - 200.0

        ctx.set_source_rgba(0.1, 0.1, 0.1, 1)
        self._rounded_rect(ctx, screen_x - 10, screen_y - 10, screen_w + 20, screen_h + 20, 15)
        ctx.fill()

        # Screen mask
        ctx.save()
        self._draw_screen_clipping(ctx, screen_x, screen_y, screen_w, screen_h, 30.0)
        ctx.set_source_rgba(self.screen_color.r, self.screen_color.g, self.screen_color.b, self.screen_color.a)
        ctx.paint()
        ctx.restore()

        # Controls panel mock
        ctx.set_source_rgba(0.2, 0.2, 0.2, 1)
        self._rounded_rect(ctx, 60, h - 40, w - 120, 30, 5)
        ctx.fill()
        # Joystick
        ctx.arc(100, h - 25, 10, 0, 2 * math.pi)
        ctx.set_source_rgba(1, 0, 0, 1)
        ctx.fill()
        # Buttons
        for i in range(3):
            ctx.arc(w - 150 + i * 30, h - 25, 8, 0, 2 * math.pi)
            ctx.set_source_rgba(0, 0, 1, 1)
            ctx.fill()

        ctx.restore()


# Semantic alias
ArcadeCabinetBezel = RetroArcadeCrtCabinet


class BeigeCrtMonitor1990s(_VintageNode):
    """
    Chunky beige PC monitor chassis with power button, brightness thumbwheels,
    degauss button, curved glass tube, and auto-clipped screen viewport.
    """
    def __init__(
        self,
        width: float = 400.0,
        height: float = 350.0,
        chassis_color: Optional[Union[Color, str]] = "#e6e1d6",
        screen_color: Optional[Union[Color, str]] = "#111111",
        shadow: Optional[Union[DropShadow, bool]] = True,
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)
        self.width_val = float(width)
        self.height_val = float(height)
        self.chassis_color = Color.from_any(chassis_color)
        self.screen_color = Color.from_any(screen_color)

        if shadow is True:
            self.shadow = DropShadow.elevated(blur=28.0, offset=(0, 14), color=Color.BLACK.with_alpha(0.40))
        elif isinstance(shadow, DropShadow):
            self.shadow = shadow
        else:
            self.shadow = None

        screen_x, screen_y = 20.0, 20.0
        screen_w, screen_h = self.width_val - 40.0, self.height_val - 90.0
        self.screen = FlexContainer(
            direction="column",
            gap=0.0,
            padding=0.0,
            width=screen_w,
            height=screen_h,
            position=(screen_x, screen_y),
            fill=self.screen_color,
            stroke=Color.TRANSPARENT,
            corner_radius=12.0,
        )
        self.add(self.screen)

    def add_screen(self, *nodes: Node) -> BeigeCrtMonitor1990s:
        self.screen.add(*nodes)
        return self

    def add_screen_content(self, *nodes: Node) -> BeigeCrtMonitor1990s:
        return self.add_screen(*nodes)

    def local_bounds(self, time: float = 0.0) -> Tuple[float, float, float, float]:
        return (0.0, 0.0, self.width_val, self.height_val)

    def draw(self, ctx: Any, time: float = 0.0) -> None:
        w = self.width_val
        h = self.height_val
        ctx.save()

        # Shadow (only with real surface)
        if self.shadow is not None and hasattr(ctx, "set_source_surface"):
            self.shadow.render_shadow(ctx, (0, 0, w, h), 20.0)

        # Monitor Chassis
        self._rounded_rect(ctx, 0, 0, w, h, 20.0)
        ctx.set_source_rgba(self.chassis_color.r, self.chassis_color.g, self.chassis_color.b, self.chassis_color.a)
        ctx.fill()

        # Inner bezel groove
        self._rounded_rect(ctx, 15, 15, w - 30, h - 80, 15.0)
        ctx.set_source_rgba(0, 0, 0, 0.1)
        ctx.set_line_width(2.0)
        ctx.stroke()

        # Screen mask
        screen_x, screen_y = 20.0, 20.0
        screen_w, screen_h = w - 40.0, h - 90.0

        ctx.save()
        self._draw_screen_clipping(ctx, screen_x, screen_y, screen_w, screen_h, 40.0)
        ctx.set_source_rgba(self.screen_color.r, self.screen_color.g, self.screen_color.b, self.screen_color.a)
        ctx.paint()
        ctx.arc(w / 2, -h, w * 1.5, 0, math.pi)
        ctx.set_source_rgba(1, 1, 1, 0.05)
        ctx.fill()
        ctx.restore()

        # Power Button
        ctx.arc(w - 40, h - 35, 12, 0, 2 * math.pi)
        ctx.set_source_rgba(0.9, 0.9, 0.85, 1.0)
        ctx.fill_preserve()
        ctx.set_source_rgba(0, 0, 0, 0.2)
        ctx.set_line_width(1.0)
        ctx.stroke()
        # LED
        ctx.arc(w - 40, h - 35, 3, 0, 2 * math.pi)
        ctx.set_source_rgba(0.2, 0.8, 0.2, 1.0)
        ctx.fill()

        # Degauss button
        ctx.arc(w - 80, h - 35, 8, 0, 2 * math.pi)
        ctx.set_source_rgba(0.85, 0.85, 0.8, 1.0)
        ctx.fill_preserve()
        ctx.set_source_rgba(0, 0, 0, 0.2)
        ctx.stroke()

        # Thumbwheels
        self._rounded_rect(ctx, 30, h - 40, 40, 10, 2)
        ctx.set_source_rgba(0.7, 0.7, 0.65, 1.0)
        ctx.fill_preserve()
        ctx.set_source_rgba(0, 0, 0, 0.3)
        ctx.stroke()
        self._rounded_rect(ctx, 80, h - 40, 40, 10, 2)
        ctx.set_source_rgba(0.7, 0.7, 0.65, 1.0)
        ctx.fill_preserve()
        ctx.set_source_rgba(0, 0, 0, 0.3)
        ctx.stroke()

        # Vent lines
        ctx.set_source_rgba(0, 0, 0, 0.1)
        ctx.set_line_width(2.0)
        for i in range(5):
            ctx.move_to(w / 2 - 30 + i * 15, h - 50)
            ctx.line_to(w / 2 - 30 + i * 15, h - 20)
        ctx.stroke()

        ctx.restore()


class RetroPortableTvAntenna(_VintageNode):
    """
    1970s portable television with rabbit-ear telescopic antennas and dual rotary dials.
    """
    def __init__(
        self,
        width: float = 350.0,
        height: float = 280.0,
        chassis_color: Optional[Union[Color, str]] = "#cc5500",
        screen_color: Optional[Union[Color, str]] = "#1a1a24",
        shadow: Optional[Union[DropShadow, bool]] = True,
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)
        self.width_val = float(width)
        self.height_val = float(height)
        self.chassis_color = Color.from_any(chassis_color)
        self.screen_color = Color.from_any(screen_color)

        if shadow is True:
            self.shadow = DropShadow.elevated(blur=28.0, offset=(0, 14), color=Color.BLACK.with_alpha(0.40))
        elif isinstance(shadow, DropShadow):
            self.shadow = shadow
        else:
            self.shadow = None

        screen_x, screen_y = 25.0, 25.0
        screen_w, screen_h = self.width_val - 120.0, self.height_val - 50.0
        self.screen = FlexContainer(
            direction="column",
            gap=0.0,
            padding=0.0,
            width=screen_w,
            height=screen_h,
            position=(screen_x, screen_y),
            fill=self.screen_color,
            stroke=Color.TRANSPARENT,
            corner_radius=12.0,
        )
        self.add(self.screen)

    def add_screen(self, *nodes: Node) -> RetroPortableTvAntenna:
        self.screen.add(*nodes)
        return self

    def add_screen_content(self, *nodes: Node) -> RetroPortableTvAntenna:
        return self.add_screen(*nodes)

    def local_bounds(self, time: float = 0.0) -> Tuple[float, float, float, float]:
        return (0.0, 0.0, self.width_val, self.height_val)

    def draw(self, ctx: Any, time: float = 0.0) -> None:
        w = self.width_val
        h = self.height_val
        ctx.save()

        # Antennas
        ctx.set_line_width(4)
        ctx.set_source_rgba(0.8, 0.8, 0.8, 1)
        ctx.move_to(w / 2 - 20, 0)
        ctx.line_to(w / 2 - 100, -100)
        ctx.stroke()
        ctx.move_to(w / 2 + 20, 0)
        ctx.line_to(w / 2 + 100, -120)
        ctx.stroke()
        # Antenna base
        ctx.arc(w / 2, 0, 25, math.pi, 2 * math.pi)
        ctx.set_source_rgba(0.2, 0.2, 0.2, 1)
        ctx.fill()

        # Shadow (only with real surface)
        if self.shadow is not None and hasattr(ctx, "set_source_surface"):
            self.shadow.render_shadow(ctx, (0, 0, w, h), 30.0)

        # TV Chassis
        self._rounded_rect(ctx, 0, 0, w, h, 30.0)
        ctx.set_source_rgba(self.chassis_color.r, self.chassis_color.g, self.chassis_color.b, self.chassis_color.a)
        ctx.fill()

        # Inner bezel
        ctx.set_source_rgba(0.1, 0.1, 0.1, 1)
        self._rounded_rect(ctx, 15, 15, w - 100, h - 30, 25.0)
        ctx.fill()

        # Screen mask
        screen_x, screen_y = 25.0, 25.0
        screen_w, screen_h = w - 120.0, h - 50.0

        ctx.save()
        self._draw_screen_clipping(ctx, screen_x, screen_y, screen_w, screen_h, 50.0)
        ctx.set_source_rgba(self.screen_color.r, self.screen_color.g, self.screen_color.b, self.screen_color.a)
        ctx.paint()
        ctx.arc(screen_x + screen_w / 2, screen_y - screen_h, screen_w * 1.5, 0, math.pi)
        ctx.set_source_rgba(1, 1, 1, 0.08)
        ctx.fill()
        ctx.restore()

        # Side panel (controls)
        ctx.set_source_rgba(0.2, 0.2, 0.2, 1)
        self._rounded_rect(ctx, w - 75, 15, 60, h - 30, 10.0)
        ctx.fill()

        # Rotary Dials (VHF / UHF)
        for dy in [50, 130]:
            ctx.arc(w - 45, dy, 20, 0, 2 * math.pi)
            ctx.set_source_rgba(0.8, 0.8, 0.8, 1)
            ctx.fill_preserve()
            ctx.set_source_rgba(0.1, 0.1, 0.1, 1)
            ctx.set_line_width(2)
            ctx.stroke()
            ctx.move_to(w - 45, dy)
            ctx.line_to(w - 45 + 15 * math.cos(math.pi / 4), dy - 15 * math.sin(math.pi / 4))
            ctx.stroke()

        # Speaker grille
        ctx.set_source_rgba(0, 0, 0, 0.5)
        ctx.set_line_width(2)
        for i in range(8):
            ctx.move_to(w - 65, 190 + i * 8)
            ctx.line_to(w - 25, 190 + i * 8)
        ctx.stroke()

        ctx.restore()


class VintageCrtSuite:
    """
    Suite factory for vintage arcade cabinets, CRT PC monitors, and retro televisions.
    """
    @staticmethod
    def arcade_cabinet(**kwargs: Any) -> RetroArcadeCrtCabinet:
        return RetroArcadeCrtCabinet(**kwargs)

    @staticmethod
    def pc_monitor(**kwargs: Any) -> BeigeCrtMonitor1990s:
        return BeigeCrtMonitor1990s(**kwargs)

    @staticmethod
    def portable_tv(**kwargs: Any) -> RetroPortableTvAntenna:
        return RetroPortableTvAntenna(**kwargs)
