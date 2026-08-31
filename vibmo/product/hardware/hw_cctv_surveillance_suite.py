from __future__ import annotations
import math
from datetime import datetime
from typing import Any, Optional, Sequence, Tuple, Union

import cairo

from vibmo.scene.node import Node
from vibmo.core.color import Color, colors
from vibmo.layout.container import FlexContainer


class CctvQuadViewOverlay(Node):
    """
    CCTV 4-camera multi-quadrant surveillance grid overlay with live timestamp,
    blinking REC indicators, camera tags, and nested screen viewports per quadrant.
    """
    def __init__(
        self,
        width: float = 1920.0,
        height: float = 1080.0,
        labels: Tuple[str, str, str, str] = (
            "CAM 01 - LOBBY",
            "CAM 02 - VAULT",
            "CAM 03 - HALLWAY",
            "CAM 04 - EXTERIOR"
        ),
        timestamp: bool = True,
        rec_indicator: bool = True,
        **kwargs: Any
    ) -> None:
        super().__init__(**kwargs)
        self.width = float(width)
        self.height = float(height)
        self.labels = labels
        self.show_timestamp = timestamp
        self.rec_indicator = rec_indicator
        self.line_color = Color.rgba(255, 255, 255, 180 / 255.0)
        self.text_color = Color.rgba(255, 255, 255, 220 / 255.0)
        self.rec_color = Color.rgba(255, 0, 0, 255 / 255.0)

        cw, ch = self.width / 2, self.height / 2
        self.screen_1 = FlexContainer(width=cw, height=ch, position=(0, 0), fill=Color.TRANSPARENT)
        self.screen_2 = FlexContainer(width=cw, height=ch, position=(cw, 0), fill=Color.TRANSPARENT)
        self.screen_3 = FlexContainer(width=cw, height=ch, position=(0, ch), fill=Color.TRANSPARENT)
        self.screen_4 = FlexContainer(width=cw, height=ch, position=(cw, ch), fill=Color.TRANSPARENT)

        self.screen = self.screen_1
        self.add(self.screen_1, self.screen_2, self.screen_3, self.screen_4)

    def add_screen(self, *nodes: Node, quadrant: int = 1) -> CctvQuadViewOverlay:
        """Add child nodes to specified quadrant screen viewport (1-4)."""
        target = [self.screen_1, self.screen_2, self.screen_3, self.screen_4][max(0, min(3, quadrant - 1))]
        target.add(*nodes)
        return self

    def add_screen_content(self, *nodes: Node) -> CctvQuadViewOverlay:
        """Alias for add_screen (adds to quadrant 1)."""
        return self.add_screen(*nodes, quadrant=1)

    def local_bounds(self, time: float = 0.0) -> Tuple[float, float, float, float]:
        return (0.0, 0.0, self.width, self.height)

    def draw(self, ctx: Any, time: float = 0.0) -> None:
        cw, ch = self.width / 2, self.height / 2

        ctx.save()

        # Grid lines
        ctx.set_source_rgba(self.line_color.r, self.line_color.g, self.line_color.b, self.line_color.a)
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

        if hasattr(ctx, "select_font_face"):
            ctx.select_font_face("monospace", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
        if hasattr(ctx, "set_font_size"):
            ctx.set_font_size(24)

        for qx, qy, label in quads:
            ctx.save()
            # Draw camera label
            ctx.set_source_rgba(self.text_color.r, self.text_color.g, self.text_color.b, self.text_color.a)
            ctx.move_to(qx + 20, qy + 40)
            if hasattr(ctx, "show_text"):
                ctx.show_text(label)

            # Draw REC indicator
            if self.rec_indicator:
                rec_blink = math.sin(time * 4.0) > 0
                if rec_blink:
                    ctx.set_source_rgba(self.rec_color.r, self.rec_color.g, self.rec_color.b, self.rec_color.a)
                    if hasattr(ctx, "arc"):
                        ctx.arc(qx + cw - 40, qy + 35, 8, 0, 2 * math.pi)
                        ctx.fill()
                    if hasattr(ctx, "move_to"):
                        ctx.move_to(qx + cw - 95, qy + 42)
                    if hasattr(ctx, "set_font_size"):
                        ctx.set_font_size(18)
                    if hasattr(ctx, "show_text"):
                        ctx.show_text("REC")

            # Draw timestamp
            if self.show_timestamp:
                ctx.set_source_rgba(self.text_color.r, self.text_color.g, self.text_color.b, self.text_color.a)
                if hasattr(ctx, "set_font_size"):
                    ctx.set_font_size(20)
                now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                ctx.move_to(qx + 20, qy + ch - 20)
                if hasattr(ctx, "show_text"):
                    ctx.show_text(now_str)

            ctx.restore()

        ctx.restore()


# Semantic alias
CctvQuadCameraGrid = CctvQuadViewOverlay


class PtzCameraTargetingHud(Node):
    """
    Pan-Tilt-Zoom security camera targeting reticle and auto-tracking bounding boxes.
    """
    def __init__(
        self,
        width: float = 1920.0,
        height: float = 1080.0,
        target_x: float = 960.0,
        target_y: float = 540.0,
        target_w: float = 180.0,
        target_h: float = 240.0,
        target_pos: Optional[Tuple[float, float]] = None,
        **kwargs: Any
    ) -> None:
        super().__init__(**kwargs)
        self.width = float(width)
        self.height = float(height)
        if target_pos is not None:
            self.target_x = float(target_pos[0])
            self.target_y = float(target_pos[1])
        else:
            self.target_x = float(target_x)
            self.target_y = float(target_y)
        self.target_w = float(target_w)
        self.target_h = float(target_h)
        self.color = Color.rgba(0, 255, 128, 200 / 255.0)

    def local_bounds(self, time: float = 0.0) -> Tuple[float, float, float, float]:
        return (0.0, 0.0, self.width, self.height)

    def draw(self, ctx: Any, time: float = 0.0) -> None:
        tx, ty = self.target_x, self.target_y
        tw, th = self.target_w, self.target_h

        ctx.save()
        ctx.set_source_rgba(self.color.r, self.color.g, self.color.b, self.color.a)
        ctx.set_line_width(2.0)

        # Crosshair Reticle
        if hasattr(ctx, "arc"):
            ctx.arc(tx, ty, 60, 0, 2 * math.pi)
        ctx.stroke()

        ctx.move_to(tx - 80, ty)
        ctx.line_to(tx - 10, ty)
        ctx.move_to(tx + 10, ty)
        ctx.line_to(tx + 80, ty)

        ctx.move_to(tx, ty - 80)
        ctx.line_to(tx, ty - 10)
        ctx.move_to(tx, ty + 10)
        ctx.line_to(tx, ty + 80)
        ctx.stroke()

        # Bounding box
        bl = min(30.0, tw * 0.3, th * 0.3)

        ctx.move_to(tx - tw / 2, ty - th / 2 + bl)
        ctx.line_to(tx - tw / 2, ty - th / 2)
        ctx.line_to(tx - tw / 2 + bl, ty - th / 2)

        ctx.move_to(tx + tw / 2 - bl, ty - th / 2)
        ctx.line_to(tx + tw / 2, ty - th / 2)
        ctx.line_to(tx + tw / 2, ty - th / 2 + bl)

        ctx.move_to(tx + tw / 2, ty + th / 2 - bl)
        ctx.line_to(tx + tw / 2, ty + th / 2)
        ctx.line_to(tx + tw / 2 - bl, ty + th / 2)

        ctx.move_to(tx - tw / 2 + bl, ty + th / 2)
        ctx.line_to(tx - tw / 2, ty + th / 2)
        ctx.line_to(tx - tw / 2, ty + th / 2 - bl)
        ctx.stroke()

        # Target ID tag
        if hasattr(ctx, "select_font_face"):
            ctx.select_font_face("monospace", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
        if hasattr(ctx, "set_font_size"):
            ctx.set_font_size(14)
        if hasattr(ctx, "move_to"):
            ctx.move_to(tx - tw / 2, ty - th / 2 - 10)
        if hasattr(ctx, "show_text"):
            ctx.show_text("ID: TARGET_OBJ_04 [LOCKED]")

        ctx.restore()


class BodyCamRecOverlay(Node):
    """
    Axon body camera overlay with officer ID badge, UTC timestamp watermark, and battery state.
    """
    def __init__(
        self,
        width: float = 1920.0,
        height: float = 1080.0,
        officer_id: str = "OFFICER: 4921",
        dept: str = "AXON BODY 3",
        **kwargs: Any
    ) -> None:
        super().__init__(**kwargs)
        self.width = float(width)
        self.height = float(height)
        self.officer_id = officer_id
        self.dept = dept
        self.text_color = Color.rgba(255, 255, 255, 220 / 255.0)

    def local_bounds(self, time: float = 0.0) -> Tuple[float, float, float, float]:
        return (0.0, 0.0, self.width, self.height)

    def draw(self, ctx: Any, time: float = 0.0) -> None:
        ctx.save()

        if hasattr(ctx, "select_font_face"):
            ctx.select_font_face("monospace", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
        if hasattr(ctx, "set_font_size"):
            ctx.set_font_size(32)
        ctx.set_source_rgba(self.text_color.r, self.text_color.g, self.text_color.b, self.text_color.a)

        dept_w = 200.0
        if hasattr(ctx, "text_extents"):
            dept_extents = ctx.text_extents(self.dept)
            dept_w = dept_extents.width

        ctx.move_to(self.width - dept_w - 40, 60)
        if hasattr(ctx, "show_text"):
            ctx.show_text(self.dept)

        now_str = datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ")
        time_w = 200.0
        if hasattr(ctx, "text_extents"):
            time_extents = ctx.text_extents(now_str)
            time_w = time_extents.width

        ctx.move_to(self.width - time_w - 40, 100)
        if hasattr(ctx, "show_text"):
            ctx.show_text(now_str)

        # Bottom left watermark
        ctx.move_to(40, self.height - 40)
        if hasattr(ctx, "show_text"):
            ctx.show_text(self.officer_id)

        ctx.restore()


class CctvSurveillanceSuite:
    """
    Suite factory for CCTV surveillance quad views, PTZ targeting HUDs, and body cam overlays.
    """
    @staticmethod
    def quad_view(timestamp: bool = True, rec_indicator: bool = True, **kwargs: Any) -> CctvQuadViewOverlay:
        return CctvQuadViewOverlay(timestamp=timestamp, rec_indicator=rec_indicator, **kwargs)

    @staticmethod
    def ptz_hud(**kwargs: Any) -> PtzCameraTargetingHud:
        return PtzCameraTargetingHud(**kwargs)

    @staticmethod
    def body_cam(**kwargs: Any) -> BodyCamRecOverlay:
        return BodyCamRecOverlay(**kwargs)
