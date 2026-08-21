import unittest
import numpy as np
from vibmo.audio.generators.sfx_glitch_stutter_suite import GlitchStutterSuite

class TestGlitchStutterSuite(unittest.TestCase):
    def setUp(self):
        self.sr = GlitchStutterSuite.SAMPLE_RATE

    def test_tape_motor_stop(self):
        # Generate 1 second sine wave
        t = np.linspace(0, 1.0, self.sr, endpoint=False)
        audio_in = np.sin(2 * np.pi * 440 * t).astype(np.float32)

        out = GlitchStutterSuite.tape_motor_stop(audio_in, slowdown_curve=2.0)

        self.assertEqual(len(out), len(audio_in))
        self.assertEqual(out.dtype, np.float32)

        # Output should be different from input due to time stretching / pitch drop
        self.assertFalse(np.array_equal(out, audio_in))

        # Test empty input
        empty_out = GlitchStutterSuite.tape_motor_stop(np.array([], dtype=np.float32))
        self.assertEqual(len(empty_out), 0)

    def test_bitcrush_buffer_freeze(self):
        duration = 0.4
        bit_depth = 4
        srr = 8
        out = GlitchStutterSuite.bitcrush_buffer_freeze(duration=duration, bit_depth=bit_depth, sample_rate_reduction=srr)

        expected_len = int(duration * self.sr)
        self.assertEqual(len(out), expected_len)
        self.assertEqual(out.dtype, np.float32)

        # Test sample rate reduction: blocks of `srr` should have the same value
        if len(out) >= srr:
            self.assertEqual(out[0], out[1])
            self.assertEqual(out[0], out[srr - 1])

        # Test bit depth quantization: unique values should not exceed 2^bit_depth
        unique_vals = np.unique(out)
        self.assertLessEqual(len(unique_vals), 2 ** bit_depth)

    def test_digital_glitch_stutter(self):
        duration = 0.5
        slice_count = 12
        out = GlitchStutterSuite.digital_glitch_stutter(duration=duration, slice_count=slice_count, randomize=False)

        expected_len = int(duration * self.sr)
        self.assertEqual(len(out), expected_len)
        self.assertEqual(out.dtype, np.float32)

        # In non-random mode, some slices are repeated.
        # This just checks it runs and produces valid audio.
        self.assertTrue(np.any(out != 0.0))

    def test_data_corruption_burst(self):
        duration = 0.3
        out = GlitchStutterSuite.data_corruption_burst(duration=duration)

        expected_len = int(duration * self.sr)
        self.assertEqual(len(out), expected_len)
        self.assertEqual(out.dtype, np.float32)

        # Audio should contain a significant amount of extreme values due to hard clipping and digital generation
        extremes = np.sum(np.abs(out) >= 0.99)
        self.assertGreater(extremes, expected_len * 0.1) # At least 10% extreme values

if __name__ == '__main__':
    unittest.main()
