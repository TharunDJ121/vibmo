"""
Unit tests for Vibmo Tier Extras:
Aesthetic Style Presets, Aspect Ratio Auto-Reflow, Cinematic Transitions Suite,
Particle Force Fields, and Rack Focus Camera.
"""

import math
import numpy as np
import pytest

from vibmo.agent_api import (
    Scene,
    GlassCard,
    KineticText,
    MetricCounter,
    Styles,
    StylePreset,
    AspectRatio,
    SceneReflowEngine,
    WhipPan,
    ZoomPunch,
    GlitchTransition,
    LightLeak,
    ShapeWipe,
    DipToColor,
    ForceField,
    GravityField,
    VortexForce,
    TurbulentNoiseField,
    AttractorPoint,
    ParticleEmitter,
    Camera3D,
    Vector2D,
    colors,
)


def test_style_presets_and_application():
    scene = Scene(width=1920, height=1080, duration=3.0)
    card = GlassCard(position=(200, 200))
    title = KineticText("Cyberpunk Edition", font_size=32)
    counter = MetricCounter(start_val=0, end_val=100000)

    card.add(title, counter)
    scene.add(card)

    # Apply Cyberpunk aesthetic
    scene.apply_style(Styles.CYBERPUNK)
    assert scene.background == Styles.CYBERPUNK.background
    assert card.fill == Styles.CYBERPUNK.card_fill
    assert title.color == Styles.CYBERPUNK.text_primary
    assert counter.color == Styles.CYBERPUNK.accent
    assert len(scene.post_fx) > 0


def test_aspect_ratio_auto_reflow():
    scene = Scene(width=1920, height=1080, duration=3.0)
    card = GlassCard(position=(200, 200), width=400, height=200)
    scene.add(card)

    # Reflow to TikTok/Shorts 9:16 (1080x1920)
    reflowed = scene.reflow(AspectRatio.PORTRAIT_9_16)
    assert reflowed.width == 1080
    assert reflowed.height == 1920
    assert reflowed._rasterizer.width == 1080
    assert reflowed._rasterizer.height == 1920

    # Reflow to Instagram Square 1:1 (1080x1080)
    reflowed_sq = scene.reflow(AspectRatio.SQUARE_1_1)
    assert reflowed_sq.width == 1080
    assert reflowed_sq.height == 1080


def test_cinematic_transitions_suite():
    # 100x100 RGBA frame buffers
    img_a = np.full((100, 100, 4), 50, dtype=np.uint8)
    img_b = np.full((100, 100, 4), 200, dtype=np.uint8)

    # 1. WhipPan
    whip = WhipPan(direction="right", blur=True, duration=0.4)
    blended_whip = whip.blend(img_a, img_b, progress=0.5)
    assert blended_whip.shape == (100, 100, 4)

    # 2. ZoomPunch
    zoom = ZoomPunch(max_scale=2.0, duration=0.4)
    blended_zoom = zoom.blend(img_a, img_b, progress=0.25)
    assert blended_zoom.shape == (100, 100, 4)

    # 3. GlitchTransition
    glitch = GlitchTransition(slices=8, duration=0.3)
    blended_glitch = glitch.blend(img_a, img_b, progress=0.5)
    assert blended_glitch.shape == (100, 100, 4)

    # 4. LightLeak
    leak = LightLeak(duration=0.5)
    blended_leak = leak.blend(img_a, img_b, progress=0.5)
    assert blended_leak.shape == (100, 100, 4)

    # 5. ShapeWipe
    wipe = ShapeWipe(shape="circle", duration=0.5)
    blended_wipe = wipe.blend(img_a, img_b, progress=0.5)
    assert blended_wipe.shape == (100, 100, 4)

    # 6. DipToColor
    dip = DipToColor(color=colors.BLACK, duration=0.5)
    blended_dip = dip.blend(img_a, img_b, progress=0.5)
    assert blended_dip.shape == (100, 100, 4)


def test_particle_physics_force_fields():
    emitter = ParticleEmitter(preset="sparkles")
    vortex = VortexForce(center=(500, 500), strength=200.0)
    turb = TurbulentNoiseField(strength=100.0)
    attractor = AttractorPoint(center=(300, 300), mass=1000.0)

    emitter.add_force(vortex, turb, attractor)
    assert len(emitter.forces) == 3

    emitter.burst(count=10, time=0.0)
    assert len(emitter._particles) == 10

    # Verify force calculation
    f_vortex = vortex.calculate_force(Vector2D(600, 500), Vector2D(0, 0), time=0.5)
    assert abs(f_vortex.y - 200.0) < 1.0


def test_camera_rack_focus_group():
    cam = Camera3D()
    target_node = GlassCard(position=(200, 200), z=50.0)

    action = cam.rack_focus(target=target_node, aperture=0.12, duration=0.6)
    assert hasattr(action, "apply_at")
    assert hasattr(action, "actions")
    assert len(action.actions) == 2
