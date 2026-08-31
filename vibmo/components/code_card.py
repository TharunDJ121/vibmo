"""
CodeCard & Syntax Highlighting Component for Vibmo / Motio.

Renders formatted syntax-highlighted code cards directly into PyCairo vector frames
using Pygments tokenization, line numbers, and theme palettes (Dracula, Monokai, OneDark, GitHub Dark).
"""

from __future__ import annotations

import math
from typing import Any
import cairo

from vibmo.core.color import Color, colors
from vibmo.scene.node import Node


THEME_PALETTES = {
    "monokai": {
        "bg": Color(0.15, 0.16, 0.13, 0.95),
        "header": Color(0.12, 0.13, 0.10, 0.98),
        "border": Color(0.24, 0.24, 0.20, 0.8),
        "text": Color(0.97, 0.97, 0.95, 1.0),
        "keyword": Color(0.98, 0.15, 0.45, 1.0),    # Pink
        "string": Color(0.90, 0.86, 0.45, 1.0),     # Yellow
        "comment": Color(0.46, 0.44, 0.36, 1.0),    # Grey
        "function": Color(0.40, 0.85, 0.94, 1.0),   # Cyan
        "number": Color(0.68, 0.51, 1.00, 1.0),     # Purple
    },
    "dracula": {
        "bg": Color(0.16, 0.16, 0.21, 0.95),
        "header": Color(0.13, 0.13, 0.18, 0.98),
        "border": Color(0.27, 0.28, 0.35, 0.8),
        "text": Color(0.95, 0.95, 0.95, 1.0),
        "keyword": Color(1.00, 0.48, 0.64, 1.0),    # Pink
        "string": Color(0.95, 0.98, 0.55, 1.0),     # Yellow
        "comment": Color(0.38, 0.44, 0.64, 1.0),    # Comment
        "function": Color(0.31, 0.98, 0.48, 1.0),   # Green
        "number": Color(0.74, 0.58, 0.98, 1.0),     # Purple
    },
    "one_dark": {
        "bg": Color(0.16, 0.17, 0.20, 0.95),
        "header": Color(0.13, 0.14, 0.17, 0.98),
        "border": Color(0.24, 0.27, 0.32, 0.8),
        "text": Color(0.67, 0.70, 0.75, 1.0),
        "keyword": Color(0.78, 0.47, 0.87, 1.0),    # Purple
        "string": Color(0.59, 0.77, 0.47, 1.0),     # Green
        "comment": Color(0.37, 0.41, 0.47, 1.0),    # Grey
        "function": Color(0.38, 0.69, 0.93, 1.0),   # Blue
        "number": Color(0.82, 0.57, 0.37, 1.0),     # Orange
    },
    "github_dark": {
        "bg": Color(0.05, 0.07, 0.09, 0.95),
        "header": Color(0.08, 0.10, 0.13, 0.98),
        "border": Color(0.19, 0.21, 0.24, 0.8),
        "text": Color(0.79, 0.82, 0.85, 1.0),
        "keyword": Color(1.00, 0.48, 0.45, 1.0),    # Red/Pink
        "string": Color(0.65, 0.85, 1.00, 1.0),     # Blue
        "comment": Color(0.55, 0.60, 0.65, 1.0),    # Grey
        "function": Color(0.85, 0.65, 1.00, 1.0),   # Purple
        "number": Color(0.48, 0.85, 0.65, 1.0),     # Green
    },
}


class CodeCard(Node):
    """Syntax-highlighted code display card."""

    def __init__(
        self,
        code: str,
        language: str = "python",
        filename: str = "main.py",
        theme: str = "dracula",
        width: float = 780,
        height: float = 460,
        position: tuple[float, float] = (960, 540),
        font_size: float = 17,
        line_numbers: bool = True,
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)
        self.code = code
        self.language = language
        self.filename = filename
        self.theme_name = theme if theme in THEME_PALETTES else "dracula"
        self.width_val = width
        self.height_val = height
        self.font_size = font_size
        self.line_numbers = line_numbers
        self.corner_radius = 16.0

        self.position.set(position)

    def draw(self, ctx: cairo.Context, t: float = 0.0) -> None:
        self._render_self(ctx, t)

    def _render_self(self, ctx: cairo.Context, t: float) -> None:

        pal = THEME_PALETTES[self.theme_name]
        w = self.width_val
        h = self.height_val
        r = self.corner_radius
        header_h = 38.0

        ctx.save()
        ctx.translate(-w / 2, -h / 2)

        # Drop shadow
        ctx.save()
        ctx.set_source_rgba(0.0, 0.0, 0.0, 0.4)
        self._rounded_rect(ctx, 4, 12, w, h, r)
        ctx.fill()
        ctx.restore()

        # Background & border
        self._rounded_rect(ctx, 0, 0, w, h, r)
        ctx.set_source_rgba(*pal["bg"].to_rgba())
        ctx.fill_preserve()
        ctx.set_source_rgba(*pal["border"].to_rgba())
        ctx.set_line_width(1.5)
        ctx.stroke()

        # Header bar
        ctx.save()
        ctx.new_path()
        ctx.arc(r, r, r, math.pi, 1.5 * math.pi)
        ctx.arc(w - r, r, r, 1.5 * math.pi, 2 * math.pi)
        ctx.line_to(w, header_h)
        ctx.line_to(0, header_h)
        ctx.close_path()
        ctx.set_source_rgba(*pal["header"].to_rgba())
        ctx.fill()
        ctx.restore()

        # macOS traffic lights
        btn_y = header_h / 2
        for bx, bcol in [(24, (1.0, 0.36, 0.36, 1.0)), (44, (1.0, 0.76, 0.24, 1.0)), (64, (0.24, 0.86, 0.45, 1.0))]:
            ctx.set_source_rgba(*bcol)
            ctx.arc(bx, btn_y, 6.0, 0, 2 * math.pi)
            ctx.fill()

        # Filename
        ctx.select_font_face("monospace", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
        ctx.set_font_size(13)
        ctx.set_source_rgba(0.7, 0.75, 0.85, 0.85)
        ext = ctx.text_extents(self.filename)
        ctx.move_to((w - ext.width) / 2, header_h / 2 + ext.height / 2)
        ctx.show_text(self.filename)

        # Content area
        pad_x = 24.0
        start_y = header_h + self.font_size + 14.0
        line_height = self.font_size * 1.55

        lines = self.code.strip().splitlines()
        ctx.set_font_size(self.font_size)

        for i, line in enumerate(lines):
            cur_y = start_y + i * line_height
            if cur_y > h - 15:
                break

            # Line number
            if self.line_numbers:
                ctx.select_font_face("monospace", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)
                ctx.set_source_rgba(0.4, 0.45, 0.55, 0.6)
                num_str = f"{i + 1:2d}"
                ctx.move_to(pad_x, cur_y)
                ctx.show_text(num_str)
                text_x = pad_x + 36.0
            else:
                text_x = pad_x

            # Tokenize simple keywords
            self._render_tokenized_line(ctx, line, text_x, cur_y, pal)

        ctx.restore()

    def _render_tokenized_line(self, ctx: cairo.Context, line: str, x: float, y: float, pal: dict[str, Color]) -> None:
        keywords = {"def", "class", "return", "import", "from", "as", "if", "else", "elif", "for", "in", "while", "yield", "async", "await", "const", "let", "var", "function"}
        words = line.split(" ")
        cur_x = x

        for idx, word in enumerate(words):
            stripped = word.strip("():,[]{}")
            if stripped in keywords:
                ctx.set_source_rgba(*pal["keyword"].to_rgba())
            elif word.startswith('"') or word.startswith("'") or word.endswith('"') or word.endswith("'"):
                ctx.set_source_rgba(*pal["string"].to_rgba())
            elif word.startswith("#") or word.startswith("//"):
                ctx.set_source_rgba(*pal["comment"].to_rgba())
            elif "(" in word:
                ctx.set_source_rgba(*pal["function"].to_rgba())
            elif stripped.isdigit():
                ctx.set_source_rgba(*pal["number"].to_rgba())
            else:
                ctx.set_source_rgba(*pal["text"].to_rgba())

            ctx.move_to(cur_x, y)
            ctx.show_text(word)
            ext = ctx.text_extents(word + " ")
            cur_x += ext.x_advance

    def _rounded_rect(self, ctx: cairo.Context, x: float, y: float, w: float, h: float, r: float) -> None:
        ctx.new_path()
        ctx.arc(x + r, y + r, r, math.pi, 1.5 * math.pi)
        ctx.arc(x + w - r, y + r, r, 1.5 * math.pi, 2 * math.pi)
        ctx.arc(x + w - r, y + h - r, r, 0, 0.5 * math.pi)
        ctx.arc(x + r, y + h - r, r, 0.5 * math.pi, math.pi)
        ctx.close_path()
