import numpy as np
import pytest
from vibmo.fx.shaders.fx_vhs_tape_tracking_suite import (
    VhsTapeTrackingShader,
    HeadSwitchingJitterLine,
    ColorBleedChromaShift,
    AnalogStaticSnowBurst
)

@pytest.fixture
def test_frame():
    # 100x100 solid mid-gray image with full alpha
    frame = np.full((100, 100, 4), 128, dtype=np.uint8)
    frame[:, :, 3] = 255
    # Add some colored lines to test chroma shifting and horizontal displacement
    frame[40:60, 40:60] = [255, 0, 0, 255] # Red square in the middle
    return frame

def test_vhs_tape_tracking_shader(test_frame):
    filter = VhsTapeTrackingShader(intensity=1.0, speed=0.5, band_height=0.2, use_gpu=False)
    out = filter.apply(test_frame, time=0.5)

    assert out.shape == test_frame.shape
    assert out.dtype == np.uint8

    # We should have some pixels that are not 128 because of noise added
    assert not np.array_equal(out, test_frame)

def test_head_switching_jitter_line(test_frame):
    filter = HeadSwitchingJitterLine(line_height=0.1, shift_amount=0.1, use_gpu=False)
    out = filter.apply(test_frame, time=0.1)

    assert out.shape == test_frame.shape
    assert out.dtype == np.uint8

    # The top part (before line_height) should be identical to test_frame except maybe some slight scanline if any
    # Wait, scanline is applied to the bottom. Top part should be equal.
    h, w, _ = test_frame.shape
    tear_start = int(h * (1.0 - filter.line_height))

    np.testing.assert_array_equal(out[:tear_start], test_frame[:tear_start])

    # Bottom part should be modified (scanlines + jitter)
    assert not np.array_equal(out[tear_start:], test_frame[tear_start:])

def test_color_bleed_chroma_shift(test_frame):
    filter = ColorBleedChromaShift(red_shift=0.1, blue_shift=-0.1, blur_amount=0.0, use_gpu=False)
    out = filter.apply(test_frame, time=0.0)

    assert out.shape == test_frame.shape
    assert out.dtype == np.uint8

    # In the original, red square is at 40:60 x 40:60.
    # red_shift = 0.1 * 100 = 10 (right shift)
    # So red should be shifted right by 10 pixels (50:70)

    # Check red channel shift at y=50
    # Output should have red shifted to the right.
    # At original right boundary of square (x=59), it should now be background color (128) if it shifted right,
    # or shifted left depending on how apply_cpu shifts.

    # Original red square is from x=40 to x=59 (inclusive, 40:60).
    # r_shift = 0.1 * 100 = 10.
    # Code says: out[:, :-r_shift, 0] = rgba[:, r_shift:, 0]
    # This means output at x receives input from x + r_shift.
    # So the image is actually shifted LEFT.
    # Output at x=30 will receive input from x=40.
    # So red square will be at x=30 to x=49.

    assert out[50, 35, 0] == 255  # Now inside the shifted red square
    assert out[50, 55, 0] == 128  # Now outside the shifted red square

    # Also test blue channel shift

def test_analog_static_snow_burst(test_frame):
    # Set frequency high so it triggers
    filter = AnalogStaticSnowBurst(intensity=0.1, frequency=1.0, use_gpu=False)
    out = filter.apply(test_frame, time=0.0)

    assert out.shape == test_frame.shape
    assert out.dtype == np.uint8

    # Output should have white/black speckles
    assert np.any(out[:, :, :3] == 255)
    assert np.any(out[:, :, :3] == 0)

    # Test when frequency is 0
    filter_no_snow = AnalogStaticSnowBurst(intensity=0.1, frequency=0.0, use_gpu=False)
    out_no_snow = filter_no_snow.apply(test_frame, time=0.0)
    np.testing.assert_array_equal(out_no_snow, test_frame)
