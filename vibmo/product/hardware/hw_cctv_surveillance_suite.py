"""
CCTV Surveillance & Security Monitoring Mockup Suite.
"""
from typing import Any, Optional, Tuple
import math
from datetime import datetime

import cairo

from vibmo.scene.node import Node
from vibmo.core.color import Color, colors

class CctvQuadCameraGrid(Node):
    def __init__(
        self,
        width: float = 1920.0,
        height: float = 1080.0,
        labels: Tuple[str, str, str, str] = ("CAM 01 - LOBBY", "CAM 02 - VAULT", "CAM 03 - HALLWAY", "CAM 04 - EXTERIOR"),
        **kwargs
    ):
        super().__init__(**kwargs)
        self.width = width
        self.height = height
        self.labels = labels
        self.line_color = Color.rgba(255, 255, 255, 180 / 255.0)
        self.text_color = Color.rgba(255, 255, 255, 220 / 255.0)
        self.rec_color = Color.rgba(255, 0, 0, 255 / 255.0)

    def local_bounds(self, time: float = 0.0) -> Tuple[float, float, float, float]:
        return (0.0, 0.0, self.width, self.height)

    def draw(self, ctx: Any, time: float = 0.0) -> None:
        cw, ch = self.width / 2, self.height / 2

        ctx.save()

        # Grid lines
        ctx.set_source_rgba(*(self.line_color.r, self.line_color.g, self.line_color.b, self.line_color.a))
        ctx.set_line_width(2.0)

        ctx.move_to(cw, 0)
        ctx.line_to(cw, self.height)

        ctx.move_to(0, ch)
        ctx.line_to(self.width, ch)
        ctx.stroke()

        # Quadrants
        quads = [
            (0, 0, self.labels[0]),
            (cw, 0, self.labels[1]),
            (0, ch, self.labels[2]),
            (cw, ch, self.labels[3])
        ]

        ctx.select_font_face("monospace", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
        ctx.set_font_size(24)

        for qx, qy, label in quads:
            ctx.save()
            ctx.translate(qx, qy)

            # Label
            ctx.set_source_rgba(*(self.text_color.r, self.text_color.g, self.text_color.b, self.text_color.a))
            ctx.move_to(30, 40)
            ctx.show_text(label)

            # Flashing REC
            # 1 Hz flash, visible when sin > 0
            if math.sin(time * math.pi * 2) > 0:
                ctx.set_source_rgba(*(self.rec_color.r, self.rec_color.g, self.rec_color.b, self.rec_color.a))
                ctx.arc(cw - 120, 32, 8, 0, 2 * math.pi)
                ctx.fill()

                ctx.move_to(cw - 100, 40)
                ctx.show_text("REC")

            # Timestamp
            now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            ctx.set_source_rgba(*(self.text_color.r, self.text_color.g, self.text_color.b, self.text_color.a))
            ctx.move_to(30, ch - 30)
            ctx.show_text(now_str)

            ctx.restore()

        ctx.restore()


class PtzCameraTargetingHud(Node):
    def __init__(
        self,
        width: float = 800.0,
        height: float = 600.0,
        target_x: float = 400.0,
        target_y: float = 300.0,
        target_w: float = 150.0,
        target_h: float = 200.0,
        **kwargs
    ):
        super().__init__(**kwargs)
        self.width = width
        self.height = height
        self.target_x = target_x
        self.target_y = target_y
        self.target_w = target_w
        self.target_h = target_h
        self.color = Color.rgba(0, 255, 0, 200 / 255.0)

    def local_bounds(self, time: float = 0.0) -> Tuple[float, float, float, float]:
        return (0.0, 0.0, self.width, self.height)

    def draw(self, ctx: Any, time: float = 0.0) -> None:
        ctx.save()

        ctx.set_source_rgba(*(self.color.r, self.color.g, self.color.b, self.color.a))
        ctx.set_line_width(2.0)

        # Center crosshair
        cx, cy = self.width / 2, self.height / 2

        ctx.move_to(cx - 50, cy)
        ctx.line_to(cx - 10, cy)
        ctx.move_to(cx + 10, cy)
        ctx.line_to(cx + 50, cy)

        ctx.move_to(cx, cy - 50)
        ctx.line_to(cx, cy - 10)
        ctx.move_to(cx, cy + 10)
        ctx.line_to(cx, cy + 50)

        ctx.stroke()

        # Target bounding box (animate with time if we wanted, but static for now or driven by signals)
        # Using a simple sine wave for movement if target coords aren't signals
        tx = self.target_x + math.sin(time) * 50
        ty = self.target_y + math.cos(time * 0.7) * 30

        ctx.set_line_width(3.0)

        # Draw corners
        corner_len = 20

        # Top-left
        ctx.move_to(tx, ty + corner_len)
        ctx.line_to(tx, ty)
        ctx.line_to(tx + corner_len, ty)

        # Top-right
        ctx.move_to(tx + self.target_w - corner_len, ty)
        ctx.line_to(tx + self.target_w, ty)
        ctx.line_to(tx + self.target_w, ty + corner_len)

        # Bottom-right
        ctx.move_to(tx + self.target_w, ty + self.target_h - corner_len)
        ctx.line_to(tx + self.target_w, ty + self.target_h)
        ctx.line_to(tx + self.target_w - corner_len, ty + self.target_h)

        # Bottom-left
        ctx.move_to(tx + corner_len, ty + self.target_h)
        ctx.line_to(tx, ty + self.target_h)
        ctx.line_to(tx, ty + self.target_h - corner_len)

        ctx.stroke()

        # ID Tag
        ctx.select_font_face("monospace", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
        ctx.set_font_size(14)
        ctx.move_to(tx, ty - 10)
        ctx.show_text("ID: UNKNOWN_OBJ [AUTO-TRACK]")

        ctx.restore()


class BodyCamRecOverlay(Node):
    def __init__(
        self,
        width: float = 1920.0,
        height: float = 1080.0,
        officer_id: str = "OFFICER: 4921",
        dept: str = "AXON BODY 3",
        **kwargs
    ):
        super().__init__(**kwargs)
        self.width = width
        self.height = height
        self.officer_id = officer_id
        self.dept = dept
        self.text_color = Color.rgba(255, 255, 255, 220 / 255.0)

    def local_bounds(self, time: float = 0.0) -> Tuple[float, float, float, float]:
        return (0.0, 0.0, self.width, self.height)

    def draw(self, ctx: Any, time: float = 0.0) -> None:
        ctx.save()

        ctx.select_font_face("monospace", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)

        # Top right watermark
        ctx.set_font_size(32)
        ctx.set_source_rgba(*(self.text_color.r, self.text_color.g, self.text_color.b, self.text_color.a))

        dept_extents = ctx.text_extents(self.dept)
        ctx.move_to(self.width - dept_extents.width - 40, 60)
        ctx.show_text(self.dept)

        now_str = datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ")
        time_extents = ctx.text_extents(now_str)
        ctx.move_to(self.width - time_extents.width - 40, 100)
        ctx.show_text(now_str)

        # Bottom left watermark
        ctx.move_to(40, self.height - 40)
        ctx.show_text(self.officer_id)

        ctx.restore()
