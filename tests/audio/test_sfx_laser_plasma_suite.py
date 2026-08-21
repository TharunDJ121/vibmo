import numpy as np
import pytest
from vibmo.audio.generators.sfx_laser_plasma_suite import LaserPlasmaSuite

def check_valid_audio(audio, duration):
    # Check type
    assert audio.dtype == np.float32, f"Expected float32, got {audio.dtype}"

    # Check length
    expected_len = int(LaserPlasmaSuite.SAMPLE_RATE * duration)
    assert len(audio) == expected_len, f"Expected {expected_len} samples, got {len(audio)}"

    # Check not all zeros
    assert np.any(audio != 0.0), "Audio array is completely silent"

    # Check bounds (clipping might happen, but shouldn't exceed +/- ~1.5 depending on sum, ideally [-1, 1])
    assert np.max(audio) <= 2.0 and np.min(audio) >= -2.0, f"Audio bounds exceeded: [{np.min(audio)}, {np.max(audio)}]"

def test_arcade_laser_zap():
    duration = 0.18
    audio = LaserPlasmaSuite.arcade_laser_zap(duration=duration)
    check_valid_audio(audio, duration)

def test_plasma_pulse_blast():
    duration = 0.32
    audio = LaserPlasmaSuite.plasma_pulse_blast(duration=duration)
    check_valid_audio(audio, duration)

def test_energy_beam_charge():
    duration = 1.2
    audio = LaserPlasmaSuite.energy_beam_charge(duration=duration)
    check_valid_audio(audio, duration)

def test_shield_deflect_ping():
    duration = 0.25
    audio = LaserPlasmaSuite.shield_deflect_ping(duration=duration)
    check_valid_audio(audio, duration)

def test_frequency_modulation():
    # specifically check arcade_laser_zap to see if frequency modulates down
    # we can do this by checking zero crossings in first half vs second half
    duration = 0.18
    audio = LaserPlasmaSuite.arcade_laser_zap(duration=duration)

    midpoint = len(audio) // 2
    first_half = audio[:midpoint]
    second_half = audio[midpoint:]

    crossings_first = np.sum(np.diff(np.sign(first_half)) != 0)
    crossings_second = np.sum(np.diff(np.sign(second_half)) != 0)

    # since frequency decays, first half should have more zero crossings
    assert crossings_first > crossings_second, "Frequency does not appear to decrease in arcade_laser_zap"
