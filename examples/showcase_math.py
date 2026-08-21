"""
Mathematical Motion Graphics in Vibmo: Outperforming traditional math animation tools
with instant rendering, glowing equations, dynamic function plotting, and vibe coding ergonomics.
"""

import math
from vibmo import (
    Scene,
    GlassCard,
    MathFormula,
    Axes,
    KineticText,
    Ease,
    FilmGrain,
    Vignette,
    colors,
)


def create_math_scene() -> Scene:
    scene = Scene(
        width=1920,
        height=1080,
        fps=60,
        duration=5.0,
        background=colors.hex("#050811"),
    )

    # 1. Header with Kinetic Title
    header = GlassCard(
        direction="column",
        gap=8.0,
        padding=24.0,
        position=(100, 80),
    )
    title = KineticText("Fourier Waveform & Gaussian Integral", font_size=28.0, bold=True, color=colors.WHITE)
    subtitle = KineticText(r"Instant Vector Math • Zero LaTeX Wait Time", font_size=18.0, color=colors.CYAN)
    header.add(title, subtitle)

    # 2. Math Formula Display
    formula = MathFormula(
        latex=r"\int_{-\infty}^{\infty} e^{-x^2} dx = \sqrt{\pi}",
        font_size=42.0,
        color=colors.AMBER,
        glow=True,
        position=(100, 240),
    )

    # 3. Coordinate System & Dynamic Function Plot
    axes = Axes(
        x_range=(-4.0, 4.0),
        y_range=(-1.5, 1.5),
        width=850.0,
        height=450.0,
        grid=True,
        grid_step=1.0,
        position=(920, 220),
    )

    # Plot wave function: y = sin(2x) * e^(-0.2 * x^2)
    wave_curve = axes.plot(
        lambda x: math.sin(2.5 * x) * math.exp(-0.25 * (x ** 2)),
        color=colors.CYAN,
        stroke_width=3.5,
    )
    wave_curve.trim_end.set(0.0)  # Start hidden for trim reveal

    # Vector Arrow
    vector = axes.draw_vector((2.5, 1.0), label="v(t)", color=colors.PINK)

    scene.add(header, formula, axes)
    scene.add_post_fx(Vignette(intensity=0.25), FilmGrain(amount=0.015))

    # 4. Choreography Script
    @scene.animate
    def script():
        # Pop in the header and axes
        yield scene.all(
            header.pop_in(delay=0.1),
            formula.pop_in(delay=0.2),
            axes.fade_up(offset=40.0, delay=0.3),
        )

        # Stagger title characters and trace out the wave curve
        yield scene.all(
            title.reveal_characters(stagger=0.02),
            wave_curve.trim_end.to(1.0, duration=2.0, ease=Ease.in_out_cubic),
        )

        # Morph formula to Euler's formula
        yield formula.transform_to(r"e^{i \pi} + 1 = 0", duration=1.0)

        yield scene.wait(1.2)

    return scene


if __name__ == "__main__":
    scene = create_math_scene()
    print("[+] Generating Mathematical Storyboard contact sheet...")
    scene.storyboard(path="math_storyboard.png", rows=2, cols=3)
    print("[OK] Saved math_storyboard.png")

    print("[+] Rendering 60 FPS Mathematical video...")
    scene.render(output_path="math_showcase.mp4", preset="mp4")
    print("[OK] Successfully rendered math_showcase.mp4!")
