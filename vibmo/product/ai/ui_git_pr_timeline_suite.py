"""
GitHub PR Timeline & Merge UI Suite for Vibmo / Motio.
Components:
- GitPrTimeline
- MergeStatusPill
- GitPullRequestCard
- CommitShaBadge
- CiCdCheckStatusPill
- MergeSquashButton
"""

from __future__ import annotations
import math
from typing import Any, Dict, List, Optional, Sequence, Tuple, Union
import cairo

from vibmo.core.color import Color, colors
from vibmo.core.vector import Vector2D
from vibmo.core.signal import Signal, AnimationAction
from vibmo.core.easing import Ease, EasingFunc
from vibmo.scene.node import Node
from vibmo.layout.container import FlexContainer
from vibmo.primitives.circle import Circle
from vibmo.primitives.rect import Rect, RoundedRect
from vibmo.typography.text import Text
from vibmo.spatial.shadows import DropShadow


class MergeStatusPill(FlexContainer):
    """Status badge showing 'Open', 'Merged', 'Draft', 'Closed' with icons and colors."""

    def __init__(
        self,
        status: str = "Open",
        **kwargs: Any,
    ) -> None:
        is_merged = status.lower() == "merged"
        pill_fill = Color(0.2, 0.1, 0.35, 0.9) if is_merged else Color(0.08, 0.28, 0.16, 0.9)
        pill_stroke = colors.PURPLE if is_merged else colors.EMERALD

        super().__init__(
            direction="row",
            gap=6.0,
            padding=(4.0, 10.0),
            corner_radius=12.0,
            fill=pill_fill,
            stroke=pill_stroke,
            stroke_width=1.0,
            align_items="center",
            **kwargs,
        )
        self.status = Signal(status, f"{self.name}.status")
        self.dot = Circle(radius=3.5, fill=pill_stroke)
        self.label = Text(status, font_size=11.0, color=colors.WHITE, bold=True)
        self.add(self.dot, self.label)


class CommitShaBadge(Node):
    """Git commit SHA badge (e.g. `e4f9b1c`) with commit message."""

    def __init__(
        self,
        sha: str = "7a89f2d",
        message: str = "feat: implement 15 AI UI suites with signal reactivity",
        author: str = "agent-m4",
        width: float = 580.0,
        height: float = 38.0,
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)
        self.sha = sha
        self.message = message
        self.author = author
        self.width_val = float(width)
        self.height_val = float(height)

    def draw(self, ctx: Any, time: float = 0.0) -> None:
        w, h = self.width_val, self.height_val
        ctx.save()
        r = 6.0
        ctx.new_path()
        ctx.arc(w - r, r, r, -math.pi * 0.5, 0)
        ctx.arc(w - r, h - r, r, 0, math.pi * 0.5)
        ctx.arc(r, h - r, r, math.pi * 0.5, math.pi)
        ctx.arc(r, r, r, math.pi, math.pi * 1.5)
        ctx.close_path()

        ctx.set_source_rgba(0.06, 0.09, 0.14, 0.7)
        ctx.fill_preserve()
        ctx.set_source_rgba(0.18, 0.24, 0.35, 0.5)
        ctx.set_line_width(1.0)
        ctx.stroke()

        # SHA badge
        ctx.select_font_face("Consolas", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
        ctx.set_font_size(11.0)
        ctx.set_source_rgba(0.2, 0.8, 1.0, 0.95)
        ctx.move_to(12.0, 23.0)
        ctx.show_text(self.sha)

        # Commit message
        ctx.select_font_face("Inter", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)
        ctx.set_font_size(12.0)
        ctx.set_source_rgba(0.88, 0.92, 0.98, 0.95)
        ctx.move_to(80.0, 23.0)
        preview_msg = self.message[:50] + ("..." if len(self.message) > 50 else "")
        ctx.show_text(preview_msg)

        # Author
        ctx.set_font_size(10.0)
        ctx.set_source_rgba(0.5, 0.6, 0.75, 0.8)
        ext = ctx.text_extents(self.author)
        ctx.move_to(w - ext.width - 14.0, 23.0)
        ctx.show_text(self.author)

        ctx.restore()


class CiCdCheckStatusPill(Node):
    """Status bar showing passing test suite checks (e.g. `✓ 67 checks passed in 3.7s`)."""

    def __init__(self, checks_count: int = 67, duration_str: str = "3.7s", width: float = 580.0, height: float = 38.0, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.checks_count = checks_count
        self.duration_str = duration_str
        self.width_val = float(width)
        self.height_val = float(height)

    def draw(self, ctx: Any, time: float = 0.0) -> None:
        w, h = self.width_val, self.height_val
        ctx.save()
        r = 6.0
        ctx.new_path()
        ctx.arc(w - r, r, r, -math.pi * 0.5, 0)
        ctx.arc(w - r, h - r, r, 0, math.pi * 0.5)
        ctx.arc(r, h - r, r, math.pi * 0.5, math.pi)
        ctx.arc(r, r, r, math.pi, math.pi * 1.5)
        ctx.close_path()

        ctx.set_source_rgba(0.04, 0.15, 0.09, 0.8)
        ctx.fill_preserve()
        ctx.set_source_rgba(0.1, 0.75, 0.4, 0.6)
        ctx.set_line_width(1.0)
        ctx.stroke()

        # Checkmark
        ctx.set_source_rgba(0.2, 0.95, 0.5, 0.95)
        ctx.select_font_face("Inter", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
        ctx.set_font_size(12.0)
        ctx.move_to(12.0, 23.0)
        ctx.show_text(f"✓ All {self.checks_count} checks passed ({self.duration_str})")
        ctx.restore()


class MergeSquashButton(Node):
    """GitHub style 'Squash and Merge' button with animated merge state."""

    def __init__(self, is_merged: bool = False, width: float = 180.0, height: float = 38.0, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.width_val = float(width)
        self.height_val = float(height)
        self.is_merged = Signal(1.0 if is_merged else 0.0, f"{self.name}.is_merged")

    def draw(self, ctx: Any, time: float = 0.0) -> None:
        w, h = self.width_val, self.height_val
        merged = self.is_merged.get(time) > 0.5

        ctx.save()
        r = 6.0
        ctx.new_path()
        ctx.arc(w - r, r, r, -math.pi * 0.5, 0)
        ctx.arc(w - r, h - r, r, 0, math.pi * 0.5)
        ctx.arc(r, h - r, r, math.pi * 0.5, math.pi)
        ctx.arc(r, r, r, math.pi, math.pi * 1.5)
        ctx.close_path()

        if merged:
            ctx.set_source_rgba(0.4, 0.15, 0.6, 0.95)
            ctx.fill()
            btn_text = "Merged & Closed"
        else:
            ctx.set_source_rgba(0.12, 0.55, 0.28, 0.95)
            ctx.fill()
            btn_text = "Squash and Merge"

        ctx.select_font_face("Inter", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
        ctx.set_font_size(11.5)
        ctx.set_source_rgba(1.0, 1.0, 1.0, 1.0)
        ext = ctx.text_extents(btn_text)
        ctx.move_to((w - ext.width) * 0.5, h * 0.5 + ext.height * 0.35)
        ctx.show_text(btn_text)
        ctx.restore()


class GitPullRequestCard(Node):
    """Header card for GitHub Pull Request."""

    def __init__(self, pr_number: int = 88, title: str = "feat(ai): Add Section 4 SaaS UI suites", status: str = "Open", width: float = 640.0, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.pr_number = pr_number
        self.title = title
        self.status = status
        self.width_val = float(width)
        self.height_val = 58.0

    def draw(self, ctx: Any, time: float = 0.0) -> None:
        ctx.save()
        # PR Title
        ctx.select_font_face("Inter", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
        ctx.set_font_size(15.0)
        ctx.set_source_rgba(0.95, 0.98, 1.0, 0.95)
        ctx.move_to(0.0, 24.0)
        ctx.show_text(f"#{self.pr_number} {self.title}")
        ctx.restore()


class GitPrTimeline(Node):
    """
    GitHub Pull Request Timeline Suite.
    Renders realistic GitHub PR interface with commit timeline, automated CI/CD checks,
    code review status, and animated merge squash sequence.
    """

    def __init__(
        self,
        pr_number: int = 88,
        title: str = "feat(ai): Add 15 AI & SaaS Interactive UI Suites",
        status: str = "Open",
        width: float = 680.0,
        height: float = 460.0,
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)
        self.pr_number = pr_number
        self.pr_title = title
        self.width_val = float(width)
        self.height_val = float(height)
        self.shadow = DropShadow(color=Color(0.0, 0.0, 0.0, 0.5), blur=32.0, offset=(0.0, 16.0))

        # Status Pill
        self.status_pill = MergeStatusPill(status=status)
        self.status_pill.position.set(Vector2D(self.width_val - 120.0, 24.0))
        self.add(self.status_pill)

        # Commits list
        self.commits = [
            CommitShaBadge(sha="a1c49e2", message="feat: add TokenStreamer and TreeOfThought", author="worker-m4", width=self.width_val - 48.0),
            CommitShaBadge(sha="f830d1b", message="test: add comprehensive pytest coverage for product ai", author="worker-m4", width=self.width_val - 48.0),
        ]
        for i, c in enumerate(self.commits):
            c.position.set(Vector2D(24.0, 85.0 + i * 46.0))
            self.add(c)

        # CI Checks
        self.ci_pill = CiCdCheckStatusPill(checks_count=67, duration_str="3.7s", width=self.width_val - 48.0)
        self.ci_pill.position.set(Vector2D(24.0, 185.0))
        self.add(self.ci_pill)

        # Merge Button
        self.merge_btn = MergeSquashButton(is_merged=(status.lower() == "merged"), width=170.0, height=36.0)
        self.merge_btn.position.set(Vector2D(24.0, 240.0))
        self.add(self.merge_btn)

    def animate_merge(self, duration: float = 1.2, ease: EasingFunc = Ease.out_quad) -> List[AnimationAction]:
        """
        Fluent generator animation verb to trigger the PR merge sequence.
        """
        return [
            self.merge_btn.is_merged.to(1.0, duration=duration, ease=ease),
            self.status_pill.status.to("Merged", duration=duration, ease=ease),
        ]

    def local_bounds(self, time: float = 0.0) -> Tuple[float, float, float, float]:
        return (0.0, 0.0, self.width_val, self.height_val)

    def draw(self, ctx: Any, time: float = 0.0) -> None:
        w, h = self.width_val, self.height_val
        ctx.save()

        # Container card
        r = 16.0
        ctx.new_path()
        ctx.arc(w - r, r, r, -math.pi * 0.5, 0)
        ctx.arc(w - r, h - r, r, 0, math.pi * 0.5)
        ctx.arc(r, h - r, r, math.pi * 0.5, math.pi)
        ctx.arc(r, r, r, math.pi, math.pi * 1.5)
        ctx.close_path()

        ctx.set_source_rgba(0.04, 0.06, 0.1, 0.95)
        ctx.fill_preserve()
        ctx.set_source_rgba(0.18, 0.25, 0.38, 0.8)
        ctx.set_line_width(1.5)
        ctx.stroke()

        # PR Header Title
        ctx.select_font_face("Inter", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
        ctx.set_font_size(14.0)
        ctx.set_source_rgba(0.95, 0.98, 1.0, 0.95)
        ctx.move_to(24.0, 42.0)
        ctx.show_text(f"#{self.pr_number}  {self.pr_title[:42]}...")

        # Divider
        ctx.set_source_rgba(0.2, 0.25, 0.35, 0.4)
        ctx.set_line_width(1.0)
        ctx.move_to(20.0, 64.0)
        ctx.line_to(w - 20.0, 64.0)
        ctx.stroke()

        super().draw(ctx, time)
        ctx.restore()
