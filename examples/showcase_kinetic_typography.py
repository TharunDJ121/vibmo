"""
Showcase 3: Cinematic Cryptographic Decryptor & Embers Title Sequence.
Demonstrates KineticText scramble_decrypt, ParticleEmitter fire_embers, CosmicNebula, and Bloom.
"""

from motio.agent_api import *

# 1. Initialize Scene (1080p @ 60 FPS)
scene = Scene(
    width=1920,
    height=1080,
    fps=60,
    duration=4.0,
    background=colors.DARK_NAVY,
)

# 2. Cosmic Background & Post-FX
nebula = CosmicNebula(swirl_speed=0.15, star_count=100)
scene.add(nebula)

scene.add_post_fx(
    Bloom(threshold=0.55, intensity=0.6, radius=30.0),
    FilmGrain(amount=0.015, luminance_weighted=True),
    Vignette(intensity=0.4, radius=0.65),
    ColorGrade(contrast=1.18, saturation=1.15, temperature=0.15),
)

# 3. Kinetic Decryptor Title
title = KineticText(
    "QUANTUM INTELLIGENCE",
    font_size=64,
    bold=True,
    color=colors.CYAN,
    position=(360, 480),
)
subtitle = KineticText(
    "NEXT-GENERATION AUTONOMOUS MOTION ENGINE",
    font_size=24,
    color=colors.SLATE_200,
    position=(460, 570),
)

# Rising Glowing Fire Embers
embers = ParticleEmitter(preset="fire_embers", position=(960, 1000))

scene.add(title, subtitle, embers)

# 4. Choreograph
@scene.animate
def main():
    embers.burst(count=45, time=0.0)
    yield scene.all(
        title.scramble_decrypt(duration=1.4, stagger=0.035),
        subtitle.reveal_characters(stagger=0.015, delay=0.8),
    )
    title.wave(amplitude=8, speed=1.2)
    yield scene.wait(1.5)

if __name__ == "__main__":
    import os
    os.makedirs("output", exist_ok=True)
    scene.storyboard("output/showcase_kinetic_typography_storyboard.png")
    print("[+] Generated showcase_kinetic_typography_storyboard.png successfully!")
