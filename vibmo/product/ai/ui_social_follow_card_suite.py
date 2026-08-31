"""
✦ Vibmo AI Suites: X Social Follow Card & GitHub Stars Card
Inspired by Remocn x-follow-card & github-stars with interactive button clicks and metric increments.
"""

from __future__ import annotations

import math
from typing import Any, List, Optional, Tuple, Union
import cairo

from vibmo.core.color import Color, colors
from vibmo.core.signal import Signal, AnimationAction
from vibmo.core.easing import Ease
from vibmo.scene.node import Node
from vibmo.layout.container import FlexContainer
from vibmo.typography.text import Text
from vibmo.spatial.shadows import DropShadow
from vibmo.timeline.scheduler import all as sched_all, sequence as sched_seq


class XFollowCard(FlexContainer):
    """
    Social profile card with dynamic 'Follow' / 'Following' button click and follower increment.
    """
    def __init__(
        self,
        name: str = "Vibmo",
        handle: str = "@vibmo_ai",
        bio: str = "The AI-agent native semantic motion-design framework for Python.",
        followers_count: int = 14200,
        following_count: int = 42,
        width: float = 480.0,
        **kwargs: Any,
    ):
        super().__init__(
            direction="column",
            padding=(24, 28),
            gap=16,
            corner_radius=20.0,
            fill=Color(0.06, 0.08, 0.12, 0.98),
            stroke=Color(0.18, 0.22, 0.32, 0.8),
            stroke_width=1.0,
            shadow=DropShadow(color=Color(0, 0, 0, 0.4), blur=24.0, offset=(0, 10)),
            **kwargs,
        )
        self.base_followers = followers_count
        self.following_count = following_count
        self.is_following = Signal(0.0, f"{self.name}.is_following")

        # Top Row: Avatar & Follow Button
        top_row = FlexContainer(direction="row", justify="between", align_items="center")

        # Avatar + Name/Handle
        user_group = FlexContainer(direction="row", gap=12, align_items="center")
        avatar = FlexContainer(
            width=48,
            height=48,
            corner_radius=24,
            fill=colors.CYAN,
            justify="center",
            align_items="center",
        )
        avatar.add(Text(text="✦", font_size=24.0, font_family="Inter", color=colors.DARK_NAVY, bold=True))
        user_group.add(avatar)

        name_col = FlexContainer(direction="column", gap=2)
        name_col.add(Text(text=name, font_size=17.0, font_family="Inter", color=colors.WHITE, bold=True))
        name_col.add(Text(text=handle, font_size=13.0, font_family="Inter", color=Color(0.6, 0.65, 0.75, 1.0)))
        user_group.add(name_col)
        top_row.add(user_group)

        # Follow Button
        self.btn = FlexContainer(
            direction="row",
            padding=(8, 18),
            corner_radius=18.0,
            fill=colors.WHITE,
            justify="center",
            align_items="center",
        )
        self.btn_text = Text(
            text="Follow",
            font_size=14.0,
            font_family="Inter",
            color=Color(0.05, 0.05, 0.08, 1.0),
            bold=True,
        )
        self.btn.add(self.btn_text)
        top_row.add(self.btn)
        self.add(top_row)

        # Bio text
        self.add(Text(text=bio, font_size=14.0, font_family="Inter", color=Color(0.85, 0.9, 0.95, 1.0), line_height=1.35))

        # Metrics Row
        stats_row = FlexContainer(direction="row", gap=18, align_items="center")
        self.followers_stat_node = Text(
            text=f"{followers_count:,} Followers",
            font_size=13.5,
            font_family="Inter",
            color=colors.CYAN,
            bold=True,
        )
        following_stat = Text(
            text=f"{following_count} Following",
            font_size=13.5,
            font_family="Inter",
            color=Color(0.65, 0.7, 0.8, 1.0),
        )
        stats_row.add(self.followers_stat_node)
        stats_row.add(following_stat)
        self.add(stats_row)

    def click_follow(self, duration: float = 0.6) -> AnimationAction:
        """Simulates clicking Follow button and incrementing follower count."""
        return self.is_following.to(1.0, duration=duration, ease=Ease.out_back)

    def draw(self, ctx: Any, time: float = 0.0) -> None:
        prog = self.is_following.get(time)
        if prog >= 0.5:
            self.btn.fill.set(Color(0.12, 0.16, 0.24, 1.0))
            self.btn.stroke.set(Color(0.3, 0.4, 0.6, 0.8))
            self.btn.stroke_width.set(1.0)
            self.btn_text.text.set("Following ✓")
            self.btn_text.color.set(colors.WHITE)
            cur_count = self.base_followers + 1
        else:
            self.btn.fill.set(colors.WHITE)
            self.btn_text.text.set("Follow")
            self.btn_text.color.set(Color(0.05, 0.05, 0.08, 1.0))
            cur_count = self.base_followers

        self.followers_stat_node.text.set(f"{cur_count:,} Followers")
        super().draw(ctx, time)


class GitHubStarsCard(FlexContainer):
    """
    GitHub repository card with live star count animation and star button click.
    """
    def __init__(
        self,
        repo: str = "Remocn / remocn",
        description: str = "The shadcn registry for Remotion motion graphics.",
        stars_count: int = 4250,
        forks_count: int = 180,
        **kwargs: Any,
    ):
        super().__init__(
            direction="column",
            padding=(20, 24),
            gap=14,
            corner_radius=16.0,
            fill=Color(0.07, 0.09, 0.13, 0.98),
            stroke=Color(0.2, 0.24, 0.35, 0.8),
            stroke_width=1.0,
            shadow=DropShadow(color=Color(0, 0, 0, 0.35), blur=20.0, offset=(0, 8)),
            **kwargs,
        )
        self.base_stars = stars_count
        self.is_starred = Signal(0.0, f"{self.name}.is_starred")

        # Top: Repo name & Star button
        top = FlexContainer(direction="row", justify="between", align_items="center")
        top.add(Text(text=f"📁 {repo}", font_size=16.0, font_family="Inter", color=colors.CYAN, bold=True))

        self.star_btn = FlexContainer(
            direction="row",
            padding=(6, 14),
            gap=6,
            corner_radius=8.0,
            fill=Color(0.15, 0.18, 0.26, 1.0),
            stroke=Color(0.25, 0.32, 0.45, 0.8),
            stroke_width=1.0,
            align_items="center",
        )
        self.star_btn_text = Text(text="★ Star", font_size=13.0, font_family="Inter", color=colors.WHITE, bold=True)
        self.star_btn.add(self.star_btn_text)
        top.add(self.star_btn)
        self.add(top)

        # Description
        self.add(Text(text=description, font_size=13.5, font_family="Inter", color=Color(0.75, 0.8, 0.9, 1.0)))

        # Counts
        counts = FlexContainer(direction="row", gap=16, align_items="center")
        self.stars_text = Text(text=f"★ {stars_count:,} stars", font_size=13.0, font_family="Inter", color=Color(0.9, 0.75, 0.2, 1.0), bold=True)
        counts.add(self.stars_text)
        counts.add(Text(text=f"⑂ {forks_count} forks", font_size=13.0, font_family="Inter", color=Color(0.6, 0.65, 0.75, 1.0)))
        self.add(counts)

    def click_star(self, duration: float = 0.5) -> AnimationAction:
        """Simulates starring the repo."""
        return self.is_starred.to(1.0, duration=duration, ease=Ease.out_back)

    def draw(self, ctx: Any, time: float = 0.0) -> None:
        prog = self.is_starred.get(time)
        if prog >= 0.5:
            self.star_btn.fill.set(Color(0.9, 0.75, 0.2, 0.2))
            self.star_btn_text.text.set("★ Starred")
            self.star_btn_text.color.set(Color(1.0, 0.85, 0.3, 1.0))
            self.stars_text.text.set(f"★ {self.base_stars + 1:,} stars")
        else:
            self.star_btn.fill.set(Color(0.15, 0.18, 0.26, 1.0))
            self.star_btn_text.text.set("★ Star")
            self.star_btn_text.color.set(colors.WHITE)
            self.stars_text.text.set(f"★ {self.base_stars:,} stars")

        super().draw(ctx, time)
