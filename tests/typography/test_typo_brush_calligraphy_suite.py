import unittest
from unittest.mock import MagicMock
import cairo
import math

from vibmo.core.color import colors
from vibmo.typography.kinetic.typo_brush_calligraphy_suite import (
    BrushCalligraphyPathReveal,
    BristleTextureStroke,
    InkSplatterBleed,
    WaterColorWashBackdrop
)

class TestTypoBrushCalligraphySuite(unittest.TestCase):
    def setUp(self):
        self.surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, 100, 100)
        self.ctx = cairo.Context(self.surface)
        
        # Test path: simple straight line as a single cubic bezier segment
        self.test_path = [
            ((0.0, 0.0), (10.0, 0.0), (20.0, 0.0), (30.0, 0.0))
        ]

    def test_brush_calligraphy_path_reveal(self):
        node = BrushCalligraphyPathReveal(path=self.test_path, color=colors.RED, stroke_width=2.0)
        
        # Progress 0: nothing drawn
        mock_ctx = MagicMock()
        node.draw(mock_ctx, 0.0)
        mock_ctx.stroke.assert_not_called()
        
        # Progress 0.5: De Casteljau splitting expected (curve_to should be called)
        node.progress.set(0.5)
        mock_ctx = MagicMock()
        node.draw(mock_ctx, 0.5)
        mock_ctx.curve_to.assert_called_once()
        mock_ctx.stroke.assert_called_once()
        
        # Progress 1.0: Full curve drawn
        node.progress.set(1.0)
        mock_ctx = MagicMock()
        node.draw(mock_ctx, 1.0)
        mock_ctx.curve_to.assert_called_once_with(10.0, 0.0, 20.0, 0.0, 30.0, 0.0)
        mock_ctx.stroke.assert_called_once()

    def test_bristle_texture_stroke(self):
        p0 = (0.0, 0.0)
        p1 = (50.0, 50.0)
        node = BristleTextureStroke(p0, p1, num_bristles=3, max_width=10.0)
        
        mock_ctx = MagicMock()
        node.draw(mock_ctx, 0.0)
        
        # Should set line cap and draw strokes for bristles
        mock_ctx.set_line_cap.assert_called_with(cairo.LINE_CAP_ROUND)
        self.assertEqual(mock_ctx.stroke.call_count, 3)
        self.assertEqual(mock_ctx.move_to.call_count, 3)
        self.assertEqual(mock_ctx.line_to.call_count, 3)

    def test_bristle_zero_length(self):
        p0 = (0.0, 0.0)
        p1 = (0.0, 0.0)
        node = BristleTextureStroke(p0, p1, num_bristles=3, max_width=10.0)
        
        mock_ctx = MagicMock()
        node.draw(mock_ctx, 0.0)
        # Shouldn't crash and shouldn't stroke anything
        mock_ctx.stroke.assert_not_called()

    def test_ink_splatter_bleed(self):
        center = (50.0, 50.0)
        node = InkSplatterBleed(center, num_splatters=4, max_radius=10.0)
        
        # Progress 0: nothing drawn
        mock_ctx = MagicMock()
        node.draw(mock_ctx, 0.0)
        mock_ctx.fill.assert_not_called()
        
        # Progress 0.5: some splatters drawn
        node.bleed_progress.set(0.5)
        mock_ctx = MagicMock()
        node.draw(mock_ctx, 0.5)
        
        self.assertEqual(mock_ctx.arc.call_count, 4)
        self.assertEqual(mock_ctx.fill.call_count, 4)
        
        # Progress > 1: clamped internally
        node.bleed_progress.set(1.5)
        mock_ctx = MagicMock()
        node.draw(mock_ctx, 1.5)
        
        self.assertEqual(mock_ctx.arc.call_count, 4)
        self.assertEqual(mock_ctx.fill.call_count, 4)

    def test_watercolor_wash_backdrop(self):
        rect = (10, 10, 80, 80)
        node = WaterColorWashBackdrop(rect, color=colors.BLUE, max_alpha=0.5)
        
        # Zero intensity: nothing drawn
        node.intensity.set(0.0)
        mock_ctx = MagicMock()
        node.draw(mock_ctx, 0.0)
        mock_ctx.fill.assert_not_called()
        
        # Non-zero intensity: draws 5 radial gradient blobs
        node.intensity.set(1.0)
        mock_ctx = MagicMock()
        
        # Replace the real cairo module calls inside draw?
        # Actually it creates cairo.RadialGradient in the method. 
        # We can just test that it runs against a real cairo context.
        try:
            node.draw(self.ctx, 1.0)
        except Exception as e:
            self.fail(f"draw() raised Exception: {e}")

if __name__ == '__main__':
    unittest.main()
