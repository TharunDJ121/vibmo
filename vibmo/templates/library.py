"""
Turnkey Motion Graphics Template Library with broadcast-grade presets.
"""

from __future__ import annotations
from typing import Any, Dict, Optional, Tuple, Union

from vibmo.core.color import Color, colors
from vibmo.scene.scene import Scene
from vibmo.components.glass import GlassCard
from vibmo.components.counter import MetricCounter
from vibmo.components.code import CodeWindow
from vibmo.components.toast import NotificationToast
from vibmo.product.mockups import BrowserWindow, PhoneFrame
from vibmo.product.charts import AreaChart
from vibmo.product.charts_advanced import LineChart
from vibmo.product.cursor import Cursor
from vibmo.product.callouts import Spotlight, Callout
from vibmo.typography.effects import NeonText
from vibmo.typography.kinetic import KineticText
from vibmo.physics.particles_advanced import AdvancedParticleEmitter
from vibmo.fx.filters import FilmGrain, Vignette


class SceneTemplateLibrary:
    """
    Collection of turnkey production-grade scene templates.
    """

    @classmethod
    def saas_product_launch(
        cls,
        title: str = "PulseMetrics — Realtime Analytics",
        url: str = "https://app.pulsemetrics.io",
        mrr_val: int = 248500,
        duration: float = 5.0,
    ) -> Scene:
        """Create a complete Silicon Valley style SaaS product launch video scene."""
        scene = Scene(width=1920, height=1080, fps=60, duration=duration, background=colors.DARK_NAVY)
        scene.add_post_fx(Vignette(intensity=0.25), FilmGrain(amount=0.012))

        browser = BrowserWindow(
            url=url,
            title=title,
            width=1440,
            height=880,
            position=(240, 100),
        )

        chart = LineChart(
            series={"MRR": [10, 28, 45, 78, 120, 180, 248]},
            width=1340,
            height=420,
        )

        counter_card = GlassCard(
            direction="row",
            gap=20,
            padding=24,
            corner_radius=20,
            position=(40, 480),
        )
        counter = MetricCounter(
            start_val=0,
            end_val=mrr_val,
            prefix="$",
            suffix=" MRR",
            font_size=44,
            bold=True,
            color=colors.EMERALD,
        )
        counter_card.add(counter)

        browser.add_content(chart, counter_card)
        cursor = Cursor(position=(960, 540))
        spotlight = Spotlight(target=browser, radius=420)

        scene.add(browser, spotlight, cursor)

        @scene.animate
        def main():
            yield browser.pop_in(duration=0.8)
            yield scene.all(
                chart.trace(duration=1.8),
                counter.count_to(duration=1.8),
            )
            yield cursor.glide_to((1200, 350), duration=1.0)
            yield cursor.click()
            yield scene.wait(1.0)

        return scene

    @classmethod
    def metric_milestone_celebration(
        cls,
        metric_name: str = "Total Active Users",
        metric_val: int = 1000000,
        duration: float = 4.0,
    ) -> Scene:
        """Create an explosive milestone celebration with confetti particles and golden counter."""
        scene = Scene(width=1920, height=1080, fps=60, duration=duration, background=colors.DARK_NAVY)
        scene.add_post_fx(Vignette(intensity=0.35))

        card = GlassCard(direction="column", gap=16, padding=40, corner_radius=28, position=(560, 360))
        title = KineticText(metric_name, font_size=32, bold=True, color=colors.CYAN)
        counter = MetricCounter(
            start_val=0,
            end_val=metric_val,
            prefix="",
            suffix=" 🚀",
            font_size=56,
            bold=True,
            color=colors.AMBER,
        )
        card.add(title, counter)

        confetti = AdvancedParticleEmitter(rate=60.0, preset="confetti", origin=(960, 540))

        scene.add(confetti, card)

        @scene.animate
        def main():
            yield card.pop_in(duration=0.8)
            yield scene.all(
                title.reveal_characters(stagger=0.03),
                counter.count_to(duration=2.0),
            )
            yield scene.wait(1.2)

        return scene

    @classmethod
    def cyberpunk_terminal_intro(
        cls,
        headline: str = "CYBERNETIC CORE",
        code_snippet: str = "const system = new NeuralMatrix();\nawait system.synchronize();",
        duration: float = 4.5,
    ) -> Scene:
        """Create a futuristic neon cyberpunk title and code terminal intro."""
        scene = Scene(width=1920, height=1080, fps=60, duration=duration, background=Color.hex("#02020a"))
        scene.add_post_fx(FilmGrain(amount=0.02))

        neon = NeonText(text=headline, font_size=56, color=colors.CYAN, position=(360, 160))
        code_win = CodeWindow(
            code=code_snippet,
            title="core_init.ts",
            font_size=20,
            width=800,
            position=(560, 380),
        )

        scene.add(neon, code_win)

        @scene.animate
        def main():
            yield code_win.pop_in(duration=0.8)
            yield scene.wait(2.5)

        return scene
