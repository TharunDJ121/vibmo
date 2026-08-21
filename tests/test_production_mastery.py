"""
Comprehensive test suite for Vibmo Major Production Capabilities:
Timeline Tracks, Editorial Markers, Advanced Compositing, Blend Modes, Masks,
Rigging Constraints, Color Management, Chroma Keying, Tracking, Audio Stems, and Portable Projects.
"""

import os
import json
import math
import numpy as np
import pytest

from vibmo.agent_api import (
    Scene,
    Composition,
    Shot,
    Marker,
    LayerTrack,
    BlendMode,
    Mask,
    Constraint,
    LookAtConstraint,
    FollowConstraint,
    PathConstraint,
    ExpressionSignal,
    expression,
    ColorSpace,
    ColorManager,
    ChromaKey,
    PointTracker,
    AudioStemMixer,
    VibmoProject,
    ProjectMediaItem,
    GlassCard,
    Rect,
    Circle,
    Node,
    Vector2D,
    Color,
    colors,
)


def test_timeline_tracks_and_markers():
    comp = Composition(width=1920, height=1080, duration=5.0)

    # Markers
    m1 = comp.add_marker(time=1.2, name="Beat Drop", color=colors.CYAN, comment="Hero card pops in")
    m2 = comp.add_marker(time=3.5, name="CTA Outro", color=colors.EMERALD, duration=1.5)

    assert comp.get_marker("Beat Drop") == m1
    assert len(comp.find_markers(1.0, 4.0)) == 2
    assert m2.end_time == 5.0

    # Layer Tracks
    v1 = comp.track("Graphics", kind="video")
    v2 = comp.track("Overlays", kind="video")
    v2.solo = True

    card = GlassCard(position=(200, 200))
    v1.add(card)
    comp.add(card)

    assert card.track_name == "Graphics"
    assert len(v1.nodes) == 1
    assert comp.get_track("Graphics") == v1

    desc = comp.describe()
    assert "Beat Drop" in desc
    assert "Graphics" in desc


def test_blend_modes_and_masks():
    scene = Scene(width=640, height=480, duration=1.0)
    
    # Node with BlendMode and Mask
    card = GlassCard(position=(100, 100))
    card.set_blend_mode(BlendMode.SCREEN)
    assert card.blend_mode == "screen"

    # Set mask
    mask_shape = Circle(radius=80, position=(150, 150))
    card.set_mask(mask_shape, invert=False, feather=4.0)

    assert card.mask is not None
    assert card.mask.feather == 4.0

    scene.add(card)
    # Render frame to ensure rasterizer executes blend mode and mask clipping
    rgba = scene._rasterizer.render_frame(scene.nodes, time=0.5, background=colors.DARK_NAVY)
    assert rgba.shape == (480, 640, 4)


def test_rigging_and_constraints():
    node_a = Node(name="TargetNode", position=(400.0, 300.0))
    node_b = Node(name="FollowerNode", position=(100.0, 100.0))

    # LookAt constraint
    look_at = LookAtConstraint(target=node_a)
    node_b.add_constraint(look_at)
    node_b.apply_constraints(time=0.0)

    # dy = 200, dx = 300 -> atan2(200, 300) rad
    expected_angle = math.atan2(200.0, 300.0)
    assert abs(node_b.rotation.get(0.0) - expected_angle) < 1e-4

    # Follow constraint
    follower = Node(name="ChildFollower", position=(0.0, 0.0))
    follow = FollowConstraint(target=node_a, offset=(50.0, 20.0))
    follower.add_constraint(follow)
    follower.apply_constraints(time=0.0)
    assert follower.position.get(0.0).x == 450.0
    assert follower.position.get(0.0).y == 320.0

    # Path constraint
    path_pts = [(0.0, 0.0), (100.0, 50.0), (200.0, 200.0)]
    path_node = Node(name="PathWalker")
    p_constraint = PathConstraint(points=path_pts, progress=0.5)
    path_node.add_constraint(p_constraint)
    path_node.apply_constraints(time=0.0)
    assert path_node.position.get(0.0).x == 100.0
    assert path_node.position.get(0.0).y == 50.0

    # Expression signal
    expr_sig = expression(lambda t: math.sin(t) * 100.0)
    assert abs(expr_sig.get(0.0) - 0.0) < 1e-4
    assert abs(expr_sig.get(math.pi * 0.5) - 100.0) < 1e-4


def test_color_management_and_hdr():
    # sRGB <-> Linear
    rgb = np.array([[[0.5, 0.2, 0.8]]], dtype=np.float32)
    linear = ColorManager.srgb_to_linear(rgb)
    srgb_back = ColorManager.linear_to_srgb(linear)
    assert np.allclose(rgb, srgb_back, atol=1e-3)

    # ACES filmic tonemapping
    hdr_rgb = np.array([[[2.5, 1.2, 5.0]]], dtype=np.float32)
    tonemapped = ColorManager.aces_filmic_tonemap(hdr_rgb)
    assert tonemapped.max() <= 1.0

    # Gamut convert
    converted = ColorManager.convert(rgb, ColorSpace.SRGB, ColorSpace.ACES_CG)
    assert converted.shape == rgb.shape


def test_chroma_keying_and_tracking():
    # Chroma key test
    keyer = ChromaKey(key_color="#00ff00", tolerance=0.3, softness=0.1)
    
    # Pure green image
    green_img = np.zeros((10, 10, 4), dtype=np.uint8)
    green_img[:, :, 1] = 255
    green_img[:, :, 3] = 255

    keyed = keyer.apply(green_img)
    # Alpha should be 0 on pure green
    assert keyed[5, 5, 3] == 0

    # Point tracker test
    tracker = PointTracker([(0.0, 100.0, 100.0), (1.0, 200.0, 300.0)])
    pos_mid = tracker.get_position(0.5)
    assert pos_mid.x == 150.0
    assert pos_mid.y == 200.0

    track_node = Node(name="TrackedTag")
    tracker.attach(track_node, offset=(10, 10))
    assert track_node.position.get(0.5).x == 160.0
    assert track_node.position.get(0.5).y == 210.0


def test_audio_stems_export(tmp_path):
    scene = Scene(duration=2.0)
    dummy_wav = str(tmp_path / "soundtrack.wav")
    with open(dummy_wav, "wb") as f:
        f.write(b"RIFFdummydata")

    scene.add_audio_track(dummy_wav, start=0.0, duration=2.0, name="Main Music")
    scene.add_audio_track(dummy_wav, start=0.5, duration=1.0, name="VO Narration")

    stems_dir = str(tmp_path / "stems")
    stems = scene.export_audio_stems(stems_dir)
    assert isinstance(stems, dict)


def test_vibmo_project_and_bundling(tmp_path):
    proj = VibmoProject(name="Launch Promo 2026", width=1920, height=1080, fps=60.0)
    
    # Add dummy asset
    asset_path = str(tmp_path / "logo.png")
    with open(asset_path, "wb") as f:
        f.write(b"PNGFAKE")

    item = proj.add_media(asset_path, kind="image", name="Company Logo")
    assert item.name == "Company Logo"
    assert not item.missing

    # Save project JSON
    proj_file = str(tmp_path / "project.vibmo")
    proj.save(proj_file)
    assert os.path.exists(proj_file)

    # Load project
    loaded_proj = VibmoProject.load(proj_file)
    assert loaded_proj.name == "Launch Promo 2026"
    assert len(loaded_proj.media_items) == 1

    # Bundle to zip
    bundle_zip = str(tmp_path / "project_bundle.vibmo")
    res_path = proj.bundle(bundle_zip)
    assert os.path.exists(res_path)
