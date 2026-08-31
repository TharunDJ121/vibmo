"""
Text rendering, Multi-line layout, Font resolution, and Precise Cairo Text Extents.
"""

from __future__ import annotations
import os
from typing import Any, Optional, Tuple, Union
import cairo
from vibmo.core.vector import Vector2D
from vibmo.core.color import Color, LinearGradient, colors
from vibmo.core.signal import Signal
from vibmo.scene.node import Node
from vibmo.importers.fonts import FontManager


class Text(Node):
    """Multi-line vector text node with font family, alignment, precise metrics, and gradient fills."""

    def __init__(
        self,
        text: str = "",
        font_size: float = 32.0,
        font_family: str = "Inter",
        bold: bool = False,
        italic: bool = False,
        color: Optional[Union[Color, LinearGradient, str]] = colors.WHITE,
        line_height: float = 1.3,
        align: str = "left",  # "left", "center", "right"
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)
        self.text = Signal(str(text), f"{self.name}.text")
        self.font_size = Signal(float(font_size), f"{self.name}.font_size")
        self.font_family = font_family
        self.bold = bold
        self.italic = italic
        
        resolved_color = Color.from_any(color) if isinstance(color, (str, Color)) else color
        self.color = Signal(resolved_color, f"{self.name}.color")
        self.line_height = line_height
        self.text_align = align.lower()

    def _setup_cairo_font(self, ctx: cairo.Context, font_size: float) -> None:
        font_path = FontManager.get_font_path(self.font_family, bold=self.bold, italic=self.italic)
        if font_path and os.path.exists(font_path):
            try:
                import freetype
                face = freetype.Face(font_path)
            except Exception:
                pass
        
        # Fallback to standard Cairo text selection
        slant = cairo.FONT_SLANT_ITALIC if self.italic else cairo.FONT_SLANT_NORMAL
        weight = cairo.FONT_WEIGHT_BOLD if self.bold else cairo.FONT_WEIGHT_NORMAL
        ctx.select_font_face(self.font_family, slant, weight)
        ctx.set_font_size(font_size)

    def local_bounds(self, time: float = 0.0) -> Tuple[float, float, float, float]:
        txt = str(self.text.get(time))
        if not txt:
            return (0.0, 0.0, 0.0, 0.0)

        fs = max(1.0, float(self.font_size.get(time)))
        lines = txt.split("\n")
        
        # Measure precise Cairo bounds
        surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, 1, 1)
        m_ctx = cairo.Context(surf)
        self._setup_cairo_font(m_ctx, fs)
        
        max_w = 0.0
        for line in lines:
            if line:
                ext = m_ctx.text_extents(line)
                max_w = max(max_w, ext.width)
            else:
                max_w = max(max_w, fs * 0.5)

        h = len(lines) * fs * self.line_height
        return (0.0, 0.0, max_w, h)

    def draw(self, ctx: Any, time: float = 0.0) -> None:
        txt = str(self.text.get(time))
        if not txt:
            return

        fs = max(1.0, float(self.font_size.get(time)))
        c = self.color.get(time)
        if c is None:
            return

        ctx.save()
        self._setup_cairo_font(ctx, fs)

        lines = txt.split("\n")
        line_spacing = fs * self.line_height
        y_offset = fs * 0.88  # True typographical baseline

        for line in lines:
            extents = ctx.text_extents(line)
            if self.text_align == "center":
                x_offset = -extents.width * 0.5
            elif self.text_align == "right":
                x_offset = -extents.width
            else:
                x_offset = 0.0


            if isinstance(c, Color):
                ctx.set_source_rgba(c.r, c.g, c.b, c.a)
            elif isinstance(c, LinearGradient):
                w = max(10.0, extents.width)
                pat = cairo.LinearGradient(
                    x_offset + c.start[0] * w, y_offset + c.start[1] * fs,
                    x_offset + c.end[0] * w, y_offset + c.end[1] * fs
                )
                for stop in c.stops:
                    pat.add_color_stop_rgba(stop.offset, stop.color.r, stop.color.g, stop.color.b, stop.color.a)
                ctx.set_source(pat)

            ctx.move_to(x_offset, y_offset)
            ctx.show_text(line)
            y_offset += line_spacing

        ctx.restore()

