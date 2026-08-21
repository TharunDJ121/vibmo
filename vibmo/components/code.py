"""
Code Window Terminal Mockup with traffic light buttons and syntax line displays.
"""

from __future__ import annotations
from typing import Any, Optional
from vibmo.core.color import Color, colors
from vibmo.layout.container import FlexContainer
from vibmo.primitives.circle import Circle
from vibmo.typography.text import Text
from vibmo.typography.kinetic import KineticText


class CodeWindow(FlexContainer):
    """macOS-styled terminal/code window frame with title and traffic light buttons."""

    def __init__(
        self,
        code: str = "",
        title: str = "script.py",
        font_size: float = 20.0,
        width: float = 650.0,
        **kwargs: Any,
    ) -> None:
        super().__init__(
            direction="column",
            gap=16.0,
            padding=20.0,
            corner_radius=18.0,
            fill=Color.hex("#0D1117").with_alpha(0.9),
            stroke=Color.WHITE.with_alpha(0.12),
            stroke_width=1.5,
            width=width,
            **kwargs,
        )

        # Header with traffic light dots
        header = FlexContainer(direction="row", gap=8.0, padding=0.0, align_items="center")
        dot_red = Circle(radius=6.0, fill=Color.hex("#FF5F56"))
        dot_yellow = Circle(radius=6.0, fill=Color.hex("#FFBD2E"))
        dot_green = Circle(radius=6.0, fill=Color.hex("#27C93F"))
        title_text = Text(title, font_size=14.0, font_family="Inter", color=Color.hex("#8B949E"))

        header.add(dot_red, dot_yellow, dot_green, title_text)

        # Code content
        self.code_node = KineticText(
            text=code,
            font_size=font_size,
            font_family="JetBrains Mono",
            color=Color.hex("#58A6FF"),
            line_height=1.4,
        )

        self.add(header, self.code_node)
