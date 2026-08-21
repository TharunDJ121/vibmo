"""
✦ Multi-Scene Motion Graphics Showcase (Production Master)
Chains 4 distinct motion graphics styles into a unified, broadcast-grade multi-scene Sequence:
  Scene 1: SaaS Product Launch & 3D Interactive UI
  Scene 2: Developer Tooling & Cyberpunk Code Terminal
  Scene 3: Mathematical Curves & Organic Vector Morphing
  Scene 4: Kinetic Typography & High-Energy Brand Outro
"""

import math
from vibmo.agent_api import *


def create_saas_scene() -> Scene:
    """Scene 1: Sleek SaaS Product Launch with Glass Cards & Charts."""
    scene = Scene(
        width=1920,
        height=1080,
        fps=60,
        duration=4.5,
        background=Color.hex("#030712"),
    )
    scene.add_post_fx(
        Bloom(threshold=0.65, intensity=0.35, radius=24.0),
        Vignette(intensity=0.25),
        FilmGrain(amount=0.005),
    )

    title = KineticText(
        "<bold>PulseMetrics</bold> <gradient:#6366f1:#06b6d4>Cloud Intelligence</gradient>",
        font_size=38,
        color=colors.WHITE,
        align="center",
    ).align("top_center", (1920, 1080)).at(450, 60)
    scene.add(title)

    browser = BrowserWindow(
        url="https://app.pulsemetrics.io",
        title="PulseMetrics — Live Analytics",
        width=1360,
        height=760,
    ).align("center", (1920, 1080)).at(280, 180)

    metrics_row = GlassCard(direction="row", gap=32, padding=24, width=1280)
    kpi_card = GlassCard(direction="column", gap=8, padding=20, width=360)
    kpi_label = KineticText("<#94a3b8>MONTHLY ACTIVE REVENUE</#94a3b8>", font_size=12, bold=True)
    kpi_counter = MetricCounter(
        start_val=10000,
        end_val=148500,
        prefix="$",
        font_size=44,
        bold=True,
        color=colors.EMERALD,
    )
    kpi_card.add(kpi_label, kpi_counter)

    chart = AreaChart(
        data=[25, 40, 35, 65, 52, 88, 80, 120, 110, 160],
        width=780,
        height=200,
        color=colors.EMERALD,
    )
    metrics_row.add(kpi_card, chart)
    browser.add_content(metrics_row)
    scene.add(browser)

    cursor = Cursor(position=(1750, 920))
    scene.add(cursor)

    @scene.animate
    def saas_anim():
        scene.add_sfx("whoosh", 0.0)
        yield scene.all(
            title.reveal_characters(stagger=0.018, duration=0.7),
            browser.pop_in(delay=0.1, duration=0.8),
        )
        scene.add_sfx("pop", 0.8)
        yield scene.all(
            browser.tilt_3d(pitch=0.16, yaw=-0.18, duration=1.1),
            browser.gleam(duration=1.1, delay=0.1),
            chart.trace(duration=1.3),
            kpi_counter.count_to(duration=1.4, ease=Ease.out_expo),
        )
        yield cursor.move_to(kpi_card, duration=0.6)
        scene.add_sfx("click", 2.6)
        yield scene.all(
            cursor.click(),
            kpi_card.bounce(amplitude=1.08, count=1),
        )
        browser.float_idle(amplitude=5, speed=1.2)
        yield scene.wait(1.0)

    return scene


def create_code_scene() -> Scene:
    """Scene 2: Developer Tooling & Cyberpunk Code Terminal."""
    scene = Scene(
        width=1920,
        height=1080,
        fps=60,
        duration=4.5,
        background=Color.hex("#090d16"),
    )
    scene.add_post_fx(
        Bloom(threshold=0.6, intensity=0.45, radius=28.0),
        Vignette(intensity=0.3),
    )

    heading = KineticText(
        "<gradient:#38bdf8:#818cf8>Autonomous Agent Pipeline</gradient>",
        font_size=40,
        bold=True,
        align="center",
    ).align("top_center", (1920, 1080)).at(470, 70)
    scene.add(heading)

    code_snippet = (
        "@agent.task(runtime='edge')\n"
        "async def synthesize_motion(prompt: str) -> Video:\n"
        "    scene = Scene.build_from_intent(prompt)\n"
        "    return await scene.render_async(gpu_accelerated=True)"
    )
    code_win = CodeWindow(
        code=code_snippet,
        title="agent_executor.py",
        font_size=22,
        width=960,
        position=(480, 240),
    )
    scene.add(code_win)

    toast = NotificationToast(
        title="Edge Deployment Live",
        description="Cluster ready in 14ms across 35 regions",
        icon_name="lucide:zap",
        icon_color=colors.AMBER,
        position=(1340, 100),
    )
    scene.add(toast)

    @scene.animate
    def code_anim():
        yield scene.all(
            heading.reveal_words(stagger=0.08, duration=0.8),
            code_win.fade_up(offset=50, duration=0.8),
        )
        scene.add_sfx("pop", 0.9)
        yield scene.all(
            toast.pop_in(delay=0.2, duration=0.7),
            code_win.code_node.reveal_characters(stagger=0.01, duration=1.2),
        )
        code_win.float_idle(amplitude=6.0, speed=1.0)
        yield scene.wait(1.5)

    return scene


def create_math_morph_scene() -> Scene:
    """Scene 3: Vector Shape Metamorphosis & Animated Mathematics."""
    scene = Scene(
        width=1920,
        height=1080,
        fps=60,
        duration=4.5,
        background=Color.hex("#070a14"),
    )
    scene.add_post_fx(
        Bloom(threshold=0.55, intensity=0.4, radius=22.0),
        Vignette(intensity=0.2),
    )

    header = GlassCard(
        direction="column",
        gap=8,
        padding=24,
        corner_radius=20,
        fill=Color.hex("#0f172a").with_alpha(0.8),
        stroke=Color.WHITE.with_alpha(0.12),
        position=(620, 60),
    )
    math_title = KineticText("Vector Morphing & Harmonic Curves", font_size=30, bold=True)
    header.add(math_title)
    scene.add(header)

    morph = MorphPath(
        shape=Shape.circle(radius=90),
        fill=Color.hex("#06b6d4").with_alpha(0.25),
        stroke=Color.hex("#22d3ee"),
        stroke_width=3,
        position=(480, 560),
    )
    scene.add(morph)

    formula = MathFormula(
        latex=r"\mathcal{F}(\omega) = \int_{-\infty}^{\infty} f(t) e^{-i\omega t} dt",
        font_size=36,
        color=colors.AMBER,
        position=(1020, 260),
    )
    scene.add(formula)

    axes = Axes(
        x_range=(-3, 3),
        y_range=(-1.5, 1.5),
        width=650,
        height=340,
        grid=True,
        position=(980, 480),
    )
    curve = axes.plot(lambda x: math.sin(2.5 * x) * math.exp(-0.35 * abs(x)), color=colors.CYAN)
    scene.add(axes)

    @scene.animate
    def math_anim():
        yield scene.all(
            header.pop_in(duration=0.7),
            morph.pop_in(duration=0.7),
            formula.pop_in(duration=0.8),
            axes.fade_in(duration=0.8),
        )
        yield scene.all(
            morph.morph_to(Shape.star(outer_radius=110, inner_radius=50), duration=1.0, ease=Ease.in_out_back),
            curve.trim_end.to(1.0, duration=1.2, ease=Ease.out_cubic),
        )
        yield morph.morph_to(Shape.gear(radius=95, teeth=8), duration=1.1, ease=Ease.in_out_cubic)
        yield scene.wait(0.8)

    return scene


def create_outro_scene() -> Scene:
    """Scene 4: Kinetic Typography & High-Impact Brand Outro."""
    scene = Scene(
        width=1920,
        height=1080,
        fps=60,
        duration=4.0,
        background=Color.hex("#050811"),
    )
    scene.add_post_fx(
        Bloom(threshold=0.6, intensity=0.5, radius=30.0),
        Vignette(intensity=0.35),
    )

    card = GlassCard(direction="column", gap=20, padding=40, corner_radius=28, position=(520, 320))
    icon = Icon("lucide:sparkles", size=54, color=colors.INDIGO)
    title = KineticText(
        "<gradient:#6366f1:#a855f7:#ec4899>The Future of Motion Graphics</gradient>",
        font_size=44,
        bold=True,
    )
    subtitle = KineticText(
        "<#94a3b8>Built for AI Agents, Developers, and Creators</#94a3b8>",
        font_size=22,
    )
    badge = Badge(text="OPEN SOURCE • 60 FPS", color=colors.CYAN)

    card.add(icon, title, subtitle, badge)
    scene.add(card)

    @scene.animate
    def outro_anim():
        scene.add_sfx("whoosh", 0.0)
        yield card.pop_in(duration=0.8)
        scene.add_sfx("pop", 0.6)
        yield scene.all(
            title.reveal_characters(stagger=0.015, duration=0.8),
            subtitle.fade_in(duration=0.6),
            icon.bounce(amplitude=1.35, count=2),
        )
        card.float_idle(amplitude=6, speed=1.0)
        yield scene.wait(1.5)

    return scene


# Assemble all 4 scenes into a multi-scene sequence with smooth transitions
def build_multi_scene_sequence() -> Sequence:
    s1 = create_saas_scene()
    s2 = create_code_scene()
    s3 = create_math_morph_scene()
    s4 = create_outro_scene()

    # Chain scenes with smooth directional slide & crossfade transitions
    sequence = Sequence(
        s1, s2, s3, s4,
        transition=Slide(direction="left", duration=0.6, ease=Ease.in_out_cubic),
    )
    return sequence


if __name__ == "__main__":
    seq = build_multi_scene_sequence()
    
    # 1. Pre-flight check
    issues = seq.validate()
    if issues:
        print(f"Validation warnings: {issues}")
    else:
        print("Sequence validation passed successfully!")

    # 2. Generate contact sheet storyboard
    seq.storyboard("multi_scene_storyboard.png", rows=2, cols=3)
    print("Storyboard saved to multi_scene_storyboard.png")
