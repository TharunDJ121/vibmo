import unittest
from unittest.mock import MagicMock
import math
import cairo

from vibmo.typography.kinetic.typo_magnetic_gravity_suite import (
    MagneticGravityLetters,
    ExplosiveScatterForce,
    MagnetPullReassembly,
    FloorContactShadow
)
from vibmo.core.color import Color

class TestMagneticGravityLetters(unittest.TestCase):
    def test_gravity_velocity_bouncing(self):
        node = MagneticGravityLetters("Test", gravity=2000.0, floor_y=500.0, restitution=0.5, stagger_time=0.0)
        
        # Test free fall logic
        # At t=0, y=0
        self.assertEqual(node.get_letter_y(0.0), 0.0)
        
        # Free fall time = sqrt(2 * 500 / 2000) = sqrt(0.5) ≈ 0.707s
        t_drop = math.sqrt(2 * 500.0 / 2000.0)
        
        # Mid air drop (t=0.5s) -> y = 0.5 * 2000 * 0.5^2 = 250
        self.assertAlmostEqual(node.get_letter_y(0.5), 250.0)
        
        # Hit the floor exactly
        self.assertAlmostEqual(node.get_letter_y(t_drop), 500.0)
        
        # Let's test a bounce:
        # After hitting the floor at t_drop, it bounces back up
        # Initial bounce velocity = sqrt(2 * 2000 * 500) * 0.5 = sqrt(2000000) * 0.5 ≈ 1414.2 * 0.5 = 707.1
        # It takes t = 2 * v / g = 2 * 707.1 / 2000 = 0.707s for full bounce
        # At halfway through bounce (t_curr = 0.3535s)
        t_bounce_peak = t_drop + (707.1 / 2000.0)
        
        y_peak = node.get_letter_y(t_bounce_peak)
        # Should be peak of bounce
        # Peak height = floor_y - (v * t - 0.5 * g * t^2)
        # = 500 - (707.1 * 0.3535 - 1000 * 0.3535^2) ≈ 500 - (250 - 125) = 375
        self.assertAlmostEqual(y_peak, 375.0, places=1)
        
        # After bouncing forever, should settle at floor_y
        self.assertAlmostEqual(node.get_letter_y(10.0), 500.0)
        
    def test_draw_with_mock_context(self):
        node = MagneticGravityLetters("BOOM", font_size=50)
        ctx = MagicMock()
        
        # We need mock text extents to avoid errors
        class Extent:
            x_advance = 30.0
        ctx.text_extents.return_value = Extent()
        
        node.progress.set(0.5)
        node.draw(ctx, time=0.0)
        
        self.assertTrue(ctx.save.called)
        self.assertTrue(ctx.restore.called)
        self.assertEqual(ctx.show_text.call_count, 4)

class TestExplosiveScatterForce(unittest.TestCase):
    def test_explosive_force_logic(self):
        node = ExplosiveScatterForce("SCATTER", blast_force=1000.0, explosion_center=(0, 0))
        
        ctx = MagicMock()
        class Extent:
            x_advance = 40.0
        ctx.text_extents.return_value = Extent()
        
        # At progress 0, just draws straight text
        node.progress.set(0.0)
        node.draw(ctx, 0.0)
        self.assertEqual(ctx.show_text.call_count, len("SCATTER"))
        
        ctx.reset_mock()
        ctx.text_extents.return_value = Extent()
        
        # At progress 1.0, scatters
        node.progress.set(1.0)
        node.draw(ctx, 0.0)
        
        self.assertTrue(ctx.translate.called)
        self.assertTrue(ctx.rotate.called)
        self.assertEqual(ctx.show_text.call_count, len("SCATTER"))
        
class TestMagnetPullReassembly(unittest.TestCase):
    def test_magnetic_pull_logic(self):
        node = MagnetPullReassembly("REASSEMBLE", pull_speed=2.0)
        
        ctx = MagicMock()
        class Extent:
            x_advance = 35.0
        ctx.text_extents.return_value = Extent()
        
        # At progress 0, heavily scattered
        node.progress.set(0.0)
        node.draw(ctx, 0.0)
        self.assertEqual(ctx.show_text.call_count, len("REASSEMBLE"))
        
        ctx.reset_mock()
        ctx.text_extents.return_value = Extent()
        
        # At progress 10.0, snapped completely to grid (exp(-20) ≈ 0.0, snaps to 0)
        node.progress.set(10.0)
        node.draw(ctx, 0.0)
        
        # It translates back to normal position. Since scatter factor goes to 0
        self.assertTrue(ctx.translate.called)
        
        # At high progress, it snaps exactly due to factor < 0.01 logic
        # So rotation will be zero
        # Find the calls to rotate and check they are 0
        rot_calls = ctx.rotate.call_args_list
        for call in rot_calls:
            self.assertAlmostEqual(call[0][0], 0.0)

class TestFloorContactShadow(unittest.TestCase):
    def test_shadow_scaling(self):
        node = FloorContactShadow(floor_y=500.0, max_shadow_width=200.0, max_shadow_height=40.0)
        
        ctx = MagicMock()
        
        # High above floor, no shadow drawn or scale very small
        node.object_y.set(0.0)
        node.draw(ctx, 0.0)
        self.assertFalse(ctx.fill.called) # distance is 500, scale = 1 - (500/500) = 0
        
        ctx.reset_mock()
        
        # Right at floor, max shadow drawn
        node.object_y.set(500.0)
        node.draw(ctx, 0.0)
        
        self.assertTrue(ctx.fill.called)
        self.assertTrue(ctx.scale.called)
        
        # Extract scale call arguments to check if it's max width/height
        scale_call = ctx.scale.call_args
        self.assertAlmostEqual(scale_call[0][0], 200.0)
        self.assertAlmostEqual(scale_call[0][1], 40.0)
        
        ctx.reset_mock()
        
        # Mid way, half scale
        node.object_y.set(250.0)
        node.draw(ctx, 0.0)
        
        self.assertTrue(ctx.fill.called)
        scale_call = ctx.scale.call_args
        self.assertAlmostEqual(scale_call[0][0], 100.0)
        self.assertAlmostEqual(scale_call[0][1], 20.0)

if __name__ == '__main__':
    unittest.main()
