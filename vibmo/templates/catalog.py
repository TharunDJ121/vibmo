"""
Turnkey Production Templates for Vibmo:
- saas_launch: High-converting SaaS product launch video
- app_demo: Mobile smartphone app showcase with PhoneFrame
- tech_intro: High-energy kinetic title & logo reveal
- audio_visualizer: Radial circular spectrum + rotating vinyl disc
"""

from typing import Dict

TEMPLATES: Dict[str, Dict[str, str]] = {
    "saas_launch": {
        "description": "High-converting SaaS product demo with BrowserWindow, Cursor, Spotlight, and Metric counters",
        "code": '''"""
SaaS Product Launch Demo Template
"""

import math
from vibmo import (
    Scene,
    BrowserWindow,
    GlassCard,
    KineticText,
    MetricCounter,
    NotificationToast,
    Axes,
    Icon,
    Cursor,
    ClickIndicator,
    Spotlight,
    Callout,
    ParticleEmitter,
    Ease,
    FilmGrain,
    Vignette,
    colors,
    Color,
)

# 1. Initialize Scene (1080p @ 60 FPS)
scene = Scene(
    width=1920,
    height=1080,
    fps=60,
    duration=10.0,
    background=Color.hex("#030712"),
)

# 2. Ambient Particles & Shaders
particles = ParticleEmitter(preset="ambient_dust", position=(960, 540))
particles.emit(duration=10.0, rate=15.0)
scene.add(particles)
scene.add_post_fx(Vignette(intensity=0.35), FilmGrain(amount=0.012))

# 3. Assemble BrowserWindow App Mockup
browser = BrowserWindow(
    url="https://app.pulsemetrics.io",
    title="PulseMetrics — Analytics",
    width=1400.0,
    height=840.0,
    position=(260, 120),
)

metrics_row = GlassCard(direction="row", gap=24.0, fill=Color.TRANSPARENT, stroke=Color.TRANSPARENT)
card_mrr = GlassCard(direction="column", gap=8.0, padding=20.0, width=380.0)
counter_mrr = MetricCounter(start_val=100000, end_val=250000, prefix="$", font_size=36.0, bold=True, color=colors.EMERALD)
card_mrr.add(KineticText("MONTHLY RECURRING REVENUE", font_size=12.0, bold=True, color=colors.SLATE_400), counter_mrr)
metrics_row.add(card_mrr)

chart_card = GlassCard(direction="column", gap=12.0, padding=24.0, width=1200.0, height=440.0)
chart_axes = Axes(x_range=(-3, 3), y_range=(-1, 3), width=1150.0, height=340.0, grid=True)
curve = chart_axes.plot(lambda x: 1.2 + 0.8 * math.tanh(x * 1.2), color=colors.CYAN, stroke_width=3.5)
chart_card.add(KineticText("GROWTH TRAJECTORY", font_size=14.0, bold=True), chart_axes)

browser.add_content(metrics_row, chart_card)
scene.add(browser)

# 4. Cursor & Navigation
cursor = Cursor(position=(1800, 900))
click_fx = ClickIndicator()
click_fx.opacity.set(0.0)
spotlight = Spotlight(target=chart_card, radius=320.0)
spotlight.opacity.set(0.0)
scene.add(cursor, click_fx, spotlight)

# 5. Choreograph Motion Verbs
@scene.animate
def script():
    browser.position.set((260, 260))
    browser.opacity.set(0.0)
    yield scene.all(
        browser.position.to((260, 120), duration=1.0, ease=Ease.spring(stiffness=120, damping=12)),
        browser.opacity.to(1.0, duration=0.8),
        curve.trim_end.to(1.0, duration=1.8, ease=Ease.out_cubic),
    )

    yield cursor.move_to(card_mrr, duration=0.8)
    click_fx.position.set(cursor.position.get())
    yield scene.all(
        *cursor.click(),
        *click_fx.trigger(),
        card_mrr.bounce(amplitude=1.1, count=1),
    )

    yield scene.all(
        *scene.camera.zoom_to(chart_card, zoom=1.7, duration=1.2, ease=Ease.out_expo),
        spotlight.opacity.to(1.0, duration=0.8),
    )
    yield scene.wait(1.0)

    yield scene.all(
        *scene.camera.reset(duration=1.0, ease=Ease.out_expo),
        spotlight.opacity.to(0.0, duration=0.6),
        counter_mrr.count_to(duration=1.6, ease=Ease.out_expo),
    )
    browser.float_idle(amplitude=6, speed=1.2)
    yield scene.wait(1.5)

if __name__ == "__main__":
    scene.storyboard("storyboard/preview.png")
    scene.render("renders/output.mp4", quality="high")
''',
    },
    "app_demo": {
        "description": "Mobile smartphone walkthrough with PhoneFrame, app header, dynamic cards, and push toasts",
        "code": '''"""
Mobile Smartphone App Showcase Template
"""

from vibmo import (
    Scene,
    PhoneFrame,
    GlassCard,
    KineticText,
    NotificationToast,
    Icon,
    ParticleEmitter,
    Ease,
    FilmGrain,
    Vignette,
    colors,
    Color,
)

scene = Scene(
    width=1920,
    height=1080,
    fps=60,
    duration=8.0,
    background=Color.hex("#090d16"),
)

scene.add_post_fx(Vignette(intensity=0.3), FilmGrain(amount=0.015))

# 1. Centered Phone Mockup
phone = PhoneFrame(
    width=420.0,
    height=860.0,
    position=(750, 110),
)

# App Content Inside Phone
header = GlassCard(direction="row", gap=12.0, padding=12.0, fill=Color.TRANSPARENT, stroke=Color.TRANSPARENT)
header.add(Icon("lucide:sparkles", size=24.0, color=colors.CYAN), KineticText("Pulse App", font_size=20.0, bold=True))

card1 = GlassCard(direction="column", gap=8.0, padding=16.0, corner_radius=16.0)
card1.add(KineticText("Instant AI Transfer", font_size=16.0, bold=True), KineticText("+$1,250.00 from Stripe", font_size=13.0, color=colors.EMERALD))

phone.add_screen_content(header, card1)
scene.add(phone)

# Push Notification
toast = NotificationToast(
    title="Payment Confirmed",
    description="Your transfer of $1,250.00 is complete",
    icon_name="lucide:check",
    icon_color=colors.EMERALD,
    position=(1250, 200),
)
toast.opacity.set(0.0)
scene.add(toast)

@scene.animate
def script():
    phone.position.set((750, 300))
    phone.opacity.set(0.0)
    
    yield scene.all(
        phone.position.to((750, 110), duration=1.0, ease=Ease.spring(stiffness=130, damping=12)),
        phone.opacity.to(1.0, duration=0.8),
    )
    yield scene.wait(0.5)

    yield scene.all(
        *toast.fade_up(offset=30, duration=0.8),
        toast.bounce(amplitude=1.1, count=1, delay=0.4),
    )
    phone.float_idle(amplitude=6, speed=1.2)
    yield scene.wait(2.0)

if __name__ == "__main__":
    scene.storyboard("storyboard/preview.png")
    scene.render("renders/output.mp4", quality="high")
''',
    },
    "tech_intro": {
        "description": "High-energy kinetic typography, glowing vector morphing, and brand title sequence",
        "code": '''"""
Tech Title Sequence & Kinetic Reveal Template
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

scene = Scene(
    width=1920,
    height=1080,
    fps=60,
    duration=6.0,
    background=Color.hex("#030712"),
)

particles = ParticleEmitter(preset="sparkles", position=(960, 540))
particles.emit(duration=6.0, rate=25.0)
scene.add(particles)
scene.add_post_fx(Vignette(intensity=0.4), FilmGrain(amount=0.02))

morph = MorphPath(shape=Shape.circle(70.0), fill=colors.INDIGO.with_alpha(0.25), stroke=colors.INDIGO, position=(960, 420))
title = KineticText("ACCELERATE <cyan>MOTION</cyan>", font_size=56.0, bold=True, position=(620, 560))
subtitle = KineticText("The AI-Native Motion Design Framework", font_size=20.0, color=colors.SLATE_400, position=(740, 650))
scene.add(morph, title, subtitle)

@scene.animate
def script():
    yield scene.all(
        morph.pop_in(duration=0.8),
        title.reveal_characters(stagger=0.03),
        *subtitle.fade_up(offset=25, duration=0.8, delay=0.4),
    )
    yield morph.morph_to(Shape.star(outer_radius=90, inner_radius=40), duration=1.0, ease=Ease.in_out_back)
    yield morph.morph_to(Shape.gear(radius=75, teeth=8), duration=1.0, ease=Ease.in_out_expo)
    yield scene.wait(1.5)

if __name__ == "__main__":
    scene.storyboard("storyboard/preview.png")
    scene.render("renders/output.mp4", quality="high")
''',
    },
}
