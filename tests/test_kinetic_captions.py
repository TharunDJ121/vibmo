"""
Tests for KineticCaptions and word-by-word subtitle rendering.
"""

import pytest
from vibmo.typography.captions import KineticCaptions, CaptionWord
from vibmo.scene.scene import Scene
from vibmo.core.color import Color


def test_caption_word_parsing():
    w = CaptionWord(text="Vibmo", start=0.0, end=0.5)
    assert w.text == "Vibmo"
    assert w.start == 0.0
    assert w.end == 0.5

    w_dict = CaptionWord.from_dict({"text": "Superpower", "start": 0.5, "end": 1.2, "color": "#10B981"})
    assert w_dict.text == "Superpower"
    assert w_dict.start == 0.5
    assert w_dict.color is not None


def test_kinetic_captions_line_chunking():
    words = [
        {"text": "Welcome", "start": 0.0, "end": 0.3},
        {"text": "to", "start": 0.3, "end": 0.5},
        {"text": "the", "start": 0.5, "end": 0.7},
        {"text": "future", "start": 0.7, "end": 1.1},
        {"text": "of", "start": 1.1, "end": 1.3},
        # This will wrap to line 2 (words_per_line=5)
        {"text": "motion", "start": 1.3, "end": 1.7},
        {"text": "design", "start": 1.7, "end": 2.2},
    ]

    captions = KineticCaptions(words=words, words_per_line=5)
    assert len(captions.lines) == 2
    assert len(captions.lines[0]) == 5
    assert len(captions.lines[1]) == 2
    assert captions.lines[0][0].text == "Welcome"
    assert captions.lines[1][0].text == "motion"


def test_kinetic_captions_in_scene():
    scene = Scene(width=1080, height=1920, duration=3.0)  # 9:16 vertical shorts video
    captions = KineticCaptions(
        words=[
            {"text": "AI", "start": 0.0, "end": 0.4},
            {"text": "Agents", "start": 0.4, "end": 0.9},
            {"text": "Rule", "start": 0.9, "end": 1.5},
        ],
        style_preset="tiktok_bounce",
    )
    scene.add(captions)
    assert len(scene.nodes) == 1

    # Render frame 1.0 (time = 1.0s, "Rule" is active)
    frame = scene.render_frame(1.0)
    assert frame is not None
    assert frame.shape == (1920, 1080, 4)
