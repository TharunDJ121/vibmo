"""
Showcase Demo: High-End Motion Graphics in Python with Vibe Coding superpowers.
"""

from vibmo import (
    Scene,
    GlassCard,
    KineticText,
    MetricCounter,
    CodeWindow,
    Icon,
    Ease,
    FilmGrain,
    Vignette,
    colors,
)


def create_showcase_scene() -> Scene:
    # 1. Initialize Scene
    scene = Scene(
        width=1920,
        height=1080,
        fps=60,
        duration=4.5,
        background=colors.DARK_NAVY,
    )

    # 2. Glassmorphic Notification / Stats Card
    card = GlassCard(
        direction="column",
        gap=16.0,
        padding=32.0,
        corner_radius=24.0,
        position=(160, 240),
    )

    header_row = GlassCard(
        direction="row",
        gap=14.0,
        padding=0.0,
        fill=None,
        stroke=None,
        align_items="center",
    )
    icon = Icon("lucide:sparkles", size=36.0, color=colors.INDIGO)
    title = KineticText("Autonomous Motion Engine", font_size=32.0, bold=True, color=colors.WHITE)
    header_row.add(icon, title)

    subtitle = KineticText(
        "Vibe Coding • Instant Storyboards • Auto-Layout",
        font_size=20.0,
        color=colors.SLATE_400,
    )

    counter = MetricCounter(
        start_val=0,
        end_val=250000,
        prefix="$",
        suffix=" MRR",
        font_size=56.0,
        bold=True,
        color=colors.EMERALD,
    )

    card.add(header_row, subtitle, counter)

    # 3. macOS Terminal Code Window Mockup
    sample_code = 'card = GlassCard(glow=True)\nyield card.pop_in()\nyield title.reveal_characters()'
    code_win = CodeWindow(
        code=sample_code,
        title="vibe_scene.py",
        font_size=20.0,
        position=(1020, 240),
    )

    scene.add(card, code_win)

    # 4. Cinematic Post-Processing
    scene.add_post_fx(Vignette(intensity=0.3), FilmGrain(amount=0.02))

    # 5. Choreography Script
    @scene.animate
    def script():
        # Pop in the card with spring physics while terminal slides upward
        yield scene.all(
            card.pop_in(delay=0.1, duration=0.8),
            code_win.fade_up(offset=50.0, delay=0.2, duration=0.8),
        )

        # Stagger kinetic title & count up metrics with exponential ease
        yield scene.all(
            title.reveal_characters(stagger=0.025),
            counter.count_to(duration=1.8, ease=Ease.out_expo),
            icon.bounce(amplitude=1.3, count=2, duration=0.7),
        )

        # Gentle floating idle
        card.float_idle(amplitude=6.0, speed=1.2)
        code_win.float_idle(amplitude=8.0, speed=0.9)

        yield scene.wait(1.5)

    return scene


if __name__ == "__main__":
    scene = create_showcase_scene()
    print("[+] Generating AI Storyboard contact sheet...")
    scene.storyboard(path="showcase_storyboard.png", rows=2, cols=3)
    print("[OK] Saved showcase_storyboard.png")

    print("[+] Rendering master 60 FPS MP4 video...")
    scene.render(output_path="showcase.mp4", preset="mp4", motion_blur=False)
    print("[OK] Successfully rendered showcase.mp4!")
