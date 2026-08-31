"""
Syntax Highlighted Code Block Component for Streaming Developer Demos.
"""

from __future__ import annotations
import re
from typing import Any, List, Optional, Tuple, Union
import cairo

from vibmo.core.color import Color, colors
from vibmo.core.vector import Vector2D
from vibmo.core.signal import Signal, AnimationAction
from vibmo.core.easing import Ease, EasingFunc
from vibmo.scene.node import Node


class SyntaxHighlightCode(Node):
    """
    Renders syntax-highlighted C/Python/TypeScript code with per-token color parsing,
    line numbering, and smooth vertical scrolling.
    """

    # Syntax color theme (Warm Amber / Dark Void)
    KEYWORD_COLOR = Color.from_hex("#ff7a45")   # Orange
    TYPE_COLOR = Color.from_hex("#fde047")      # Warm Gold
    STRING_COLOR = Color.from_hex("#86efac")    # Mint Green
    NUMBER_COLOR = Color.from_hex("#38bdf8")    # Cyan / Peach
    COMMENT_COLOR = Color.from_hex("#78716c")   # Warm Muted Gray
    DEFAULT_COLOR = Color.from_hex("#f5f5f4")   # Off-white

    KEYWORDS = {
        "struct", "var", "char", "int", "void", "return", "for", "if", "else", 
        "while", "class", "def", "async", "await", "import", "from", "export",
        "const", "let", "function", "public", "private", "typedef"
    }

    TYPES = {"User", "string", "bool", "float", "double", "size_t", "Node", "Vector2D", "Signal"}

    def __init__(
        self,
        code: str,
        font_size: float = 22.0,
        font_family: str = "Consolas",
        line_height: float = 1.45,
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)
        self.code_text = code
        self.font_size = float(font_size)
        self.font_family = font_family
        self.line_height = float(line_height)
        self.scroll_y = Signal(0.0, f"{self.name}.scroll_y")
        self.visible_lines = Signal(100.0, f"{self.name}.visible_lines")
        self._parsed_lines = self._parse_code(code)

    def _parse_code(self, code: str) -> List[List[Tuple[str, Color]]]:
        lines = []
        token_regex = re.compile(r'("(?:\\.|[^"\\])*"|\b\d+\b|\b[a-zA-Z_]\w*\b|//.*|/\*.*?\*/|[^\s\w]|\s+)')
        
        for raw_line in code.split("\n"):
            line_tokens = []
            for match in token_regex.finditer(raw_line):
                token = match.group(0)
                if token.startswith('"') and token.endswith('"'):
                    line_tokens.append((token, self.STRING_COLOR))
                elif token.startswith("//") or token.startswith("/*"):
                    line_tokens.append((token, self.COMMENT_COLOR))
                elif token.isdigit():
                    line_tokens.append((token, self.NUMBER_COLOR))
                elif token in self.KEYWORDS:
                    line_tokens.append((token, self.KEYWORD_COLOR))
                elif token in self.TYPES:
                    line_tokens.append((token, self.TYPE_COLOR))
                else:
                    line_tokens.append((token, self.DEFAULT_COLOR))
            lines.append(line_tokens)
        return lines

    def scroll_to(self, target_y: float, duration: float = 2.0, ease: EasingFunc = Ease.linear) -> AnimationAction:
        return self.scroll_y.to(float(target_y), duration=duration, ease=ease)

    def local_bounds(self, time: float = 0.0) -> Tuple[float, float, float, float]:
        lh = self.font_size * self.line_height
        total_h = len(self._parsed_lines) * lh
        return (0.0, 0.0, 900.0, total_h)

    def draw(self, ctx: Any, time: float = 0.0) -> None:
        ctx.save()
        ctx.select_font_face(self.font_family, cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)
        ctx.set_font_size(self.font_size)

        lh = self.font_size * self.line_height
        sy = float(self.scroll_y.get(time))
        ctx.translate(0.0, -sy)

        for line_idx, line in enumerate(self._parsed_lines):
            y = (line_idx + 1) * lh
            x = 0.0
            
            for token, color in line:
                ctx.set_source_rgba(color.r, color.g, color.b, color.a)
                ctx.move_to(x, y)
                ctx.show_text(token)
                ext = ctx.text_extents(token)
                x += ext.x_advance

        ctx.restore()
