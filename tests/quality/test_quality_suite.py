"""
Unit tests for Vibmo Quality, Slideshow Risk & Scene Pacing suite.
"""

import pytest
from vibmo.quality.slideshow_risk import SlideshowRiskScorer, SlideshowRiskReport
from vibmo.quality.pacing import ScenePacingVerifier, TimelineLandmark, PacingReport
from vibmo.quality.preflight import PreflightValidator, PreflightReport
from vibmo.ai.cinematography import ShotPromptBuilder, ShotSpecification
from vibmo.styles.harmony import ColorHarmonizer, TypographicScale
from vibmo.scene.scene import Scene


def test_slideshow_risk_scorer_empty():
    report = SlideshowRiskScorer.evaluate([])
    assert report.verdict == "fail"
    assert report.average_score == 5.0


def test_slideshow_risk_scorer_good_scene():
    scenes = [
        {"type": "hero_title", "has_motion": True, "description": "Kinetic Title with spring zoom", "shot_language": {"shot_size": "medium"}},
        {"type": "mockup_demo", "has_motion": True, "description": "Browser window with cursor click", "shot_language": {"movement": "dolly_in"}},
        {"type": "metric_counter", "has_motion": True, "description": "MRR Counter count up", "shot_language": {"lighting": "neon"}},
        {"type": "terminal_session", "has_motion": True, "description": "CLI live installation", "shot_language": {"shot_size": "close_up"}},
    ]
    report = SlideshowRiskScorer.evaluate(scenes)
    assert report.average_score < 2.5
    assert report.verdict in ("strong", "acceptable")


def test_slideshow_risk_evaluate_live_scene():
    scene = Scene(duration=4.0)
    report = SlideshowRiskScorer.evaluate_scene(scene)
    assert isinstance(report, SlideshowRiskReport)


def test_scene_pacing_landmark_tracing():
    steps = [
        {"kind": "cmd", "text": "pip install vibmo", "typeSpeed": 0.02, "holdSeconds": 0.2},
        {"kind": "out", "text": "Successfully installed vibmo-1.0.0", "holdSeconds": 0.15},
        {"kind": "pause", "seconds": 0.5},
    ]
    landmarks = ScenePacingVerifier.trace_landmarks(steps, scene_start=1.0)
    assert len(landmarks) == 3
    assert landmarks[0].video_time == 1.0
    assert landmarks[0].kind == "CMD"


def test_scene_pacing_alignment_verification():
    steps = [
        {"kind": "cmd", "text": "git clone", "typeSpeed": 0.03, "holdSeconds": 0.5},
        {"kind": "out", "text": "Done", "holdSeconds": 0.5},
    ]
    report = ScenePacingVerifier.verify_alignment(
        steps=steps,
        scene_start=0.0,
        scene_end=5.0,
        narration_cues=[(0.0, "Start clone"), (0.8, "Done clone")],
        tolerance=1.0,
    )
    assert report.is_aligned is True
    assert len(report.mismatches) == 0


def test_preflight_validator():
    scene = Scene(width=1920, height=1080, fps=60, duration=5.0)
    report = PreflightValidator.validate_scene(scene)
    assert report.passed is True


def test_shot_prompt_builder():
    spec = ShotSpecification(
        shot_size="medium_wide",
        movement="dolly_in",
        lighting="neon",
        depth_of_field="shallow",
        subject="Glassmorphic metric card",
    )
    prompt = ShotPromptBuilder.build_prompt(spec)
    assert "dolly in" in prompt
    assert "neon" in prompt
    assert "shallow depth of field" in prompt


def test_color_harmony_and_contrast():
    # White on dark background
    eval_res = ColorHarmonizer.evaluate_contrast("#FFFFFF", "#0B0F1A")
    assert eval_res.ratio > 10.0
    assert eval_res.is_wcag_aaa is True
    assert eval_res.rating == "AAA"

    # Complementary
    comp = ColorHarmonizer.generate_complementary("#00FFFF")
    assert comp.startswith("#")

    # Triadic & Analogous
    tri = ColorHarmonizer.generate_triadic("#FF0055")
    assert len(tri) == 3
    ana = ColorHarmonizer.generate_analogous("#00FF88")
    assert len(ana) == 3


def test_typographic_scale():
    scale = TypographicScale.generate_scale(base_size=16.0, ratio="perfect_fourth")
    assert "base" in scale
    assert scale["base"] == 16.0
    assert scale["h1"] > scale["base"]


def test_subtitle_generator_and_parser():
    from vibmo.typography.subtitles import SubtitleGenerator, SubtitleCue
    cues = [
        SubtitleCue(start_time=0.5, end_time=2.0, text="Welcome to Vibmo"),
        SubtitleCue(start_time=2.2, end_time=4.5, text="High performance motion graphics"),
    ]
    srt = SubtitleGenerator.generate_srt(cues)
    assert "00:00:00,500 --> 00:00:02,000" in srt
    assert "Welcome to Vibmo" in srt

    vtt = SubtitleGenerator.generate_vtt(cues)
    assert "WEBVTT" in vtt

    # Parse back
    parsed = SubtitleGenerator.parse_srt(srt)
    assert len(parsed) == 2
    assert parsed[0].text == "Welcome to Vibmo"


def test_background_remover_interface():
    from vibmo.video_post.bg_remove import BackgroundRemover
    avail = BackgroundRemover.is_available()
    assert isinstance(avail, bool)


def test_scene_detector_empty_or_synthetic():
    from vibmo.tracking.scene_detect import SceneDetector
    res = SceneDetector.detect_scenes("non_existent_video.mp4")
    assert isinstance(res, list)

