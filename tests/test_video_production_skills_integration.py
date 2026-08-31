"""
Unit and Integration Tests for Video Production Skills in Vibmo.
Verifies Dark SaaS Magic UI suites, Black & White Foley Typing Opener,
Anti-PPT Meta-Director & BeatGraph, and Video Replica QC Verifier.
"""

import pytest
import numpy as np
import cairo

from vibmo.agent_api import *


def test_dark_starfield_stage():
    stage = DarkStarfieldStage(particle_count=50, horizon_color="#7c3aed")
    surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, 1920, 1080)
    ctx = cairo.Context(surface)
    stage.draw(ctx, time=0.5)


def test_prompt_invocation_card():
    card = PromptInvocationCard(
        prompt_text="Build AI video engine",
        cta_text="Generate Video ✨",
        position=(960, 540),
    )
    action_enter = card.enter_card(duration=0.6)
    action_type = card.type_prompt(duration=1.0)
    action_click = card.click_cta(duration=0.4)

    assert action_enter is not None
    assert action_type is not None
    assert action_click is not None

    surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, 1920, 1080)
    ctx = cairo.Context(surface)
    card.draw(ctx, time=0.5)


def test_model_orbit_and_export_burst():
    orbit = ModelCapabilityOrbit(
        center_title="MULTI-MODEL",
        models=["Claude 3.7", "GPT-4o", "DeepSeek R1"],
        position=(960, 540),
    )
    action_open = orbit.open_ring(duration=0.5)
    action_rot = orbit.rotate_orbit(revolutions=0.5, duration=0.8)
    assert action_open is not None
    assert action_rot is not None

    burst = ExportBurstContainer(
        headline="Export Ready",
        formats=["PDF", "MP4", "API"],
        position=(960, 540),
    )
    action_burst = burst.trigger_burst(duration=0.6)
    assert action_burst is not None

    slot = ConnectEcosystemSlot(hub_name="Cloud Hub", integrations=["GitHub", "Slack"], position=(960, 540))
    action_slot = slot.animate_connect(duration=0.6)
    assert action_slot is not None

    surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, 1920, 1080)
    ctx = cairo.Context(surface)
    orbit.draw(ctx, time=0.3)
    burst.draw(ctx, time=0.4)
    slot.draw(ctx, time=0.4)


def test_tmpl_dark_saas_magic_suite():
    scene = TmplDarkSaasMagicSuite.build_scene(
        product_name="Vibmo Magic",
        prompt_text="Generate high-converting SaaS video in Python",
        duration=5.0,
    )
    assert len(scene.nodes) == 4
    report = AntiSlopValidator.evaluate_scene(scene)
    assert report.score >= 0.0


def test_black_white_typing_opener():
    opener = BlackWhiteTypingOpener(
        title_prefix="AI Video Engine",
        replace_phrases=["from raw idea", "to shipped promo"],
        position=(960, 540),
    )
    action_type = opener.type_intro(duration=0.8)
    action_rep = opener.cycle_replace(1.0, duration=0.5)
    action_wipe = opener.velocity_wipe(duration=0.4)

    assert action_type is not None
    assert action_rep is not None
    assert action_wipe is not None

    surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, 1920, 1080)
    ctx = cairo.Context(surface)
    opener.draw(ctx, time=0.4)


def test_anti_ppt_meta_director():
    thesis = MotionThesis(
        visual_metaphor="branching neural stream",
        start_state="single raw cursor input",
        end_state="distributed multi-agent verified code",
        core_claim="zero manual boilerplate",
    )
    assert "branching neural stream" in thesis.to_statement()

    graph = BeatGraph(thesis=thesis)
    graph.add_beat(0.0, 1.5, "hook", "cursor", "idle", "prompt typed", "stream", has_state_change=True)
    graph.add_beat(1.5, 3.0, "reveal", "model ring", "closed", "orbiting 3D", "orbit", has_state_change=True)
    graph.add_beat(3.0, 4.5, "mechanism", "export box", "compact", "radiating pills", "expand", has_state_change=True)
    graph.add_beat(4.5, 6.0, "close", "brand wordmark", "small", "hero hold", "cluster", has_state_change=True)

    assert graph.state_change_ratio() == 1.0
    report = AntiPptGate.evaluate_beat_graph(graph)
    assert report.verdict == "pass"
    assert report.score >= 8.0


def test_anti_ppt_gate_rejects_static_slides():
    thesis = MotionThesis("deck", "slide 1", "slide 2", "presentation")
    graph = BeatGraph(thesis=thesis)
    graph.add_beat(0.0, 2.0, "hook", "title", "none", "shown", "fade", has_state_change=False)
    graph.add_beat(2.0, 4.0, "reveal", "bullets", "none", "shown", "pop", has_state_change=False)
    graph.add_beat(4.0, 6.0, "close", "footer", "none", "shown", "appear", has_state_change=False)

    report = AntiPptGate.evaluate_beat_graph(graph)
    assert report.verdict in ["warning", "fail"]
    assert len(report.violations) > 0


def test_video_replica_verifier():
    # Construct synthetic reference and identical candidate frames
    ref_frame = np.full((1080, 1920, 3), 128, dtype=np.uint8)
    cand_frame = np.full((1080, 1920, 3), 128, dtype=np.uint8)

    result_exact = VideoReplicaVerifier.compare_frame_arrays([ref_frame], [cand_frame])
    assert result_exact.mean_absolute_error == 0.0
    assert result_exact.psnr_db == 100.0
    assert result_exact.fidelity_achieved == FidelityLevel.LEVEL_2_LOSSLESS_RENDER

    verdict = VideoReplicaVerifier.evaluate_three_gates(result_exact)
    assert verdict.overall_status == "aligned"
    assert verdict.asset_gate_passed is True
    assert verdict.delivery_gate_passed is True

    # Construct slightly modified candidate frame
    cand_noisy = (ref_frame.astype(np.int16) + 4).clip(0, 255).astype(np.uint8)
    result_close = VideoReplicaVerifier.compare_frame_arrays([ref_frame], [cand_noisy])
    assert result_close.mean_absolute_error == 4.0
    assert result_close.fidelity_achieved in [FidelityLevel.LEVEL_3_FRAME_ALIGNED_MP4, FidelityLevel.LEVEL_4_VISUAL_REBUILD]
