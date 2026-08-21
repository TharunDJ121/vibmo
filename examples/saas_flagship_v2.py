"""
✦ Flagship SaaS Product Launch Demo V2 (Production Broadcast Grade)
Demonstrates:
- True 3D Perspective Homography & 3D Tilt
- Specular Edge Lighting & .gleam() Sweep Shaders
- Glowing AreaChart with Neon Tracing & Pulsating Dot
- Multi-Pass Bloom & Film Dithering
- Foley Sound Effects (Whoosh, Pop, Mechanical Click)
- Rich Inline Typography (<bold>, <gradient>, <#hex>)
"""

from vibmo.agent_api import *

# 1. Initialize Scene (1080p @ 60 FPS, Dark Luxury Navy)
scene = Scene(
    width=1920,
    height=1080,
    fps=60,
    duration=5.5,
    background=Color.hex("#030712"),
)

# 2. Cinematic Post-Processing
scene.add_post_fx(
    Bloom(threshold=0.62, intensity=0.40, radius=26.0),
    Vignette(intensity=0.25),
    FilmGrain(amount=0.005),
    Dither(amount=0.8),
)

# 3. Kinetic Headline with Rich Tags
title = KineticText(
    "<bold>PulseMetrics</bold> <gradient:#6366f1:#06b6d4>Cloud Intelligence</gradient>",
    font_size=40,
    color=colors.WHITE,
    align="center",
).align("top_center", (1920, 1080)).at(440, 50)
scene.add(title)

# 4. 3D Browser Window Mockup
browser = BrowserWindow(
    url="https://app.pulsemetrics.io",
    title="PulseMetrics — Analytics Dashboard",
    width=1400,
    height=820,
).align("center", (1920, 1080)).at(260, 150)

# 5. Inside Browser: KPI Card + Glowing Area Chart
metrics_row = GlassCard(direction="row", gap=32, padding=24, width=1320)

kpi_card = GlassCard(direction="column", gap=8, padding=20, width=380)
kpi_label = KineticText("<#94a3b8>MONTHLY RECURRING REVENUE</#94a3b8>", font_size=12, bold=True)
kpi_counter = MetricCounter(
    start_val=100000,
    end_val=248500,
    prefix="$",
    font_size=46,
    bold=True,
    color=colors.EMERALD,
)
kpi_card.add(kpi_label, kpi_counter)

chart = AreaChart(
    data=[30, 42, 38, 68, 55, 92, 85, 128, 115, 168],
    width=840,
    height=210,
    color=colors.EMERALD,
)

metrics_row.add(kpi_card, chart)
browser.add_content(metrics_row)
scene.add(browser)

# 6. Magnetic Cursor
cursor = Cursor(position=(1800, 950))
scene.add(cursor)

# 7. Animation Choreography & Foley Sound
@scene.animate
def main():
    # Whoosh sound + headline wave entrance + browser spring pop-in
    scene.add_sfx("whoosh", 0.0)
    yield scene.all(
        *title.reveal_characters(stagger=0.018, duration=0.7),
        *browser.pop_in(delay=0.1, duration=0.8),
    )

    # 3D Perspective Tilt + Specular Edge Gleam + Chart Line Trace + Counter Ticker
    scene.add_sfx("pop", 0.8)
    yield scene.all(
        *browser.tilt_3d(pitch=0.18, yaw=-0.20, duration=1.2),
        browser.gleam(duration=1.2, delay=0.1),
        chart.trace(duration=1.4),
        kpi_counter.count_to(duration=1.5, ease=Ease.out_expo),
    )

    # Cursor glides in and clicks KPI card with crisp mechanical sound
    yield cursor.move_to(kpi_card, duration=0.7)
    scene.add_sfx("click", 2.8)
    yield scene.all(
        *cursor.click(),
        *kpi_card.bounce(amplitude=1.08, count=1),
    )

    # Gentle floating idle
    browser.float_idle(amplitude=6, speed=1.2)
    yield scene.wait(1.5)


if __name__ == "__main__":
    # Generate storyboard contact sheet
    scene.storyboard("saas_v2_storyboard.png")
    print("Storyboard saved to saas_v2_storyboard.png")
