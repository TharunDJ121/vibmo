"""
Unit tests for typography, rich markup tokens, and kinetic text animations.
"""

import pytest
from vibmo.typography.text import Text
from vibmo.typography.kinetic import KineticText


def test_text_bounds_and_rendering():
    txt = Text("Hello World", font_size=28.0)
    bx, by, bw, bh = txt.local_bounds(0.0)
    assert bw > 50
    assert bh > 15


def test_kinetic_text_rich_markup():
    rich_text = KineticText(
        "<bold>Autonomous</bold> <cyan>Motion</cyan> <gradient:#6366f1:#ec4899>Engine</gradient>",
        font_size=32.0,
    )
    tokens = rich_text._parse_rich_tokens(rich_text.raw_text, rich_text.color)
    assert len(tokens) >= 3
    assert tokens[0].bold is True
    assert tokens[1].color is not None
    assert len(tokens[0].text) > 0



def test_kinetic_text_verbs():
    kt = KineticText("Kinetic Title", font_size=36.0)

    # 1. reveal_characters
    action_chars = kt.reveal_characters(stagger=0.03, duration=0.8)
    assert action_chars is not None

    # 2. reveal_words
    action_words = kt.reveal_words(stagger=0.1, duration=0.6)
    assert action_words is not None

    # 3. typewriter
    action_type = kt.typewriter(speed=20.0)
    assert action_type is not None

    # 4. wave
    kt.wave(amplitude=8.0, speed=1.5)
    assert len(kt.children) > 0
