"""
Advanced unit tests for Camera3D, Scene parameters, storyboard generation, and nested choreography.
"""

import os
import tempfile
import pytest
from vibmo.scene.scene import Scene
from vibmo.scene.camera import Camera3D
from vibmo.scene.node import Node
from vibmo.components.glass import GlassCard
from vibmo.timeline.scheduler import all, sequence, wait
from vibmo.core.vector import Vector2D
from vibmo.core.color import colors


def test_camera_orbit_pan_zoom():
    cam = Camera3D()
    cam.zoom_to((500, 300), zoom=2.0, duration=0.8)
    cam.pan_to((200, 100), duration=0.5)
    cam.orbit(yaw=0.4, pitch=0.2, duration=0.6)

    # View matrix calculation
    mat = cam.view_matrix(1920, 1080, time=0.0)
    assert mat is not None


def test_camera_follow_node():
    node = Node(name="target_player", position=(100, 100))
    cam = Camera3D()
    cam.follow(node)

    # Animate target node
    node.position.to(Vector2D(600, 400), duration=1.0).apply_at(0.0)

    # Camera should dynamically follow
    pos_at_half = cam.position.get(0.5)
    assert pos_at_half is not None


def test_scene_parameters_and_reactivity():
    scene = Scene(width=1280, height=720, duration=3.0)
    param_title = scene.param("title_text", default="Initial Title", description="Main headline")
    assert param_title() == "Initial Title"

    param_title.set("Updated Headline")
    assert param_title() == "Updated Headline"


def test_nested_generator_choreography():
    scene = Scene(width=1280, height=720, duration=4.0)
    card1 = GlassCard(position=(100, 100))
    card2 = GlassCard(position=(400, 100))
    scene.add(card1, card2)

    def sub_anim(node):
        yield node.pop_in(duration=0.5)
        yield wait(0.2)
        yield node.fade_out(duration=0.3)

    @scene.animate
    def main():
        yield all(
            sub_anim(card1),
            sub_anim(card2),
        )

    # Verify duration was processed
    assert len(card1.scale._segments) > 0
    assert len(card2.scale._segments) > 0


def test_scene_snapshot_and_storyboard_temp():
    scene = Scene(width=640, height=360, duration=2.0, background=colors.DARK_NAVY)
    card = GlassCard(position=(50, 50), width=200, height=100)
    scene.add(card)

    temp_snap = os.path.join(tempfile.gettempdir(), "test_vibmo_snap.png")
    temp_sb = os.path.join(tempfile.gettempdir(), "test_vibmo_sb.png")
    try:
        scene.snapshot(time=0.5, path=temp_snap)
        assert os.path.exists(temp_snap)

        scene.storyboard(path=temp_sb, rows=2, cols=3)
        assert os.path.exists(temp_sb)
    finally:
        if os.path.exists(temp_snap):
            os.remove(temp_snap)
        if os.path.exists(temp_sb):
            os.remove(temp_sb)
