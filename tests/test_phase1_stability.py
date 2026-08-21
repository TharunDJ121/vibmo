"""
Phase 1 Stability & Pre-flight Diagnostics Test Suite.
Verifies all 5 bug fixes, scene.validate(), scene.describe(), and API stubs.
"""

import os
import pytest
from fastapi.testclient import TestClient
from vibmo import (
    Scene,
    GlassCard,
    KineticText,
    MetricCounter,
    Color,
    colors,
    Camera,
    Vector2D,
    DropShadow,
    Ease,
)
from vibmo.physics.particles import ParticleEmitter
from vibmo.studio import create_studio_app


def test_scene_validate_and_describe():
    scene = Scene(width=1920, height=1080, fps=60, duration=4.0)
    card = GlassCard(position=(200, 200), width=400, height=200)
    title = KineticText("Valid Scene Title", font_size=32)
    card.add(title)
    scene.add(card)

    # 1. Valid scene should have 0 issues
    issues = scene.validate()
    assert issues == []

    # 2. Scene describe should return structured ASCII tree
    desc = scene.describe()
    assert "Scene (1920x1080 @ 60 FPS, 4.00s)" in desc
    assert "GlassCard" in desc
    assert "KineticText" in desc

    # 3. Invalid audio asset triggers validation warning
    scene.audio_path = "non_existent_audio_file.mp3"
    issues_with_audio = scene.validate()
    assert any("Audio file not found" in msg for msg in issues_with_audio)


def test_scene_validate_timing_overflow():
    scene = Scene(width=1920, height=1080, fps=60, duration=3.0)
    card = GlassCard(position=(100, 100), width=200, height=100)
    scene.add(card)

    # Schedule an animation that ends at t=5.0s on a 3.0s scene
    action = card.position.to(Vector2D(500, 500), duration=2.0, delay=3.0)
    action.apply_at(0.0)

    issues = scene.validate()
    assert any("exceeding scene duration" in msg for msg in issues)


def test_color_token_matching():
    # Exact keyword
    c_green = Color.from_any("green")
    assert c_green.g > c_green.r and c_green.g > c_green.b

    # Token with hyphens
    c_slate = Color.from_any("dark-slate-900")
    assert 0.0 <= c_slate.r <= 1.0

    # Specific alias
    c_neon = Color.from_any("neon_green")
    assert c_neon.g > 0.9


def test_shadow_lru_cache():
    from vibmo.spatial.shadows import _SHADOW_CACHE, DropShadow
    import cairo

    surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, 200, 200)
    ctx = cairo.Context(surface)

    shadow = DropShadow(blur=20.0)
    shadow.render_shadow(ctx, (10, 10, 100, 100), corner_radius=10.0)

    # Verify key exists in LRU cache
    assert len(_SHADOW_CACHE) > 0


def test_camera_shake_one_shot_decay():
    cam = Camera()
    action = cam.shake(amplitude=20.0, duration=0.5, frequency=20.0, start_time=1.0)
    assert action is not None

    # Before start_time -> 0 offset
    off_before = cam.get_shake_offset(0.5)
    assert off_before.x == 0.0 and off_before.y == 0.0

    # During shake -> non-zero offset
    off_during = cam.get_shake_offset(1.1)
    assert off_during.magnitude > 0.0

    # After duration -> 0 offset (no infinite loop)
    off_after = cam.get_shake_offset(2.0)
    assert off_after.x == 0.0 and off_after.y == 0.0


def test_particles_burst_and_emit_actions():
    emitter = ParticleEmitter(preset="confetti")
    burst_action = emitter.burst(count=20, time=0.5)
    assert burst_action is not None

    emit_action = emitter.emit(duration=1.0, rate=20.0, start_time=0.0)
    assert emit_action is not None


def test_studio_sfx_play_endpoint():
    scene = Scene(width=1920, height=1080, duration=2.0)
    app = create_studio_app(scene)
    client = TestClient(app)

    # Trigger pop sound
    res = client.get("/api/sfx/play/pop")
    assert res.status_code == 200
    assert res.headers["content-type"] == "audio/wav"
    assert len(res.content) > 100

    # Unknown sound triggers 404
    res_unknown = client.get("/api/sfx/play/unknown_sound_xyz")
    assert res_unknown.status_code == 404
