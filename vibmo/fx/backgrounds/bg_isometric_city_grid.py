import math
import cairo
from typing import Any
from vibmo.scene.node import Node

class IsometricCityGridBackdrop(Node):
    """Isometric 2.5D grid of minimalist building monoliths with glowing rooftop lights."""
    def __init__(self, grid_size=10, cell_size=40, **kwargs):
        super().__init__(**kwargs)
        # Setup grid size and elements
        self.grid_size = grid_size
        self.cell_size = cell_size

    def _apply_isometric_transform(self, ctx: cairo.Context):
        matrix = cairo.Matrix()
        matrix.scale(1, 0.5)
        matrix.rotate(math.pi / 4)
        ctx.transform(matrix)

    def draw(self, ctx: Any, time: float = 0.0) -> None:
        c = ctx
        c.save()

        self._apply_isometric_transform(c)

        t = time
        offset = (self.grid_size * self.cell_size) / 2
        c.translate(-offset, -offset)

        for i in range(self.grid_size):
            for j in range(self.grid_size):
                x = i * self.cell_size
                y = j * self.cell_size

                # Height variation based on position and time
                # In isometric projection, increasing height shifts Y up (negative Y direction in typical coordinates before transform, or draw an offset top face)
                # Since we already transformed context, actual height in 3D would just shift along screen Y,
                # but to do that while transformed we need to counter-transform or just shift along (-x, -y) equally to go "up".
                # To go straight up in the transformed space, we can translate by (-h, -h)

                h = 20 + 30 * (math.sin(t * 2 + i * 0.5 + j * 0.3) * 0.5 + 0.5)

                c.save()
                c.translate(x, y)

                # Draw front-left face (simplification)
                # Not strictly necessary for "minimalist" but better with height

                # Top face
                c.translate(-h, -h)
                c.rectangle(0, 0, self.cell_size * 0.8, self.cell_size * 0.8)
                c.set_source_rgba(0.2, 0.2, 0.3, 1.0)
                c.fill_preserve()

                # Rooftop light
                glow_intensity = 0.5 + 0.5 * math.sin(t * 5 + i * 1.2 + j * 0.8)
                c.set_source_rgba(0.0, 1.0, 1.0, glow_intensity)
                c.set_line_width(2)
                c.stroke()

                c.restore()

        c.restore()

class PulsingDataHighways(Node):
    """Glowing neon data packets racing along grid lines and intersecting pathways."""
    def __init__(self, grid_size=10, cell_size=40, **kwargs):
        super().__init__(**kwargs)
        self.grid_size = grid_size
        self.cell_size = cell_size

    def _apply_isometric_transform(self, ctx: cairo.Context):
        matrix = cairo.Matrix()
        matrix.scale(1, 0.5)
        matrix.rotate(math.pi / 4)
        ctx.transform(matrix)

    def draw(self, ctx: Any, time: float = 0.0) -> None:
        c = ctx
        c.save()

        self._apply_isometric_transform(c)

        t = time
        offset = (self.grid_size * self.cell_size) / 2
        c.translate(-offset, -offset)

        # Draw grid lines
        c.set_source_rgba(0.1, 0.1, 0.2, 0.5)
        c.set_line_width(1)
        for i in range(self.grid_size + 1):
            c.move_to(i * self.cell_size, 0)
            c.line_to(i * self.cell_size, self.grid_size * self.cell_size)
            c.move_to(0, i * self.cell_size)
            c.line_to(self.grid_size * self.cell_size, i * self.cell_size)
        c.stroke()

        # Draw data packets
        c.set_source_rgba(0.0, 1.0, 0.5, 0.8)
        c.set_line_width(3)
        for i in range(self.grid_size):
            # Horizontal highways
            if i % 2 == 0:
                pos = (t * 100 + i * 20) % (self.grid_size * self.cell_size)
                c.move_to(pos, i * self.cell_size)
                c.line_to(pos + 20, i * self.cell_size)
                c.stroke()
            # Vertical highways
            if i % 3 == 0:
                pos = (t * 120 + i * 30) % (self.grid_size * self.cell_size)
                c.move_to(i * self.cell_size, pos)
                c.line_to(i * self.cell_size, pos + 20)
                c.stroke()

        c.restore()

class ServerRackMatrixBackdrop(Node):
    """Isometric datacenter rack towers with blinking green/cyan status LEDs."""
    def __init__(self, grid_size=8, cell_size=50, **kwargs):
        super().__init__(**kwargs)
        self.grid_size = grid_size
        self.cell_size = cell_size

    def _apply_isometric_transform(self, ctx: cairo.Context):
        matrix = cairo.Matrix()
        matrix.scale(1, 0.5)
        matrix.rotate(math.pi / 4)
        ctx.transform(matrix)

    def draw(self, ctx: Any, time: float = 0.0) -> None:
        c = ctx
        c.save()

        self._apply_isometric_transform(c)

        t = time
        offset = (self.grid_size * self.cell_size) / 2
        c.translate(-offset, -offset)

        for i in range(self.grid_size):
            for j in range(self.grid_size):
                x = i * self.cell_size
                y = j * self.cell_size

                h = 40

                c.save()
                c.translate(x, y)
                c.translate(-h, -h)

                # Draw rack base
                c.rectangle(0, 0, self.cell_size * 0.7, self.cell_size * 0.7)
                c.set_source_rgba(0.15, 0.15, 0.15, 1.0)
                c.fill_preserve()
                c.set_source_rgba(0.3, 0.3, 0.3, 1.0)
                c.set_line_width(1)
                c.stroke()

                # Blinking LEDs
                # Simple grid of LEDs on the top face for effect
                c.set_line_width(2)
                for led_x in range(3):
                    for led_y in range(3):
                        lx = 10 + led_x * 10
                        ly = 10 + led_y * 10

                        # Randomish blinking
                        blink = math.sin(t * 10 + i * 3.1 + j * 7.4 + led_x * 1.2 + led_y * 0.9)
                        if blink > 0.5:
                            c.set_source_rgba(0.0, 1.0, 0.5, 0.9) # Green
                        elif blink < -0.5:
                            c.set_source_rgba(0.0, 0.8, 1.0, 0.9) # Cyan
                        else:
                            c.set_source_rgba(0.1, 0.1, 0.1, 1.0) # Off

                        c.move_to(lx, ly)
                        c.line_to(lx + 2, ly)
                        c.stroke()

                c.restore()

        c.restore()
