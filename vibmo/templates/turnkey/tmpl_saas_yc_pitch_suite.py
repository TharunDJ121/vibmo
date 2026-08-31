"""
Turnkey YC SaaS Pitch Deck Motion Graphics Template Suite.
"""

from __future__ import annotations
from typing import Any, Optional, Sequence, Union
import re

from vibmo.scene.scene import Scene
from vibmo.core.color import Color, LinearGradient, colors
from vibmo.core.easing import Ease
from vibmo.components.glass import GlassCard
from vibmo.components.counter import MetricCounter
from vibmo.typography.kinetic import KineticText
from vibmo.product.social import Badge
from vibmo.product.charts import AreaChart
from vibmo.physics.particles import ParticleEmitter
from vibmo.fx.backgrounds.bg_mesh_gradient_flow import MeshGradientFlow
from vibmo.fx.filters import Bloom, FilmGrain, Vignette


def _parse_numeric_val(val_str: Any, default: float = 120000.0) -> float:
    """Helper to extract float value from strings like '$120k', '40%', '250,000'."""
    if isinstance(val_str, (int, float)):
        return float(val_str)
    if not isinstance(val_str, str):
        return default
    
    clean = val_str.strip().replace("$", "").replace("%", "").replace(",", "")
    if clean.lower().endswith("k"):
        try:
            return float(clean[:-1]) * 1000.0
        except ValueError:
            return default
    elif clean.lower().endswith("m"):
        try:
            return float(clean[:-1]) * 1000000.0
        except ValueError:
            return default
    try:
        return float(clean)
    except ValueError:
        return default


class SaasYcPitchTemplate:
    """
    Broadcast-ready Silicon Valley Y Combinator SaaS demo day pitch deck scene builder.
    """

    @classmethod
    def create_scene(
        cls,
        company: str = "HyperScale AI",
        headline: str = "Autonomous Cloud Compute Infrastructure",
        mrr: Union[str, float] = "$120k",
        growth: Union[str, float] = "+40%",
        nrr: str = "142% NRR",
        chart_data: Sequence[float] = (15, 22, 30, 42, 60, 85, 120),
        duration: float = 6.0,
        **kwargs: Any,
    ) -> Scene:
        scene = Scene(
            width=1920,
            height=1080,
            fps=60,
            duration=duration,
            background=Color.hex("#040714"),
        )

        # 1. Mesh Gradient Backdrop
        bg = MeshGradientFlow(
            width=1920,
            height=1080,
            colors=[Color.hex("#040714"), Color.hex("#0a192f"), Color.hex("#0f3460"), Color.hex("#020c1b")],
            speed=0.4,
        )
        scene.add(bg)

        # 2. Cinematic Post-Processing
        scene.add_post_fx(
            Bloom(threshold=0.68, intensity=0.35, radius=24.0),
            Vignette(intensity=0.25),
            FilmGrain(amount=0.008),
        )

        # 3. YC Batch Badge & Header
        badge = Badge(text="Y COMBINATOR ✦ W26 BATCH DEMO DAY", color=Color.hex("#ff6600"))
        badge.align("top_center", (1920, 1080)).at(740, 50)
        scene.add(badge)

        title = KineticText(
            f"<bold>{company}</bold>: <#94a3b8>{headline}</#94a3b8>",
            font_size=36,
            color=colors.WHITE,
            align="center",
        ).align("top_center", (1920, 1080)).at(440, 110)
        scene.add(title)

        # 4. Main Pitch Card Container
        main_card = GlassCard(
            direction="column",
            gap=32,
            padding=36,
            width=1400,
            height=700,
            corner_radius=28,
            fill=Color.hex("#0a1128").with_alpha(0.7),
            stroke=Color.hex("#1e293b"),
            stroke_width=2.0,
            glow=True,
            specular_rim=True,
        ).align("center", (1920, 1080)).at(260, 200)

        # 5. Row of 3 KPI Metrics
        mrr_num = _parse_numeric_val(mrr, 120000.0)
        growth_num = _parse_numeric_val(growth, 40.0)

        kpis_row = GlassCard(
            direction="row",
            gap=40,
            padding=0,
            width=1320,
            fill=Color.TRANSPARENT,
            stroke=None,
            shadow=False,
            specular_rim=False,
        )

        # Left KPI: MRR
        kpi_mrr = GlassCard(
            direction="column",
            gap=8,
            padding=20,
            width=400,
            corner_radius=20,
            fill=Color.hex("#0f172a").with_alpha(0.8),
        )
        kpi_mrr_label = KineticText("<#94a3b8>ANNUALIZED / MONTHLY MRR</#94a3b8>", font_size=13, bold=True)
        mrr_counter = MetricCounter(
            start_val=0,
            end_val=mrr_num,
            prefix="$",
            font_size=44,
            bold=True,
            color=colors.EMERALD,
        )
        kpi_mrr.add(kpi_mrr_label, mrr_counter)

        # Center KPI: Growth
        kpi_growth = GlassCard(
            direction="column",
            gap=8,
            padding=20,
            width=400,
            corner_radius=20,
            fill=Color.hex("#0f172a").with_alpha(0.8),
        )
        kpi_growth_label = KineticText("<#94a3b8>MONTH-OVER-MONTH GROWTH</#94a3b8>", font_size=13, bold=True)
        growth_counter = MetricCounter(
            start_val=0,
            end_val=growth_num,
            prefix="+",
            suffix="%",
            font_size=44,
            bold=True,
            color=colors.CYAN,
        )
        kpi_growth.add(kpi_growth_label, growth_counter)

        # Right KPI: NRR
        kpi_nrr = GlassCard(
            direction="column",
            gap=8,
            padding=20,
            width=400,
            corner_radius=20,
            fill=Color.hex("#0f172a").with_alpha(0.8),
        )
        kpi_nrr_label = KineticText("<#94a3b8>NET REVENUE RETENTION</#94a3b8>", font_size=13, bold=True)
        nrr_counter = MetricCounter(
            start_val=0,
            end_val=_parse_numeric_val(nrr, 142.0),
            suffix="%",
            font_size=44,
            bold=True,
            color=colors.PURPLE,
        )
        kpi_nrr.add(kpi_nrr_label, nrr_counter)

        kpis_row.add(kpi_mrr, kpi_growth, kpi_nrr)

        # 6. Exponential Hockey-Stick Revenue Chart
        chart = AreaChart(
            data=chart_data,
            width=1320,
            height=280,
            color=colors.EMERALD,
        )

        main_card.add(kpis_row, chart)
        scene.add(main_card)

        # 7. Ambient Particle Emitter
        particles = ParticleEmitter(preset="ambient_dust", position=(960, 540))
        scene.add(particles)

        # 8. Choreography
        @scene.animate
        def script():
            scene.add_sfx("whoosh", 0.0)
            yield scene.all(
                *badge.pop_in(duration=0.6),
                *title.reveal_characters(stagger=0.015, duration=0.8),
                *main_card.pop_in(delay=0.1, duration=0.9),
            )

            scene.add_sfx("pop", 0.9)
            yield scene.all(
                chart.trace(duration=1.4),
                mrr_counter.count_to(duration=1.6, ease=Ease.out_expo),
                growth_counter.count_to(duration=1.6, ease=Ease.out_expo),
                nrr_counter.count_to(duration=1.6, ease=Ease.out_expo),
                main_card.gleam(duration=1.4, delay=0.1),
            )

            main_card.float_idle(amplitude=6, speed=1.2)
            yield scene.wait(1.5)

        return scene


class TmplSaasYcPitchSuite(SaasYcPitchTemplate):
    """
    Turnkey Production Suite for YC SaaS Pitch Deck motion graphics.
    """

    @classmethod
    def build_scene(
        cls,
        company: str = "HyperScale AI",
        headline: str = "Autonomous Cloud Compute Infrastructure",
        mrr: Union[str, float] = "$120k",
        growth: Union[str, float] = "+40%",
        nrr: str = "142% NRR",
        duration: float = 6.0,
        **kwargs: Any,
    ) -> Scene:
        """
        Builds and returns a fully configured YC pitch scene.
        """
        return cls.create_scene(
            company=company,
            headline=headline,
            mrr=mrr,
            growth=growth,
            nrr=nrr,
            duration=duration,
            **kwargs,
        )


__all__ = [
    "SaasYcPitchTemplate",
    "TmplSaasYcPitchSuite",
]
