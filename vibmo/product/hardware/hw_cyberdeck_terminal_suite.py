"""
Cyberpunk Cyberdeck Hardware Mockup Suite.
"""
from typing import Any
import math
from vibmo.scene.node import Node
from vibmo.core.color import Color, colors

class CyberdeckMechanicalKeyboard(Node):
    """Rugged industrial military-grade chassis with exposed mechanical keycaps and carry handle."""
    def __init__(self, width: float = 600, height: float = 200, **kwargs):
        super().__init__(**kwargs)
        self.width = width
        self.height = height

    def local_bounds(self, time: float = 0.0):
        return (0.0, 0.0, self.width, self.height)

    def draw(self, ctx: Any, time: float = 0.0) -> None:
        w = self.width
        h = self.height

        # Chassis base
        ctx.set_source_rgba(*colors.SLATE_900.to_tuple_rgba())
        ctx.rectangle(0, 0, w, h)
        ctx.fill()

        # Carry handle
        ctx.set_source_rgba(*colors.SLATE_700.to_tuple_rgba())
        ctx.rectangle(-20, h/2 - 40, 20, 80)
        ctx.fill()

        # Exposed mechanical keycaps
        keys_x = 15
        keys_y = 15
        key_w = 40
        key_h = 40
        gap = 10
        cols = int((w - 20) / (key_w + gap))
        rows = int((h - 20) / (key_h + gap))

        ctx.set_source_rgba(*colors.SLATE_800.to_tuple_rgba())
        for r in range(rows):
            for c in range(cols):
                kx = keys_x + c * (key_w + gap)
                ky = keys_y + r * (key_h + gap)
                ctx.rectangle(kx, ky, key_w, key_h)
                ctx.fill()


class PopUpLcdScreen(Node):
    """Angled ultra-wide articulating LCD screen connected via heavy metal hinges."""
    def __init__(self, width: float = 500, height: float = 250, **kwargs):
        super().__init__(**kwargs)
        self.width = width
        self.height = height

    def local_bounds(self, time: float = 0.0):
        return (0.0, 0.0, self.width, self.height)

    def draw(self, ctx: Any, time: float = 0.0) -> None:
        w = self.width
        h = self.height

        # Metal hinges
        ctx.set_source_rgba(*colors.SLATE_700.to_tuple_rgba())
        ctx.rectangle(w * 0.2, h, 30, 20)
        ctx.fill()
        ctx.rectangle(w * 0.8 - 30, h, 30, 20)
        ctx.fill()

        # Screen bezel
        ctx.set_source_rgba(*colors.SLATE_950.to_tuple_rgba())
        ctx.rectangle(0, 0, w, h)
        ctx.fill()

        # Screen glow/display area
        ctx.set_source_rgba(*colors.CYAN_500.with_alpha(0.8).to_tuple_rgba())
        ctx.rectangle(10, 10, w - 20, h - 20)
        ctx.fill()


class IndustrialBumperCase(Node):
    """Shock-absorbent rubberized corner bumpers and hazard stripe accents."""
    def __init__(self, width: float = 700, height: float = 400, **kwargs):
        super().__init__(**kwargs)
        self.width = width
        self.height = height

    def local_bounds(self, time: float = 0.0):
        return (0.0, 0.0, self.width, self.height)

    def draw(self, ctx: Any, time: float = 0.0) -> None:
        w = self.width
        h = self.height
        bw = 40 # bumper size

        # Main case body
        ctx.set_source_rgba(*colors.SLATE_800.to_tuple_rgba())
        ctx.rectangle(0, 0, w, h)
        ctx.fill()

        # Hazard stripe accents
        ctx.set_source_rgba(*colors.YELLOW_500.to_tuple_rgba())
        ctx.rectangle(w/2 - 100, 10, 200, 20)
        ctx.fill()
        ctx.set_source_rgba(*colors.BLACK.to_tuple_rgba())
        for i in range(10):
            ctx.rectangle(w/2 - 100 + i * 20, 10, 10, 20)
            ctx.fill()

        # Corner bumpers (rubberized)
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


class PatchCablesAndAntenna(Node):
    """Decorative coiled BNC patch cables and pivoting brass antenna."""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def draw(self, ctx: Any, time: float = 0.0) -> None:
        # Coiled cable
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

        # Antenna tip
        ctx.set_source_rgba(*colors.RED_500.to_tuple_rgba())
        ctx.arc(0, -60, 4, 0, math.pi * 2)
        ctx.fill()
        ctx.restore()
