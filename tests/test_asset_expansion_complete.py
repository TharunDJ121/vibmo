"""
Comprehensive test suite for the complete Vibmo Studio Asset Expansion (Phases 1 through 8).
"""

import pytest
import numpy as np
import cairo

# God Import test
from vibmo.agent_api import *


def test_agent_api_god_import():
    """Verify single-line god import brings in all essential classes."""
    assert Scene is not None
    assert GlassCard is not None
    assert MetricCounter is not None
    assert BrowserWindow is not None
    assert PhoneFrame is not None
    assert TabletFrame is not None
    assert LaptopFrame is not None
    assert WatchFrame is not None
    assert DesktopFrame is not None
    assert LineChart is not None
    assert AreaChart is not None
    assert NeonText is not None
    assert SpringSimulation is not None
    assert SceneTemplateLibrary is not None
    assert Exporter is not None


def test_phase2_noise_and_grain_effects():
    """Verify Phase 2.5 Noise and Grain filters."""
    img = np.zeros((100, 100, 4), dtype=np.uint8)
    img[:, :, 3] = 255
    img[:, :, :3] = 128

    n = Noise(intensity=0.2)
    out_n = n.apply(img, time=0.5)
    assert out_n.shape == (100, 100, 4)

    wn = WhiteNoise(intensity=0.1)
    out_wn = wn.apply(img, time=0.5)
    assert out_wn.shape == (100, 100, 4)

    sp = Speckle(density=0.01)
    out_sp = sp.apply(img, time=0.5)
    assert out_sp.shape == (100, 100, 4)

    sc = Scanlines(spacing=4, intensity=0.3)
    out_sc = sc.apply(img, time=0.5)
    assert out_sc.shape == (100, 100, 4)

    tv = TVSignalOff(progress=0.3)
    out_tv = tv.apply(img, time=0.5)
    assert out_tv.shape == (100, 100, 4)


def test_phase2_digital_and_pixel_effects():
    """Verify Phase 2.6 Digital and Pixel filters."""
    img = np.full((120, 120, 4), 180, dtype=np.uint8)
    img[:, :, 3] = 255

    pix = Pixelate(size=8)
    out_pix = pix.apply(img)
    assert out_pix.shape == (120, 120, 4)

    pd = PixelDissolve(progress=0.4, block_size=12)
    out_pd = pd.apply(img)
    assert out_pd.shape == (120, 120, 4)

    ht = Halftone(dot_size=8)
    out_ht = ht.apply(img)
    assert out_ht.shape == (120, 120, 4)

    dg = DotGrid(grid_size=6)
    out_dg = dg.apply(img)
    assert out_dg.shape == (120, 120, 4)

    dith = Dither(levels=3)
    out_dith = dith.apply(img)
    assert out_dith.shape == (120, 120, 4)


def test_phase2_light_and_blur_suites():
    """Verify Phase 2.7 Light and 2.8 Blur filters."""
    img = np.full((100, 100, 4), 100, dtype=np.uint8)
    img[:, :, 3] = 255

    ll = LightLeakFX(intensity=0.5)
    out_ll = ll.apply(img, time=0.5)
    assert out_ll.shape == (100, 100, 4)

    sh = Shine(progress=0.5)
    out_sh = sh.apply(img, time=0.5)
    assert out_sh.shape == (100, 100, 4)

    lf = LensFlare(intensity=0.8)
    out_lf = lf.apply(img, time=0.5)
    assert out_lf.shape == (100, 100, 4)

    lpb = LinearProgressiveBlur(start_blur=0.0, end_blur=10.0)
    out_lpb = lpb.apply(img)
    assert out_lpb.shape == (100, 100, 4)

    rpb = RadialProgressiveBlur(max_blur=12.0)
    out_rpb = rpb.apply(img)
    assert out_rpb.shape == (100, 100, 4)

    rb = RegionBlur(bounds=(0.2, 0.2, 0.6, 0.6), radius=8.0)
    out_rb = rb.apply(img)
    assert out_rb.shape == (100, 100, 4)


def test_phase3_mockup_components():
    """Verify Phase 3.1 Device Mockup components render via Cairo."""
    surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, 1280, 800)
    ctx = cairo.Context(surface)

    tab = TabletFrame(width=600, height=420)
    tab.draw(ctx, 0.0)

    lap = LaptopFrame(width=800, height=500)
    lap.draw(ctx, 0.0)

    wat = WatchFrame(width=280, height=340)
    wat.draw(ctx, 0.0)

    desk = DesktopFrame(width=900, height=600)
    desk.draw(ctx, 0.0)


def test_phase3_charts_and_ui_components():
    """Verify Phase 3.2 Advanced Charts and 3.3 UI Components."""
    surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, 800, 600)
    ctx = cairo.Context(surface)

    # Charts
    lc = LineChart(series={"A": [10, 30, 20, 50], "B": [15, 25, 35, 45]})
    lc.draw(ctx, 0.0)

    sc = ScatterChart()
    sc.draw(ctx, 0.0)

    rc = RadarChart()
    rc.draw(ctx, 0.0)

    fc = FunnelChart()
    fc.draw(ctx, 0.0)

    hm = Heatmap()
    hm.draw(ctx, 0.0)

    cand = CandlestickChart()
    cand.draw(ctx, 0.0)

    # UI Components
    pb = ProgressBar(progress=0.75)
    pb.draw(ctx, 0.0)

    sl = Slider(value=0.4)
    sl.draw(ctx, 0.0)

    tb = Tabs(items=["A", "B", "C"])
    tb.draw(ctx, 0.0)

    acc = Accordion(is_open=True)
    acc.draw(ctx, 0.0)

    mod = Modal()
    mod.draw(ctx, 0.0)

    # Forms & Feedback
    inp = InputField(value="test@example.com")
    inp.draw(ctx, 0.0)

    toast = NotificationToast(title="Test Notification")
    toast.draw(ctx, 0.0)

    spin = LoadingSpinner()
    spin.draw(ctx, 0.5)


def test_phase4_icons_and_gradients():
    """Verify Phase 4 Built-in Icons and Curated Gradients."""
    surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, 400, 400)
    ctx = cairo.Context(surface)

    for icon_name in ["sparkles", "check", "alert", "chart", "gear", "zap", "heart"]:
        ic = BuiltinIcon(name=icon_name, size=32)
        ic.draw(ctx, 0.0)

    g_sunset = Gradients.SUNSET
    assert g_sunset is not None
    assert len(g_sunset.stops) >= 2

    browser = get_asset_browser()
    summary = browser.get_catalog_summary()
    assert summary["total_assets"] >= 0


def test_phase5_typography_effects_and_animations():
    """Verify Phase 5 NeonText, GradientText, 3DText, WordReveal, and Karaoke."""
    surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, 800, 600)
    ctx = cairo.Context(surface)

    neon = NeonText(text="VIBE")
    neon.draw(ctx, 0.5)

    gt = GradientText(text="GRADIENT")
    gt.draw(ctx, 0.0)

    t3d = Text3D(text="3D")
    t3d.draw(ctx, 0.0)

    wr = WordReveal(text="Staggered word reveal test")
    wr.draw(ctx, 0.5)

    ts = TextScramble(target_text="HACKER")
    ts.draw(ctx, 0.5)

    tt = TextTypewriter(text="console.log('hello');")
    tt.draw(ctx, 0.5)

    captions = AdvancedKaraokeCaptions()
    captions.draw(ctx, 0.7)


def test_phase6_physics_and_particles():
    """Verify Phase 6 Springs, Dynamics, and Particles."""
    spring = SpringSimulation(stiffness=200.0, damping=15.0)
    val = spring.evaluate(0.2)
    assert isinstance(val, float)

    pend = PendulumDynamics(length=150.0)
    pos = pend.position_at(0.5)
    assert len(pos) == 2

    bounce = BounceDynamics(height=200.0)
    b_val = bounce.evaluate(0.3)
    assert 0.0 <= b_val <= 1.0

    curve = CubicBezierCurve((0, 0), (50, 100), (150, -50), (200, 50))
    pt = curve.evaluate(0.5)
    assert len(pt) == 2

    surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, 400, 400)
    ctx = cairo.Context(surface)
    emitter = AdvancedParticleEmitter(preset="confetti")
    emitter.draw(ctx, 1.0)


def test_phase7_audio_visualizers_and_sfx():
    """Verify Phase 7 Audio Visualizers and Procedural SFX."""
    surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, 600, 400)
    ctx = cairo.Context(surface)

    spec = SpectrumVisualizer(bars=16)
    spec.draw(ctx, 1.0)

    circ = CircularEqualizer(bars=24)
    circ.draw(ctx, 1.0)

    # Procedural SFX
    click_audio = ProceduralSFXGenerator.click()
    assert len(click_audio) > 0
    pop_audio = ProceduralSFXGenerator.pop()
    assert len(pop_audio) > 0
    whoosh_audio = ProceduralSFXGenerator.whoosh()
    assert len(whoosh_audio) > 0
    chime_audio = ProceduralSFXGenerator.chime()
    assert len(chime_audio) > 0
    impact_audio = ProceduralSFXGenerator.impact()
    assert len(impact_audio) > 0


def test_phase8_templates_and_exporter():
    """Verify Phase 8 Turnkey Templates and Exporter presets."""
    sc_saas = SceneTemplateLibrary.saas_product_launch(duration=2.0)
    assert sc_saas.duration >= 2.0
    assert len(sc_saas.nodes) > 0

    sc_milestone = SceneTemplateLibrary.metric_milestone_celebration(duration=2.0)
    assert sc_milestone.duration >= 2.0

    sc_cyber = SceneTemplateLibrary.cyberpunk_terminal_intro(duration=2.0)
    assert sc_cyber.duration >= 2.0

    assert "high" in QUALITY_PRESETS
    assert "draft" in QUALITY_PRESETS
    assert "4k60" in QUALITY_PRESETS
