"""
The Flagship SaaS Product Demo Showcase for Vibmo.
A complete, broadcast-ready 12-second software launch video built with high-level semantic primitives:
- Brand Logo intro
- BrowserWindow device mockup
- Live Metrics & Animated Axes charts
- Realistic Mouse Cursor navigation & shockwave clicks
- Camera Directing (zoom_to, pan_to, reset)
- Feature Spotlight & Callout badges
- Metric Counter tickers & Notification Toasts
- Call-To-Action button pop-in
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


def create_saas_demo_scene() -> Scene:
    # 1. Initialize Scene (1080p @ 60 FPS, Obsidian aesthetic)
    scene = Scene(
        width=1920,
        height=1080,
        fps=60,
        duration=12.0,
        background=Color.hex("#030712"),
    )

    # 2. Ambient Particles & Cinematic Shaders
    particles = ParticleEmitter(
        preset="ambient_dust",
        position=(960, 540),
        colors_palette=[
            colors.INDIGO.with_alpha(0.4),
            colors.CYAN.with_alpha(0.35),
            colors.EMERALD.with_alpha(0.25),
        ],
    )
    particles.emit(duration=12.0, rate=16.0)
    scene.add(particles)
    scene.add_post_fx(Vignette(intensity=0.35, radius=0.7), FilmGrain(amount=0.012))

    # 3. Intro Brand Header (Logo + Title)
    brand_header = GlassCard(
        direction="row",
        gap=16.0,
        padding=16.0,
        corner_radius=20.0,
        fill=Color.TRANSPARENT,
        stroke=Color.TRANSPARENT,
        position=(780, 480),
    )
    brand_icon = Icon("lucide:sparkles", size=44.0, color=colors.INDIGO)
    brand_title = KineticText("PulseMetrics", font_size=42.0, bold=True, color=colors.WHITE)
    brand_header.add(brand_icon, brand_title)
    scene.add(brand_header)

    # 4. Assemble the SaaS Application Inside a BrowserWindow
    browser = BrowserWindow(
        url="https://app.pulsemetrics.io/dashboard",
        title="PulseMetrics — Analytics",
        width=1440.0,
        height=880.0,
        position=(240, 100),
    )
    browser.opacity.set(0.0)

    # 4a. Top Dashboard Metrics Row (3 GlassCards with Counters)
    metrics_row = GlassCard(
        direction="row",
        gap=24.0,
        padding=0.0,
        fill=Color.TRANSPARENT,
        stroke=Color.TRANSPARENT,
    )

    counter_mrr = MetricCounter(start_val=120000, end_val=248500, prefix="$", font_size=36.0, bold=True, color=colors.EMERALD)
    card_mrr = GlassCard(direction="column", gap=8.0, padding=20.0, corner_radius=14.0, width=380.0)
    card_mrr.add(
        KineticText("MONTHLY RECURRING REVENUE", font_size=12.0, bold=True, color=colors.SLATE_400),
        counter_mrr,
    )

    counter_users = MetricCounter(start_val=14200, end_val=38450, prefix="+", font_size=36.0, bold=True, color=colors.CYAN)
    card_users = GlassCard(direction="column", gap=8.0, padding=20.0, corner_radius=14.0, width=380.0)
    card_users.add(
        KineticText("ACTIVE SUBSCRIBERS", font_size=12.0, bold=True, color=colors.SLATE_400),
        counter_users,
    )

    counter_retention = MetricCounter(start_val=98, end_val=142, suffix="%", font_size=36.0, bold=True, color=colors.AMBER)
    card_churn = GlassCard(direction="column", gap=8.0, padding=20.0, corner_radius=14.0, width=380.0)
    card_churn.add(
        KineticText("NET RETENTION RATE", font_size=12.0, bold=True, color=colors.SLATE_400),
        counter_retention,
    )

    metrics_row.add(card_mrr, card_users, card_churn)

    # 4b. Main Analytics Chart Card
    chart_card = GlassCard(
        direction="column",
        gap=12.0,
        padding=24.0,
        corner_radius=16.0,
        width=1200.0,
        height=460.0,
    )
    chart_header = KineticText("REVENUE TRAJECTORY (Q1 - Q4)", font_size=14.0, bold=True, color=colors.WHITE)
    
    chart_axes = Axes(x_range=(-3, 3), y_range=(-1, 3), width=1150.0, height=360.0, grid=True, grid_color=Color.hex("#1e293b"))
    curve = chart_axes.plot(lambda x: 1.2 + 0.8 * math.tanh(x * 1.2) + 0.15 * math.sin(x * 4.0), color=colors.CYAN, stroke_width=3.5)
    
    chart_card.add(chart_header, chart_axes)

    browser.add_content(metrics_row, chart_card)
    scene.add(browser)

    # 5. Spotlight & Feature Callout
    spotlight = Spotlight(target=chart_card, radius=340.0)
    spotlight.opacity.set(0.0)
    
    callout = Callout(
        title="AI Anomaly Engine",
        description="+48.2% surge detected in enterprise tier",
        badge="LIVE",
        badge_color=colors.EMERALD,
        position=(1020, 480),
    )
    callout.opacity.set(0.0)
    scene.add(spotlight, callout)

    # 6. Interactive Mouse Cursor & Click Indicator
    cursor = Cursor(position=(1900, 1000), size=24.0)
    click_fx = ClickIndicator(position=(0, 0))
    click_fx.opacity.set(0.0)
    scene.add(cursor, click_fx)

    # 7. Toast Notification & CTA Banner
    toast = NotificationToast(
        title="Target Milestone Unlocked",
        description="$250,000 ARR boundary passed",
        icon_name="lucide:sparkles",
        icon_color=colors.EMERALD,
        position=(1380, 910),
    )
    toast.opacity.set(0.0)

    cta_btn = GlassCard(
        direction="row",
        gap=12.0,
        padding=16.0,
        corner_radius=24.0,
        fill=colors.INDIGO.with_alpha(0.85),
        stroke=colors.INDIGO,
        position=(840, 960),
    )
    cta_btn.add(
        KineticText("Start Free 14-Day Trial →", font_size=16.0, bold=True, color=colors.WHITE)
    )
    cta_btn.opacity.set(0.0)
    scene.add(toast, cta_btn)

    # 8. Choreograph 10-Scene Product Story
    @scene.animate
    def script():
        # Scene 1: Brand Logo Intro Pop-in
        yield scene.all(
            brand_header.pop_in(duration=0.8),
            brand_icon.bounce(amplitude=1.3, count=2),
        )
        yield scene.wait(0.6)

        # Scene 2: Brand Header Fades Out & BrowserWindow Spring Entrance
        browser.position.set((240, 260))
        yield scene.all(
            brand_header.fade_out(duration=0.5),
            browser.position.to((240, 100), duration=1.0, ease=Ease.spring(stiffness=120, damping=12)),
            browser.opacity.to(1.0, duration=0.8),
            curve.trim_end.to(1.0, duration=1.8, ease=Ease.out_cubic),
        )

        # Scene 3: Cursor Glides to MRR Metric Card & Clicks
        yield cursor.move_to(card_mrr, duration=0.8, ease=Ease.in_out_quad)
        
        click_fx.position.set(cursor.position.get())
        yield scene.all(
            *cursor.click(duration=0.35),
            *click_fx.trigger(duration=0.4),
            card_mrr.bounce(amplitude=1.12, count=1),
        )

        # Scene 4: Camera Zooms Into Main Chart & Spotlight Dims Background
        yield scene.all(
            *scene.camera.zoom_to(chart_card, zoom=1.75, duration=1.2, ease=Ease.out_expo),
            spotlight.opacity.to(1.0, duration=0.8),
            *callout.fade_up(offset=25, duration=0.8, delay=0.3),
        )

        yield scene.wait(1.2)

        # Scene 5: Camera Pulls Back, Metrics Ticker Counts Up, Toast & CTA Appear
        yield scene.all(
            *scene.camera.reset(duration=1.0, ease=Ease.out_expo),
            spotlight.opacity.to(0.0, duration=0.6),
            callout.opacity.to(0.0, duration=0.5),
            counter_mrr.count_to(duration=1.6, ease=Ease.out_expo),
            counter_users.count_to(duration=1.6, ease=Ease.out_expo),
            counter_retention.count_to(duration=1.6, ease=Ease.out_expo),
            *toast.fade_up(offset=30, duration=0.8, delay=0.4),
            *cta_btn.fade_up(offset=30, duration=0.8, delay=0.6),
            toast.bounce(amplitude=1.08, count=1, delay=1.2),
        )

        # Scene 6: Continuous Organic Idle Float
        browser.float_idle(amplitude=6, speed=1.2)
        yield scene.wait(1.8)

    return scene


if __name__ == "__main__":
    print("[+] Initializing Flagship SaaS Product Demo...")
    scene = create_saas_demo_scene()

    print("[+] Generating 6-frame storyboard contact sheet...")
    scene.storyboard("saas_storyboard.png", rows=2, cols=3)
    print("[OK] Storyboard saved to saas_storyboard.png")

    print("[+] Rendering master 60 FPS video...")
    scene.render("saas_demo.mp4", quality="high", resume=True)
    print("[OK] Successfully rendered saas_demo.mp4!")
