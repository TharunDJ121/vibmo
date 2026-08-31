"""
TerminalWindow & Animated Terminal Session Node for Vibmo / Motio.

A native PyCairo-rendered interactive animated terminal window featuring:
  - macOS style window frame with traffic light window controls.
  - Character-by-character typing animation with blinking block caret.
  - Dynamic command output reveals with configurable hold durations.
  - Floating pill status badges (e.g., [✓ Success], [Building...]).
  - Smooth auto-scrolling buffer keeping latest execution output in view.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Any, Sequence
import cairo

from vibmo.core.color import Color, colors
from vibmo.core.signal import Signal
from vibmo.scene.node import Node


@dataclass
class TerminalStep:
    kind: str  # "cmd", "out", "pause", "pill"
    text: str = ""
    type_speed: float = 0.035  # seconds per char
    hold_seconds: float = 0.3
    color: Color | None = None
    duration: float = 2.0


class TerminalWindow(Node):
    """Native PyCairo animated terminal window component."""

    def __init__(
        self,
        title: str = "bash — 80x24",
        prompt: str = "user@vibmo:~$ ",
        steps: Sequence[TerminalStep | dict[str, Any]] | None = None,
        width: float = 840,
        height: float = 520,
        position: tuple[float, float] = (960, 540),
        font_size: float = 18,
        theme: str = "dark",
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)
        self.title = title
        self.prompt = prompt
        self.width_val = width
        self.height_val = height
        self.font_size = font_size
        self.theme = theme
        self.corner_radius = 16.0

        self.position.set(position)
        
        self.steps: list[TerminalStep] = []
        if steps:
            for s in steps:
                if isinstance(s, dict):
                    self.steps.append(
                        TerminalStep(
                            kind=s.get("kind", "cmd"),
                            text=s.get("text", ""),
                            type_speed=s.get("type_speed", s.get("typeSpeed", 0.035)),
                            hold_seconds=s.get("hold_seconds", s.get("holdSeconds", 0.3)),
                            color=s.get("color"),
                            duration=s.get("duration", 2.0),
                        )
                    )
                else:
                    self.steps.append(s)

        # Colors
        self.bg_color = Color(0.06, 0.08, 0.12, 0.95)
        self.header_color = Color(0.10, 0.13, 0.18, 0.98)
        self.border_color = Color(0.20, 0.25, 0.35, 0.8)
        self.text_color = Color(0.92, 0.95, 0.98, 1.0)
        self.prompt_color = Color(0.13, 0.83, 0.93, 1.0)  # Cyan
        self.output_color = Color(0.70, 0.75, 0.82, 0.9)
        self.cursor_color = Color(0.20, 0.85, 0.55, 1.0)  # Emerald

    def add_command(self, text: str, type_speed: float = 0.035, hold_seconds: float = 0.3) -> TerminalWindow:
        self.steps.append(TerminalStep(kind="cmd", text=text, type_speed=type_speed, hold_seconds=hold_seconds))
        return self

    def add_output(self, text: str, hold_seconds: float = 0.2) -> TerminalWindow:
        self.steps.append(TerminalStep(kind="out", text=text, hold_seconds=hold_seconds))
        return self

    def add_pause(self, seconds: float = 0.5) -> TerminalWindow:
        self.steps.append(TerminalStep(kind="pause", hold_seconds=seconds))
        return self

    def add_pill(self, text: str, color: Color = colors.EMERALD, duration: float = 2.0) -> TerminalWindow:
        self.steps.append(TerminalStep(kind="pill", text=text, color=color, duration=duration))
        return self

    def draw(self, ctx: cairo.Context, t: float = 0.0) -> None:
        self._render_self(ctx, t)

    def _render_self(self, ctx: cairo.Context, t: float) -> None:

        w = self.width_val
        h = self.height_val
        r = self.corner_radius
        header_h = 38.0

        ctx.save()
        # Translate to top-left of window relative to node center
        ctx.translate(-w / 2, -h / 2)

        # 1. Window Drop Shadow & Glow
        ctx.save()
        ctx.set_source_rgba(0.0, 0.0, 0.0, 0.45)
        self._rounded_rect(ctx, 4, 12, w, h, r)
        ctx.fill()
        ctx.restore()

        # 2. Main Window Background
        self._rounded_rect(ctx, 0, 0, w, h, r)
        ctx.set_source_rgba(*self.bg_color.to_rgba())
        ctx.fill_preserve()
        ctx.set_source_rgba(*self.border_color.to_rgba())
        ctx.set_line_width(1.5)
        ctx.stroke()

        # 3. Header Bar
        ctx.save()
        ctx.new_path()
        ctx.arc(r, r, r, math.pi, 1.5 * math.pi)
        ctx.arc(w - r, r, r, 1.5 * math.pi, 2 * math.pi)
        ctx.line_to(w, header_h)
        ctx.line_to(0, header_h)
        ctx.close_path()
        ctx.set_source_rgba(*self.header_color.to_rgba())
        ctx.fill()
        ctx.restore()

        # Traffic light buttons
        btn_y = header_h / 2
        colors_btn = [
            (24, btn_y, 6.0, (1.0, 0.36, 0.36, 1.0)),  # Red
            (44, btn_y, 6.0, (1.0, 0.76, 0.24, 1.0)),  # Yellow
            (64, btn_y, 6.0, (0.24, 0.86, 0.45, 1.0)),  # Green
        ]
        for bx, by, br, bcol in colors_btn:
            ctx.set_source_rgba(*bcol)
            ctx.arc(bx, by, br, 0, 2 * math.pi)
            ctx.fill()

        # Title
        ctx.select_font_face("monospace", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
        ctx.set_font_size(13)
        ctx.set_source_rgba(0.6, 0.65, 0.75, 0.8)
        ext = ctx.text_extents(self.title)
        ctx.move_to((w - ext.width) / 2, header_h / 2 + ext.height / 2)
        ctx.show_text(self.title)

        # 4. Terminal Content Area (Clipping)
        ctx.save()
        content_pad = 20.0
        clip_y = header_h + 10.0
        clip_h = h - clip_y - 15.0
        ctx.rectangle(content_pad, clip_y, w - 2 * content_pad, clip_h)
        ctx.clip()

        # Layout lines based on time `t`
        lines: list[tuple[str, Color, bool]] = []  # (text, color, is_cmd)
        pills: list[tuple[str, Color]] = []
        cursor = 0.0
        active_cmd_typing = False
        cursor_visible = (int(t * 3.0) % 2 == 0)

        for step in self.steps:
            if step.kind == "cmd":
                type_dur = len(step.text) * step.type_speed
                end_time = cursor + type_dur + step.hold_seconds
                if t >= cursor:
                    if t < cursor + type_dur:
                        # Partial typed string
                        chars = int((t - cursor) / step.type_speed)
                        typed_text = self.prompt + step.text[:chars]
                        lines.append((typed_text, self.text_color, True))
                        active_cmd_typing = True
                    else:
                        lines.append((self.prompt + step.text, self.text_color, True))
                cursor = end_time

            elif step.kind == "out":
                end_time = cursor + step.hold_seconds
                if t >= cursor:
                    lines.append((step.text, self.output_color, False))
                cursor = end_time

            elif step.kind == "pause":
                cursor += step.hold_seconds

            elif step.kind == "pill":
                if cursor <= t <= cursor + step.duration:
                    pill_col = step.color or self.cursor_color
                    pills.append((step.text, pill_col))

        # Render lines
        line_height = self.font_size * 1.5
        max_visible_lines = int(clip_h / line_height)
        start_line_idx = max(0, len(lines) - max_visible_lines)
        visible_lines = lines[start_line_idx:]

        draw_y = clip_y + self.font_size + 8.0
        ctx.select_font_face("monospace", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)
        ctx.set_font_size(self.font_size)

        for idx, (ltext, lcol, is_cmd) in enumerate(visible_lines):
            ctx.set_source_rgba(*lcol.to_rgba())
            ctx.move_to(content_pad + 6.0, draw_y)
            ctx.show_text(ltext)

            # If this is the last line and active or recent, draw block caret
            if idx == len(visible_lines) - 1 and cursor_visible:
                ext = ctx.text_extents(ltext)
                ctx.set_source_rgba(*self.cursor_color.to_rgba())
                ctx.rectangle(content_pad + 8.0 + ext.x_advance, draw_y - self.font_size + 2, self.font_size * 0.55, self.font_size)
                ctx.fill()

            draw_y += line_height

        # Render floating pills (top right of terminal)
        pill_x = w - content_pad - 10.0
        pill_y = header_h + 20.0
        for ptext, pcol in pills:
            ctx.set_font_size(13)
            ctx.select_font_face("sans-serif", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
            pext = ctx.text_extents(ptext)
            pw = pext.width + 24.0
            ph = 26.0
            px = pill_x - pw

            # Pill background
            self._rounded_rect(ctx, px, pill_y, pw, ph, 13.0)
            ctx.set_source_rgba(pcol.r, pcol.g, pcol.b, 0.25)
            ctx.fill_preserve()
            ctx.set_source_rgba(pcol.r, pcol.g, pcol.b, 0.9)
            ctx.set_line_width(1.2)
            ctx.stroke()

            # Pill text
            ctx.move_to(px + 12.0, pill_y + 17.5)
            ctx.set_source_rgba(1.0, 1.0, 1.0, 0.95)
            ctx.show_text(ptext)
            pill_y += ph + 8.0

        ctx.restore()
        ctx.restore()

    def _rounded_rect(self, ctx: cairo.Context, x: float, y: float, w: float, h: float, r: float) -> None:
        ctx.new_path()
        ctx.arc(x + r, y + r, r, math.pi, 1.5 * math.pi)
        ctx.arc(x + w - r, y + r, r, 1.5 * math.pi, 2 * math.pi)
        ctx.arc(x + w - r, y + h - r, r, 0, 0.5 * math.pi)
        ctx.arc(x + r, y + h - r, r, 0.5 * math.pi, math.pi)
        ctx.close_path()
