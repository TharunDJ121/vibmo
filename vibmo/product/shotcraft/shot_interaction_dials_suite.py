"""
Interactive UI & Parameter Dynamics Suites for Vibmo.
Inspired by video-shotcraft:
- autolayout-gap-dial: Parameter dial driving layout spacing in real-time.
- chip-grid-single-select-blackout: Active chip selection with 1-frame flash & background blackout.
- avatar-bracket-carousel: 4-corner focus brackets with vertical spring cycling.
- bezier-source-converge-merge: Multi-source bezier paths converging into single hub.
"""

from __future__ import annotations
import math
from typing import List, Optional, Tuple, Dict, Any, Union
import cairo
import numpy as np

from vibmo.core.color import Color, colors
from vibmo.core.signal import Signal, AnimationAction
from vibmo.core.easing import Ease
from vibmo.scene.node import Node


class AutolayoutGapDial(Node):
    """
    Parameter dial driving UI layout spacing in real-time with spring bounce.
    Renders measurement ticks, numerical gap badge, and animated separating blocks.
    """

    def __init__(
        self,
        block_labels: Optional[List[str]] = None,
        min_gap: float = 8.0,
        max_gap: float = 48.0,
        accent_color: Union[Color, str] = colors.CYAN,
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)
        self.block_labels = block_labels or ["Header", "Content", "Actions", "Footer"]
        self.min_gap = min_gap
        self.max_gap = max_gap
        self.accent_color = Color.from_any(accent_color)

        self.dial_progress = Signal(0.0, f"{self.id}.dial")
        self.gap_value = Signal(min_gap, f"{self.id}.gap")

    def expand_gap(self, target_gap: float = 48.0, duration: float = 1.2, delay: float = 0.0) -> AnimationAction:
        """Expands the layout gap parameter with spring overshoot."""
        return self.gap_value.to(target_gap, duration=duration, delay=delay, ease=Ease.out_back)

    def draw(self, ctx: cairo.Context, time: float = 0.0) -> None:
        cx, cy = self.position.evaluate_at(time)
        curr_gap = self.gap_value.evaluate_at(time)
        n = len(self.block_labels)

        ctx.save()
        ctx.translate(cx, cy)

        # 1. Parameter Dial Badge at Top
        badge_w, badge_h = 160.0, 38.0
        ctx.set_source_rgba(0.08, 0.12, 0.20, 0.95)
        ctx.rectangle(-badge_w / 2, -180.0, badge_w, badge_h)
        ctx.fill_preserve()

        ctx.set_source_rgba(
            self.accent_color.r,
            self.accent_color.g,
            self.accent_color.b,
            0.6,
        )
        ctx.set_line_width(1.5)
        ctx.stroke()

        ctx.select_font_face("Inter", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
        ctx.set_font_size(14.0)
        ctx.set_source_rgba(0.9, 0.95, 1.0, 1.0)
        ctx.move_to(-badge_w / 2 + 16.0, -156.0)
        ctx.show_text(f"GAP: {curr_gap:.0f}px")

        # 2. Separating UI Blocks
        total_block_w = 120.0
        total_w = n * total_block_w + (n - 1) * curr_gap
        start_x = -total_w / 2

        for i, label in enumerate(self.block_labels):
            bx = start_x + i * (total_block_w + curr_gap)
            by = -60.0
            bw, bh = total_block_w, 120.0
            r = 12.0

            # Block Body
            ctx.set_source_rgba(0.10, 0.14, 0.24, 0.9)
            ctx.new_sub_path()
            ctx.arc(bx + bw - r, by + bh - r, r, 0, math.pi / 2)
            ctx.arc(bx + r, by + bh - r, r, math.pi / 2, math.pi)
            ctx.arc(bx + r, by + r, r, math.pi, 3 * math.pi / 2)
            ctx.arc(bx + bw - r, by + r, r, 3 * math.pi / 2, 2 * math.pi)
            ctx.close_path()
            ctx.fill_preserve()

            ctx.set_source_rgba(0.25, 0.35, 0.50, 0.5)
            ctx.set_line_width(1.2)
            ctx.stroke()

            # Label
            ctx.select_font_face("Inter", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
            ctx.set_font_size(14.0)
            ctx.set_source_rgba(0.85, 0.90, 0.98, 1.0)
            ctx.move_to(bx + 20.0, by + bh / 2 + 5.0)
            ctx.show_text(label)

            # Draw Dimension Measurement Line Between Blocks
            if i < n - 1 and curr_gap > 12.0:
                mx_start = bx + bw
                mx_end = mx_start + curr_gap
                my = by + bh / 2

                ctx.set_source_rgba(
                    self.accent_color.r,
                    self.accent_color.g,
                    self.accent_color.b,
                    0.7,
                )
                ctx.set_line_width(1.0)
                ctx.move_to(mx_start, my - 6)
                ctx.line_to(mx_start, my + 6)
                ctx.move_to(mx_start, my)
                ctx.line_to(mx_end, my)
                ctx.move_to(mx_end, my - 6)
                ctx.line_to(mx_end, my + 6)
                ctx.stroke()

        ctx.restore()


class ChipGridSelectBlackout(Node):
    """
    Selection chip matrix with 1-frame active state flash and background blackout.
    Simulates genuine UI interaction with focused attention convergence.
    """

    def __init__(
        self,
        options: Optional[List[str]] = None,
        selected_index: int = 1,
        accent_color: Union[Color, str] = colors.CYAN,
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)
        self.options = options or ["Standard Tier", "Pro Performance", "Enterprise AI", "Custom Dedicated"]
        self.selected_index = selected_index
        self.accent_color = Color.from_any(accent_color)

        self.selection_progress = Signal(0.0, f"{self.id}.select")
        self.flash_progress = Signal(0.0, f"{self.id}.flash")

    def trigger_select(self, duration: float = 0.8, delay: float = 0.0) -> AnimationAction:
        """Selects the target chip with initial active flash and dimming."""
        return self.selection_progress.to(1.0, duration=duration, delay=delay, ease=Ease.out_expo)

    def draw(self, ctx: cairo.Context, time: float = 0.0) -> None:
        sp = self.selection_progress.evaluate_at(time)
        cx, cy = self.position.evaluate_at(time)

        ctx.save()
        ctx.translate(cx, cy)

        chip_w, chip_h = 240.0, 52.0
        gap = 20.0
        n = len(self.options)
        start_x = -((n * chip_w + (n - 1) * gap) / 2)

        for idx, text in enumerate(self.options):
            x = start_x + idx * (chip_w + gap)
            y = -chip_h / 2
            r = 12.0

            is_target = idx == self.selected_index
            
            # Opacity dim for unselected chips
            alpha = 1.0 - 0.75 * sp if not is_target else 1.0
            scale_factor = 1.0 + (0.06 * sp if is_target else 0.0)

            ctx.save()
            ctx.translate(x + chip_w / 2, y + chip_h / 2)
            ctx.scale(scale_factor, scale_factor)
            ctx.translate(-chip_w / 2, -chip_h / 2)

            # Surface
            ctx.new_sub_path()
            ctx.arc(chip_w - r, chip_h - r, r, 0, math.pi / 2)
            ctx.arc(r, chip_h - r, r, math.pi / 2, math.pi)
            ctx.arc(r, r, r, math.pi, 3 * math.pi / 2)
            ctx.arc(chip_w - r, r, r, 3 * math.pi / 2, 2 * math.pi)
            ctx.close_path()

            if is_target and sp > 0.01:
                # Active highlight color
                ctx.set_source_rgba(
                    self.accent_color.r * 0.25,
                    self.accent_color.g * 0.25,
                    self.accent_color.b * 0.25,
                    0.95,
                )
                ctx.fill_preserve()
                ctx.set_source_rgba(
                    self.accent_color.r,
                    self.accent_color.g,
                    self.accent_color.b,
                    0.9 * sp,
                )
                ctx.set_line_width(2.0)
                ctx.stroke()
            else:
                ctx.set_source_rgba(0.08, 0.11, 0.18, 0.85 * alpha)
                ctx.fill_preserve()
                ctx.set_source_rgba(0.22, 0.28, 0.38, 0.5 * alpha)
                ctx.set_line_width(1.0)
                ctx.stroke()

            # Text
            ctx.select_font_face("Inter", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
            ctx.set_font_size(15.0)
            if is_target and sp > 0.01:
                ctx.set_source_rgba(1, 1, 1, 1.0)
            else:
                ctx.set_source_rgba(0.8, 0.85, 0.95, alpha)

            ctx.move_to(24.0, chip_h / 2 + 5.0)
            ctx.show_text(text)

            ctx.restore()

        ctx.restore()


class AvatarBracketCarousel(Node):
    """
    4-corner focus brackets with vertical spring item cycling (Case Law: fixed bracket framing).
    """

    def __init__(
        self,
        roles: Optional[List[str]] = None,
        prefix_text: str = "Your autonomous",
        suffix_text: str = "agent",
        accent_color: Union[Color, str] = colors.CYAN,
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)
        self.roles = roles or ["Researcher", "Architect", "Full-Stack Coder", "QA Verifier"]
        self.prefix_text = prefix_text
        self.suffix_text = suffix_text
        self.accent_color = Color.from_any(accent_color)

        self.cycle_step = Signal(0.0, f"{self.id}.cycle")

    def cycle_to(self, step: float, duration: float = 0.6, delay: float = 0.0) -> AnimationAction:
        """Cycles to the next role slot with spring overshoot."""
        return self.cycle_step.to(step, duration=duration, delay=delay, ease=Ease.out_back)

    def draw(self, ctx: cairo.Context, time: float = 0.0) -> None:
        cx, cy = self.position.evaluate_at(time)
        step = self.cycle_step.evaluate_at(time)

        ctx.save()
        ctx.translate(cx, cy)

        # Prefix Text
        ctx.select_font_face("Inter", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
        ctx.set_font_size(32.0)
        ctx.set_source_rgba(0.9, 0.95, 1.0, 1.0)
        ctx.move_to(-380.0, 10.0)
        ctx.show_text(self.prefix_text)

        # Focus Bracket Box
        bx, by = -80.0, -40.0
        bw, bh = 240.0, 70.0
        b_len = 16.0

        ctx.set_source_rgba(self.accent_color.r, self.accent_color.g, self.accent_color.b, 0.8)
        ctx.set_line_width(2.5)

        # Top-Left
        ctx.move_to(bx, by + b_len)
        ctx.line_to(bx, by)
        ctx.line_to(bx + b_len, by)
        # Top-Right
        ctx.move_to(bx + bw - b_len, by)
        ctx.line_to(bx + bw, by)
        ctx.line_to(bx + bw, by + b_len)
        # Bottom-Left
        ctx.move_to(bx, by + bh - b_len)
        ctx.line_to(bx, by + bh)
        ctx.line_to(bx + b_len, by + bh)
        # Bottom-Right
        ctx.move_to(bx + bw - b_len, by + bh)
        ctx.line_to(bx + bw, by + bh)
        ctx.line_to(bx + bw, by + bh - b_len)
        ctx.stroke()

        # Vertical Scrolling Role Text
        ctx.save()
        ctx.rectangle(bx + 4, by + 4, bw - 8, bh - 8)
        ctx.clip()

        for idx, role in enumerate(self.roles):
            y_offset = (idx - step) * 55.0
            alpha = max(0.0, 1.0 - abs(idx - step) * 0.8)

            ctx.set_font_size(28.0)
            ctx.set_source_rgba(
                self.accent_color.r,
                self.accent_color.g,
                self.accent_color.b,
                alpha,
            )
            ctx.move_to(bx + 20.0, by + 45.0 + y_offset)
            ctx.show_text(role)

        ctx.restore()

        # Suffix Text
        ctx.set_font_size(32.0)
        ctx.set_source_rgba(0.9, 0.95, 1.0, 1.0)
        ctx.move_to(bx + bw + 24.0, 10.0)
        ctx.show_text(self.suffix_text)

        ctx.restore()


class BezierSourceConvergeMerge(Node):
    """
    Multi-source bezier paths flowing data packets from 4 distributed nodes into a central hub.
    """

    def __init__(
        self,
        hub_name: str = "Central Intelligence Hub",
        sources: Optional[List[str]] = None,
        accent_color: Union[Color, str] = colors.CYAN,
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)
        self.hub_name = hub_name
        self.sources = sources or ["GitHub PRs", "Postgres DB", "SaaS Webhooks", "Log Streams"]
        self.accent_color = Color.from_any(accent_color)

        self.stream_progress = Signal(0.0, f"{self.id}.stream")

    def animate_flow(self, duration: float = 1.6, delay: float = 0.0) -> AnimationAction:
        """Draws bezier trace lines and flows particles into hub."""
        return self.stream_progress.to(1.0, duration=duration, delay=delay, ease=Ease.in_out_cubic)

    def draw(self, ctx: cairo.Context, time: float = 0.0) -> None:
        p = self.stream_progress.evaluate_at(time)
        cx, cy = self.position.evaluate_at(time)

        ctx.save()
        ctx.translate(cx, cy)

        hub_x, hub_y = 180.0, 0.0

        # Draw Source Nodes and Bezier Lines
        for idx, src_name in enumerate(self.sources):
            src_x = -340.0
            src_y = -150.0 + idx * 100.0

            # Source Node Pill
            ctx.set_source_rgba(0.09, 0.12, 0.20, 0.9)
            ctx.rectangle(src_x - 70, src_y - 20, 140, 40)
            ctx.fill_preserve()
            ctx.set_source_rgba(0.25, 0.35, 0.48, 0.6)
            ctx.set_line_width(1.2)
            ctx.stroke()

            ctx.select_font_face("Inter", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
            ctx.set_font_size(13.0)
            ctx.set_source_rgba(0.85, 0.9, 0.98, 1.0)
            ctx.move_to(src_x - 55, src_y + 5)
            ctx.show_text(src_name)

            # Bezier Connecting Path
            ctx.move_to(src_x + 70, src_y)
            cp1_x, cp1_y = (src_x + 70 + hub_x - 70) / 2, src_y
            cp2_x, cp2_y = (src_x + 70 + hub_x - 70) / 2, hub_y
            ctx.curve_to(cp1_x, cp1_y, cp2_x, cp2_y, hub_x - 70, hub_y)

            ctx.set_source_rgba(
                self.accent_color.r,
                self.accent_color.g,
                self.accent_color.b,
                0.35,
            )
            ctx.set_line_width(1.5)
            ctx.stroke()

            # Data Packet Sliding Along Path
            if p > 0.01:
                t_val = (p + idx * 0.25) % 1.0
                # Approximate bezier point
                bx = math.pow(1 - t_val, 3) * (src_x + 70) + 3 * math.pow(1 - t_val, 2) * t_val * cp1_x + 3 * (1 - t_val) * math.pow(t_val, 2) * cp2_x + math.pow(t_val, 3) * (hub_x - 70)
                by = math.pow(1 - t_val, 3) * src_y + 3 * math.pow(1 - t_val, 2) * t_val * cp1_y + 3 * (1 - t_val) * math.pow(t_val, 2) * cp2_y + math.pow(t_val, 3) * hub_y

                ctx.set_source_rgba(1, 1, 1, 0.9)
                ctx.arc(bx, by, 4.0, 0, 2 * math.pi)
                ctx.fill()

        # Central Hub Node
        ctx.set_source_rgba(0.06, 0.09, 0.15, 0.95)
        ctx.rectangle(hub_x - 70, hub_y - 45, 180, 90)
        ctx.fill_preserve()

        ctx.set_source_rgba(
            self.accent_color.r,
            self.accent_color.g,
            self.accent_color.b,
            0.8,
        )
        ctx.set_line_width(2.0)
        ctx.stroke()

        ctx.select_font_face("Inter", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
        ctx.set_font_size(15.0)
        ctx.set_source_rgba(1, 1, 1, 1.0)
        ctx.move_to(hub_x - 55, hub_y + 5)
        ctx.show_text("INTELLIGENCE HUB")

        ctx.restore()
