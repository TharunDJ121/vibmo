"""
Vertical 9:16 SaaS Product Demo Reel / YouTube Short.
High-end UI animation featuring Glassmorphic Dashboard, Kinetic Typography,
Interactive Cursor Navigation, 2.5D Depth, and Glowing Metric Charts.
"""

import math
from vibmo.agent_api import *

# 1. Initialize Vertical 9:16 Scene (1080x1920 @ 60 FPS)
scene = Scene(
    width=1080,
    height=1920,
    fps=60,
    duration=6.5,
    background=Color.hex("#030712"),
)

# 2. Cinematic Post-Processing
scene.add_post_fx(
    Vignette(intensity=0.35),
    FilmGrain(amount=0.005),
)

# 3. Top Header: Category Pill & Main Headline
header_container = FlexContainer(
    direction="column",
    gap=18,
    padding=0,
    align_items="center",
    position=(80, 160),
    width=920,
)

badge = GlassCard(
    direction="row",
    gap=10,
    padding=(10, 20),
    corner_radius=24,
    fill=Color.hex("#0ea5e9").with_alpha(0.12),
    stroke=Color.hex("#38bdf8").with_alpha(0.35),
)
badge.add(
    Icon("lucide:sparkles", size=20, color=Color.hex("#38bdf8")),
    KineticText("PULSE AI ENGINE", font_size=18, bold=True, color=Color.hex("#38bdf8")),
)

headline = KineticText(
    "Automate Your Revenue\nIn Real Time",
    font_size=46,
    bold=True,
    align="center",
    line_height=1.2,
    color=Color.WHITE,
)

header_container.add(badge, headline)
scene.add(header_container)

# 4. Main Elevating 2.5D Dashboard Glass Card
dash_card = GlassCard(
    direction="column",
    gap=24,
    padding=32,
    corner_radius=32,
    width=920,
    position=(80, 560),
    fill=Color.hex("#0f172a").with_alpha(0.75),
    stroke=Color.WHITE.with_alpha(0.18),
    shadow=DropShadow(color=Color.hex("#000000").with_alpha(0.6), blur=36.0, offset=(0, 20)),
)

# 4a. Metric KPI Row
kpi_row = FlexContainer(direction="row", gap=24, padding=0, width=856, justify_content="space_between")

card_mrr = GlassCard(
    direction="column",
    gap=8,
    padding=20,
    width=400,
    corner_radius=20,
    fill=Color.WHITE.with_alpha(0.04),
    stroke=Color.WHITE.with_alpha(0.1),
)
counter_mrr = MetricCounter(
    start_val=50000,
    end_val=148500,
    prefix="$",
    font_size=38,
    bold=True,
    color=Color.hex("#10b981"),
)
card_mrr.add(
    KineticText("MONTHLY REVENUE", font_size=13, bold=True, color=Color.hex("#64748b")),
    counter_mrr,
    KineticText("+48.2% vs last month", font_size=14, bold=True, color=Color.hex("#34d399")),
)

card_users = GlassCard(
    direction="column",
    gap=8,
    padding=20,
    width=400,
    corner_radius=20,
    fill=Color.WHITE.with_alpha(0.04),
    stroke=Color.WHITE.with_alpha(0.1),
)
counter_users = MetricCounter(
    start_val=1200,
    end_val=8940,
    suffix=" users",
    font_size=38,
    bold=True,
    color=Color.hex("#06b6d4"),
)
card_users.add(
    KineticText("ACTIVE ACCOUNTS", font_size=13, bold=True, color=Color.hex("#64748b")),
    counter_users,
    KineticText("+124 today", font_size=14, bold=True, color=Color.hex("#38bdf8")),
)

kpi_row.add(card_mrr, card_users)

# 4b. Glowing Revenue Trend Curve
chart_card = GlassCard(
    direction="column",
    gap=14,
    padding=24,
    width=856,
    corner_radius=24,
    fill=Color.WHITE.with_alpha(0.03),
    stroke=Color.WHITE.with_alpha(0.08),
)
chart_header = FlexContainer(direction="row", gap=12, padding=0, align_items="center")
chart_header.add(
    Icon("lucide:trending-up", size=22, color=Color.hex("#10b981")),
    KineticText("Live Conversion Velocity", font_size=20, bold=True, color=Color.WHITE),
)

axes = Axes(
    x_range=(0, 6),
    y_range=(0, 100),
    width=808,
    height=240,
    grid=True,
    grid_color=Color.WHITE.with_alpha(0.06),
    axis_color=Color.TRANSPARENT,
)

# Smooth analytical growth curve
growth_curve = axes.plot(
    lambda x: 15.0 + 12.0 * x + 1.2 * (x ** 2) + 6.0 * math.sin(x * 2.2),
    color=Color.hex("#06b6d4"),
    stroke_width=4.0,
    glow=True,
    glow_color=Color.hex("#06b6d4").with_alpha(0.4),
)

chart_card.add(chart_header, axes)

# 4c. Notification Toast Popup
toast = NotificationToast(
    title="New Enterprise Conversion",
    description="Acme Corp upgraded to Scale Plan ($2,400/mo)",
    icon_name="lucide:zap",
    icon_color=Color.hex("#f59e0b"),
    width=856,
)

dash_card.add(kpi_row, chart_card, toast)
scene.add(dash_card)

# 5. Interactive Navigation Tools
cursor = Cursor(position=(950, 1800))
click_fx = ClickIndicator()
spotlight = Spotlight(target=card_mrr, radius=380, scene_width=1080, scene_height=1920)
spotlight.opacity.set(0.0)
scene.add(spotlight, cursor, click_fx)

# 6. Ambient Particle Flare
particles = ParticleEmitter(
    preset="ambient_dust",
    colors_palette=[Color.hex("#38bdf8"), Color.hex("#06b6d4"), Color.hex("#a855f7")],
)
scene.add(particles)


# 7. Cinematic Choreography
@scene.animate
def script():
    # 0.0s - 0.8s: Header & Card spring entrance
    yield scene.all(
        header_container.fade_up(offset=50, duration=0.8),
        headline.reveal_words(stagger=0.06),
        dash_card.pop_in(delay=0.15, duration=0.9),
    )

    # 0.8s - 2.2s: Cursor glides to MRR card, clicks with shockwave
    yield cursor.move_to(card_mrr, duration=0.9, ease=Ease.in_out_cubic)
    yield scene.all(
        *cursor.click(),
        *click_fx.trigger(),
        card_mrr.bounce(amplitude=1.12, count=1),
        spotlight.opacity.to(1.0, duration=0.4),
    )

    # 2.2s - 4.0s: Numbers tick up + Curve traces + 2.5D Perspective Tilt
    yield scene.all(
        *dash_card.tilt_3d(pitch=0.18, yaw=-0.22, duration=1.4, ease=Ease.out_expo),
        counter_mrr.count_to(duration=1.8, ease=Ease.out_expo),
        counter_users.count_to(duration=1.8, ease=Ease.out_expo),
        growth_curve.trim_end.to(1.0, duration=1.6, ease=Ease.out_cubic),
        card_mrr.scale.to(Vector2D(1.04, 1.04), duration=0.6),
    )

    # 4.0s - 5.0s: Notification pops in & Cursor navigates to toast
    yield scene.all(
        toast.pop_in(duration=0.6),
        cursor.move_to(toast, duration=0.7, ease=Ease.out_quad),
    )
    yield scene.all(
        *cursor.click(),
        *click_fx.trigger(),
        toast.bounce(amplitude=1.06, count=1),
    )

    # 5.0s - 6.5s: Floating organic idle drift
    dash_card.float_idle(amplitude=8.0, speed=1.1)
    yield scene.wait(1.5)


if __name__ == "__main__":
    # Generate 6-frame storyboard contact sheet
    scene.storyboard("saas_short_storyboard.png")
    
    # Master 1080x1920 60 FPS Render
    scene.render("saas_short_demo.mp4", quality="high")
