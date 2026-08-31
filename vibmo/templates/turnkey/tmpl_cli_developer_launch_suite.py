"""
✦ Vibmo Turnkey: Developer CLI Tool Launch Video Suite
Inspired by Remocn cli-tool-demo archetype with high-speed terminal execution.
"""

from __future__ import annotations

from typing import Any, List, Optional, Sequence, Union

from vibmo.scene.scene import Scene
from vibmo.core.color import Color, colors
from vibmo.core.easing import Ease
from vibmo.components.glass import GlassCard
from vibmo.typography.kinetic import KineticText
from vibmo.product.social import Badge
from vibmo.product.ai.ui_claude_code_sim_suite import ClaudeCodeSimulator
from vibmo.fx.backgrounds.bg_mesh_gradient_flow import MeshGradientFlow
from vibmo.fx.filters import Vignette, FilmGrain


class TmplCliDeveloperLaunchSuite:
    """
    Turnkey template builder for developer CLI and terminal tool launches.
    """
    @classmethod
    def build_scene(
        cls,
        tool_name: str = "vibmo-cli",
        command: str = "vibmo build --spine=saas-demo --fps=60",
        duration: float = 5.0,
        **kwargs: Any,
    ) -> Scene:
        scene = Scene(
            width=1920,
            height=1080,
            fps=60,
            duration=duration,
            background=Color.hex("#05070c"),
        )

        bg = MeshGradientFlow(
            width=1920,
            height=1080,
            colors=[Color.hex("#05070c"), Color.hex("#09101c"), Color.hex("#0f1f33"), Color.hex("#030508")],
            speed=0.5,
        )
        scene.add(bg)
        scene.add_post_fx(Vignette(intensity=0.25), FilmGrain(amount=0.012))

        # Title
        badge = Badge(text=f"DEVELOPER TOOL ✦ {tool_name}", color=colors.EMERALD)
        badge.align("top_center", (1920, 1080)).at(780, 50)
        scene.add(badge)

        title = KineticText(
            f"Autonomous Video Generation from Terminal",
            font_size=36,
            color=colors.WHITE,
            align="center",
        ).align("top_center", (1920, 1080)).at(540, 100)
        scene.add(title)

        # Terminal
        term = ClaudeCodeSimulator(
            title=f"bash — {tool_name}",
            width=960,
            height=600,
            position=(480, 180),
        )
        term.add_command(command)
        term.add_output("⚡ Compiling scene graph and AST...", colors.CYAN)
        term.add_tool_call("GPU Pipeline", "Allocated WebGL shader framebuffers")
        term.add_output("✓ Rendered 360 frames (1080p @ 60 FPS) in 0.42s", colors.EMERALD)
        term.add_output("✓ Exported master video: output/product_launch.mp4 (4.2 MB)", colors.WHITE)
        scene.add(term)

        @scene.animate
        def main():
            yield term.pop_in(duration=0.8)
            yield term.step_to(2, delay=0.2)
            yield term.step_to(4, delay=0.6)
            yield term.step_to(6, delay=0.6)
            yield scene.wait(1.5)

        return scene
