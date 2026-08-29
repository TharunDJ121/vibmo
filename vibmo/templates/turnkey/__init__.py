"""
Turnkey One-Liner Production Scene Builders and Template Suites.
"""

from __future__ import annotations
from typing import Any, List, Optional, Sequence, Union
from vibmo.core.color import Color, colors
from vibmo.core.easing import Ease
from vibmo.scene.scene import Scene
from vibmo.components.glass import GlassCard
from vibmo.components.counter import MetricCounter
from vibmo.typography.kinetic import KineticText
from vibmo.product.mockups import BrowserWindow
from vibmo.product.charts import AreaChart
from vibmo.product.cursor import Cursor
from vibmo.product.command_palette import CommandPalette, CommandItem
from vibmo.fx.filters import Bloom, FilmGrain, Vignette, Dither

from vibmo.templates.turnkey.tmpl_social_audiogram_suite import (
    TmplSocialAudiogramSuite,
    SocialAudiogramTemplate,
)
from vibmo.templates.turnkey.tmpl_developer_cli_launch_suite import (
    TmplDeveloperCliLaunchSuite,
    DeveloperCliLaunchTemplate,
)
from vibmo.templates.turnkey.tmpl_ai_code_assistant_suite import (
    TmplAiCodeAssistantSuite,
    AiCodeAssistantTemplate,
)


def create_saas_launch_scene(
    app_title: str = "PulseMetrics",
    app_url: str = "https://app.pulsemetrics.io",
    headline: str = "Instant SaaS Analytics at Edge Scale",
    metric_label: str = "MONTHLY RECURRING REVENUE",
    metric_start: float = 100000,
    metric_end: float = 248500,
    chart_data: Sequence[float] = (30, 45, 38, 70, 62, 95, 88, 130, 122, 175),
    duration: float = 6.0,
) -> Scene:
    """
    Builds a complete, broadcast-ready Silicon-Valley SaaS launch motion graphic in 1 function call.
    Includes 3D browser fly-in, specular gleam, glowing revenue chart, magnetic cursor clicks, and Foley SFX!
    """
    scene = Scene(
        width=1920,
        height=1080,
        fps=60,
        duration=duration,
        background=Color.hex("#030712"),
    )
    # Cinematic post-processing
    scene.add_post_fx(
        Bloom(threshold=0.65, intensity=0.35, radius=28.0),
        Vignette(intensity=0.25),
        FilmGrain(amount=0.005),
        Dither(amount=0.8),
    )

    # 1. Headline
    heading = KineticText(
        f"<bold>{headline}</bold>",
        font_size=42,
        color=colors.WHITE,
        align="center",
    ).align("top_center", (1920, 1080)).at(460, 60)
    scene.add(heading)

    # 2. 3D Browser Window Mockup
    browser = BrowserWindow(
        url=app_url,
        title=f"{app_title} — Dashboard",
        width=1400,
        height=820,
    ).align("center", (1920, 1080)).at(260, 160)

    # 3. Inside Browser: Metrics Card + Glowing Area Chart
    metrics_row = GlassCard(direction="row", gap=40, padding=24, width=1320)
    
    # Left KPI
    kpi_box = GlassCard(direction="column", gap=8, padding=16, width=380)
    kpi_title = KineticText(f"<#94a3b8>{metric_label}</#94a3b8>", font_size=13, bold=True)
    kpi_counter = MetricCounter(
        start_val=metric_start,
        end_val=metric_end,
        prefix="$",
        font_size=48,
        bold=True,
        color=colors.EMERALD,
    )
    kpi_box.add(kpi_title, kpi_counter)

    # Right Chart
    chart = AreaChart(data=chart_data, width=820, height=220, color=colors.EMERALD)

    metrics_row.add(kpi_box, chart)
    browser.add_content(metrics_row)
    scene.add(browser)

    # 4. Magnetic Cursor
    cursor = Cursor(position=(1800, 950))
    scene.add(cursor)

    # 5. Choreography & SFX
    @scene.animate
    def script():
        # Pop in headline with characters wave and foley whoosh
        scene.add_sfx("whoosh", 0.0)
        yield scene.all(
            *heading.reveal_characters(stagger=0.02, duration=0.7),
            *browser.pop_in(delay=0.1, duration=0.8),
        )

        # 3D Tilt + Specular Edge Gleam + Chart Trace + Counter surge
        scene.add_sfx("pop", 0.8)
        yield scene.all(
            *browser.tilt_3d(pitch=0.18, yaw=-0.22, duration=1.2),
            browser.gleam(duration=1.2, delay=0.1),
            chart.trace(duration=1.4),
            kpi_counter.count_to(duration=1.5, ease=Ease.out_expo),
        )

        # Cursor moves in, clicks KPI card with mechanical click sound
        yield cursor.move_to(kpi_box, duration=0.7)
        scene.add_sfx("click", 2.8)
        yield scene.all(
            *cursor.click(),
            *kpi_box.bounce(amplitude=1.08, count=1),
        )

        # Smooth idle float
        browser.float_idle(amplitude=6, speed=1.2)
        yield scene.wait(1.5)

    return scene


__all__ = [
    "create_saas_launch_scene",
    "TmplSocialAudiogramSuite",
    "SocialAudiogramTemplate",
    "TmplDeveloperCliLaunchSuite",
    "DeveloperCliLaunchTemplate",
    "TmplAiCodeAssistantSuite",
    "AiCodeAssistantTemplate",
]
