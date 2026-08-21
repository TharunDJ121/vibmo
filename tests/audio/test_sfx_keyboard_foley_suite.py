import numpy as np
import pytest
from vibmo.audio.generators.sfx_keyboard_foley_suite import KeyboardFoleySuite

def test_clicky_blue_switch():
    dur = 0.06
    sr = 48000
    audio = KeyboardFoleySuite.clicky_blue_switch(duration=dur)

    assert len(audio) == int(dur * sr)
    assert audio.dtype == np.float32

    max_idx = np.argmax(np.abs(audio))
    assert max_idx < len(audio) * 0.5

def test_tactile_brown_switch():
    dur = 0.05
    sr = 48000
    audio = KeyboardFoleySuite.tactile_brown_switch(duration=dur)

    assert len(audio) == int(dur * sr)
    assert audio.dtype == np.float32

    max_idx = np.argmax(np.abs(audio))
    assert max_idx < len(audio) * 0.5

def test_linear_red_switch():
    dur = 0.04
    sr = 48000
    audio = KeyboardFoleySuite.linear_red_switch(duration=dur)

    assert len(audio) == int(dur * sr)
    assert audio.dtype == np.float32

    max_idx = np.argmax(np.abs(audio))
    assert max_idx < len(audio) * 0.8

def test_spacebar_thud():
    dur = 0.09
    sr = 48000
    audio = KeyboardFoleySuite.spacebar_thud(duration=dur)

    assert len(audio) == int(dur * sr)
    assert audio.dtype == np.float32

    max_idx = np.argmax(np.abs(audio))
    assert max_idx < len(audio) * 0.5

def test_typewriter_bell():
    dur = 0.6
    sr = 48000
    audio = KeyboardFoleySuite.typewriter_bell(duration=dur)

    assert len(audio) == int(dur * sr)
    assert audio.dtype == np.float32

    max_idx = np.argmax(np.abs(audio))
    assert max_idx < len(audio) * 0.1
