"""
Showcase 1: High-End SaaS Metrics & Frosted Glassmorphism Card.
Demonstrates GlassCard with backdrop blur, specular rim, gleam sweep, metric counter, particles, and 4-octave bloom.
"""

from motio.agent_api import *

# 1. Initialize Scene (1080p @ 60 FPS, Dark Luxury aesthetic)
scene = Scene(
    width=1920,
    height=1080,
    fps=60,
    duration=4.0,
    background=colors.DARK_NAVY,
)

# 2. Add Background & Cinematic Post-FX
bg = MeshGradientFlow(speed=0.5, complexity=3)
scene.add(bg)

# Professional Post-FX Pipeline
scene.add_post_fx(
    Bloom(threshold=0.6, intensity=0.5, radius=24.0),
    Vignette(intensity=0.3, radius=0.7),
    FilmGrain(amount=0.012, luminance_weighted=True),
    ColorGrade(contrast=1.12, saturation=1.08, color_boost=0.15),
)

# 3. Assemble Frosted Glass Card UI
card = GlassCard(
    direction="column",
    gap=20,
    padding=36,
    corner_radius=28,
    position=(280, 240),
    backdrop_blur=24.0,
    specular_rim=True,
)

icon = Icon("lucide:sparkles", size=42, color=colors.CYAN)
title = KineticText("Automated Motion in Python", font_size=34, bold=True)
counter = MetricCounter(
    start_val=0,
    end_val=250000,
    prefix="$",
    suffix=" MRR",
    font_size=56,
    bold=True,
    color=colors.EMERALD,
)

# Particle Confetti Celebratory Burst
particles = ParticleEmitter(preset="confetti", position=(960, 540))

card.add(icon, title, counter)
scene.add(card, particles)

# 4. Choreograph Animation Sequence
@scene.animate
def main():
    # Pop in the card with spring physics
    yield card.pop_in(delay=0.1, duration=0.8)
    
    # Staggered reveals + counting + gleam sweep + particle burst
    yield scene.all(
        title.reveal_characters(stagger=0.025),
        counter.count_to(duration=1.8, ease=Ease.out_expo),
        card.gleam(duration=1.2, delay=0.3),
        particles.burst(count=60, time=0.8),
    )
    
    # Gentle idle float
    card.float_idle(amplitude=8, speed=1.2)
    yield scene.wait(1.0)

if __name__ == "__main__":
    import os
    os.makedirs("output", exist_ok=True)
    scene.storyboard("output/showcase_saas_glass_storyboard.png")
    print("[+] Generated showcase_saas_glass_storyboard.png successfully!")
