"""
Vector Path Morphing & Shape Metamorphosis Showcase.
Demonstrating organic vector transformations between arbitrary shapes:
Circle -> Star -> Heart -> Gear -> Play -> Checkmark
with dynamic color transitions and kinetic typography.
"""

from vibmo import (
    Scene,
    MorphPath,
    Shape,
    KineticText,
    GlassCard,
    ParticleEmitter,
    Ease,
    FilmGrain,
    Vignette,
    colors,
    Color,
)


def create_morph_scene() -> Scene:
    scene = Scene(
        width=1920,
        height=1080,
        fps=60,
        duration=10.0,
        background=Color.hex("#090d16"),
    )

    # 1. Ambient Particle Dust
    particles = ParticleEmitter(
        preset="sparkles",
        position=(960, 540),
        colors_palette=[
            colors.CYAN.with_alpha(0.5),
            colors.PINK.with_alpha(0.5),
            colors.AMBER.with_alpha(0.4),
        ],
    )
    particles.emit(duration=10.0, rate=20.0)
    scene.add(particles)
    scene.add_post_fx(Vignette(intensity=0.25), FilmGrain(amount=0.004))

    # 2. Headline & Title
    header = GlassCard(
        direction="column",
        gap=8.0,
        padding=24.0,
        corner_radius=20.0,
        fill=Color.hex("#0f172a").with_alpha(0.8),
        stroke=Color.WHITE.with_alpha(0.12),
        position=(660, 100),
    )
    title = KineticText("Vector <cyan>Path Morphing</cyan> in Vibmo", font_size=32.0, bold=True)
    subtitle = KineticText("Organic Bézier shape interpolation with zero keyframe math", font_size=16.0, color=colors.SLATE_400)
    header.add(title, subtitle)
    scene.add(header)

    # 3. Main Morphing Shape
    morph = MorphPath(
        shape=Shape.circle(radius=90.0),
        num_points=160,
        fill=colors.CYAN.with_alpha(0.18),
        stroke=colors.CYAN,
        stroke_width=4.0,
        position=(960, 560),
    )
    scene.add(morph)

    # 4. Status Badge Tag
    badge = GlassCard(
        direction="row",
        gap=8.0,
        padding=12.0,
        corner_radius=12.0,
        fill=Color.hex("#1e293b").with_alpha(0.9),
        stroke=colors.CYAN,
        position=(880, 840),
    )
    badge_label = KineticText("Shape: <cyan>Circle</cyan>", font_size=18.0, bold=True)
    badge.add(badge_label)
    scene.add(badge)

    # 5. Choreograph Morph Sequence
    @scene.animate
    def script():
        # Intro
        yield scene.all(
            header.pop_in(duration=0.8),
            morph.pop_in(duration=0.8),
            badge.fade_up(offset=20, duration=0.6),
        )
        yield scene.wait(0.6)

        # 1. Circle -> 5-Point Star (Amber)
        yield scene.all(
            morph.morph_to(Shape.star(outer_radius=110.0, inner_radius=48.0, points=5), duration=1.2, ease=Ease.in_out_back),
            morph.stroke.to(colors.AMBER, duration=1.0),
            morph.fill.to(colors.AMBER.with_alpha(0.2), duration=1.0),
            morph.rotation.to(3.14159 * 0.5, duration=1.2, ease=Ease.out_expo),
        )
        yield scene.wait(0.6)

        # 2. Star -> Heart (Rose)
        yield scene.all(
            morph.morph_to(Shape.heart(size=120.0), duration=1.2, ease=Ease.in_out_cubic),
            morph.stroke.to(colors.ROSE, duration=1.0),
            morph.fill.to(colors.ROSE.with_alpha(0.25), duration=1.0),
            morph.rotation.to(0.0, duration=1.0),
            morph.bounce(amplitude=1.15, count=2),
        )
        yield scene.wait(0.6)

        # 3. Heart -> Mechanical Gear (Indigo)
        yield scene.all(
            morph.morph_to(Shape.gear(radius=90.0, teeth=8, tooth_depth=16.0), duration=1.2, ease=Ease.in_out_expo),
            morph.stroke.to(colors.INDIGO, duration=1.0),
            morph.fill.to(colors.INDIGO.with_alpha(0.2), duration=1.0),
            morph.rotation.to(3.14159 * 2.0, duration=1.8, ease=Ease.in_out_quad),
        )
        yield scene.wait(0.6)

        # 4. Gear -> Play Triangle (Emerald)
        yield scene.all(
            morph.morph_to(Shape.play(size=110.0), duration=1.0, ease=Ease.out_back),
            morph.stroke.to(colors.EMERALD, duration=0.8),
            morph.fill.to(colors.EMERALD.with_alpha(0.3), duration=0.8),
            morph.rotation.to(0.0, duration=0.8),
        )
        yield scene.wait(0.6)

        # 5. Play -> Perfect Circle Outro
        yield scene.all(
            morph.morph_to(Shape.circle(radius=90.0), duration=1.0, ease=Ease.in_out_cubic),
            morph.stroke.to(colors.CYAN, duration=1.0),
            morph.fill.to(colors.CYAN.with_alpha(0.18), duration=1.0),
        )
        morph.float_idle(amplitude=8, speed=1.0)
        yield scene.wait(1.0)

    return scene


if __name__ == "__main__":
    scene = create_morph_scene()
    scene.storyboard("morph_storyboard.png", rows=2, cols=3)
    print("[OK] Storyboard saved to morph_storyboard.png")
    scene.render("morph_showcase.mp4", quality="high", resume=True)
    print("[OK] Rendered morph_showcase.mp4!")
