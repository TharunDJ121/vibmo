"""
Split Code Sandbox & Playground UI Suite for Vibmo / Motio.
Components:
- CodeSandboxPlayground (SplitCodePlayground)
- SplitConsoleOutput (InteractiveTerminalLogs)
- RunCodeSuccessIndicator
- DependencyInstallPill
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
from vibmo.spatial.shadows import DropShadow


class DependencyInstallPill(Node):
    """Pill indicating active package dependencies (e.g. `pip: vibmo, cairo, numpy`)."""

    def __init__(self, package_str: str = "pip: vibmo, pycairo, numpy", width: float = 220.0, height: float = 26.0, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.package_str = package_str
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

        ctx.set_source_rgba(0.08, 0.12, 0.18, 0.8)
        ctx.fill_preserve()
        ctx.set_source_rgba(0.2, 0.3, 0.45, 0.6)
        ctx.set_line_width(1.0)
        ctx.stroke()

        ctx.select_font_face("Consolas", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)
        ctx.set_font_size(10.0)
        ctx.set_source_rgba(0.4, 0.8, 1.0, 0.9)
        ext = ctx.text_extents(self.package_str)
        ctx.move_to((w - ext.width) * 0.5, h * 0.5 + ext.height * 0.35)
        ctx.show_text(self.package_str)
        ctx.restore()


class RunCodeSuccessIndicator(Node):
    """Badge indicating zero error execution status (`Exit code 0 (24ms)`)."""

    def __init__(self, exit_code: int = 0, time_ms: int = 24, width: float = 160.0, height: float = 28.0, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.exit_code = exit_code
        self.time_ms = time_ms
        self.width_val = float(width)
        self.height_val = float(height)
        self.opacity = Signal(1.0, f"{self.name}.opacity")

    def animate_success(self, duration: float = 0.5, ease: EasingFunc = Ease.out_quad) -> AnimationAction:
        return self.opacity.to(1.0, duration=duration, ease=ease)

    def draw(self, ctx: Any, time: float = 0.0) -> None:
        op = max(0.0, min(1.0, self.opacity.get(time)))
        if op <= 0.0:
            return

        w, h = self.width_val, self.height_val
        ctx.save()
        r = 6.0
        ctx.new_path()
        ctx.arc(w - r, r, r, -math.pi * 0.5, 0)
        ctx.arc(w - r, h - r, r, 0, math.pi * 0.5)
        ctx.arc(r, h - r, r, math.pi * 0.5, math.pi)
        ctx.arc(r, r, r, math.pi, math.pi * 1.5)
        ctx.close_path()

        ctx.set_source_rgba(0.05, 0.2, 0.1, 0.9 * op)
        ctx.fill_preserve()
        ctx.set_source_rgba(0.1, 0.85, 0.45, 0.8 * op)
        ctx.set_line_width(1.0)
        ctx.stroke()

        ctx.select_font_face("Inter", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
        ctx.set_font_size(10.5)
        ctx.set_source_rgba(0.2, 0.95, 0.55, 0.95 * op)
        text = f"✓ Exit {self.exit_code} ({self.time_ms}ms)"
        ext = ctx.text_extents(text)
        ctx.move_to((w - ext.width) * 0.5, h * 0.5 + ext.height * 0.35)
        ctx.show_text(text)
        ctx.restore()


class SplitConsoleOutput(Node):
    """Terminal output pane displaying stdout/stderr and status."""

    def __init__(
        self,
        output_text: str = "$ python main.py\n[Vibmo AI Engine v0.2.0]\n> Initializing neural pipeline...\n> Output: vibe coded motion graphics rendered successfully.\n✓ Finished with exit code 0.",
        width: float = 380.0,
        height: float = 380.0,
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)
        self.output_text = Signal(output_text, f"{self.name}.output_text")
        self.width_val = float(width)
        self.height_val = float(height)

    def draw(self, ctx: Any, time: float = 0.0) -> None:
        w, h = self.width_val, self.height_val
        ctx.save()
        r = 10.0
        ctx.new_path()
        ctx.arc(w - r, r, r, -math.pi * 0.5, 0)
        ctx.arc(w - r, h - r, r, 0, math.pi * 0.5)
        ctx.arc(r, h - r, r, math.pi * 0.5, math.pi)
        ctx.arc(r, r, r, math.pi, math.pi * 1.5)
        ctx.close_path()

        ctx.set_source_rgba(0.02, 0.04, 0.08, 0.95)
        ctx.fill_preserve()
        ctx.set_source_rgba(0.15, 0.22, 0.35, 0.6)
        ctx.set_line_width(1.0)
        ctx.stroke()

        # Terminal Header
        ctx.select_font_face("Inter", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
        ctx.set_font_size(11.0)
        ctx.set_source_rgba(0.6, 0.7, 0.8, 0.8)
        ctx.move_to(14.0, 24.0)
        ctx.show_text("Terminal Output")

        # Lines
        ctx.select_font_face("Consolas", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)
        ctx.set_font_size(11.0)
        lines = self.output_text.get(time).split("\n")
        for i, line in enumerate(lines[:12]):
            if "✓" in line:
                ctx.set_source_rgba(0.2, 0.9, 0.5, 0.95)
            elif ">" in line:
                ctx.set_source_rgba(0.3, 0.8, 1.0, 0.9)
            else:
                ctx.set_source_rgba(0.75, 0.82, 0.9, 0.85)
            ctx.move_to(14.0, 52.0 + i * 20.0)
            ctx.show_text(line)

        ctx.restore()


InteractiveTerminalLogs = SplitConsoleOutput


class CodeSandboxPlayground(Node):
    """
    Code Sandbox & Interactive Execution Playground Suite.
    Renders split-screen code editor, interactive terminal logs,
    live execute button with spinner, and exit status indicators.
    """

    def __init__(
        self,
        code: str = "from motio.agent_api import *\n\nscene = Scene(duration=5.0)\ncard = scene.add(GlassCard())\n\n@scene.animate\ndef main():\n    yield card.pop_in()\n    yield scene.wait(2.0)",
        language: str = "python",
        width: float = 840.0,
        height: float = 500.0,
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)
        self.code = code
        self.language = language
        self.width_val = float(width)
        self.height_val = float(height)
        self.shadow = DropShadow(color=Color(0.0, 0.0, 0.0, 0.5), blur=32.0, offset=(0.0, 16.0))

        # Right pane: Terminal Console Output
        self.console = SplitConsoleOutput(width=380.0, height=410.0)
        self.console.position.set(Vector2D(self.width_val - 404.0, 66.0))
        self.add(self.console)

        # Status badge
        self.success_indicator = RunCodeSuccessIndicator()
        self.success_indicator.position.set(Vector2D(self.width_val - 190.0, 20.0))
        self.add(self.success_indicator)

        # Dependency Pill
        self.dep_pill = DependencyInstallPill(width=200.0)
        self.dep_pill.position.set(Vector2D(180.0, 20.0))
        self.add(self.dep_pill)

    def run_execution(
        self,
        output: Optional[str] = None,
        duration: float = 1.5,
        ease: EasingFunc = Ease.out_quad,
    ) -> AnimationAction:
        """
        Fluent generator animation verb to trigger code execution and terminal log output.
        """
        if output is not None:
            self.console.output_text.set(output)
        return self.success_indicator.opacity.to(1.0, duration=duration, ease=ease)

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
        ctx.set_font_size(14.0)
        ctx.set_source_rgba(0.95, 0.98, 1.0, 0.95)
        ctx.move_to(24.0, 38.0)
        ctx.show_text("Code Sandbox")

        # Left Editor Pane
        ew = 380.0
        eh = 410.0
        ex = 24.0
        ey = 66.0
        er = 10.0

        ctx.new_path()
        ctx.arc(ex + ew - er, ey + er, er, -math.pi * 0.5, 0)
        ctx.arc(ex + ew - er, ey + eh - er, er, 0, math.pi * 0.5)
        ctx.arc(ex + er, ey + eh - er, er, math.pi * 0.5, math.pi)
        ctx.arc(ex + er, ey + er, er, math.pi, math.pi * 1.5)
        ctx.close_path()

        ctx.set_source_rgba(0.03, 0.05, 0.09, 0.9)
        ctx.fill_preserve()
        ctx.set_source_rgba(0.15, 0.22, 0.35, 0.6)
        ctx.set_line_width(1.0)
        ctx.stroke()

        # Code lines
        ctx.select_font_face("Consolas", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)
        ctx.set_font_size(11.0)
        lines = self.code.split("\n")
        for i, line in enumerate(lines[:14]):
            ctx.set_source_rgba(0.4, 0.45, 0.55, 0.7)
            ctx.move_to(ex + 12.0, ey + 28.0 + i * 22.0)
            ctx.show_text(f"{i+1:2d}")

            if "import" in line or "from" in line:
                ctx.set_source_rgba(0.95, 0.45, 0.75, 0.95)
            elif "def " in line or "@" in line:
                ctx.set_source_rgba(0.3, 0.85, 1.0, 0.95)
            else:
                ctx.set_source_rgba(0.85, 0.9, 0.95, 0.9)

            ctx.move_to(ex + 38.0, ey + 28.0 + i * 22.0)
            ctx.show_text(line)

        super().draw(ctx, time)
        ctx.restore()


SplitCodePlayground = CodeSandboxPlayground
