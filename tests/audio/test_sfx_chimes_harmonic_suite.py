import pytest
import numpy as np
import scipy.signal
from vibmo.audio.generators.sfx_chimes_harmonic_suite import ChimesHarmonicSuite

def test_crystal_bell_chime_output():
    audio = ChimesHarmonicSuite.crystal_bell_chime(duration=1.2, fundamental=1046.50)
    assert isinstance(audio, np.ndarray)
    assert audio.dtype == np.float32
    assert len(audio) == int(48000 * 1.2)
    assert np.max(np.abs(audio)) <= 1.0

def test_crystal_bell_chime_overtones():
    audio = ChimesHarmonicSuite.crystal_bell_chime(duration=1.0, fundamental=1000.0)

    fft_vals = np.abs(np.fft.rfft(audio))
    freqs = np.fft.rfftfreq(len(audio), 1/48000)

    peaks, _ = scipy.signal.find_peaks(fft_vals, height=np.max(fft_vals)*0.01)
    peak_freqs = freqs[peaks]

    expected_overtones = [1000.0 * ratio for ratio in [1.0, 2.76, 5.4, 8.9]]

    for expected in expected_overtones:
        assert any(np.isclose(expected, peak_freqs, atol=10.0))

def test_crystal_bell_chime_envelope_decay():
    audio = ChimesHarmonicSuite.crystal_bell_chime(duration=1.2, fundamental=1046.50)

    # Calculate energy in first and second halves
    mid_idx = len(audio) // 2
    energy_first_half = np.sum(audio[:mid_idx] ** 2)
    energy_second_half = np.sum(audio[mid_idx:] ** 2)

    assert energy_first_half > energy_second_half * 2 # Envelope should decay significantly

def test_sparkle_magic_glimmer():
    audio = ChimesHarmonicSuite.sparkle_magic_glimmer(duration=0.8, density=16)
    assert isinstance(audio, np.ndarray)
    assert audio.dtype == np.float32
    assert len(audio) == int(48000 * 0.8)
    assert np.max(np.abs(audio)) <= 1.0

def test_dream_harp_glissando_output():
    audio = ChimesHarmonicSuite.dream_harp_glissando(duration=1.4, scale="pentatonic_major")
    assert isinstance(audio, np.ndarray)
    assert audio.dtype == np.float32
    assert len(audio) == int(48000 * 1.4)
    assert np.max(np.abs(audio)) <= 1.0

def test_celebration_fanfare_tone_output():
    audio = ChimesHarmonicSuite.celebration_fanfare_tone(duration=1.0)
    assert isinstance(audio, np.ndarray)
    assert audio.dtype == np.float32
    assert len(audio) == int(48000 * 1.0)
    assert np.max(np.abs(audio)) <= 1.0

def test_celestial_wind_chime():
    audio = ChimesHarmonicSuite.celestial_wind_chime()
    assert isinstance(audio, np.ndarray)
    assert audio.dtype == np.float32
    assert len(audio) == int(48000 * 1.2)
    assert np.max(np.abs(audio)) > 0
    assert np.max(np.abs(audio)) <= 1.0

