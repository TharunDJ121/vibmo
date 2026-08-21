"""
Notification Toast Component for mobile and desktop alert mockups.
"""

from __future__ import annotations
from typing import Any, Optional, Union
from vibmo.core.color import Color, colors
from vibmo.layout.container import FlexContainer
from vibmo.importers.icons import Icon
from vibmo.typography.text import Text


class NotificationToast(FlexContainer):
    """Notification toast with icon, title, description, and glass styling."""

    def __init__(
        self,
        title: str = "Notification",
        description: str = "Operation completed successfully.",
        icon_name: str = "lucide:check",
        icon_color: Optional[Union[Color, str]] = colors.EMERALD,
        **kwargs: Any,
    ) -> None:
        super().__init__(
            direction="row",
            gap=16.0,
            padding=18.0,
            corner_radius=20.0,
            fill=Color.hex("#1E293B").with_alpha(0.85),
            stroke=Color.WHITE.with_alpha(0.15),
            stroke_width=1.5,
            align_items="center",
            **kwargs,
        )

        icon = Icon(icon_name, size=32.0, color=icon_color)

        text_col = FlexContainer(direction="column", gap=4.0, padding=0.0)
        t_node = Text(title, font_size=18.0, bold=True, color=colors.WHITE)
        d_node = Text(description, font_size=14.0, color=Color.hex("#94A3B8"))
        text_col.add(t_node, d_node)

        self.add(icon, text_col)
