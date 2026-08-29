import math
import unittest
from unittest.mock import MagicMock
import cairo

from vibmo.typography.kinetic.typo_liquid_wave_suite import (
    LiquidWaveText,
    ChromaticBaselineDrift,
    SubmergedTextRefraction,
    RippleWordReveal
)
from vibmo.core.color import colors


class TestTypoLiquidWaveSuite(unittest.TestCase):
    def setUp(self):
        self.ctx = MagicMock()

        # We must return a proper mock object for text_extents
        class ExtentsMock:
            width = 10.0
            height = 10.0
            x_advance = 12.0
            y_advance = 0.0
            x_bearing = 0.0
            y_bearing = 0.0

        self.ctx.text_extents.return_value = ExtentsMock()

    def test_liquid_wave_text(self):
        node = LiquidWaveText(text="WAVE", font_size=40.0, amplitude=15.0, frequency=0.5, speed=2.0)

        node.draw(self.ctx, time=1.0)

        self.assertEqual(self.ctx.show_text.call_count, 4)

        # Verify wave offset applied to Y axis
        # For 'W', i=0, time=1.0. Math.sin(0 * 0.5 + 1.0 * 2.0) = math.sin(2.0)
        expected_y_offset = math.sin(2.0) * 15.0
        expected_y = 40.0 * 0.88 + expected_y_offset

        # Find the first move_to call
        first_move_to_args = self.ctx.move_to.call_args_list[0][0]
        self.assertAlmostEqual(first_move_to_args[0], 0.0) # current_x starts at 0
        self.assertAlmostEqual(first_move_to_args[1], expected_y)

    def test_chromatic_baseline_drift(self):
        node = ChromaticBaselineDrift(text="RGB", font_size=30.0, amplitude=10.0, frequency=1.0, speed=1.0, rgb_split_max=8.0)

        node.draw(self.ctx, time=0.0)

        # 3 characters * 3 channels = 9 show_text calls
        self.assertEqual(self.ctx.show_text.call_count, 9)

        # Check drift for first character, i=0, time=0 -> phase = 0, sin(0) = 0
        # Wait, for i=0, time=0, math.sin(0) = 0, so no drift.
        # Let's test with time=math.pi/2 so sin(time) = 1
        self.ctx.reset_mock()
        node.draw(self.ctx, time=math.pi/2)

        # phase = pi/2. Drift = math.sin(pi/2) * 8.0 = 8.0
        # First char 'R' Red channel
        first_move_to = self.ctx.move_to.call_args_list[0][0]
        self.assertAlmostEqual(first_move_to[0], -8.0) # current_x (0) - drift (8.0)

    def test_submerged_text_refraction(self):
        node = SubmergedTextRefraction(text="DEEP", font_size=20.0)

        node.draw(self.ctx, time=1.5)

        # Base text + shimmer layer (if alpha > 0.01)
        # Should be between 4 and 8 show_text calls
        self.assertGreaterEqual(self.ctx.show_text.call_count, 4)

        # Check source color is set correctly
        sources = [call[0] for call in self.ctx.set_source_rgba.call_args_list]
        self.assertTrue(any(c[3] > 0.0 for c in sources)) # Some positive alpha

    def test_ripple_word_reveal(self):
        node = RippleWordReveal(text="Splash Down", font_size=50.0)

        # At time=0, progress=0, alpha=0, so no show_text
        node.draw(self.ctx, time=0.0)
        self.assertEqual(self.ctx.show_text.call_count, 0)

        # Advance time to get progress > 0
        node.progress.set(1.0) # fully revealed
        self.ctx.reset_mock()
        node.draw(self.ctx, time=1.0)

        self.assertEqual(self.ctx.show_text.call_count, 2)

        # Partial reveal
        node.progress.set(0.25)
        self.ctx.reset_mock()
        node.draw(self.ctx, time=0.5)

        # Alpha should be calculated correctly
        self.assertTrue(self.ctx.set_source_rgba.called)

if __name__ == '__main__':
    unittest.main()
