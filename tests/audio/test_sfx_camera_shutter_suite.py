import pytest
import numpy as np
from vibmo.audio.generators.sfx_camera_shutter_suite import CameraShutterSuite

@pytest.mark.parametrize("method, expected_duration", [
    ("dslr_mirror_slap", 0.16),
    ("vintage_motor_advance", 0.65),
    ("smartphone_snap_flash", 0.12),
    ("polaroid_eject", 0.85),
    ("dslr_rapid_burst", 0.60)
])
def test_camera_shutter_suite_lengths_and_types(method, expected_duration):
    """Test that all generator outputs match expected duration and dtype."""
    generator = getattr(CameraShutterSuite, method)
    audio = generator(duration=expected_duration)

    expected_length = int(48000 * expected_duration)

    assert isinstance(audio, np.ndarray), f"{method} did not return a NumPy array."
    assert audio.dtype == np.float32, f"{method} did not return float32."
    assert len(audio) == expected_length, f"{method} returned length {len(audio)}, expected {expected_length}."

@pytest.mark.parametrize("method", [
    "dslr_mirror_slap",
    "vintage_motor_advance",
    "smartphone_snap_flash",
    "polaroid_eject",
    "dslr_rapid_burst"
])
def test_camera_shutter_suite_bounds(method):
    """Test that all outputs are bounded between -1.0 and 1.0."""
    generator = getattr(CameraShutterSuite, method)
    audio = generator()

    assert np.all(audio >= -1.0), f"{method} output has values < -1.0"
    assert np.all(audio <= 1.0), f"{method} output has values > 1.0"

    # Also verify that it's not perfectly silent
    assert np.max(np.abs(audio)) > 0.01, f"{method} output is too quiet or completely silent"

def test_camera_shutter_suite_envelope():
    """Test that the envelope functions start and end at zero or near zero to prevent clicks."""
    # Check start and end of polaroid_eject which uses a prominent envelope
    audio = CameraShutterSuite.polaroid_eject(duration=0.5)

    # The start should be quiet due to attack
    assert np.abs(audio[0]) < 1e-4, "Envelope did not start at zero."

    # The end should be quiet due to release
    assert np.abs(audio[-1]) < 1e-4, "Envelope did not end at zero."

def test_custom_durations():
    """Test that custom durations scale properly."""
    audio1 = CameraShutterSuite.dslr_mirror_slap(duration=0.5)
    assert len(audio1) == int(48000 * 0.5)

    audio2 = CameraShutterSuite.smartphone_snap_flash(duration=0.25)
    assert len(audio2) == int(48000 * 0.25)
