"""
UI Prompt Diff Suite
Components: PromptDiffCard, InlineDiffHighlighter, PromptTokenCostBadge, MergePromptButton.
"""

from __future__ import annotations
import math
import re
from typing import Any, Dict, List, Optional, Sequence, Tuple, Union
import cairo

from vibmo.core.vector import Vector2D
from vibmo.core.color import Color, colors
from vibmo.core.signal import Signal, AnimationAction
from vibmo.core.easing import Ease, EasingFunc
from vibmo.scene.node import Node
from vibmo.spatial.shadows import DropShadow


class PromptDiffCard(Node):
    """
    Split card showing 'Version A (Original)' vs 'Version B (Optimized)'.
    """

    def __init__(
        self,
        width: float = 800.0,
        height: float = 400.0,
        corner_radius: float = 16.0,
        bg_color: Union[Color, str] = "#0f172a", # SLATE_900
        border_color: Union[Color, str] = "#334155", # SLATE_700
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)
        self.w = float(width)
        self.h = float(height)
        self.corner_radius = corner_radius
        self.bg_color = Color.from_any(bg_color)
        self.border_color = Color.from_any(border_color)
        self.shadow = DropShadow.elevated(blur=24.0, offset=(0, 12), color=Color.hex("#000000").with_alpha(0.3))

    def _rounded_rect(self, ctx: cairo.Context, x: float, y: float, w: float, h: float, r: float) -> None:
        ctx.new_path()
        ctx.arc(x + w - r, y + r, r, -math.pi / 2, 0)
        ctx.arc(x + w - r, y + h - r, r, 0, math.pi / 2)
        ctx.arc(x + r, y + h - r, r, math.pi / 2, math.pi)
        ctx.arc(x + r, y + r, r, math.pi, 3 * math.pi / 2)
        ctx.close_path()

    def local_bounds(self, time: float = 0.0) -> Tuple[float, float, float, float]:
        return (0.0, 0.0, self.w, self.h)

    def draw(self, ctx: Any, time: float = 0.0) -> None:
        ctx.save()
        
        # Draw background
        self._rounded_rect(ctx, 0, 0, self.w, self.h, self.corner_radius)
        ctx.set_source_rgba(*self.bg_color.to_cairo())
        ctx.fill_preserve()
        ctx.set_line_width(2.0)
        ctx.set_source_rgba(*self.border_color.to_cairo())
        ctx.stroke()
        
        # Draw divider
        ctx.move_to(self.w / 2, 0)
        ctx.line_to(self.w / 2, self.h)
        ctx.set_source_rgba(*self.border_color.to_cairo())
        ctx.stroke()
        
        # Draw Titles
        ctx.select_font_face("sans-serif", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
        ctx.set_font_size(18)
        
        # Title A
        title_a = "Version A (Original)"
        ctx.set_source_rgba(*Color.hex("#94a3b8").to_cairo()) # SLATE_400
        extents_a = ctx.text_extents(title_a)
        ctx.move_to((self.w / 4) - (extents_a.width / 2), 30)
        ctx.show_text(title_a)
        
        # Title B
        title_b = "Version B (Optimized)"
        ctx.set_source_rgba(*Color.hex("#f8fafc").to_cairo()) # SLATE_50
        extents_b = ctx.text_extents(title_b)
        ctx.move_to((3 * self.w / 4) - (extents_b.width / 2), 30)
        ctx.show_text(title_b)
        
        ctx.restore()
        super().draw(ctx, time)


class InlineDiffHighlighter(Node):
    """
    Text block with highlighted green additions (+) and strike-through red deletions (-).
    """

    def __init__(
        self,
        text: str,
        font_size: float = 16.0,
        line_height: float = 24.0,
        width: float = 400.0,
        font_family: str = "monospace",
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)
        self.text = text
        self.font_size = font_size
        self.line_height = line_height
        self.w = float(width)
        self.font_family = font_family
        
        self.text_color = Color.hex("#e2e8f0") # SLATE_200
        self.add_color = Color.hex("#22c55e") # GREEN_500
        self.add_bg = Color.hex("#22c55e").with_alpha(0.2)
        self.del_color = Color.hex("#ef4444") # RED_500
        self.del_bg = Color.hex("#ef4444").with_alpha(0.2)
        
        self.parsed_lines = self._parse_diff(text)
        
    def _parse_diff(self, text: str) -> List[Tuple[str, str]]:
        # Returns list of (type, line) where type in ('normal', 'add', 'del')
        lines = []
        for line in text.split('\n'):
            if line.startswith('+'):
                lines.append(('add', line))
            elif line.startswith('-'):
                lines.append(('del', line))
            else:
                lines.append(('normal', line))
        return lines

    def local_bounds(self, time: float = 0.0) -> Tuple[float, float, float, float]:
        h = max(1, len(self.parsed_lines)) * self.line_height
        return (0.0, 0.0, self.w, h)

    def draw(self, ctx: Any, time: float = 0.0) -> None:
        ctx.save()
        ctx.select_font_face(self.font_family, cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)
        ctx.set_font_size(self.font_size)
        
        y = 0.0
        for ltype, line in self.parsed_lines:
            # Draw bg if needed
            if ltype == 'add':
                ctx.rectangle(0, y, self.w, self.line_height)
                ctx.set_source_rgba(*self.add_bg.to_cairo())
                ctx.fill()
                ctx.set_source_rgba(*self.add_color.to_cairo())
            elif ltype == 'del':
                ctx.rectangle(0, y, self.w, self.line_height)
                ctx.set_source_rgba(*self.del_bg.to_cairo())
                ctx.fill()
                ctx.set_source_rgba(*self.del_color.to_cairo())
            else:
                ctx.set_source_rgba(*self.text_color.to_cairo())
                
            # Draw text
            extents = ctx.text_extents(line)
            text_y = y + (self.line_height + extents.height) / 2.0
            ctx.move_to(8.0, text_y)
            ctx.show_text(line)
            
            # Strike-through for del
            if ltype == 'del':
                strike_y = text_y - extents.height / 2.0 + 2.0
                ctx.move_to(8.0, strike_y)
                ctx.line_to(8.0 + extents.width, strike_y)
                ctx.set_line_width(1.5)
                ctx.stroke()
            
            y += self.line_height
            
        ctx.restore()
        super().draw(ctx, time)


class PromptTokenCostBadge(Node):
    """
    Comparative badge showing token count reduction and cost savings (-38% tokens).
    """

    def __init__(
        self,
        reduction_text: str = "-38% tokens",
        cost_savings: str = "$0.04 saved",
        width: float = 240.0,
        height: float = 48.0,
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)
        self.reduction_text = reduction_text
        self.cost_savings = cost_savings
        self.w = float(width)
        self.h = float(height)
        
    def _rounded_rect(self, ctx: cairo.Context, x: float, y: float, w: float, h: float, r: float) -> None:
        ctx.new_path()
        ctx.arc(x + w - r, y + r, r, -math.pi / 2, 0)
        ctx.arc(x + w - r, y + h - r, r, 0, math.pi / 2)
        ctx.arc(x + r, y + h - r, r, math.pi / 2, math.pi)
        ctx.arc(x + r, y + r, r, math.pi, 3 * math.pi / 2)
        ctx.close_path()

    def local_bounds(self, time: float = 0.0) -> Tuple[float, float, float, float]:
        return (0.0, 0.0, self.w, self.h)

    def draw(self, ctx: Any, time: float = 0.0) -> None:
        ctx.save()
        
        self._rounded_rect(ctx, 0, 0, self.w, self.h, self.h / 2)
        # Background gradient: slightly green
        pat = cairo.LinearGradient(0, 0, self.w, 0)
        pat.add_color_stop_rgba(0.0, *Color.hex("#064e3b").with_alpha(0.8).to_cairo())
        pat.add_color_stop_rgba(1.0, *Color.hex("#0f766e").with_alpha(0.8).to_cairo())
        ctx.set_source(pat)
        ctx.fill_preserve()
        
        ctx.set_line_width(1.5)
        ctx.set_source_rgba(*Color.hex("#10b981").with_alpha(0.5).to_cairo())
        ctx.stroke()
        
        ctx.select_font_face("sans-serif", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
        ctx.set_font_size(14)
        
        # Draw reduction text
        ctx.set_source_rgba(*Color.hex("#34d399").to_cairo())
        r_extents = ctx.text_extents(self.reduction_text)
        
        # Draw cost savings text
        ctx.set_source_rgba(*Color.hex("#a7f3d0").to_cairo())
        c_extents = ctx.text_extents(self.cost_savings)
        
        total_w = r_extents.width + 12 + c_extents.width
        start_x = (self.w - total_w) / 2
        
        text_y = (self.h + r_extents.height) / 2 - 2
        
        ctx.set_source_rgba(*Color.hex("#34d399").to_cairo())
        ctx.move_to(start_x, text_y)
        ctx.show_text(self.reduction_text)
        
        # Divider dot
        ctx.arc(start_x + r_extents.width + 6, self.h / 2, 2.0, 0, 2 * math.pi)
        ctx.set_source_rgba(*Color.hex("#10b981").to_cairo())
        ctx.fill()
        
        ctx.set_source_rgba(*Color.hex("#a7f3d0").to_cairo())
        ctx.move_to(start_x + r_extents.width + 12, text_y)
        ctx.show_text(self.cost_savings)
        
        ctx.restore()
        super().draw(ctx, time)


class MergePromptButton(Node):
    """
    High-converting gradient action button to accept changes.
    """

    def __init__(
        self,
        label: str = "Accept Optimization",
        width: float = 280.0,
        height: float = 56.0,
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)
        self.label = label
        self.w = float(width)
        self.h = float(height)
        
        # Gradient colors
        self.color_start = Color.hex("#6366f1") # INDIGO_500
        self.color_end = Color.hex("#a855f7") # PURPLE_500
        
        # Scale signal for interaction/pop in
        self.scale_sig = Signal(1.0, f"{self.name}.scale")
        
        self.shadow = DropShadow.elevated(blur=16.0, offset=(0, 8), color=Color.hex("#6366f1").with_alpha(0.4))

    def local_bounds(self, time: float = 0.0) -> Tuple[float, float, float, float]:
        return (0.0, 0.0, self.w, self.h)
        
    def _rounded_rect(self, ctx: cairo.Context, x: float, y: float, w: float, h: float, r: float) -> None:
        ctx.new_path()
        ctx.arc(x + w - r, y + r, r, -math.pi / 2, 0)
        ctx.arc(x + w - r, y + h - r, r, 0, math.pi / 2)
        ctx.arc(x + r, y + h - r, r, math.pi / 2, math.pi)
        ctx.arc(x + r, y + r, r, math.pi, 3 * math.pi / 2)
        ctx.close_path()

    def draw(self, ctx: Any, time: float = 0.0) -> None:
        ctx.save()
        
        scale = self.scale_sig.get(time)
        if scale != 1.0:
            ctx.translate(self.w / 2, self.h / 2)
            ctx.scale(scale, scale)
            ctx.translate(-self.w / 2, -self.h / 2)
            
        self._rounded_rect(ctx, 0, 0, self.w, self.h, self.h / 2)
        
        pat = cairo.LinearGradient(0, 0, self.w, 0)
        pat.add_color_stop_rgba(0.0, *self.color_start.to_cairo())
        pat.add_color_stop_rgba(1.0, *self.color_end.to_cairo())
        ctx.set_source(pat)
        ctx.fill()
        
        # Shine
        ctx.save()
        self._rounded_rect(ctx, 0, 0, self.w, self.h, self.h / 2)
        ctx.clip()
        shine_pat = cairo.LinearGradient(0, 0, 0, self.h / 2)
        shine_pat.add_color_stop_rgba(0.0, 1.0, 1.0, 1.0, 0.2)
        shine_pat.add_color_stop_rgba(1.0, 1.0, 1.0, 1.0, 0.0)
        ctx.set_source(shine_pat)
        ctx.rectangle(0, 0, self.w, self.h / 2)
        ctx.fill()
        ctx.restore()
        
        # Label text
        ctx.select_font_face("sans-serif", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
        ctx.set_font_size(18)
        ctx.set_source_rgba(1.0, 1.0, 1.0, 1.0)
        
        extents = ctx.text_extents(self.label)
        text_x = (self.w - extents.width) / 2
        text_y = (self.h + extents.height) / 2 - 2
        
        ctx.move_to(text_x, text_y)
        ctx.show_text(self.label)
        
        ctx.restore()
        super().draw(ctx, time)

