"""
✦ Vibmo Studio: Full Asset Expansion Master Showcase
Demonstrates expanded components across Effects, Device Mockups, Advanced Charts, UI Controls,
Typography, Physics, Audio Visualizers, and Turnkey Templates.
"""

from motio.agent_api import *


def create_showcase_scene() -> Scene:
    # 1. Initialize Scene (1080p @ 60 FPS, High-Vibe Dark Slate Theme)
    scene = Scene(
        width=1920,
        height=1080,
        fps=60,
        duration=5.0,
        background=colors.DARK_NAVY,
    )

    # 2. Cinematic Post-Processing Chain
    scene.add_post_fx(
        Vignette(intensity=0.3),
        FilmGrain(amount=0.012),
        LightLeakFX(intensity=0.35, color=colors.AMBER),
    )

    # 3. Assemble Hero UI Layout (BrowserWindow with nested multi-series chart and stats)
    browser = BrowserWindow(
        url="https://cloud.vibmo.design",
        title="Vibmo Cloud — Real-Time Motion Pipeline",
        width=1380,
        height=820,
        position=(270, 130),
    )

    chart = LineChart(
        series={
            "GPU Compute": [12, 35, 28, 62, 54, 88, 76, 120],
            "Throughput": [20, 30, 42, 48, 68, 75, 95, 110],
        },
        width=1280,
        height=380,
        series_colors={"GPU Compute": colors.CYAN, "Throughput": colors.EMERALD},
    )

    card_row = FlexContainer(direction="row", gap=24, padding=0)

    # Glass Stat Card
    stat_card = GlassCard(direction="column", gap=12, padding=24, corner_radius=20)
    stat_title = KineticText("Monthly Active Pipelines", font_size=18, color=colors.SLATE_400)
    stat_counter = MetricCounter(start_val=0, end_val=485000, prefix="", suffix=" Ops/s", font_size=36, bold=True, color=colors.EMERALD)
    stat_card.add(stat_title, stat_counter)

    # Tabs control
    tabs = Tabs(items=["Overview", "Real-Time", "Security", "Logs"], selected_index=1, width=420)

    # Neon badge
    neon = NeonText(text="LIVE GPU VIBE", font_size=28, color=colors.CYAN)

    card_row.add(stat_card, tabs, neon)
    browser.add_content(chart, card_row)

    # 4. Interactive Cursor, Spotlight, and Particle Emitter
    cursor = Cursor(position=(960, 540))
    spotlight = Spotlight(target=browser, radius=400)
    confetti = AdvancedParticleEmitter(rate=40.0, preset="confetti", origin=(960, 450))

    scene.add(confetti, browser, spotlight, cursor)

    # 5. Choreograph with Natural Semantic Motion Verbs
    @scene.animate
    def main():
        # Entrance
        yield browser.pop_in(duration=0.8)
        
        # Parallel tracing, counting, and cursor glide
        yield scene.all(
            chart.trace(duration=1.8),
            stat_counter.count_to(duration=1.8),
            cursor.move_to((1150, 480), duration=1.2),
        )
        
        # Click action
        yield cursor.click()
        
        # Tab selection animation
        yield tabs.select(2, duration=0.6)
        
        yield scene.wait(1.0)

    return scene


if __name__ == "__main__":
    print("[Vibmo] Building Full Showcase Scene...")
    scene = create_showcase_scene()
    
    print("[Vibmo] Generating visual 6-frame storyboard contact sheet...")
    scene.storyboard("full_showcase_storyboard.png")
    print("[Vibmo] Storyboard saved to full_showcase_storyboard.png")
    
    print("[Vibmo] Pre-flight validation...")
    scene.validate()
    print("[Vibmo] Pre-flight checks passed!")
