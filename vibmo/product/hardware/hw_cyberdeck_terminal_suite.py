from __future__ import annotations
import math
from typing import Any, Optional, Tuple, Union

import cairo

from vibmo.scene.node import Node
from vibmo.core.color import Color, colors
from vibmo.layout.container import FlexContainer
from vibmo.spatial.shadows import DropShadow


class CyberdeckChassisFrame(Node):
    """
    Shock-absorbent industrial cyberdeck terminal chassis with hazard stripes,
    rubberized corner bumpers, optional mechanical switch keyboard deck, and auto-clipped screen.
    """
    def __init__(
        self,
        width: float = 700.0,
        height: float = 400.0,
        mechanical_switches: bool = False,
        shadow: Optional[Union[DropShadow, bool]] = True,
        **kwargs: Any
    ) -> None:
        super().__init__(**kwargs)
        self.width = float(width)
        self.height = float(height)
        self.mechanical_switches = mechanical_switches

        if shadow is True:
            self.shadow = DropShadow.elevated(blur=36.0, offset=(0, 18), color=Color.BLACK.with_alpha(0.50))
        elif isinstance(shadow, DropShadow):
            self.shadow = shadow
        else:
            self.shadow = None

        screen_h = self.height * 0.50 if self.mechanical_switches else self.height * 0.80
        self.screen = FlexContainer(
            direction="column",
            gap=8.0,
            padding=16.0,
            width=self.width - 100.0,
            height=screen_h,
            position=(50.0, 40.0),
            fill=Color.hex("#050914"),
            stroke=colors.CYAN_500.with_alpha(0.50),
            corner_radius=4.0,
        )
        self.add(self.screen)

    def add_screen(self, *nodes: Node) -> CyberdeckChassisFrame:
        """Add child nodes to the cyberdeck terminal viewport."""
        self.screen.add(*nodes)
        return self

    def add_screen_content(self, *nodes: Node) -> CyberdeckChassisFrame:
        """Alias for add_screen."""
        return self.add_screen(*nodes)

    def local_bounds(self, time: float = 0.0) -> Tuple[float, float, float, float]:
        return (0.0, 0.0, self.width, self.height)

    def draw(self, ctx: Any, time: float = 0.0) -> None:
        w = self.width
        h = self.height
        bw = 40.0

        ctx.save()

        # Drop shadow
        if self.shadow is not None and hasattr(ctx, "set_source_surface"):
            self.shadow.render_shadow(ctx, (0, 0, w, h), 10.0)

        # 1. Main case body (1 rect)
        ctx.set_source_rgba(*colors.SLATE_800.to_tuple_rgba())
        ctx.rectangle(0, 0, w, h)
        ctx.fill()

        # 2. Hazard stripe base (1 rect)
        ctx.set_source_rgba(*colors.YELLOW_500.to_tuple_rgba())
        ctx.rectangle(w / 2 - 100, 10, 200, 20)
        ctx.fill()

        # 3. Hazard stripes (10 rects)
        ctx.set_source_rgba(*colors.BLACK.to_tuple_rgba())
        for i in range(10):
            ctx.rectangle(w / 2 - 100 + i * 20, 10, 10, 20)
            ctx.fill()

        # 4. Corner bumpers (rubberized - 4 rects)
        ctx.set_source_rgba(*colors.SLATE_950.to_tuple_rgba())
        # Top-left
        ctx.rectangle(0, 0, bw, bw)
        ctx.fill()
        # Top-right
        ctx.rectangle(w - bw, 0, bw, bw)
        ctx.fill()
        # Bottom-left
        ctx.rectangle(0, h - bw, bw, bw)
        ctx.fill()
        # Bottom-right
        ctx.rectangle(w - bw, h - bw, bw, bw)
        ctx.fill()

        # Mechanical Switches Keyboard area (if enabled)
        if self.mechanical_switches:
            kb_y = h * 0.62
            ctx.set_source_rgba(*colors.SLATE_900.to_tuple_rgba())
            ctx.rectangle(50, kb_y, w - 100, h - kb_y - 20)
            ctx.fill()

            key_w, key_h = 32.0, 24.0
            gap = 6.0
            cols = int((w - 120) / (key_w + gap))
            rows = 3
            ctx.set_source_rgba(*colors.SLATE_700.to_tuple_rgba())
            for r in range(rows):
                for c in range(cols):
                    kx = 60 + c * (key_w + gap)
                    ky = kb_y + 10 + r * (key_h + gap)
                    ctx.rectangle(kx, ky, key_w, key_h)
                    ctx.fill()

        ctx.restore()


# Semantic alias
IndustrialBumperCase = CyberdeckChassisFrame


class PopUpLcdScreen(Node):
    """
    Angled ultra-wide articulating LCD screen connected via heavy metal hinges.
    """
    def __init__(self, width: float = 500.0, height: float = 250.0, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.width = float(width)
        self.height = float(height)

        self.screen = FlexContainer(
            direction="column",
            gap=4.0,
            padding=10.0,
            width=self.width - 20.0,
            height=self.height - 20.0,
            position=(10.0, 10.0),
            fill=colors.CYAN_500.with_alpha(0.85),
            stroke=Color.TRANSPARENT,
            corner_radius=2.0,
        )
        self.add(self.screen)

    def add_screen(self, *nodes: Node) -> PopUpLcdScreen:
        self.screen.add(*nodes)
        return self

    def add_screen_content(self, *nodes: Node) -> PopUpLcdScreen:
        return self.add_screen(*nodes)

    def local_bounds(self, time: float = 0.0) -> Tuple[float, float, float, float]:
        return (0.0, 0.0, self.width, self.height)

    def draw(self, ctx: Any, time: float = 0.0) -> None:
        w = self.width
        h = self.height

        ctx.save()

        # Metal hinges (2 rects)
        ctx.set_source_rgba(*colors.SLATE_700.to_tuple_rgba())
        ctx.rectangle(w * 0.2, h, 30, 20)
        ctx.fill()
        ctx.rectangle(w * 0.8 - 30, h, 30, 20)
        ctx.fill()

        # Screen bezel (1 rect)
        ctx.set_source_rgba(*colors.SLATE_950.to_tuple_rgba())
        ctx.rectangle(0, 0, w, h)
        ctx.fill()

        # Screen glow underlay (1 rect)
        ctx.set_source_rgba(*colors.CYAN_500.with_alpha(0.8).to_tuple_rgba())
        ctx.rectangle(10, 10, w - 20, h - 20)
        ctx.fill()

        ctx.restore()


class CyberdeckMechanicalKeyboard(Node):
    """
    Rugged industrial military-grade chassis with exposed mechanical keycaps and carry handle.
    """
    def __init__(self, width: float = 600.0, height: float = 200.0, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.width = float(width)
        self.height = float(height)

        self.screen = FlexContainer(
            direction="row",
            gap=4.0,
            padding=8.0,
            width=self.width - 40.0,
            height=self.height - 40.0,
            position=(20.0, 20.0),
            fill=Color.TRANSPARENT,
            stroke=Color.TRANSPARENT,
        )
        self.add(self.screen)

    def add_screen(self, *nodes: Node) -> CyberdeckMechanicalKeyboard:
        self.screen.add(*nodes)
        return self

    def local_bounds(self, time: float = 0.0) -> Tuple[float, float, float, float]:
        return (0.0, 0.0, self.width, self.height)

    def draw(self, ctx: Any, time: float = 0.0) -> None:
        w = self.width
        h = self.height

        ctx.save()

        # Chassis base
        ctx.set_source_rgba(*colors.SLATE_900.to_tuple_rgba())
        ctx.rectangle(0, 0, w, h)
        ctx.fill()

        # Carry handle
        ctx.set_source_rgba(*colors.SLATE_700.to_tuple_rgba())
        ctx.rectangle(-20, h / 2 - 40, 20, 80)
        ctx.fill()

        # Exposed mechanical keycaps
        keys_x = 15.0
        keys_y = 15.0
        key_w = 40.0
        key_h = 40.0
        gap = 10.0
        cols = int((w - 20) / (key_w + gap))
        rows = int((h - 20) / (key_h + gap))

        ctx.set_source_rgba(*colors.SLATE_800.to_tuple_rgba())
        for r in range(rows):
            for c in range(cols):
                kx = keys_x + c * (key_w + gap)
                ky = keys_y + r * (key_h + gap)
                ctx.rectangle(kx, ky, key_w, key_h)
                ctx.fill()

        ctx.restore()


class PatchCablesAndAntenna(Node):
    """
    Decorative coiled BNC patch cables and pivoting brass antenna.
    """
    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)

    def draw(self, ctx: Any, time: float = 0.0) -> None:
        ctx.save()

        # Coiled cable (5 arcs)
        ctx.set_source_rgba(*colors.RED_500.to_tuple_rgba())
        ctx.set_line_width(4)
        for i in range(5):
            ctx.arc(50 + i * 15, 50, 10, 0, math.pi * 2)
            ctx.stroke()

        # Brass antenna base
        ctx.set_source_rgba(*colors.AMBER_500.to_tuple_rgba())
        ctx.rectangle(150, 80, 20, 10)
        ctx.fill()

        # Pivoting brass antenna
        pivot_angle = math.sin(time) * 0.5
        ctx.save()
        ctx.translate(160, 80)
        ctx.rotate(pivot_angle)
        ctx.set_source_rgba(*colors.AMBER_500.to_tuple_rgba())
        ctx.move_to(0, 0)
        ctx.line_to(-2, -60)
        ctx.line_to(2, -60)
        ctx.close_path()
        ctx.fill()

        # Antenna tip (1 arc)
        ctx.set_source_rgba(*colors.RED_500.to_tuple_rgba())
        ctx.arc(0, -60, 4, 0, math.pi * 2)
        ctx.fill()
        ctx.restore()

        ctx.restore()


class CyberdeckTerminalSuite:
    """
    Suite factory for cyberpunk cyberdecks, pop-up LCDs, and patch antennas.
    """
    @staticmethod
    def chassis(mechanical_switches: bool = True, **kwargs: Any) -> CyberdeckChassisFrame:
        return CyberdeckChassisFrame(mechanical_switches=mechanical_switches, **kwargs)

    @staticmethod
    def popup_screen(**kwargs: Any) -> PopUpLcdScreen:
        return PopUpLcdScreen(**kwargs)

    @staticmethod
    def keyboard(**kwargs: Any) -> CyberdeckMechanicalKeyboard:
        return CyberdeckMechanicalKeyboard(**kwargs)

    @staticmethod
    def cables_antenna(**kwargs: Any) -> PatchCablesAndAntenna:
        return PatchCablesAndAntenna(**kwargs)
