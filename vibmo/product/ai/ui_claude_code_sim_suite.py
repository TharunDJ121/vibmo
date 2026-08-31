"""
✦ Vibmo AI Suites: Claude Code & Instant Terminal Simulator
Inspired by Remocn claude-code & terminal-simulator with instant step-scrolling and ANSI highlights.
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


class ClaudeCodeSimulator(FlexContainer):
    """
    Realistic CLI / Claude Code agent terminal simulator with instant step-scrolling.
    """
    def __init__(
        self,
        title: str = "claude-code — ~/projects/vibmo",
        width: float = 840.0,
        height: float = 520.0,
        **kwargs: Any,
    ):
        super().__init__(
            direction="column",
            padding=(0, 0),
            gap=0,
            corner_radius=16.0,
            fill=Color(0.05, 0.06, 0.09, 0.98),
            stroke=Color(0.2, 0.22, 0.3, 0.8),
            stroke_width=1.0,
            shadow=DropShadow(color=Color(0, 0, 0, 0.5), blur=32.0, offset=(0, 16)),
            **kwargs,
        )
        self.term_width = width
        self.term_height = height
        self.lines: List[Tuple[str, Color]] = []
        self.step_index = Signal(0, f"{self.name}.step_index")

        # 1. Terminal Window Header Bar
        header = FlexContainer(
            direction="row",
            padding=(12, 16),
            gap=10,
            fill=Color(0.08, 0.1, 0.14, 1.0),
            stroke=Color(0.18, 0.2, 0.28, 0.8),
            stroke_width=1.0,
            align_items="center",
        )
        # Window controls (macOS red/yellow/green)
        dots = FlexContainer(direction="row", gap=6, align_items="center")
        dots.add(FlexContainer(width=12, height=12, corner_radius=6, fill=Color(0.95, 0.35, 0.35, 1.0)))
        dots.add(FlexContainer(width=12, height=12, corner_radius=6, fill=Color(0.95, 0.75, 0.25, 1.0)))
        dots.add(FlexContainer(width=12, height=12, corner_radius=6, fill=Color(0.35, 0.85, 0.45, 1.0)))
        header.add(dots)

        header.add(
            Text(
                text=f"  {title}",
                font_size=12.0,
                font_family="Inter",
                color=Color(0.6, 0.65, 0.75, 1.0),
                bold=True,
            )
        )
        self.add(header)

        # 2. Terminal Content Body
        self.body = FlexContainer(
            direction="column",
            padding=(16, 20),
            gap=6,
            width=width,
            height=height - 46.0,
        )
        self.add(self.body)

    def add_command(self, cmd: str, prompt: str = "user@vibmo:~$ ") -> ClaudeCodeSimulator:
        """Adds a user command prompt line."""
        self.lines.append((f"{prompt}{cmd}", colors.CYAN))
        return self

    def add_output(self, line: str, color: Optional[Color] = None) -> ClaudeCodeSimulator:
        """Adds a terminal stdout line."""
        col = color if color is not None else Color(0.8, 0.85, 0.9, 1.0)
        self.lines.append((line, col))
        return self

    def add_tool_call(self, tool_name: str, detail: str) -> ClaudeCodeSimulator:
        """Adds a collapsed agentic tool execution step."""
        self.lines.append((f"⚡ Tool: {tool_name} ({detail})", colors.EMERALD))
        return self

    def advance_step(self, step: int) -> AnimationAction:
        """Instantly jumps to step index (step-scrolling, no laggy easing)."""
        return self.step_index.set_action(step)

    def step_to(self, step: int, delay: float = 0.0) -> AnimationAction:
        """Steps forward to line count."""
        return self.step_index.to(float(step), duration=0.01, delay=delay)

    def draw(self, ctx: Any, time: float = 0.0) -> None:
        idx = int(math.floor(self.step_index.get(time)))
        visible_lines = self.lines[:max(1, idx)] if self.lines else []

        # Keep the latest ~12 lines in view (instant step-scroll)
        display_lines = visible_lines[-14:]

        self.body.children.clear()
        for text_str, col in display_lines:
            self.body.add(
                Text(
                    text=text_str,
                    font_size=13.5,
                    font_family="monospace",
                    color=col,
                )
            )

        # Active cursor caret
        blink = (int(time * 4) % 2 == 0)
        if blink:
            self.body.add(
                Text(
                    text="▌",
                    font_size=14.0,
                    font_family="monospace",
                    color=colors.CYAN,
                )
            )

        super().draw(ctx, time)


class TerminalCursorZoom(ClaudeCodeSimulator):
    """Alias for ClaudeCodeSimulator with terminal zoom-in framing."""
    pass
