import numpy as np
import pytest
from vibmo.audio.generators.sfx_liquid_bubbles_suite import LiquidBubblesSuite

def test_liquid_drop_splash():
    audio = LiquidBubblesSuite.liquid_drop_splash(duration=0.15, resonant_pitch=1200.0)
    assert isinstance(audio, np.ndarray)
    assert audio.dtype == np.float32
    assert len(audio) == int(0.15 * 48000)

    # Check if there's actual sound
    assert np.max(np.abs(audio)) > 0

def test_viscous_pop_bubble():
    audio = LiquidBubblesSuite.viscous_pop_bubble(duration=0.09)
    assert isinstance(audio, np.ndarray)
    assert audio.dtype == np.float32
    assert len(audio) == int(0.09 * 48000)
    assert np.max(np.abs(audio)) > 0

def test_submerged_bubble_cluster():
    audio = LiquidBubblesSuite.submerged_bubble_cluster(duration=0.6, bubble_count=10)
    assert isinstance(audio, np.ndarray)
    assert audio.dtype == np.float32
    assert len(audio) == int(0.6 * 48000)
    assert np.max(np.abs(audio)) > 0

def test_water_pour_stream():
    audio = LiquidBubblesSuite.water_pour_stream(duration=2.0)
    assert isinstance(audio, np.ndarray)
    assert audio.dtype == np.float32
    assert len(audio) == int(2.0 * 48000)
    assert np.max(np.abs(audio)) > 0

def test_water_bubble_pop():
    audio = LiquidBubblesSuite.water_bubble_pop()
    assert isinstance(audio, np.ndarray)
    assert audio.dtype == np.float32
    assert len(audio) == int(0.09 * 48000)
    assert np.max(np.abs(audio)) > 0

def test_liquid_bubbles_suite_zero_duration():
    # Verify handles 0 duration properly across all generators
    assert len(LiquidBubblesSuite.liquid_drop_splash(duration=0)) == 0
    assert len(LiquidBubblesSuite.viscous_pop_bubble(duration=0)) == 0
    assert len(LiquidBubblesSuite.submerged_bubble_cluster(duration=0)) == 0
    assert len(LiquidBubblesSuite.water_pour_stream(duration=0)) == 0
    assert len(LiquidBubblesSuite.water_bubble_pop(duration=0)) == 0

