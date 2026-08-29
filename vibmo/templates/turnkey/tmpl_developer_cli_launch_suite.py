from __future__ import annotations
from typing import Any
from vibmo.scene.scene import Scene
from vibmo.core.color import Color, colors
from vibmo.core.easing import Ease
from vibmo.components.code import CodeWindow
from vibmo.typography.kinetic import KineticText
from vibmo.typography.animations import TextTypewriter
from vibmo.product.ui_components import ProgressBar
from vibmo.product.charts import BarChart
from vibmo.components.counter import MetricCounter
from vibmo.physics.particles import ParticleEmitter


class DeveloperCliLaunchTemplate:
    @classmethod
    def create_scene(cls, pkg_name: str, install_cmd: str, stars: int, duration: float = 5.0) -> Scene:
        scene = Scene(width=1920, height=1080, fps=60, duration=duration, background=Color.hex("#09090b"))

        # Stage 1: Terminal entrance with glowing ASCII art banner
        banner_text = f"=== {pkg_name.upper()} CLI ==="
        banner = KineticText(banner_text, font_size=40, color=colors.CYAN, bold=True).at(0, -100)

        terminal = CodeWindow(title=f"Terminal - {pkg_name}", width=800).at(1920/2, 1080/2 - 200)
        terminal.add(banner)

        # Stage 2: High-speed installation command typing with progress bar
        cmd_text = TextTypewriter(install_cmd, font_size=28, color=colors.GREEN).at(0, 0)
        progress = ProgressBar(width=700, height=20, color=colors.GREEN).at(0, 100)
        terminal.add(cmd_text, progress)

        scene.add(terminal)

        # Stage 3: Benchmark comparison bar chart showing 10x performance boost
        chart = BarChart(
            data=[("Old CLI", 10), (pkg_name, 100)],
            width=600, height=300, color=colors.INDIGO
        ).at(1920/2 - 400, 1080/2 + 250)
        scene.add(chart)

        # Stage 4: GitHub Star milestone counter ticking up with sparkle particle explosion
        stars_counter = MetricCounter(
            start_val=0, end_val=stars, prefix="★ ", font_size=72, color=colors.YELLOW
        ).at(1920/2 + 400, 1080/2 + 250)
        sparkles = ParticleEmitter(preset="sparkles").at(1920/2 + 400, 1080/2 + 250)
        scene.add(stars_counter, sparkles)

        @scene.animate
        def script():
            # Stage 1
            yield scene.all(
                terminal.pop_in(duration=0.5),
                banner.reveal_characters(duration=0.5)
            )

            # Stage 2
            yield cmd_text.type_out(duration=0.5)
            yield progress.animate_to(1.0, duration=0.8, ease=Ease.out_expo)

            # Stage 3
            yield scene.all(
                chart.pop_in(duration=0.3),
                chart.grow_bars(duration=0.7, ease=Ease.out_elastic)
            )

            # Stage 4
            yield scene.all(
                stars_counter.pop_in(duration=0.3),
                stars_counter.count_to(duration=1.0, ease=Ease.out_expo),
            )
            sparkles.burst()
            yield scene.wait(1.0)

        return scene


class TmplDeveloperCliLaunchSuite(DeveloperCliLaunchTemplate):
    @classmethod
    def build_scene(cls, **kwargs):
        return cls.create_scene(
            pkg_name=kwargs.get("package", kwargs.get("name", "vibmo")),
            install_cmd=kwargs.get("command", "npm install -g vibmo"),
            stars=kwargs.get("stars", 10000),
            duration=kwargs.get("duration", 5.0),
        )


__all__ = [
    "DeveloperCliLaunchTemplate",
    "TmplDeveloperCliLaunchSuite",
]
