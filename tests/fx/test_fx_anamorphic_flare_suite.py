import numpy as np
from vibmo.fx.shaders.fx_anamorphic_flare_suite import (
    ThresholdGlowPass,
    AnamorphicStreakFlareShader,
    LensGhostArtifacts,
    StarburstSpikeCross
)

def test_threshold_glow_pass():
    rgba = np.zeros((10, 10, 4), dtype=np.uint8)
    rgba[:, :, 3] = 255
    # Dark area
    rgba[0:5, :, :3] = 50
    # Bright area
    rgba[5:10, :, :3] = 250

    filter = ThresholdGlowPass(threshold=0.5, intensity=1.0)
    out = filter.apply(rgba)

    # Dark area should be 0
    assert np.all(out[0:5, :, :3] == 0)
    # Bright area should be non-zero
    assert np.any(out[5:10, :, :3] > 0)
    assert out.shape == (10, 10, 4)

def test_anamorphic_streak_flare():
    rgba = np.zeros((20, 20, 4), dtype=np.uint8)
    rgba[:, :, 3] = 255
    rgba[10, 10, :3] = 255  # bright dot

    filter = AnamorphicStreakFlareShader(threshold=0.5, streak_length=5.0, color=(0.0, 1.0, 1.0))
    out = filter.apply(rgba)

    # Should be spread horizontally but not vertically
    assert out[10, 5, 1] > 0  # left of center, G channel
    assert out[10, 15, 2] > 0 # right of center, B channel

    # Should not be spread vertically
    assert np.all(out[5, 10, :3] == 0)
    assert np.all(out[15, 10, :3] == 0)

def test_lens_ghost_artifacts():
    rgba = np.zeros((20, 20, 4), dtype=np.uint8)
    rgba[:, :, 3] = 255
    # Bright spot at bottom right
    rgba[15, 15, :3] = 255

    filter = LensGhostArtifacts(threshold=0.5, ghosts=1, dispersion=0.0)
    out = filter.apply(rgba)

    # The original spot should still be there (15, 15)
    assert np.all(out[15, 15, :3] > 0)

    # For ghosts=1, scale should be -1.0
    # center is 10, 10
    # mapped_x = 10 + (x - 10) * -1
    # if x=15, mapped_x = 10 + 5 * -1 = 5
    # so ghost should appear at (5, 5)

    # Check if there is some value near (5, 5)
    assert np.any(out[4:7, 4:7, :3] > 0)

def test_starburst_spike_cross():
    rgba = np.zeros((20, 20, 4), dtype=np.uint8)
    rgba[:, :, 3] = 255
    rgba[10, 10, :3] = 255

    filter = StarburstSpikeCross(threshold=0.5, size=3.0)
    out = filter.apply(rgba)

    # Should have spread horizontally and vertically
    assert np.any(out[10, 5, :3] > 0)
    assert np.any(out[10, 15, :3] > 0)
    assert np.any(out[5, 10, :3] > 0)
    assert np.any(out[15, 10, :3] > 0)

    # But not diagonally
    assert np.all(out[5, 5, :3] == 0)
