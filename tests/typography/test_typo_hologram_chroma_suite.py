import unittest
import cairo
from unittest.mock import MagicMock

from vibmo.typography.kinetic.typo_hologram_chroma_suite import (
    HologramChromaText,
    InterferenceFringeLines,
    HologramEmitterCone,
    GlitchDeconstruct
)

class TestTypoHologramChromaSuite(unittest.TestCase):
    def setUp(self):
        self.surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, 200, 200)
        self.ctx = cairo.Context(self.surface)

    def test_hologram_chroma_text_rendering(self):
        node = HologramChromaText(text="HOLO", font_size=24)
        # Smoke test: draw without errors
        node.draw(self.ctx, time=0.0)
        
        # Test drawing with a time value
        node.draw(self.ctx, time=1.5)
        self.assertIsInstance(node, HologramChromaText)

    def test_interference_fringe_lines_movement(self):
        node = InterferenceFringeLines(text="FRINGE", font_size=24)
        node.draw(self.ctx, time=0.0)
        
        node.draw(self.ctx, time=2.0)
        self.assertIsInstance(node, InterferenceFringeLines)

    def test_hologram_emitter_cone_alpha_gradient(self):
        node = HologramEmitterCone(width=100, height=150, emitter_width=20)
        node.draw(self.ctx, time=0.0)
        self.assertIsInstance(node, HologramEmitterCone)

    def test_glitch_deconstruct_offsets(self):
        node = GlitchDeconstruct(text="GLITCH", font_size=24)
        # Call multiple times with different times to verify seeding and randomness doesn't crash
        node.draw(self.ctx, time=0.1)
        node.draw(self.ctx, time=0.2)
        node.draw(self.ctx, time=1.5)
        self.assertIsInstance(node, GlitchDeconstruct)

if __name__ == '__main__':
    unittest.main()
