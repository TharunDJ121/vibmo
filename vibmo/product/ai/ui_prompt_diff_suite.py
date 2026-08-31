"""
Prompt Diff & Versioning UI Suite for Vibmo / Motio.
Components:
- PromptDiffViewer (PromptDiffCard)
- SideBySideDiffPane
- InlineDiffHighlighter
- PromptTokenCostBadge
- MergePromptButton
"""

from __future__ import annotations
import difflib
import math
from typing import Any, Dict, List, Optional, Sequence, Tuple, Union
import cairo

from vibmo.core.color import Color, colors
from vibmo.core.vector import Vector2D
from vibmo.core.signal import Signal, AnimationAction
from vibmo.core.easing import Ease, EasingFunc
from vibmo.scene.node import Node
from vibmo.spatial.shadows import DropShadow


class PromptTokenCostBadge(Node):
    """Badge calculating estimated prompt token count and API inference cost."""

    def __init__(self, token_count: int = 142, cost_usd: float = 0.0028, width: float = 180.0, height: float = 30.0, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.token_count = Signal(float(token_count), f"{self.name}.token_count")
        self.cost_usd = Signal(float(cost_usd), f"{self.name}.cost_usd")
        self.width_val = float(width)
        self.height_val = float(height)

    def draw(self, ctx: Any, time: float = 0.0) -> None:
        w, h = self.width_val, self.height_val
        toks = int(self.token_count.get(time))
        cost = self.cost_usd.get(time)

        ctx.save()
        r = 6.0
        ctx.new_path()
        ctx.arc(w - r, r, r, -math.pi * 0.5, 0)
        ctx.arc(w - r, h - r, r, 0, math.pi * 0.5)
        ctx.arc(r, h - r, r, math.pi * 0.5, math.pi)
        ctx.arc(r, r, r, math.pi, math.pi * 1.5)
        ctx.close_path()

        ctx.set_source_rgba(0.08, 0.12, 0.18, 0.9)
        ctx.fill_preserve()
        ctx.set_source_rgba(0.2, 0.3, 0.45, 0.6)
        ctx.set_line_width(1.0)
        ctx.stroke()

        ctx.select_font_face("Inter", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
        ctx.set_font_size(11.0)
        ctx.set_source_rgba(0.2, 0.85, 1.0, 0.95)
        text = f"{toks} tokens (${cost:.4f})"
        ext = ctx.text_extents(text)
        ctx.move_to((w - ext.width) * 0.5, h * 0.5 + ext.height * 0.35)
        ctx.show_text(text)
        ctx.restore()


class MergePromptButton(Node):
    """Button to accept and merge prompt improvements."""

    def __init__(self, width: float = 140.0, height: float = 32.0, **kwargs: Any) -> None:
        super().__init__(**kwargs)
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

        ctx.set_source_rgba(0.12, 0.5, 0.25, 0.95)
        ctx.fill()

        ctx.select_font_face("Inter", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
        ctx.set_font_size(11.0)
        ctx.set_source_rgba(1.0, 1.0, 1.0, 1.0)
        text = "Accept Diff"
        ext = ctx.text_extents(text)
        ctx.move_to((w - ext.width) * 0.5, h * 0.5 + ext.height * 0.35)
        ctx.show_text(text)
        ctx.restore()


class InlineDiffHighlighter(Node):
    """Inline text block with highlighted added tokens (green) and removed tokens (red)."""

    def __init__(
        self,
        diff_tokens: Optional[List[Tuple[str, str]]] = None,
        width: float = 780.0,
        height: float = 120.0,
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)
        self.diff_tokens = diff_tokens or [
            ("equal", "You are an expert "),
            ("delete", "fast "),
            ("insert", "world-class aesthetic "),
            ("equal", "motion graphics engineer in Python."),
        ]
        self.width_val = float(width)
        self.height_val = float(height)
        self.highlight_progress = Signal(1.0, f"{self.name}.highlight_progress")

    def draw(self, ctx: Any, time: float = 0.0) -> None:
        prog = max(0.0, min(1.0, self.highlight_progress.get(time)))
        ctx.save()
        ctx.select_font_face("Consolas", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)
        ctx.set_font_size(12.5)

        x = 16.0
        y = 28.0
        line_h = 24.0

        for op, chunk in self.diff_tokens:
            ext = ctx.text_extents(chunk)
            if op == "insert":
                ctx.set_source_rgba(0.08, 0.3, 0.15, 0.85 * prog)
                ctx.rectangle(x - 2.0, y - ext.height - 3.0, ext.width + 4.0, ext.height + 6.0)
                ctx.fill()
                ctx.set_source_rgba(0.2, 0.95, 0.5, 0.95)
            elif op == "delete":
                ctx.set_source_rgba(0.35, 0.08, 0.1, 0.85 * prog)
                ctx.rectangle(x - 2.0, y - ext.height - 3.0, ext.width + 4.0, ext.height + 6.0)
                ctx.fill()
                ctx.set_source_rgba(1.0, 0.3, 0.4, 0.95)
            else:
                ctx.set_source_rgba(0.85, 0.9, 0.95, 0.9)

            ctx.move_to(x, y)
            ctx.show_text(chunk)
            x += ext.width

        ctx.restore()


class SideBySideDiffPane(Node):
    """Split-pane view comparing Version A (Original) vs Version B (Refined)."""

    def __init__(
        self,
        v1_text: str = "Generate landing page for SaaS",
        v2_text: str = "Generate high-converting, aesthetic motion landing page for AI SaaS",
        width: float = 780.0,
        height: float = 320.0,
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)
        self.v1_text = v1_text
        self.v2_text = v2_text
        self.width_val = float(width)
        self.height_val = float(height)
        self.highlight_sig = Signal(1.0, f"{self.name}.highlight_sig")

    def draw(self, ctx: Any, time: float = 0.0) -> None:
        w, h = self.width_val, self.height_val
        pane_w = (w - 20.0) * 0.5
        pane_h = h - 20.0
        r = 10.0
        hl = max(0.0, min(1.0, self.highlight_sig.get(time)))

        ctx.save()
        # Left Pane (v1)
        ctx.new_path()
        ctx.arc(pane_w - r, r, r, -math.pi * 0.5, 0)
        ctx.arc(pane_w - r, pane_h - r, r, 0, math.pi * 0.5)
        ctx.arc(r, pane_h - r, r, math.pi * 0.5, math.pi)
        ctx.arc(r, r, r, math.pi, math.pi * 1.5)
        ctx.close_path()

        ctx.set_source_rgba(0.03, 0.05, 0.09, 0.9)
        ctx.fill_preserve()
        ctx.set_source_rgba(0.18, 0.24, 0.35, 0.6)
        ctx.set_line_width(1.0)
        ctx.stroke()

        # Left Header
        ctx.select_font_face("Inter", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
        ctx.set_font_size(11.5)
        ctx.set_source_rgba(0.6, 0.7, 0.8, 0.85)
        ctx.move_to(16.0, 24.0)
        ctx.show_text("Version 1 (Original)")

        # Left Content
        ctx.select_font_face("Consolas", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)
        ctx.set_font_size(11.5)
        ctx.set_source_rgba(0.8, 0.85, 0.9, 0.9)
        ctx.move_to(16.0, 56.0)
        ctx.show_text(self.v1_text[:40])

        # Right Pane (v2)
        rx = pane_w + 20.0
        ctx.new_path()
        ctx.arc(rx + pane_w - r, r, r, -math.pi * 0.5, 0)
        ctx.arc(rx + pane_w - r, pane_h - r, r, 0, math.pi * 0.5)
        ctx.arc(rx + r, pane_h - r, r, math.pi * 0.5, math.pi)
        ctx.arc(rx + r, r, r, math.pi, math.pi * 1.5)
        ctx.close_path()

        if hl > 0.1:
            ctx.set_source_rgba(0.04, 0.08, 0.14, 0.95)
            ctx.fill_preserve()
            ctx.set_source_rgba(0.15, 0.5, 0.8, 0.8 * hl)
            ctx.set_line_width(1.5)
            ctx.stroke()
        else:
            ctx.set_source_rgba(0.03, 0.05, 0.09, 0.9)
            ctx.fill_preserve()
            ctx.set_source_rgba(0.18, 0.24, 0.35, 0.6)
            ctx.set_line_width(1.0)
            ctx.stroke()

        # Right Header
        ctx.select_font_face("Inter", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
        ctx.set_font_size(11.5)
        ctx.set_source_rgba(0.2, 0.85, 1.0, 0.95)
        ctx.move_to(rx + 16.0, 24.0)
        ctx.show_text("Version 2 (Optimized Diff)")

        # Right Content
        ctx.select_font_face("Consolas", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)
        ctx.set_font_size(11.5)
        ctx.set_source_rgba(0.2, 0.95, 0.5, 0.95)
        ctx.move_to(rx + 16.0, 56.0)
        ctx.show_text(self.v2_text[:40])

        ctx.restore()


class PromptDiffViewer(Node):
    """
    Prompt Diff & Semantic Versioning UI Suite.
    Renders side-by-side prompt comparisons, token delta highlighting,
    inference cost estimation badges, and merge decision controls.
    """

    def __init__(
        self,
        v1: str = "Analyze model weights and output predictions.",
        v2: str = "Analyze multi-head model weights, apply KV cache optimizations, and stream real-time predictions.",
        width: float = 840.0,
        height: float = 480.0,
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)
        self.v1 = v1
        self.v2 = v2
        self.width_val = float(width)
        self.height_val = float(height)
        self.shadow = DropShadow(color=Color(0.0, 0.0, 0.0, 0.5), blur=32.0, offset=(0.0, 16.0))

        # Side-by-side pane
        self.split_pane = SideBySideDiffPane(v1_text=v1, v2_text=v2, width=self.width_val - 48.0, height=260.0)
        self.split_pane.position.set(Vector2D(24.0, 80.0))
        self.add(self.split_pane)

        # Inline Highlighter below
        diff_tokens = self._compute_diff_tokens(v1, v2)
        self.highlighter = InlineDiffHighlighter(diff_tokens=diff_tokens, width=self.width_val - 48.0, height=80.0)
        self.highlighter.position.set(Vector2D(24.0, 360.0))
        self.add(self.highlighter)

        # Cost badge
        self.cost_badge = PromptTokenCostBadge(token_count=184, cost_usd=0.0036)
        self.cost_badge.position.set(Vector2D(self.width_val - 350.0, 24.0))
        self.add(self.cost_badge)

        # Merge button
        self.merge_btn = MergePromptButton(width=120.0, height=30.0)
        self.merge_btn.position.set(Vector2D(self.width_val - 150.0, 24.0))
        self.add(self.merge_btn)

    def _compute_diff_tokens(self, v1: str, v2: str) -> List[Tuple[str, str]]:
        words1 = v1.split()
        words2 = v2.split()
        matcher = difflib.SequenceMatcher(None, words1, words2)
        result = []
        for tag, i1, i2, j1, j2 in matcher.get_opcodes():
            if tag == "equal":
                result.append(("equal", " ".join(words1[i1:i2]) + " "))
            elif tag == "delete":
                result.append(("delete", " ".join(words1[i1:i2]) + " "))
            elif tag == "insert":
                result.append(("insert", " ".join(words2[j1:j2]) + " "))
            elif tag == "replace":
                result.append(("delete", " ".join(words1[i1:i2]) + " "))
                result.append(("insert", " ".join(words2[j1:j2]) + " "))
        return result

    def highlight_diffs(self, duration: float = 1.2, ease: EasingFunc = Ease.out_quad) -> List[AnimationAction]:
        """
        Fluent generator animation verb to illuminate prompt differences and update cost metrics.
        """
        self.highlighter.highlight_progress.set(0.0)
        self.split_pane.highlight_sig.set(0.0)
        return [
            self.highlighter.highlight_progress.to(1.0, duration=duration, ease=ease),
            self.split_pane.highlight_sig.to(1.0, duration=duration, ease=ease),
            self.cost_badge.token_count.to(240.0, duration=duration, ease=ease),
        ]

    def local_bounds(self, time: float = 0.0) -> Tuple[float, float, float, float]:
        return (0.0, 0.0, self.width_val, self.height_val)

    def draw(self, ctx: Any, time: float = 0.0) -> None:
        w, h = self.width_val, self.height_val
        ctx.save()

        # Canvas card
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

        # Header Title
        ctx.select_font_face("Inter", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
        ctx.set_font_size(15.0)
        ctx.set_source_rgba(0.95, 0.98, 1.0, 0.95)
        ctx.move_to(24.0, 42.0)
        ctx.show_text("Prompt Diff & Semantic Versioning")

        super().draw(ctx, time)
        ctx.restore()


PromptDiffCard = PromptDiffViewer
