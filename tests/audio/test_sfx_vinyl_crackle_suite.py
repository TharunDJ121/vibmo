import numpy as np
import pytest
from vibmo.audio.generators.sfx_vinyl_crackle_suite import VinylCrackleSuite

def test_vinyl_surface_hiss():
    duration = 1.0
    audio = VinylCrackleSuite.vinyl_surface_hiss(duration=duration, noise_floor=0.1)

    assert isinstance(audio, np.ndarray)
    assert audio.dtype == np.float32
    assert len(audio) == int(duration * 48000)
    assert np.max(np.abs(audio)) > 0
    # The amplitude should generally be bounded by the noise floor,
    # but slightly higher values might exist due to rumble. We check it's within reason.
    assert np.max(np.abs(audio)) < 0.5

def test_dust_pops():
    duration = 2.0
    audio = VinylCrackleSuite.dust_pops(duration=duration, pop_density=50.0)

    assert isinstance(audio, np.ndarray)
    assert audio.dtype == np.float32
    assert len(audio) == int(duration * 48000)
    # The minimum is likely 0, max is > 0 if pops occurred, check range
    assert np.max(np.abs(audio)) <= 1.0

    # Test zero pops
    audio_empty = VinylCrackleSuite.dust_pops(duration=1.0, pop_density=0.0)
    assert np.max(np.abs(audio_empty)) == 0.0

def test_needle_drop_thump():
    duration = 0.5
    audio = VinylCrackleSuite.needle_drop_thump(duration=duration)

    assert isinstance(audio, np.ndarray)
    assert audio.dtype == np.float32
    assert len(audio) == int(duration * 48000)
    assert np.max(np.abs(audio)) > 0

def test_analog_tape_hiss():
    duration = 1.0
    audio = VinylCrackleSuite.analog_tape_hiss(duration=duration, warm_color=True)

    assert isinstance(audio, np.ndarray)
    assert audio.dtype == np.float32
    assert len(audio) == int(duration * 48000)
    assert np.max(np.abs(audio)) > 0
    assert np.max(np.abs(audio)) < 0.5

    audio_cold = VinylCrackleSuite.analog_tape_hiss(duration=1.0, warm_color=False)
    assert isinstance(audio_cold, np.ndarray)
    assert audio_cold.dtype == np.float32

def test_vintage_turntable_hiss():
    duration = 5.0
    audio = VinylCrackleSuite.vintage_turntable_hiss(duration=duration)
    assert isinstance(audio, np.ndarray)
    assert audio.dtype == np.float32
    assert len(audio) == int(duration * 48000)
    assert np.max(np.abs(audio)) > 0

