import pytest
import cairo
import numpy as np

from vibmo.typography.kinetic.typo_slit_scan_synth_suite import SlitScanVideoSynthText, AnalogFeedbackSmear, ChromaWarpWave, CRTScanBeamWipe
from vibmo.core.color import Color, colors
from vibmo.core.vector import Vector2D

class MockContext:
    def __init__(self):
        self.ops = []
        self._font_face = None
        self._font_size = None
        self._rgba = None

    def save(self):
        self.ops.append(('save',))

    def restore(self):
        self.ops.append(('restore',))

    def select_font_face(self, family, slant, weight):
        self._font_face = (family, slant, weight)
        self.ops.append(('select_font_face', family, slant, weight))

    def set_font_size(self, size):
        self._font_size = size
        self.ops.append(('set_font_size', size))

    def set_source_rgba(self, r, g, b, a):
        self._rgba = (r, g, b, a)
        self.ops.append(('set_source_rgba', r, g, b, a))

    def move_to(self, x, y):
        self.ops.append(('move_to', x, y))

    def show_text(self, text):
        self.ops.append(('show_text', text))

    def text_extents(self, text):
        class Extents:
            width = 100.0
            x_advance = 110.0
            y_advance = 0.0
        return Extents()
        
    def rectangle(self, x, y, w, h):
        self.ops.append(('rectangle', x, y, w, h))
        
    def clip(self):
        self.ops.append(('clip',))
        
    def translate(self, tx, ty):
        self.ops.append(('translate', tx, ty))
        
    def push_group(self):
        self.ops.append(('push_group',))
        
    def set_operator(self, op):
        self.ops.append(('set_operator', op))
        
    def fill(self):
        self.ops.append(('fill',))
        
    def pop_group_to_source(self):
        self.ops.append(('pop_group_to_source',))
        
    def paint(self):
        self.ops.append(('paint',))

def test_slit_scan_video_synth_text():
    node = SlitScanVideoSynthText(text="SYNTH")
    ctx = MockContext()
    
    node.draw(ctx, time=1.0)
    
    shows = [op for op in ctx.ops if op[0] == 'show_text']
    assert len(shows) >= 10 # Num slits should be max(10, int(font_size))
    
    translates = [op for op in ctx.ops if op[0] == 'translate']
    assert len(translates) == len(shows)

def test_analog_feedback_smear():
    node = AnalogFeedbackSmear(text="TRAIL", trail_length=5, trail_offset=Vector2D(-5, 2))
    ctx = MockContext()
    
    node.draw(ctx, time=1.0)
    
    shows = [op for op in ctx.ops if op[0] == 'show_text']
    assert len(shows) == 5
    
    translates = [op for op in ctx.ops if op[0] == 'translate']
    # Check that they translate increasingly
    assert translates[0][1] == -20.0 # i = 4 (trail_length - 1)
    assert translates[0][2] == 8.0

def test_chroma_warp_wave():
    node = ChromaWarpWave(text="WARP")
    ctx = MockContext()
    
    node.draw(ctx, time=1.0)
    
    shows = [op for op in ctx.ops if op[0] == 'show_text']
    assert len(shows) >= 10
    
    rectangles = [op for op in ctx.ops if op[0] == 'rectangle']
    assert len(rectangles) == len(shows)

def test_crt_scan_beam_wipe():
    node = CRTScanBeamWipe(text="BEAM")
    ctx = MockContext()
    
    # Progress 0, should not draw
    node.draw(ctx, time=0.0)
    assert not any(op[0] == 'show_text' for op in ctx.ops)
    
    # Progress 0.5, should draw text and beam
    node.sweep_progress.set(0.5)
    ctx.ops.clear()
    node.draw(ctx, time=0.5)
    
    shows = [op for op in ctx.ops if op[0] == 'show_text']
    assert len(shows) == 2 # One for reveal, one for mask
    
    rectangles = [op for op in ctx.ops if op[0] == 'rectangle']
    assert len(rectangles) >= 3 # Reveal clip, beam fill, glowing line

    # Progress 1.0, should only draw text, no beam
    node.sweep_progress.set(1.0)
    ctx.ops.clear()
    node.draw(ctx, time=1.0)
    
    shows = [op for op in ctx.ops if op[0] == 'show_text']
    assert len(shows) == 1
    
    rectangles = [op for op in ctx.ops if op[0] == 'rectangle']
    assert len(rectangles) == 1 # Just the reveal clip
