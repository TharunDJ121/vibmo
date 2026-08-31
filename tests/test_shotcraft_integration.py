"""
Unit and Integration Tests for Video-Shotcraft in Vibmo.
Verifies all 10-motion staging suites, Keynote Outro Family Portrait,
Audio Beat-Sync Engine, CapCut/JianYing draft exporter, and Aesthetic Case Law Validator.
"""

import pytest
import numpy as np
import cairo
import json
import os

from vibmo.agent_api import *


def test_deck_deal_flyin():
    deck = DeckDealFlyIn(
        cards=[
            {"title": "Neural Engine", "metric": "99.4%"},
            {"title": "GPU Pipeline", "metric": "60 FPS"},
            {"title": "Vector Index", "metric": "100k"},
        ],
        spread_radius=300.0,
    )
    action_deal = deck.deal_cards(duration=0.8)
    action_fan = deck.fan_out(duration=0.5)
    assert action_deal is not None
    assert action_fan is not None

    surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, 1920, 1080)
    ctx = cairo.Context(surface)
    deck.draw(ctx, time=0.4)


def test_doc_park_pill_deal():
    doc = DocParkPillDeal(
        doc_title="Research Synthesis",
        pills=["Summary", "Benchmarks", "Checklist"],
    )
    action_dock = doc.dock_left(duration=0.5)
    action_pills = doc.deal_pills(duration=0.6)
    assert action_dock is not None
    assert action_pills is not None

    surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, 1920, 1080)
    ctx = cairo.Context(surface)
    doc.draw(ctx, time=0.3)


def test_spotlight_hero_suite():
    floor = DarkMetallicFloor(floor_y=600.0)
    hero = SpotlightHeroCard(
        title="Vector Engine",
        subtitle="Sub-millisecond Search",
        metric_value="0.42 ms",
    )
    action_spot = hero.ignite_spotlight(duration=0.5)
    action_lift = hero.lift_card(duration=0.6)
    action_sheen = hero.sweep_sheen(duration=0.4)

    assert action_spot is not None
    assert action_lift is not None
    assert action_sheen is not None

    surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, 1920, 1080)
    ctx = cairo.Context(surface)
    floor.draw(ctx, time=0.5)
    hero.draw(ctx, time=0.5)


def test_autolayout_gap_dial():
    dial = AutolayoutGapDial(
        block_labels=["Header", "Body", "Footer"],
        min_gap=10.0,
        max_gap=50.0,
    )
    action = dial.expand_gap(40.0, duration=0.6)
    assert action is not None

    surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, 1200, 600)
    ctx = cairo.Context(surface)
    dial.draw(ctx, time=0.3)


def test_chip_grid_select_blackout():
    grid = ChipGridSelectBlackout(
        options=["Standard", "Pro", "Enterprise"],
        selected_index=1,
    )
    action = grid.trigger_select(duration=0.5)
    assert action is not None

    surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, 1200, 400)
    ctx = cairo.Context(surface)
    grid.draw(ctx, time=0.25)


def test_avatar_bracket_carousel():
    carousel = AvatarBracketCarousel(
        roles=["Coder", "Architect", "Tester"],
    )
    action = carousel.cycle_to(1.0, duration=0.4)
    assert action is not None

    surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, 1200, 300)
    ctx = cairo.Context(surface)
    carousel.draw(ctx, time=0.2)


def test_bezier_source_converge_merge():
    merge = BezierSourceConvergeMerge(
        hub_name="Intelligence Hub",
        sources=["PRs", "DB", "Logs"],
    )
    action = merge.animate_flow(duration=0.8)
    assert action is not None

    surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, 1200, 600)
    ctx = cairo.Context(surface)
    merge.draw(ctx, time=0.4)


def test_outro_group_photo_launch():
    outro = OutroGroupPhotoLaunch(
        brand_name="Vibmo AI",
        tagline="Autonomous Motion Graphics",
        feature_cards=[
            {"title": "Neural Shaders", "corner": "top_left"},
            {"title": "Audio Sync", "corner": "top_right"},
            {"title": "CapCut Export", "corner": "bottom_left"},
        ],
    )
    action = outro.launch_family_portrait(duration=1.0)
    assert action is not None

    surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, 1920, 1080)
    ctx = cairo.Context(surface)
    outro.draw(ctx, time=0.5)


def test_brand_ink_open_and_brace_expand():
    ink = BrandInkOpen(brand_name="VIBMO", subtitle="CORE ENGINE")
    action_ink = ink.animate_intro(duration=0.6)
    assert action_ink is not None

    brace = BraceExpand(title_text="ZERO BOILERPLATE")
    action_brace = brace.expand(duration=0.5)
    assert action_brace is not None

    surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, 800, 400)
    ctx = cairo.Context(surface)
    ink.draw(ctx, time=0.3)
    brace.draw(ctx, time=0.3)


def test_rhythmic_cuts_and_flash():
    cuts = BeatCutAccelerando(cut_labels=["CUT 1", "CUT 2", "CUT 3"])
    action_cut = cuts.step_cut(1, duration=0.1)
    assert action_cut is not None

    flash = PaparazziFlash()
    action_flash = flash.trigger_flash(duration=0.2)
    assert action_flash is not None

    surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, 1200, 600)
    ctx = cairo.Context(surface)
    cuts.draw(ctx, time=0.05)
    flash.draw(ctx, time=0.05)


def test_beat_sync_grid_and_timeline_sfx():
    grid = BeatSyncGrid(bpm=120.0, beat0_sec=0.1, fps=60.0)
    assert grid.beat_period == 0.5
    assert grid.beat_time(0) == 0.1
    assert grid.beat_time(2) == 1.1
    assert grid.beat_frame(2) == 66

    assert grid.is_on_beat(1.1, tolerance_sec=0.02)
    assert not grid.is_on_beat(1.35, tolerance_sec=0.02)

    sfx_table = TimelineSFXTable(grid=grid)
    sfx_table.add_cue(
        name="whoosh_passby",
        target_beat=4.0,
        peak_offset_sec=0.15,
        volume=0.85,
        category="transition",
    )
    schedule = sfx_table.export_cues_schedule(fps=60.0)
    assert len(schedule) == 1
    assert schedule[0]["target_beat"] == 4.0
    assert schedule[0]["start_time"] == pytest.approx(1.95, rel=1e-2)


def test_jianying_draft_exporter(tmp_path):
    exporter = JianYingDraftExporter(fps=60.0, width=1920, height=1080)
    exporter.add_video_segment("Hero Section", 0, 120)
    exporter.add_subtitle("Autonomous Motion Graphics", 30, 90)
    exporter.add_audio("whoosh.mp3", 10, 45, volume=0.7)

    payload = exporter.build_draft_payload()
    assert payload["version"] == "11.2.0"
    assert len(payload["tracks"]) == 3
    assert len(payload["tracks"][0]["segments"]) == 1
    assert len(payload["tracks"][1]["segments"]) == 1
    assert len(payload["tracks"][2]["segments"]) == 1

    out_file = os.path.join(tmp_path, "draft_content.json")
    exported_path = exporter.export_to_file(out_file)
    assert os.path.exists(exported_path)

    with open(exported_path, "r", encoding="utf-8") as f:
        data = json.load(f)
        assert data["canvas_config"]["fps"] == 60.0


def test_aesthetic_case_law_validator():
    scene = Scene(width=1920, height=1080, duration=4.0)
    hero = SpotlightHeroCard(position=(960, 540))
    outro = OutroGroupPhotoLaunch(position=(960, 540))
    scene.add(hero, outro)

    report = AestheticCaseLawValidator.evaluate_scene(scene)
    assert report.verdict in ["pass", "warning", "fail"]
    assert report.score >= 0.0
