"""
Unit tests for Node scene graph hierarchy, transforms, and motion verbs.
"""

import math
import pytest
from vibmo.scene.node import Node
from vibmo.core.vector import Vector2D
from vibmo.layout.alignment import Align


def test_node_world_transform_propagation():
    parent = Node(name="parent", position=(100, 50), scale=(2.0, 2.0))
    child = Node(name="child", position=(20, 10), scale=(1.5, 1.5))
    parent.add(child)

    world_mat = child.world_matrix(0.0)
    p_trans = world_mat.transform_point(Vector2D(0, 0))

    # Parent (100, 50) + Scale(2.0, 2.0) * child (20, 10) -> (140, 70)
    assert math.isclose(p_trans.x, 140.0)
    assert math.isclose(p_trans.y, 70.0)


def test_node_motion_verbs():
    node = Node(name="verb_test", position=(0, 0))

    # 1. pop_in
    action_pop = node.pop_in(delay=0.1, duration=0.8)
    if isinstance(action_pop, list):
        from vibmo.timeline.scheduler import ParallelGroup
        action_pop = ParallelGroup(action_pop)
    action_pop.apply_at(0.0)
    assert node.scale.get(0.0).x < 0.7
    assert node.opacity.get(0.0) == 0.0

    # 2. fade_up
    node_fade = Node(name="fade_node", position=(0, 100))
    action_fade = node_fade.fade_up(offset=40.0, duration=0.6)
    if isinstance(action_fade, list):
        from vibmo.timeline.scheduler import ParallelGroup
        action_fade = ParallelGroup(action_fade)
    action_fade.apply_at(1.0)
    assert node_fade.opacity.get(1.0) == 0.0


    # 3. bounce
    action_bounce = node.bounce(amplitude=1.5, count=2, duration=0.5)
    action_bounce.apply_at(2.0)
    assert node.scale.get(2.0).x >= 0.9

    # 4. tilt_3d and reset_tilt
    action_tilt = node.tilt_3d(pitch=0.2, yaw=0.3, duration=0.5)
    action_tilt.apply_at(3.0)
    action_reset = node.reset_tilt(duration=0.5)
    action_reset.apply_at(3.5)
    assert action_reset is not None


def test_node_trim_visibility():
    node = Node(name="trim_test")
    node.trim(in_point=1.0, out_point=3.0)

    assert node.in_point == 1.0
    assert node.out_point == 3.0
    assert node.world_opacity(0.5) == 0.0
    assert node.world_opacity(2.0) == 1.0
    assert node.world_opacity(3.5) == 0.0


def test_node_alignment():
    node = Node(name="align_test")
    # Align to bottom right of 1920x1080 canvas
    node.align(Align.BOTTOM_RIGHT, canvas_size=(1920, 1080))
    pos = node.position.get(0.0)
    # (1920 - 10 - 40, 1080 - 10 - 40) = (1870, 1030)
    assert pos.x > 1800.0
    assert pos.y > 1000.0

