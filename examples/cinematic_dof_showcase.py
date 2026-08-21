"""
✦ Cinematic Depth-of-Field & 3D Camera Orbit Showcase
Demonstrates:
- 3D Camera Orbit & Perspective Yaw/Pitch Swivel
- Optical Depth-of-Field (DoF) with Luminous Circular Bokeh discs
- Foreground vs Background Parallax Rack Focus
- Elevated Glass Cards with Specular Rim Lighting
- Procedural Foley Audio Sync
"""

from vibmo.agent_api import *

# 1. Initialize Scene (1080p @ 60 FPS)
scene = Scene(
    width=1920,
    height=1080,
    fps=60,
    duration=5.5,
    background=Color.hex("#020617"),
)

# 2. Cinematic Post-Processing: Depth-of-Field Bokeh + Emissive Bloom + Film Grain
scene.add_post_fx(
    DepthOfField(focus_y=0.5, focus_width=0.28, blur_radius=20.0, bokeh_intensity=1.75),
    Bloom(threshold=0.60, intensity=0.42, radius=28.0),
    Vignette(intensity=0.30),
    FilmGrain(amount=0.006),
    Dither(amount=0.8),
)

# 3. Background Deep Layer (Out of Focus, Soft Bokeh Balls)
bg_card = GlassCard(
    direction="column",
    gap=12,
    padding=28,
    width=440,
    fill=Color.hex("#1e1b4b").with_alpha(0.35),
    stroke=Color.hex("#6366f1").with_alpha(0.20),
).at(240, 160)
bg_card.rotate_z.set(-0.08)
bg_card.add(
    KineticText("<#818cf8>CLUSTER BACKEND</#818cf8>", font_size=12, bold=True),
    KineticText("<bold>Distributed Edge DB</bold>", font_size=24, color=colors.WHITE),
    MetricCounter(start_val=1000, end_val=9840, suffix=" req/s", font_size=36, color=colors.CYAN),
)
scene.add(bg_card)

# 4. Primary Foreground Focus Layer (Sharp, In-Focus)
main_card = GlassCard(
    direction="column",
    gap=16,
    padding=36,
    width=640,
    fill=Color.hex("#0f172a").with_alpha(0.75),
    stroke=Color.hex("#38bdf8").with_alpha(0.40),
).align("center", (1920, 1080)).at(640, 360)

main_badge = KineticText("<#38bdf8>✦ NEXT-GEN WORKFLOW</#38bdf8>", font_size=13, bold=True)
main_title = KineticText(
    "<bold>Real-Time Neural Engine</bold>",
    font_size=36,
    color=colors.WHITE,
)
main_chart = AreaChart(
    data=[25, 40, 35, 75, 60, 110, 95, 140, 130, 195],
    width=560,
    height=160,
    color=colors.CYAN,
)
main_card.add(main_badge, main_title, main_chart)
scene.add(main_card)

# 5. Foreground Floating Pill (Foreground Depth Bokeh)
fg_pill = GlassCard(
    direction="row",
    gap=16,
    padding=20,
    width=420,
    fill=Color.hex("#020617").with_alpha(0.85),
    stroke=Color.hex("#10b981").with_alpha(0.45),
).at(1260, 680)
fg_pill.rotate_z.set(0.06)
fg_pill.add(
    Icon("lucide:check-circle", size=28, color=colors.EMERALD),
    KineticText("<bold>Zero Latency</bold> <#94a3b8>Synced</#94a3b8>", font_size=20),
)
scene.add(fg_pill)

# 6. Animation Choreography & 3D Camera Orbit
@scene.animate
def script():
    # Whoosh sound + pop cards in
    scene.add_sfx("whoosh", 0.0)
    yield scene.all(
        *bg_card.pop_in(delay=0.0, duration=0.7),
        *main_card.pop_in(delay=0.15, duration=0.8),
        *fg_pill.pop_in(delay=0.3, duration=0.7),
    )

    # 3D Camera Orbit Sweep + Specular Gleams on in-focus card + Chart Trace
    scene.add_sfx("pop", 0.8)
    yield scene.all(
        *scene.camera.orbit(yaw=0.14, pitch=-0.10, duration=1.6),
        *main_card.tilt_3d(pitch=0.12, yaw=-0.15, duration=1.4),
        main_card.gleam(duration=1.2, delay=0.1),
        main_chart.trace(duration=1.4),
    )

    # Reverse Camera Orbit back with subtle settle
    yield scene.camera.orbit(yaw=-0.06, pitch=0.04, duration=1.4)

    main_card.float_idle(amplitude=6, speed=1.2)
    yield scene.wait(1.5)


if __name__ == "__main__":
    scene.storyboard("cinematic_dof_storyboard.png")
    print("Storyboard saved to cinematic_dof_storyboard.png")
