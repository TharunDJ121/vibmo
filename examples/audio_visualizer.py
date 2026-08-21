"""
Advanced Audio Visualizer for 'Maamadura (From Jigarthanda DoubleX)'.
Features:
- 360-degree Radial Equalizer Spectrum (CircularSpectrum)
- Bass-Reactivity Pulsing Center Vinyl Disc (VinylRecord)
- Real-time Fluid Waveform Ribbon (WaveformRibbon)
- Frosted Glassmorphism Track Info Card (GlassCard)
- Interactive Progress Bar & Time Scrubber (AudioProgressBar)
- Ambient Generative Particle Dust (ParticleEmitter)
- Cinematic Post-Processing (Vignette & Film Grain)
"""

import os
from vibmo import (
    Scene,
    GlassCard,
    KineticText,
    Circle,
    Rect,
    Icon,
    Ease,
    FilmGrain,
    Vignette,
    colors,
    Color,
)
from vibmo.audio import (
    AudioTrack,
    AudioAnalyzer,
    SpectrumBars,
    CircularSpectrum,
    WaveformRibbon,
    VinylRecord,
    AudioProgressBar,
)
from vibmo.physics.particles import ParticleEmitter


def create_visualizer_scene(audio_path: str) -> Scene:
    # 1. Load Audio Track & Analyzer
    track = AudioTrack(audio_path)
    analyzer = AudioAnalyzer(track)
    total_duration = track.duration

    # 2. Setup 1080p 60FPS Scene
    scene = Scene(
        width=1920,
        height=1080,
        fps=60,
        duration=total_duration,
        background=Color.hex("#030712"),  # Ultra deep charcoal void
    )
    scene.add_audio(track)

    # 3. Ambient Generative Particles (Sparkles / Dust)
    ambient_dust = ParticleEmitter(
        preset="ambient_dust",
        position=(960, 540),
        gravity=(0.0, -20.0),
        colors_palette=[
            Color.hex("#f59e0b").with_alpha(0.6),
            Color.hex("#ec4899").with_alpha(0.5),
            Color.hex("#06b6d4").with_alpha(0.5),
            Color.hex("#ffffff").with_alpha(0.35),
        ],
    )
    ambient_dust.emit(duration=total_duration, rate=20.0)

    # 4. Central Audio-Reactive Visualizer Group
    center_x, center_y = 960, 480

    # 4a. Ambient Core Radial Glows
    core_glow_bg = Circle(
        radius=320.0,
        fill=Color.hex("#8b5cf6").with_alpha(0.08),
        stroke=Color.hex("#ec4899").with_alpha(0.15),
        stroke_width=1.5,
        position=(center_x, center_y),
    )
    core_glow_bg.anchor.set((0.5, 0.5))

    glow_disc = Circle(
        radius=210.0,
        fill=Color.hex("#ec4899").with_alpha(0.16),
        stroke=Color.hex("#f59e0b").with_alpha(0.35),
        stroke_width=2.5,
        position=(center_x, center_y),
    )
    glow_disc.anchor.set((0.5, 0.5))

    # 4b. Outer Radial Spectrum (96 radial equalizer bars)
    spectrum_palette = [
        Color.hex("#f59e0b"),  # Vibrant Amber
        Color.hex("#f43f5e"),  # Crimson Rose
        Color.hex("#ec4899"),  # Hot Pink
        Color.hex("#8b5cf6"),  # Electric Violet
        Color.hex("#06b6d4"),  # Neon Cyan
        Color.hex("#10b981"),  # Emerald
    ]
    radial_eq = CircularSpectrum(
        audio=track,
        radius=195.0,
        bar_count=96,
        max_bar_length=220.0,
        bar_width=4.5,
        colors_palette=spectrum_palette,
        rotation_speed=0.06,
        mirror=True,
        position=(center_x, center_y),
    )

    # 4c. Center Vinyl Record with Custom Labels
    vinyl = VinylRecord(
        radius=185.0,
        groove_count=18,
        disc_color=Color(0.06, 0.07, 0.09, 1.0),
        label_color=Color.hex("#f59e0b"),
        label_text="MAAMADURA",
        sub_text="SANTHOSH NARAYANAN",
        rotation_speed=0.22,
        position=(center_x, center_y),
    )
    # Pulse the vinyl disc & glows with bass kicks
    vinyl.bounce_on_beat(analyzer, band="bass", amplitude=1.22)
    glow_disc.bounce_on_beat(analyzer, band="bass", amplitude=1.35)
    core_glow_bg.bounce_on_beat(analyzer, band="bass", amplitude=1.20)

    # 5. Bottom Fluid Waveform Ribbons
    wave_ribbon_glow = WaveformRibbon(
        audio=track,
        width=1760.0,
        height=180.0,
        samples_count=180,
        color=Color.hex("#ec4899").with_alpha(0.35),
        line_width=6.0,
        glow=True,
        position=(80, 920),
    )
    wave_ribbon = WaveformRibbon(
        audio=track,
        width=1760.0,
        height=150.0,
        samples_count=180,
        color=Color.hex("#06b6d4"),
        line_width=2.5,
        glow=True,
        position=(80, 920),
    )

    # 6. Top Left Branding & Film Badge
    top_badge = GlassCard(
        direction="row",
        gap=12.0,
        padding=16.0,
        corner_radius=14.0,
        position=(80, 60),
    )
    live_dot = Circle(radius=6.0, fill=colors.ROSE)
    live_text = KineticText("AUDIO SPECTRUM MASTER", font_size=15.0, bold=True, color=colors.WHITE)
    top_badge.add(live_dot, live_text)

    film_title = KineticText("JIGARTHANDA DOUBLEX", font_size=32.0, bold=True, color=Color.hex("#f59e0b"))
    film_title.position.set((80, 140))

    film_subtitle = KineticText("Director: Karthik Subbaraj • Music: Santhosh Narayanan", font_size=16.0, color=Color.hex("#94a3b8"))
    film_subtitle.position.set((80, 185))

    # 7. Top Right Track Information & Scrubber Card
    info_card = GlassCard(
        direction="column",
        gap=14.0,
        padding=24.0,
        corner_radius=20.0,
        position=(1340, 60),
    )

    song_name = KineticText("Maamadura", font_size=32.0, bold=True, color=colors.WHITE)
    artist_name = KineticText("Dhee • Santhosh Narayanan", font_size=18.0, color=colors.CYAN)
    
    # Mini Equalizer bars inside card
    mini_eq = SpectrumBars(
        audio=track,
        bar_count=28,
        width=440.0,
        height=42.0,
        bar_gap=3.5,
        color=Color.hex("#ec4899"),
        corner_radius=2.0,
    )

    # Live Scrubber with Time Counter (00:00 / 02:48)
    progress_bar = AudioProgressBar(
        duration=total_duration,
        width=440.0,
        height=6.0,
        color=Color.hex("#f59e0b"),
        show_time=True,
    )

    info_card.add(song_name, artist_name, mini_eq, progress_bar)

    # 8. Assemble Scene Elements
    scene.add(
        ambient_dust,
        core_glow_bg,
        glow_disc,
        radial_eq,
        vinyl,
        wave_ribbon_glow,
        wave_ribbon,
        top_badge,
        film_title,
        film_subtitle,
        info_card,
    )

    # 9. Cinematic Post-Processing
    scene.add_post_fx(
        Vignette(intensity=0.45, radius=0.6),
        FilmGrain(amount=0.015),
    )

    # 10. Intro Choreography
    @scene.animate
    def script():
        # Entrance setup
        vinyl.scale.set((0.3, 0.3))
        vinyl.opacity.set(0.0)
        radial_eq.scale.set((0.3, 0.3))
        radial_eq.opacity.set(0.0)
        glow_disc.scale.set((0.3, 0.3))
        glow_disc.opacity.set(0.0)
        core_glow_bg.scale.set((0.3, 0.3))
        core_glow_bg.opacity.set(0.0)

        info_card_actions = info_card.fade_up(offset=40, duration=0.9)
        top_badge_actions = top_badge.fade_up(offset=20, duration=0.7)

        yield scene.all(
            vinyl.scale.to((1.0, 1.0), duration=1.2, ease=Ease.spring(stiffness=130, damping=11)),
            vinyl.opacity.to(1.0, duration=0.8),
            radial_eq.scale.to((1.0, 1.0), duration=1.2, ease=Ease.spring(stiffness=130, damping=11)),
            radial_eq.opacity.to(1.0, duration=0.8),
            glow_disc.scale.to((1.0, 1.0), duration=1.2, ease=Ease.spring(stiffness=130, damping=11)),
            glow_disc.opacity.to(1.0, duration=0.8),
            core_glow_bg.scale.to((1.0, 1.0), duration=1.2, ease=Ease.spring(stiffness=130, damping=11)),
            core_glow_bg.opacity.to(1.0, duration=0.8),
            film_title.reveal_characters(stagger=0.025),
            film_subtitle.fade_in(duration=1.0),
            *info_card_actions,
            *top_badge_actions,
        )

        # Full track timeline duration wait
        yield scene.wait(max(0.1, total_duration - 1.2))

    return scene


if __name__ == "__main__":
    audio_file = "Maamadura (From Jigarthanda DoubleX).mp3"
    if not os.path.exists(audio_file):
        raise FileNotFoundError(f"Audio file not found: {audio_file}")

    print(f"[+] Initializing Visualizer for '{audio_file}'...")
    scene = create_visualizer_scene(audio_file)
    
    print("[+] Generating 6-frame storyboard contact sheet...")
    scene.storyboard("maamadura_storyboard.png", rows=2, cols=3)
    print("[OK] Storyboard saved to maamadura_storyboard.png")

    output_video = "maamadura_visualizer.mp4"
    print(f"[+] Rendering full master video (1080p @ 60 FPS, {scene.duration:.1f}s) to '{output_video}'...")
    scene.render(output_path=output_video, preset="mp4", max_workers=16)
    print(f"[OK] Successfully rendered full audio visualizer to '{output_video}'!")
