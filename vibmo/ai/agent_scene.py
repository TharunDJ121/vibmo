"""
Natural Language Prompt to Animated Scene Generator for AI Agents.
"""

from __future__ import annotations
import re
from typing import Any, Optional
from vibmo.scene.scene import Scene
from vibmo.core.color import Color, colors
from vibmo.core.easing import Ease
from vibmo.components.glass import GlassCard
from vibmo.components.counter import MetricCounter
from vibmo.typography.kinetic import KineticText
from vibmo.importers.icons import Icon
from vibmo.product.charts import AreaChart, Sparkline, BarChart, DonutChart
from vibmo.product.cards import StatCard
from vibmo.fx.filters import Vignette, FilmGrain, Glow


class AgentSceneGenerator:
    """
    Synthesizes a complete animated Vibmo scene from a natural language prompt.
    """

    @classmethod
    def generate_from_prompt(
        cls,
        prompt: str,
        duration: float = 4.0,
        width: int = 1920,
        height: int = 1080,
        fps: int = 60,
        **kwargs: Any,
    ) -> Scene:
        scene = Scene(
            width=width,
            height=height,
            fps=fps,
            duration=duration,
            background=colors.DARK_NAVY,
        )

        p = prompt.lower()

        # 1. Detect Brand / Product Name
        name_match = re.search(r'(?:called|product|for|named|app)\s+["\']?([A-Za-z0-9\s]+?)["\']?(?:\s+with|\s+that|\s+and|\s*\.|\s*$)', prompt, re.IGNORECASE)
        app_name = name_match.group(1).strip() if name_match else "PulseMetrics"

        # 2. Detect Metrics (e.g. $148K MRR, 250,000 users)
        val_match = re.search(r'(\$?)\s*(\d+(?:,\d+)*(?:\.\d+)?)\s*([KkMmBbn]?)', prompt)
        prefix = "$" if "$" in prompt else ""
        end_val = 148500.0
        if val_match:
            try:
                num = float(val_match.group(2).replace(",", ""))
                unit = val_match.group(3).upper()
                if unit == "K":
                    num *= 1000
                elif unit == "M":
                    num *= 1000000
                end_val = num
                if val_match.group(1):
                    prefix = val_match.group(1)
            except Exception:
                pass

        # 3. Assemble Semantic Components
        card = GlassCard(
            direction="column",
            gap=16.0,
            padding=32.0,
            corner_radius=24.0,
            position=(240, 220),
        )

        icon = Icon("lucide:sparkles", size=36, color=colors.CYAN)
        title = KineticText(f"{app_name} — Autonomous Intelligence", font_size=28.0, bold=True)
        counter = MetricCounter(
            start_val=0,
            end_val=end_val,
            prefix=prefix,
            suffix=" MRR" if "$" in prefix else " Users",
            font_size=48.0,
            bold=True,
            color=colors.EMERALD,
        )

        card.add(icon, title, counter)

        # Right Chart Visual
        chart = AreaChart(
            data=[30, 45, 60, 55, 85, 95, 120, 148],
            width=580,
            height=280,
            position=(940, 220),
            color=colors.CYAN,
        )

        scene.add(card, chart)
        scene.add_post_fx(Vignette(intensity=0.25), FilmGrain(amount=0.02))

        # 4. Choreograph Motion Verbs
        step1 = 0.8
        step2 = 1.8
        wait_time = max(0.2, duration - step1 - step2)

        @scene.animate
        def choreography():
            yield scene.all(
                card.pop_in(duration=step1),
                chart.fade_up(offset=30.0, duration=step1, delay=0.1),
            )
            yield scene.all(
                title.reveal_characters(stagger=0.025),
                counter.count_to(duration=step2, ease=Ease.out_expo),
                chart.trace(duration=step2, ease=Ease.out_expo),
            )
            card.float_idle(amplitude=6.0, speed=1.2)
            yield scene.wait(wait_time)

        scene.duration = float(duration)
        return scene

