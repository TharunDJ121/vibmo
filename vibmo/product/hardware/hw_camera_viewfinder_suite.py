from __future__ import annotations
import math
from typing import Any, Optional, Tuple, Union

import cairo

from vibmo.scene.node import Node
from vibmo.core.color import Color, colors
from vibmo.layout.container import FlexContainer


class CameraViewfinderOverlay(Node):
    """
    Professional camera viewfinder HUD overlay with rule-of-thirds grid,
    autofocus brackets, battery indicator, audio VU meters, and underlying screen viewport.
    """
    def __init__(
        self,
        width: float = 1920.0,
        height: float = 1080.0,
        hud_style: str = "broadcast",
        rec_indicator: bool = True,
        **kwargs: Any
    ) -> None:
        super().__init__(**kwargs)
        self.width = float(width)
        self.height = float(height)
        self.hud_style = hud_style.lower()
        self.rec_indicator = rec_indicator

        self.screen = FlexContainer(
            direction="column",
            gap=0.0,
            padding=0.0,
            width=self.width,
            height=self.height,
            position=(0.0, 0.0),
            fill=Color.TRANSPARENT,
            stroke=Color.TRANSPARENT,
        )
        self.add(self.screen)

    def add_screen(self, *nodes: Node) -> CameraViewfinderOverlay:
        """Add child nodes to the viewfinder screen content."""
        self.screen.add(*nodes)
        return self

    def add_screen_content(self, *nodes: Node) -> CameraViewfinderOverlay:
        """Alias for add_screen."""
        return self.add_screen(*nodes)

    def local_bounds(self, time: float = 0.0) -> Tuple[float, float, float, float]:
        return (0.0, 0.0, self.width, self.height)

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
        ctx.set_source_rgba(1, 0, 0, 0.8)
        ctx.set_line_width(2)
        cx, cy = self.width / 2, self.height / 2
        bw, bh = 100.0, 80.0
        bl = 20.0

        # Top-left
        ctx.move_to(cx - bw / 2, cy - bh / 2 + bl)
        ctx.line_to(cx - bw / 2, cy - bh / 2)
        ctx.line_to(cx - bw / 2 + bl, cy - bh / 2)
        # Top-right
        ctx.move_to(cx + bw / 2 - bl, cy - bh / 2)
        ctx.line_to(cx + bw / 2, cy - bh / 2)
        ctx.line_to(cx + bw / 2, cy - bh / 2 + bl)
        # Bottom-right
        ctx.move_to(cx + bw / 2, cy + bh / 2 - bl)
        ctx.line_to(cx + bw / 2, cy + bh / 2)
        ctx.line_to(cx + bw / 2 - bl, cy + bh / 2)
        # Bottom-left
        ctx.move_to(cx - bw / 2 + bl, cy + bh / 2)
        ctx.line_to(cx - bw / 2, cy + bh / 2)
        ctx.line_to(cx - bw / 2, cy + bh / 2 - bl)
        ctx.stroke()

        # Text and Indicators at bottom
        ctx.set_source_rgba(1, 1, 1, 0.9)
        ctx.select_font_face("monospace")
        ctx.set_font_size(24)

        if self.hud_style == "broadcast":
            ctx.move_to(self.width * 0.1, self.height * 0.9)
            ctx.show_text("1/60  T1.8  ISO 800  5600K  RAW")
        else:
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
        ctx.set_source_rgba(0, 1, 0, 0.8)
        ctx.rectangle(vx, vy, 10, 40)
        ctx.rectangle(vx + 15, vy, 10, 35)
        ctx.fill()

        ctx.restore()


# Semantic alias
DslrCameraViewfinderHud = CameraViewfinderOverlay


class CinemaCameraCageRig(Node):
    """
    Cinema camera modular cage rig with matte box, 15mm rails, top handle, and battery plate.
    """
    def __init__(self, width: float = 600.0, height: float = 400.0, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.width = float(width)
        self.height = float(height)

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
        ctx.rectangle(cx - 250, cy + 120, 500, 10)
        ctx.fill()
        ctx.rectangle(cx - 250, cy + 140, 500, 10)
        ctx.fill()

        # Camera Cage Frame
        ctx.set_source_rgba(0.3, 0.3, 0.3, 1.0)
        ctx.rectangle(cx - 150, cy - 100, 300, 200)
        ctx.stroke()

        # Top Handle
        ctx.rectangle(cx - 100, cy - 150, 200, 20)
        ctx.fill()
        ctx.rectangle(cx, cy - 150, 20, 50)
        ctx.fill()

        # Side Battery Plate (right side)
        ctx.rectangle(cx + 160, cy - 50, 40, 150)
        ctx.fill_preserve()
        ctx.set_source_rgba(0.1, 0.1, 0.1, 1.0)
        ctx.stroke()

        ctx.restore()


class DroneGimbalTelemetryHud(Node):
    """
    UAV drone gimbal HUD with artificial horizon, pitch ladder, altitude tape, and telemetry status.
    """
    def __init__(self, width: float = 1920.0, height: float = 1080.0, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.width = float(width)
        self.height = float(height)

    def draw(self, ctx: Any, time: float = 0.0) -> None:
        ctx.save()
        cx, cy = self.width / 2, self.height / 2

        ctx.set_source_rgba(0, 1, 0, 0.8)
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
            if i == 0:
                continue
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


class CameraViewfinderSuite:
    """
    Suite factory for DSLR viewfinders, cinema camera rigs, and drone telemetry overlays.
    """
    @staticmethod
    def overlay(hud_style: str = "broadcast", **kwargs: Any) -> CameraViewfinderOverlay:
        return CameraViewfinderOverlay(hud_style=hud_style, **kwargs)

    @staticmethod
    def dslr_hud(**kwargs: Any) -> DslrCameraViewfinderHud:
        return DslrCameraViewfinderHud(**kwargs)

    @staticmethod
    def cinema_cage(**kwargs: Any) -> CinemaCameraCageRig:
        return CinemaCameraCageRig(**kwargs)

    @staticmethod
    def drone_hud(**kwargs: Any) -> DroneGimbalTelemetryHud:
        return DroneGimbalTelemetryHud(**kwargs)
