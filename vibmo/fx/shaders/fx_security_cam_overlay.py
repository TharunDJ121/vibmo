"""
✦ Vibmo Shaders: Security Camera / CCTV Surveillance HUD Overlay
Inspired by Remocn security-cam with customizable timestamp, REC indicator, crosshairs, and scanlines.
"""

from __future__ import annotations

import numpy as np
import cairo
import math
from typing import Any, Optional, Tuple

try:
    from vibmo.fx.filters import Filter
except ImportError:
    class Filter:
        def apply(self, rgba: np.ndarray, time: float = 0.0) -> np.ndarray:
            raise NotImplementedError


class SecurityCamOverlay(Filter):
    """
    Renders a realistic CCTV security camera surveillance HUD over the video.
    """
    def __init__(
        self,
        camera_name: str = "CAM 01 // MAIN LOBBY",
        show_rec: bool = True,
        show_timestamp: bool = True,
        show_crosshairs: bool = True,
        show_brackets: bool = True,
        scanlines: bool = True,
        tint_green: bool = False,
        **kwargs: Any,
    ):
        self.camera_name = camera_name
        self.show_rec = show_rec
        self.show_timestamp = show_timestamp
        self.show_crosshairs = show_crosshairs
        self.show_brackets = show_brackets
        self.scanlines = scanlines
        self.tint_green = tint_green

    def apply(self, rgba: np.ndarray, time: float = 0.0) -> np.ndarray:
        h, w, _ = rgba.shape
        out = rgba.copy()

        # Optional night-vision green tint
        if self.tint_green:
            gray = (
                0.299 * out[:, :, 0] +
                0.587 * out[:, :, 1] +
                0.114 * out[:, :, 2]
            )
            out[:, :, 0] = np.clip(gray * 0.15, 0, 255).astype(np.uint8)
            out[:, :, 1] = np.clip(gray * 1.1, 0, 255).astype(np.uint8)
            out[:, :, 2] = np.clip(gray * 0.25, 0, 255).astype(np.uint8)

        # Optional scanline rasterization
        if self.scanlines:
            y_indices = np.arange(h)
            scan_mask = (y_indices % 3 == 0)[:, None]
            out[scan_mask.squeeze(), :, :3] = (out[scan_mask.squeeze(), :, :3] * 0.7).astype(np.uint8)

        # Cairo HUD overlay
        surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, w, h)
        ctx = cairo.Context(surface)

        ctx.select_font_face("monospace", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)

        # 1. Top Left: Blinking REC indicator
        if self.show_rec:
            rec_blink = math.sin(time * math.pi * 2.0) > 0.0
            if rec_blink:
                # Red glowing circle
                ctx.set_source_rgba(1.0, 0.15, 0.15, 1.0)
                ctx.arc(60, 60, 10, 0, 2 * math.pi)
                ctx.fill()

                ctx.set_source_rgba(1.0, 0.2, 0.2, 0.9)
                ctx.set_font_size(24)
                ctx.move_to(80, 68)
                ctx.show_text("REC")

        # 2. Top Right: Camera Name & Format
        ctx.set_source_rgba(1.0, 1.0, 1.0, 0.85)
        ctx.set_font_size(20)
        cam_text = self.camera_name
        extents = ctx.text_extents(cam_text)
        ctx.move_to(w - extents.width - 60, 68)
        ctx.show_text(cam_text)

        # 3. Bottom Left: Dynamic Timestamp / Timecode
        if self.show_timestamp:
            total_seconds = int(time)
            frames = int((time - total_seconds) * 60)
            hours = total_seconds // 3600
            mins = (total_seconds % 3600) // 60
            secs = total_seconds % 60
            tc_str = f"2026-08-31  {hours:02d}:{mins:02d}:{secs:02d}:{frames:02d}  [LIVE]"
            ctx.set_source_rgba(1.0, 1.0, 1.0, 0.85)
            ctx.set_font_size(18)
            ctx.move_to(60, h - 50)
            ctx.show_text(tc_str)

        # 4. Bottom Right: Play indicator & battery
        ctx.set_font_size(18)
        hud_right = "PLAY ▶  HD 60FPS"
        ext_r = ctx.text_extents(hud_right)
        ctx.move_to(w - ext_r.width - 60, h - 50)
        ctx.show_text(hud_right)

        # 5. Corner Framing Brackets
        if self.show_brackets:
            ctx.set_source_rgba(1.0, 1.0, 1.0, 0.4)
            ctx.set_line_width(2.5)
            bracket_len = 40
            margin = 35

            # Top-Left
            ctx.move_to(margin, margin + bracket_len)
            ctx.line_to(margin, margin)
            ctx.line_to(margin + bracket_len, margin)

            # Top-Right
            ctx.move_to(w - margin - bracket_len, margin)
            ctx.line_to(w - margin, margin)
            ctx.line_to(w - margin, margin + bracket_len)

            # Bottom-Left
            ctx.move_to(margin, h - margin - bracket_len)
            ctx.line_to(margin, h - margin)
            ctx.line_to(margin + bracket_len, h - margin)

            # Bottom-Right
            ctx.move_to(w - margin - bracket_len, h - margin)
            ctx.line_to(w - margin, h - margin)
            ctx.line_to(w - margin, h - margin - bracket_len)

            ctx.stroke()

        # 6. Center Crosshairs
        if self.show_crosshairs:
            ctx.set_source_rgba(1.0, 1.0, 1.0, 0.25)
            ctx.set_line_width(1.5)
            cx, cy = w / 2.0, h / 2.0
            ch_len = 20

            ctx.move_to(cx - ch_len, cy)
            ctx.line_to(cx + ch_len, cy)
            ctx.move_to(cx, cy - ch_len)
            ctx.line_to(cx, cy + ch_len)
            ctx.stroke()

            ctx.arc(cx, cy, 35, 0, 2 * math.pi)
            ctx.stroke()

        buf = surface.get_data()
        hud_arr = np.ndarray(shape=(h, w, 4), dtype=np.uint8, buffer=buf)
        hud_rgba = hud_arr[:, :, [2, 1, 0, 3]]

        # Alpha composite HUD over frame
        alpha = hud_rgba[:, :, 3:4].astype(np.float32) / 255.0
        out_rgb = (out[:, :, :3].astype(np.float32) * (1.0 - alpha) +
                   hud_rgba[:, :, :3].astype(np.float32) * alpha)
        out[:, :, :3] = np.clip(out_rgb, 0, 255).astype(np.uint8)

        return out


class CctvSurveillanceHud(SecurityCamOverlay):
    """Alias for SecurityCamOverlay."""
    pass
