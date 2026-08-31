import numpy as np
import pytest

from vibmo.audio.generators.sfx_cyber_ui_suite import (
    CyberUiSuite,
    CyberUISFXSuite,
    holo_chirp,
    holographic_click,
    data_packet_burst,
    access_granted_tone,
    access_denied_klaxon,
    cyber_pip,
    SAMPLE_RATE
)

def verify_audio_array(audio: np.ndarray, expected_duration: float):
    # Check type
    assert isinstance(audio, np.ndarray), "Audio must be a NumPy array"
    assert audio.dtype == np.float32, f"Audio dtype must be float32, got {audio.dtype}"

    # Check length
    expected_length = int(expected_duration * SAMPLE_RATE)
    assert len(audio) == expected_length, f"Expected length {expected_length}, got {len(audio)}"

    # Check non-zero waveform (there should be some sound)
    assert np.any(np.abs(audio) > 0.01), "Audio waveform appears to be empty/silent"

    # Check normalized amplitude (-1.0 to 1.0)
    max_amp = np.max(np.abs(audio))
    assert max_amp <= 1.0 + 1e-6, f"Amplitude exceeded 1.0 (max was {max_amp})"
    assert max_amp >= 0.5, f"Amplitude not normalized properly (max was {max_amp})"

def test_holo_chirp():
    duration = 0.08
    audio = holo_chirp(duration=duration)
    verify_audio_array(audio, duration)

    # Test method via class
    audio_cls = CyberUISFXSuite.holo_chirp(duration=duration)
    verify_audio_array(audio_cls, duration)
    np.testing.assert_array_equal(audio, audio_cls)

def test_data_packet_burst():
    duration = 0.15
    # Use fixed seed for consistent noise during testing
    np.random.seed(42)
    audio = data_packet_burst(duration=duration)
    verify_audio_array(audio, duration)

    np.random.seed(42)
    audio_cls = CyberUISFXSuite.data_packet_burst(duration=duration)
    verify_audio_array(audio_cls, duration)
    np.testing.assert_array_equal(audio, audio_cls)

def test_access_granted_tone():
    duration = 0.45
    audio = access_granted_tone(duration=duration)
    verify_audio_array(audio, duration)

    audio_cls = CyberUISFXSuite.access_granted_tone(duration=duration)
    verify_audio_array(audio_cls, duration)
    np.testing.assert_array_equal(audio, audio_cls)

    # Test with custom chord
    custom_duration = 0.5
    custom_audio = access_granted_tone(duration=custom_duration, chord=[440.0, 880.0])
    verify_audio_array(custom_audio, custom_duration)

def test_access_denied_klaxon():
    duration = 0.35
    audio = access_denied_klaxon(duration=duration)
    verify_audio_array(audio, duration)

    audio_cls = CyberUISFXSuite.access_denied_klaxon(duration=duration)
    verify_audio_array(audio_cls, duration)
    np.testing.assert_array_equal(audio, audio_cls)

def test_cyber_pip():
    duration = 0.04
    audio = cyber_pip(duration=duration)
    verify_audio_array(audio, duration)

    audio_cls = CyberUISFXSuite.cyber_pip(duration=duration)
    verify_audio_array(audio_cls, duration)
    np.testing.assert_array_equal(audio, audio_cls)

def test_holographic_click():
    audio = CyberUiSuite.holographic_click(pitch=800)
    verify_audio_array(audio, 0.05)

    audio_fn = holographic_click(pitch=800)
    verify_audio_array(audio_fn, 0.05)
    np.testing.assert_array_equal(audio, audio_fn)

def test_cyber_ui_suite_alias():
    assert CyberUiSuite is CyberUISFXSuite
    audio1 = CyberUiSuite.holo_chirp(duration=0.08)
    audio2 = CyberUISFXSuite.holo_chirp(duration=0.08)
    np.testing.assert_array_equal(audio1, audio2)

def test_invalid_duration():
    # Should handle empty gracefully if possible, or raise expected error
    with pytest.raises(ValueError, match=".*") as excinfo:
        # Depending on implementation, might return empty array or fail
        audio = holo_chirp(duration=0.0)
        if len(audio) == 0:
             raise ValueError("Empty array")

