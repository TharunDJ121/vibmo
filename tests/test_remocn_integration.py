"""
Comprehensive tests for Remocn integration in Vibmo.
Verifies all shaders, typography, UI simulators, transitions, 6-beat product demo spine, and anti-slop validator.
"""

import pytest
import numpy as np
import cairo

from vibmo.agent_api import *


def test_ascii_render_filter():
    f = AsciiRenderFilter(glyph_size=12, colored=False, ink="#00ff00")
    dummy = np.full((120, 160, 4), 200, dtype=np.uint8)
    out = f.apply(dummy, time=0.5)
    assert out.shape == dummy.shape
    assert out.dtype == np.uint8


def test_security_cam_overlay():
    f = SecurityCamOverlay(camera_name="CAM 01 // TEST", show_rec=True)
    dummy = np.full((120, 160, 4), 100, dtype=np.uint8)
    out = f.apply(dummy, time=0.5)
    assert out.shape == dummy.shape
    assert out.dtype == np.uint8


def test_shader_neural_voronoi():
    neuro = ShaderNeuroNoise(speed=1.0)
    frame_neuro = neuro.render_frame(160, 120, time=0.5)
    assert frame_neuro.shape == (120, 160, 4)

    voronoi = ShaderVoronoiGrid(num_cells=8)
    frame_voronoi = voronoi.render_frame(160, 120, time=0.5)
    assert frame_voronoi.shape == (120, 160, 4)


def test_underwater_ripple_filter():
    f = UnderwaterRippleFilter(frequency=0.05, amplitude=4.0)
    dummy = np.full((120, 160, 4), 150, dtype=np.uint8)
    out = f.apply(dummy, time=0.5)
    assert out.shape == dummy.shape


def test_blur_out_up_typography():
    text = BlurOutUpText("Launch Week", font_size=32)
    action = text.blur_out_up(duration=0.5)
    assert action is not None

    surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, 400, 200)
    ctx = cairo.Context(surface)
    text.draw(ctx, time=0.2)


def test_matrix_decode_typography():
    text = MatrixDecodeText("QUANTUM SECURE", font_size=28)
    action = text.decode(duration=0.8)
    assert action is not None

    surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, 400, 200)
    ctx = cairo.Context(surface)
    text.draw(ctx, time=0.4)


def test_rolling_number_wheel():
    counter = RollingNumberWheel(start_val=0, end_val=5000, prefix="$", suffix=" MRR")
    action = counter.roll_to(4500, duration=1.0)
    assert action is not None

    surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, 400, 200)
    ctx = cairo.Context(surface)
    counter.draw(ctx, time=0.5)


def test_inline_pill_takeover():
    pill_text = InlinePillTakeoverText(
        before_text="Build with ",
        pill_text="zero boilerplate",
        after_text=" today.",
    )
    action = pill_text.expand_pill(duration=0.6)
    assert action is not None

    surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, 500, 200)
    ctx = cairo.Context(surface)
    pill_text.draw(ctx, time=0.3)


def test_strikethrough_replace():
    strike = StrikethroughReplaceText(
        old_text="Manual Video",
        new_text="AI Automated",
    )
    action = strike.animate_replacement(duration=0.8)
    assert action is not None

    surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, 500, 200)
    ctx = cairo.Context(surface)
    strike.draw(ctx, time=0.4)


def test_ai_prompt_flow():
    flow = AiPromptFlow(
        prompt_text="Build a SaaS product video",
        response_text="Generated 6-beat spine",
        model_name="Claude 3.7",
    )
    action_type = flow.type_prompt(duration=0.5)
    action_stream = flow.stream_response(duration=0.8)
    assert action_type is not None
    assert action_stream is not None

    surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, 800, 600)
    ctx = cairo.Context(surface)
    flow.draw(ctx, time=0.5)


def test_claude_code_simulator():
    term = ClaudeCodeSimulator(title="claude-code — ~/vibmo")
    term.add_command("pip install vibmo")
    term.add_output("Successfully installed vibmo-0.2.0")
    term.add_tool_call("GPU Pipeline", "Allocated WebGL Shaders")

    action = term.step_to(2, delay=0.1)
    assert action is not None

    surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, 900, 600)
    ctx = cairo.Context(surface)
    term.draw(ctx, time=0.3)


def test_interactive_checkout_flow():
    checkout = InteractiveCheckoutFlow(amount="$99 / year")
    action = checkout.trigger_payment(duration=1.0)
    assert action is not None

    surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, 600, 600)
    ctx = cairo.Context(surface)
    checkout.draw(ctx, time=0.5)


def test_social_follow_and_stars_cards():
    x_card = XFollowCard(name="Vibmo", handle="@vibmo_ai")
    action_x = x_card.click_follow(duration=0.4)
    assert action_x is not None

    gh_card = GitHubStarsCard(repo="Remocn/remocn")
    action_gh = gh_card.click_star(duration=0.4)
    assert action_gh is not None

    surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, 600, 400)
    ctx = cairo.Context(surface)
    x_card.draw(ctx, time=0.3)
    gh_card.draw(ctx, time=0.3)


def test_infinite_bento_pan():
    bento = InfiniteBentoPan()
    action = bento.pan_camera((100, 50), duration=1.0)
    assert action is not None

    surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, 800, 600)
    ctx = cairo.Context(surface)
    bento.draw(ctx, time=0.5)


def test_remocn_transitions():
    img_a = np.full((120, 160, 4), 50, dtype=np.uint8)
    img_b = np.full((120, 160, 4), 200, dtype=np.uint8)

    push = PushThroughTransition()
    out_push = push.blend(img_a, img_b, progress=0.4)
    assert out_push.shape == img_a.shape

    focus = FocusPullTransition()
    out_focus = focus.blend(img_a, img_b, progress=0.5)
    assert out_focus.shape == img_a.shape

    whip = WhipPanTransition()
    out_whip = whip.blend(img_a, img_b, progress=0.6)
    assert out_whip.shape == img_a.shape

    dither = DitherDissolveTransition()
    out_dither = dither.blend(img_a, img_b, progress=0.5)
    assert out_dither.shape == img_a.shape


def test_turnkey_product_demo_spine():
    scene = TmplSaasProductDemoSpineSuite.build_scene(duration=2.0)
    assert scene is not None
    assert scene.width == 1920
    assert scene.height == 1080
    assert len(scene.nodes) > 0


def test_turnkey_changelog_and_cli():
    scene_cl = TmplChangelogReleaseSuite.build_scene(duration=2.0)
    assert scene_cl is not None

    scene_cli = TmplCliDeveloperLaunchSuite.build_scene(duration=2.0)
    assert scene_cli is not None


def test_anti_slop_validator():
    scene = Scene(width=1920, height=1080, duration=2.0)
    card = GlassCard(position=(100, 100))
    title = Text("Build fast without boilerplate", font_size=24)
    card.add(title)
    scene.add(card)

    report = AntiSlopValidator.evaluate_scene(scene)
    assert report.verdict in ["pass", "warning", "fail"]
    assert report.score >= 0.0
