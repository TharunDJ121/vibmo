import numpy as np
import pytest

from vibmo.audio.generators.sfx_retro_8bit_suite import Retro8BitSuite

def test_retro_8bit_suite_pulse_wave():
    freqs = np.full(4800, 480.0)  # 100 periods in 0.1s
    wave_50 = Retro8BitSuite._pulse_wave(freqs, duty=0.5)
    wave_25 = Retro8BitSuite._pulse_wave(freqs, duty=0.25)

    assert wave_50.dtype == np.float32
    assert wave_25.dtype == np.float32

    # Check bounds
    assert np.all((wave_50 == 1.0) | (wave_50 == -1.0))
    assert np.all((wave_25 == 1.0) | (wave_25 == -1.0))

    # Check means (duty cycle validation)
    # 50% duty mean should be ~0
    assert np.abs(np.mean(wave_50)) < 0.05
    # 25% duty mean should be ~ -0.5 (25% 1.0, 75% -1.0 -> 0.25 - 0.75 = -0.5)
    assert np.abs(np.mean(wave_25) - (-0.5)) < 0.05

def test_retro_8bit_suite_jump_boing():
    duration = 0.20
    out = Retro8BitSuite.jump_boing(duration=duration)

    assert out.dtype == np.float32
    assert len(out) == int(48000 * duration)
    assert np.max(np.abs(out)) <= 1.0

def test_retro_8bit_suite_coin_pickup():
    duration = 0.30
    out = Retro8BitSuite.coin_pickup(duration=duration)

    assert out.dtype == np.float32
    assert len(out) == int(48000 * duration)
    assert np.max(np.abs(out)) <= 1.0

    # End should be zero due to fade
    assert out[-1] == 0.0

def test_retro_8bit_suite_power_down_slide():
    duration = 0.45
    out = Retro8BitSuite.power_down_slide(duration=duration)

    assert out.dtype == np.float32
    assert len(out) == int(48000 * duration)
    assert np.max(np.abs(out)) <= 1.0

    # End should be close to zero due to envelope
    assert np.abs(out[-1]) < 0.01

def test_retro_8bit_suite_level_up_fanfare():
    duration = 0.8
    out = Retro8BitSuite.level_up_fanfare(duration=duration)

    assert out.dtype == np.float32
    assert len(out) == int(48000 * duration)
    assert np.max(np.abs(out)) <= 1.0

def test_retro_8bit_suite_noise():
    noise0 = Retro8BitSuite._noise(0.1, mode=0, shift_interval=4)
    noise1 = Retro8BitSuite._noise(0.1, mode=1, shift_interval=16)

    assert noise0.dtype == np.float32
    assert noise1.dtype == np.float32
    assert len(noise0) == 4800
    assert len(noise1) == 4800

    assert np.all((noise0 == 1.0) | (noise0 == -1.0))
    assert np.all((noise1 == 1.0) | (noise1 == -1.0))

def test_retro_8bit_suite_triangle_wave():
    freqs = np.full(4800, 480.0)
    tri = Retro8BitSuite._triangle_wave(freqs)

    assert tri.dtype == np.float32
    assert len(tri) == 4800
    assert np.max(np.abs(tri)) <= 1.0

    # Check that it has intermediate values (not just 1 and -1)
    unique_vals = np.unique(tri)
    assert len(unique_vals) > 2
    # Ensure values are steps
    assert len(unique_vals) <= 16

def test_retro_8bit_suite_arcade_coin_jump():
    from vibmo.audio.generators.sfx_retro_8bit_suite import Retro8bitSuite
    assert Retro8bitSuite is Retro8BitSuite
    duration = 0.30
    out = Retro8bitSuite.arcade_coin_jump(duration=duration)
    assert out.dtype == np.float32
    assert len(out) == int(48000 * duration)
    assert np.max(np.abs(out)) <= 1.0

