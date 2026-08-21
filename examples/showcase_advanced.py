"""
Phase 2: Advanced Features Showcase.
Demonstrates 2.5D Card Rotation, Particle System, True Backdrop Blur (Glassmorphism),
and generative components.
"""

from vibmo import (
    Scene,
    GlassCard,
    KineticText,
    Ease,
    FilmGrain,
    Vignette,
    colors,
)
from vibmo.physics.particles import ParticleEmitter


def create_advanced_scene() -> Scene:
    scene = Scene(
        width=1920,
        height=1080,
        fps=60,
        duration=4.0,
        background=colors.DARK_NAVY,
    )

    # 1. True Backdrop Blur (Glassmorphism)
    # We create some background elements to be blurred
    bg_text = KineticText("MOTION GRAPHICS", font_size=200.0, bold=True, color=colors.CYAN.with_alpha(0.2))
    bg_text.position.set((960, 540))
    bg_text.anchor.set((0.5, 0.5))
    scene.add(bg_text)

    # 2. 2.5D Rotating GlassCard
    # Will blur the background text behind it
    card = GlassCard(
        direction="column",
        gap=20.0,
        padding=40.0,
        position=(960, 540),
        backdrop_blur=16.0,  # True real-time gaussian blur
    )
    card.anchor.set((0.5, 0.5))

    title = KineticText("Phase 2: Advanced Features", font_size=36.0, bold=True, color=colors.WHITE)
    subtitle = KineticText("2.5D Camera • Particles • Backdrop Blur", font_size=24.0, color=colors.CYAN)
    card.add(title, subtitle)

    # 3. Particle System
    particles = ParticleEmitter(preset="confetti", position=(960, 540))
    
    scene.add(card, particles)
    scene.add_post_fx(Vignette(intensity=0.3), FilmGrain(amount=0.03))

    @scene.animate
    def script():
        # Fly through entrance using 2.5D rotate_x and rotate_y
        card.rotate_x.set(-0.8)  # Tilt backward
        card.scale.set((0.5, 0.5))
        card.opacity.set(0.0)

        yield scene.all(
            card.scale.to((1.0, 1.0), duration=1.2, ease=Ease.out_expo),
            card.rotate_x.to(0.0, duration=1.2, ease=Ease.out_expo),
            card.opacity.to(1.0, duration=0.8),
            bg_text.reveal_characters(stagger=0.05),
        )

        # Burst particles
        particles.burst(count=150, time=1.2)
        
        # Idle floating and spinning
        card.float_idle(amplitude=10.0, speed=1.5)
        
        # 2.5D Yaw Rotation
        yield card.rotate_y.to(0.2, duration=2.0, ease=Ease.in_out_quad)
        yield scene.wait(0.8)

    return scene


if __name__ == "__main__":
    scene = create_advanced_scene()
    print("[+] Generating Advanced Storyboard contact sheet...")
    scene.storyboard(path="advanced_storyboard.png", rows=2, cols=3)
    print("[OK] Saved advanced_storyboard.png")

    print("[+] Rendering 60 FPS Advanced video utilizing multi-core processing...")
    scene.render(output_path="advanced_showcase.mp4", preset="mp4")
    print("[OK] Successfully rendered advanced_showcase.mp4!")
