import numpy as np
import pytest
from vibmo.audio.generators.sfx_alarm_siren_suite import AlarmSirenSuite

def test_emergency_klaxon_sweep():
    # default duration 1.5
    audio = AlarmSirenSuite.emergency_klaxon_sweep()
    assert isinstance(audio, np.ndarray)
    assert audio.dtype == np.float32
    assert len(audio) == int(1.5 * AlarmSirenSuite.SAMPLE_RATE)

    # check modulation by measuring frequency roughly or just check it generates sound
    assert np.max(np.abs(audio)) > 0.0

def test_nuclear_countdown_beep():
    # default duration 0.25
    audio = AlarmSirenSuite.nuclear_countdown_beep()
    assert isinstance(audio, np.ndarray)
    assert audio.dtype == np.float32
    assert len(audio) == int(0.25 * AlarmSirenSuite.SAMPLE_RATE)

    assert np.max(np.abs(audio)) > 0.0

def test_security_chirp_alarm():
    # default duration 0.8, pulses 4
    audio = AlarmSirenSuite.security_chirp_alarm()
    assert isinstance(audio, np.ndarray)
    assert audio.dtype == np.float32
    assert len(audio) == int(0.8 * AlarmSirenSuite.SAMPLE_RATE)

    assert np.max(np.abs(audio)) > 0.0

def test_biohazard_pulse_siren():
    # default duration 2.0
    audio = AlarmSirenSuite.biohazard_pulse_siren()
    assert isinstance(audio, np.ndarray)
    assert audio.dtype == np.float32
    assert len(audio) == int(2.0 * AlarmSirenSuite.SAMPLE_RATE)

    assert np.max(np.abs(audio)) > 0.0
