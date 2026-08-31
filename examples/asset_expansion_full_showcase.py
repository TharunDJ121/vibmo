"""
✦ Motio / Vibmo: 100+ Asset Expansion & Modernization Master Showcase
Demonstrates expanded components across all 7 framework suites:
1. Procedural Audio & Sound Synthesis (Whoosh, Cyber UI, Foley)
2. Non-Static Animated Backdrops (MeshGradientFlow, CyberGrid)
3. Hardware Chassis & Device Enclosures (FoldableDeviceFrame, BrowserWindow)
4. AI & SaaS Interactive UI Suites (StreamingTokenOutput, PricingTierMatrix, ApiKeyVault)
5. Financial, 3D Spatial & Motion Charts (CandlestickChartPro, SpeedometerHudDial)
6. Kinetic Typography & Title Sequences (RealisticNeonStrobeSign, GlitchDecryptorText)
7. Visual Post-FX Shaders & Turnkey Templates (CrtPhosphorBloom, AnamorphicStreakFlare)
"""

from motio.agent_api import *


def create_master_showcase_scene() -> Scene:
    # 1. Initialize Scene (1080p @ 60 FPS, Dark Navy Aesthetic)
    scene = Scene(
        width=1920,
        height=1080,
        fps=60,
        duration=6.0,
        background=colors.DARK_NAVY,
    )

    # 2. Animated Non-Static Backdrop & Cinematic Post-FX Shaders
    bg = MeshGradientFlow(
        colors=[colors.INDIGO, colors.DARK_NAVY, colors.CYAN],
        speed=0.6,
        complexity=3,
    )
    scene.add(bg)

    scene.add_post_fx(
        Vignette(intensity=0.25),
        FilmGrain(amount=0.012),
        AnamorphicStreakFlare(threshold=0.85, streak_length=400.0, tint_color=colors.CYAN),
    )

    # 3. Assemble Hero UI Layout (BrowserWindow with nested SaaS & Chart Components)
    browser = BrowserWindow(
        url="https://cloud.vibmo.design",
        title="Motio & Vibmo — 100+ Modern Asset Suite",
        width=1420,
        height=840,
        position=(250, 120),
    )

    # Hero Glass Card with KPI Metrics & Kinetic Text
    hero_card = GlassCard(
        direction="column",
        gap=16,
        padding=28,
        corner_radius=20,
        specular_rim=True,
    )
    
    title = KineticText("Next-Gen Motion Graphics Engine", font_size=28, bold=True, color=colors.WHITE)
    counter = MetricCounter(start_val=0, end_val=100, prefix="+", suffix=" Production Assets", font_size=44, bold=True, color=colors.EMERALD)
    neon_sign = RealisticNeonStrobeSign(text="LIVE AGENT API", font_size=22, color=colors.CYAN)
    
    hero_card.add(title, counter, neon_sign)

    # Professional Financial Candlestick Chart
    sample_ohlc = [
        {"time": 0, "open": 100.0, "high": 115.0, "low": 98.0, "close": 112.0, "volume": 12000},
        {"time": 1, "open": 112.0, "high": 128.0, "low": 110.0, "close": 125.0, "volume": 18500},
        {"time": 2, "open": 125.0, "high": 130.0, "low": 118.0, "close": 122.0, "volume": 9400},
        {"time": 3, "open": 122.0, "high": 142.0, "low": 120.0, "close": 139.0, "volume": 24000},
        {"time": 4, "open": 139.0, "high": 155.0, "low": 136.0, "close": 152.0, "volume": 31000},
    ]
    chart = CandlestickChartPro(
        ohlc_data=sample_ohlc,
        width=780,
        height=320,
        bullish_color=colors.EMERALD,
        bearish_color=colors.ROSE,
    )

    # Streaming AI Token Box
    streamer = StreamingTokenOutput(
        text="✦ Synthesizing 60 FPS vector paths with zero-boilerplate Agent API...",
        speed=35.0,
        width=580,
        height=140,
    )

    # Content Layout inside BrowserWindow
    content_container = FlexContainer(direction="column", gap=20, padding=20)
    top_row = FlexContainer(direction="row", gap=24, padding=0)
    top_row.add(hero_card, streamer)
    content_container.add(top_row, chart)

    browser.add_content(content_container)

    # Interactive Cursor & Focus Spotlight
    cursor = Cursor(position=(960, 540))
    spotlight = Spotlight(target=browser, radius=450)

    scene.add(browser, spotlight, cursor)

    # 4. Procedural Sound Design (Section 1)
    passby_sfx = WhooshDesignerSuite.cinematic_passby(duration=1.2)
    click_sfx = CyberUiSuite.holographic_click(pitch=880)
    sparkle_sfx = ChimesHarmonicSuite.celestial_wind_chime(duration=2.0)

    # 5. Choreograph with Natural Semantic Motion Verbs
    @scene.animate
    def main():
        # Pop in the hero browser window with spring physics
        yield browser.pop_in(delay=0.1, duration=0.8)

        # Parallel execution: chart bars draw, counter counts, AI streams tokens, neon ignites
        yield scene.all(
            chart.draw_bars(duration=2.0),
            counter.count_to(duration=2.0, ease=Ease.out_expo),
            streamer.stream_tokens(speed=30.0),
            neon_sign.ignite(duration=1.0),
            cursor.move_to((1200, 520), duration=1.5),
        )

        # Interactive click
        yield cursor.click()

        # Idle float and hold
        browser.float_idle(amplitude=6.0, speed=1.2)
        yield scene.wait(1.5)

    return scene


if __name__ == "__main__":
    print("[Motio / Vibmo] Building 100+ Asset Expansion Master Showcase Scene...")
    scene = create_master_showcase_scene()

    print("[Motio / Vibmo] Pre-flight scene constraint validation (scene.validate())...")
    report = scene.validate()
    print("[Motio / Vibmo] Pre-flight validation complete! Report:", report)

    print("[Motio / Vibmo] Generating visual 6-frame storyboard contact sheet...")
    scene.storyboard("full_showcase_storyboard.png")
    print("[Motio / Vibmo] Storyboard saved successfully to full_showcase_storyboard.png")
