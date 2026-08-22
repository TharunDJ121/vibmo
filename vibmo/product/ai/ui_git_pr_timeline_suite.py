"""
GitHub Pull Request Timeline & Merge UI Suite.
"""

from __future__ import annotations
import math
from typing import Any, Dict, Optional, Union

from vibmo.core.color import Color, colors
from vibmo.core.signal import Signal
from vibmo.scene.node import Node
from vibmo.layout.container import FlexContainer
from vibmo.typography.text import Text
from vibmo.importers.icons import Icon
from vibmo.primitives.circle import Circle
from vibmo.primitives.rect import Rect


class GitPullRequestCard(FlexContainer):
    """
    Header with PR title (e.g. '#104: Add 100 motion assets'),
    status pill ('Open' / 'Merged'), and author avatar.
    """
    def __init__(
        self,
        title: str = "#104: Add 100 motion assets",
        status: str = "Open",
        author_avatar_color: Union[Color, str] = colors.INDIGO,
        **kwargs: Any
    ):
        super().__init__(
            direction="row",
            gap=12,
            align_items="center",
            padding=16,
            corner_radius=8,
            fill=colors.SLATE_900,
            stroke=colors.SLATE_700,
            **kwargs
        )

        status_color = colors.GREEN if status.lower() == "open" else colors.PURPLE
        status_bg = status_color.with_alpha(0.2)

        self.status_pill = FlexContainer(
            direction="row",
            gap=6,
            padding=(4, 12),
            corner_radius=12,
            fill=status_bg,
            align_items="center"
        )
        status_icon_name = "lucide:git-pull-request" if status.lower() == "open" else "lucide:git-merge"
        self.status_icon = Icon(status_icon_name, size=14, color=status_color)
        self.status_text = Text(status, font_size=14, color=status_color, bold=True)
        self.status_pill.add(self.status_icon, self.status_text)

        self.title_text = Text(title, font_size=18, color=colors.SLATE_50, bold=True)

        self.avatar = Circle(radius=12, fill=author_avatar_color)

        self.add(self.status_pill, self.title_text, self.avatar)


class CommitShaBadge(FlexContainer):
    """
    Monospace commit SHA pill with commit message and branch arrow.
    """
    def __init__(
        self,
        sha: str = "a1b2c3d",
        message: str = "Update dependencies",
        **kwargs: Any
    ):
        super().__init__(
            direction="row",
            gap=8,
            align_items="center",
            padding=(6, 12),
            corner_radius=4,
            **kwargs
        )
        
        self.sha_pill = FlexContainer(
            padding=(4, 8),
            corner_radius=4,
            fill=colors.SLATE_800
        )
        self.sha_text = Text(sha, font_size=12, font_family="monospace", color=colors.SLATE_400)
        self.sha_pill.add(self.sha_text)

        self.message_text = Text(message, font_size=14, color=colors.SLATE_200)
        self.branch_arrow = Icon("lucide:arrow-right", size=14, color=colors.SLATE_400)

        self.add(self.sha_pill, self.message_text, self.branch_arrow)


class CiCdCheckStatusPill(FlexContainer):
    """
    Green checkmark / spinning amber check indicator ("All checks passed").
    """
    def __init__(
        self,
        status: str = "passed",  # "passed" or "pending"
        text: str = "All checks passed",
        **kwargs: Any
    ):
        super().__init__(
            direction="row",
            gap=8,
            align_items="center",
            padding=(8, 12),
            corner_radius=6,
            fill=colors.SLATE_800,
            **kwargs
        )
        
        icon_color = colors.GREEN if status == "passed" else colors.AMBER
        icon_name = "lucide:check-circle" if status == "passed" else "lucide:loader"
        self.icon = Icon(icon_name, size=16, color=icon_color)
        
        self.status_text = Text(text, font_size=14, color=colors.SLATE_200)

        self.add(self.icon, self.status_text)

    def draw(self, ctx: Any, time: float = 0.0) -> None:
        super().draw(ctx, time)


class MergeSquashButton(FlexContainer):
    """
    Vibrant green "Squash and Merge" button with dropdown arrow and confetti trigger.
    """
    def __init__(
        self,
        text: str = "Squash and Merge",
        **kwargs: Any
    ):
        super().__init__(
            direction="row",
            gap=0,
            align_items="stretch",
            padding=0,
            corner_radius=6,
            fill=colors.GREEN,
            **kwargs
        )
        
        self.main_btn = FlexContainer(
            direction="row",
            gap=8,
            align_items="center",
            padding=(8, 16),
            corner_radius=6
        )
        self.merge_icon = Icon("lucide:git-merge", size=16, color=colors.WHITE)
        self.btn_text = Text(text, font_size=14, color=colors.WHITE, bold=True)
        self.main_btn.add(self.merge_icon, self.btn_text)

        self.divider = Rect(width=1, height=32, fill=colors.BLACK.with_alpha(0.1))

        self.dropdown_btn = FlexContainer(
            align_items="center",
            justify_content="center",
            padding=(8, 12),
            corner_radius=6
        )
        self.dropdown_arrow = Icon("lucide:chevron-down", size=16, color=colors.WHITE)
        self.dropdown_btn.add(self.dropdown_arrow)

        self.add(self.main_btn, self.divider, self.dropdown_btn)

