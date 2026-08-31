import numpy as np
import pytest
from vibmo.audio.generators.sfx_whoosh_designer_suite import WhooshDesignerSuite

def test_doppler_whip():
    duration = 0.35
    audio = WhooshDesignerSuite.doppler_whip(duration=duration, speed=2.5)

    assert audio.dtype == np.float32
    assert audio.shape == (2, int(WhooshDesignerSuite.SAMPLE_RATE * duration))
    assert np.isclose(np.max(np.abs(audio)), 1.0, atol=1e-5)

def test_sub_bass_flyby():
    duration = 0.75
    audio = WhooshDesignerSuite.sub_bass_flyby(duration=duration, sub_freq=55.0)

    assert audio.dtype == np.float32
    assert audio.shape == (2, int(WhooshDesignerSuite.SAMPLE_RATE * duration))
    assert np.isclose(np.max(np.abs(audio)), 1.0, atol=1e-5)

def test_airy_transition():
    duration = 0.50
    audio = WhooshDesignerSuite.airy_transition(duration=duration, breath_noise=0.8)

    assert audio.dtype == np.float32
    assert audio.shape == (2, int(WhooshDesignerSuite.SAMPLE_RATE * duration))
    assert np.isclose(np.max(np.abs(audio)), 1.0, atol=1e-5)

def test_quick_snap_whoosh():
    duration = 0.18
    audio = WhooshDesignerSuite.quick_snap_whoosh(duration=duration)

    assert audio.dtype == np.float32
    assert audio.shape == (2, int(WhooshDesignerSuite.SAMPLE_RATE * duration))
    assert np.isclose(np.max(np.abs(audio)), 1.0, atol=1e-5)

def test_cinematic_passby():
    duration = 1.2
    audio = WhooshDesignerSuite.cinematic_passby(duration=duration)

    assert audio.dtype == np.float32
    assert audio.shape == (2, int(WhooshDesignerSuite.SAMPLE_RATE * duration))
    assert np.isclose(np.max(np.abs(audio)), 1.0, atol=1e-5)
    assert np.max(np.abs(audio)) > 0.0

