"""
Tests for LangGraph Motion Graphics Engine & Surgical Scene Editor.
"""

import pytest
from vibmo.ai.state import MotionGraphState
from vibmo.ai.surgical_editor import SurgicalSceneEditor
from vibmo.ai.graph import motion_langgraph, run_motion_edit


SAMPLE_SCRIPT = '''from motio.agent_api import *

s1 = Scene(width=720, height=1280, duration=1.8)
card = ModelCard(title="GPT-5", subtitle="Flagship model", position=(80, 560), shimmer=True)
s1.add(GradientBackdrop.sunset(), card)

s2 = Scene(width=720, height=1280, duration=2.0)
pill = ChatInputBar(text="Our smartest, fastest model yet", typing_speed=28.0, position=(40, 596))
s2.add(pill)

s3 = Scene(width=720, height=1280, duration=1.8)
kt = KineticSnapText(base_word="Think", word_a="deeper", word_b="faster", color_a="#8b5cf6", color_b="#f97316")
s3.add(kt)
'''


def test_surgical_text_replacement():
    modified, changes = SurgicalSceneEditor.apply_edit(
        SAMPLE_SCRIPT,
        'change "GPT-5" to "GPT-6"',
    )
    assert 'title="GPT-6"' in modified
    assert len(changes) > 0


def test_surgical_speed_adjustment():
    modified, changes = SurgicalSceneEditor.apply_edit(
        SAMPLE_SCRIPT,
        'make it type faster',
    )
    assert "typing_speed=" in modified
    assert len(changes) > 0


def test_surgical_color_modification():
    modified, changes = SurgicalSceneEditor.apply_edit(
        SAMPLE_SCRIPT,
        'in Scene 3 change color to #10b981',
    )
    assert '#10b981' in modified
    assert len(changes) > 0


def test_surgical_background_change():
    modified, changes = SurgicalSceneEditor.apply_edit(
        SAMPLE_SCRIPT,
        'change background to cerulean',
    )
    assert 'GradientBackdrop.cerulean()' in modified
    assert len(changes) > 0


def test_langgraph_invocation_surgical_edit():
    res = run_motion_edit(
        prompt='In Scene 3 change "deeper" to "bolder"',
        current_code=SAMPLE_SCRIPT,
    )
    assert res.get("intent") == "surgical_scene_edit"
    assert "bolder" in res.get("updated_code", "")
    assert res.get("is_valid", False) is True


def test_langgraph_invocation_new_story():
    res = run_motion_edit(
        prompt="Create a brand new cyber launch video with neon glow",
        current_code="",
    )
    assert res.get("intent") == "new_story_generation"
    assert "Scene(" in res.get("updated_code", "")
    assert res.get("is_valid", False) is True
