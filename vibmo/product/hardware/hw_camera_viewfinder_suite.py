import math
from typing import Any
from vibmo.scene.node import Node
from vibmo.core.color import colors

class DslrCameraViewfinderHud(Node):
    def __init__(self, width: float = 1920, height: float = 1080, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.width = width
        self.height = height

    def draw(self, ctx: Any, time: float = 0.0) -> None:
        ctx.save()

        # Rule of thirds grid
        ctx.set_source_rgba(1, 1, 1, 0.3)
        ctx.set_line_width(1)
        for i in range(1, 3):
            # Vertical lines
            ctx.move_to(self.width * i / 3, 0)
            ctx.line_to(self.width * i / 3, self.height)
            # Horizontal lines
            ctx.move_to(0, self.height * i / 3)
            ctx.line_to(self.width, self.height * i / 3)
        ctx.stroke()

        # Autofocus target brackets
        ctx.set_source_rgba(1, 0, 0, 0.8) # Red AF brackets
        ctx.set_line_width(2)
        cx, cy = self.width / 2, self.height / 2
        bw, bh = 100, 80 # bracket width, height
        bl = 20 # bracket leg length

        # Top-left
        ctx.move_to(cx - bw/2, cy - bh/2 + bl)
        ctx.line_to(cx - bw/2, cy - bh/2)
        ctx.line_to(cx - bw/2 + bl, cy - bh/2)
        # Top-right
        ctx.move_to(cx + bw/2 - bl, cy - bh/2)
        ctx.line_to(cx + bw/2, cy - bh/2)
        ctx.line_to(cx + bw/2, cy - bh/2 + bl)
        # Bottom-right
        ctx.move_to(cx + bw/2, cy + bh/2 - bl)
        ctx.line_to(cx + bw/2, cy + bh/2)
        ctx.line_to(cx + bw/2 - bl, cy + bh/2)
        # Bottom-left
        ctx.move_to(cx - bw/2 + bl, cy + bh/2)
        ctx.line_to(cx - bw/2, cy + bh/2)
        ctx.line_to(cx - bw/2, cy + bh/2 - bl)
        ctx.stroke()

        # Text and Indicators at the bottom
        ctx.set_source_rgba(1, 1, 1, 0.9)
        ctx.select_font_face("monospace")
        ctx.set_font_size(24)

        # Shutter and ISO
        ctx.move_to(self.width * 0.1, self.height * 0.9)
        ctx.show_text("1/50  F2.8  ISO 800")

        # Battery icon
        bx, by = self.width * 0.8, self.height * 0.9 - 20
        ctx.rectangle(bx, by, 40, 20)
        ctx.stroke()
        ctx.rectangle(bx + 40, by + 5, 4, 10)
        ctx.fill()

        # VU Meters
        vx, vy = self.width * 0.9, self.height * 0.85
        ctx.set_source_rgba(0, 1, 0, 0.8) # Green levels
        ctx.rectangle(vx, vy, 10, 40)
        ctx.rectangle(vx + 15, vy, 10, 35)
        ctx.fill()

        ctx.restore()


class CinemaCameraCageRig(Node):
    def __init__(self, width: float = 600, height: float = 400, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.width = width
        self.height = height

    def draw(self, ctx: Any, time: float = 0.0) -> None:
        ctx.save()
        cx, cy = self.width / 2, self.height / 2

        ctx.set_line_width(4)
        ctx.set_source_rgba(0.2, 0.2, 0.2, 1.0)

        # Matte box (left side)
        ctx.rectangle(cx - 250, cy - 80, 50, 160)
        ctx.fill_preserve()
        ctx.stroke()

        # 15mm Rails (bottom)
        ctx.set_source_rgba(0.4, 0.4, 0.4, 1.0)
        ctx.rectangle(cx - 250, cy + 120, 500, 10) # Rail 1
        ctx.fill()
        ctx.rectangle(cx - 250, cy + 140, 500, 10) # Rail 2
        ctx.fill()

        # Camera Cage Frame
        ctx.set_source_rgba(0.3, 0.3, 0.3, 1.0)
        ctx.rectangle(cx - 150, cy - 100, 300, 200)
        ctx.stroke()

        # Top Handle
        ctx.rectangle(cx - 100, cy - 150, 200, 20)
        ctx.fill()
        ctx.rectangle(cx, cy - 150, 20, 50) # handle post
        ctx.fill()

        # Side Battery Plate (right side)
        ctx.rectangle(cx + 160, cy - 50, 40, 150)
        ctx.fill_preserve()
        ctx.set_source_rgba(0.1, 0.1, 0.1, 1.0)
        ctx.stroke()

        ctx.restore()


class DroneGimbalTelemetryHud(Node):
    def __init__(self, width: float = 1920, height: float = 1080, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.width = width
        self.height = height

    def draw(self, ctx: Any, time: float = 0.0) -> None:
        ctx.save()
        cx, cy = self.width / 2, self.height / 2

        ctx.set_source_rgba(0, 1, 0, 0.8) # Green HUD
        ctx.set_line_width(2)

        # Artificial horizon (Crosshair)
        ctx.move_to(cx - 150, cy)
        ctx.line_to(cx - 50, cy)
        ctx.move_to(cx - 50, cy)
        ctx.line_to(cx - 50, cy + 20)

        ctx.move_to(cx + 150, cy)
        ctx.line_to(cx + 50, cy)
        ctx.move_to(cx + 50, cy)
        ctx.line_to(cx + 50, cy + 20)
        ctx.stroke()

        # Pitch lines
        pitch_offset = math.sin(time) * 20
        for i in range(-2, 3):
            if i == 0: continue
            y = cy + i * 40 + pitch_offset
            w = 40 if abs(i) == 2 else 80
            ctx.move_to(cx - w, y)
            ctx.line_to(cx + w, y)
        ctx.stroke()

        # Altitude tape
        ctx.move_to(self.width * 0.85, self.height * 0.2)
        ctx.line_to(self.width * 0.85, self.height * 0.8)
        ctx.stroke()

        for i in range(11):
            y = self.height * 0.2 + (i / 10) * (self.height * 0.6)
            ctx.move_to(self.width * 0.85, y)
            ctx.line_to(self.width * 0.85 + 20, y)
        ctx.stroke()

        # GPS and Telemetry Text
        ctx.select_font_face("sans-serif")
        ctx.set_font_size(20)
        ctx.move_to(self.width * 0.8, self.height * 0.15)
        ctx.show_text("ALT: 120m  SPD: 15m/s")

        ctx.move_to(self.width * 0.1, self.height * 0.15)
        ctx.show_text("GPS: 12 SAT  BAT: 85%")

        ctx.restore()
