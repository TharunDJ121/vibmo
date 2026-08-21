import numpy as np
import pytest
from scipy import signal
from vibmo.audio.generators.sfx_riser_tension_suite import RiserTensionSuite

def get_dominant_frequencies(audio: np.ndarray, sample_rate: int = 48000, nperseg: int = 4096):
    f, t, Zxx = signal.stft(audio, fs=sample_rate, nperseg=nperseg)
    # Find the peak frequency for each time slice
    peak_indices = np.argmax(np.abs(Zxx), axis=0)
    peak_freqs = f[peak_indices]
    return t, peak_freqs

def test_shepard_tone_riser():
    duration = 2.5
    audio = RiserTensionSuite.shepard_tone_riser(duration=duration, base_freq=65.4, octaves=5)

    assert isinstance(audio, np.ndarray)
    assert audio.dtype == np.float32
    assert len(audio) == int(48000 * duration)
    assert np.max(np.abs(audio)) <= 1.0

    # Shepard tone rises overall, but since it has multiple octaves, the simple peak frequency might jump.
    # However, the frequency is bounded. The lowest start is 65.4, highest end is 65.4 * 2^6 = 4185.6
    t, peak_freqs = get_dominant_frequencies(audio)
    # Exclude silence or near silence at edges due to windowing/fade
    valid_freqs = peak_freqs[1:-1]
    assert np.all(valid_freqs > 40.0) # allowing some STFT smearing
    assert np.all(valid_freqs < 5000.0)

def test_cyber_pitch_riser():
    duration = 1.8
    start_f = 100.0
    end_f = 3500.0
    audio = RiserTensionSuite.cyber_pitch_riser(duration=duration, start_f=start_f, end_f=end_f, lfo_rate=8.0)

    assert isinstance(audio, np.ndarray)
    assert audio.dtype == np.float32
    assert len(audio) == int(48000 * duration)
    assert np.max(np.abs(audio)) <= 1.0

    t, peak_freqs = get_dominant_frequencies(audio, nperseg=2048)
    valid_freqs = peak_freqs[1:-1]

    # Pitch evolution: The average pitch in the first quarter should be lower than the last quarter
    q1_mean = np.mean(valid_freqs[:len(valid_freqs)//4])
    q4_mean = np.mean(valid_freqs[-len(valid_freqs)//4:])
    assert q1_mean < q4_mean

    # Bounds check
    assert np.all(valid_freqs > start_f * 0.5)
    assert np.all(valid_freqs < end_f * 2.0)

def test_white_noise_sweep():
    duration = 1.5
    audio = RiserTensionSuite.white_noise_sweep(duration=duration, resonance=4.0)

    assert isinstance(audio, np.ndarray)
    assert audio.dtype == np.float32
    assert len(audio) == int(48000 * duration)
    assert np.max(np.abs(audio)) <= 1.0

    t, peak_freqs = get_dominant_frequencies(audio, nperseg=2048)
    valid_freqs = peak_freqs[2:-2] # skip fade-ins

    # Noise sweep rises from 200 to 12000
    q1_mean = np.mean(valid_freqs[:len(valid_freqs)//4])
    q4_mean = np.mean(valid_freqs[-len(valid_freqs)//4:])
    assert q1_mean < q4_mean

    # Ensure it's not all low frequency or all high frequency
    assert np.min(valid_freqs) < 1000
    assert np.max(valid_freqs) > 5000

def test_tension_alarm_build():
    duration = 2.0
    audio = RiserTensionSuite.tension_alarm_build(duration=duration, pulses=8)

    assert isinstance(audio, np.ndarray)
    assert audio.dtype == np.float32
    assert len(audio) == int(48000 * duration)
    assert np.max(np.abs(audio)) <= 1.0

    t, peak_freqs = get_dominant_frequencies(audio, nperseg=2048)
    valid_freqs = peak_freqs[1:-1]

    # Pitch evolution: The overall pitch rises from 400 to 1200
    q1_mean = np.mean(valid_freqs[:len(valid_freqs)//4])
    q4_mean = np.mean(valid_freqs[-len(valid_freqs)//4:])
    assert q1_mean < q4_mean

    # The high pass filter is 200Hz, we shouldn't see strong components much below that
    assert np.all(valid_freqs > 100.0)
