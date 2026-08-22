import math
import pytest
import cairo
import numpy as np

from vibmo.typography.kinetic.typo_isometric_3d_suite import IsometricExtruded3DText, CastShadowExtrusion, BevelGleamLight, IsometricFloatIdle
from vibmo.core.color import Color, colors
from vibmo.core.signal import Signal

class MockContext:
    def __init__(self):
        self.ops = []
        self._font_face = None
        self._font_size = None
        self._rgba = None
        self._path = []
        self._clip = []

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
        
    def text_path(self, text):
        self.ops.append(('text_path', text))
        
    def clip(self):
        self.ops.append(('clip',))
        
    def text_extents(self, text):
        class Extents:
            width = 100.0
            height = 20.0
            x_advance = 110.0
            y_advance = 0.0
        return Extents()
        
    def set_source(self, source):
        self.ops.append(('set_source', source))
        
    def paint(self):
        self.ops.append(('paint',))
        
    def translate(self, tx, ty):
        self.ops.append(('translate', tx, ty))

def test_isometric_extruded_3d_text():
    node = IsometricExtruded3DText(text="ISO", depth=5)
    ctx = MockContext()

    node.draw(ctx, time=0.0)

    # Should have 5 background layers + 1 top layer
    shows = [op for op in ctx.ops if op[0] == 'show_text']
    assert len(shows) == 6
    assert all(show[1] == "ISO" for show in shows)
    
    # Check move_to offsets for extrusion
    moves = [op for op in ctx.ops if op[0] == 'move_to']
    assert len(moves) == 6
    
    # Check if the final layer is at the front (0, fs * 0.88)
    assert moves[-1][1] == 0
    
    # Check facet lighting calculations
    # There should be 5 depth layers + 1 front layer of set_source_rgba
    rgbas = [op for op in ctx.ops if op[0] == 'set_source_rgba']
    assert len(rgbas) == 6
    
    # Check that background layers are appropriately shaded
    c = node.color.get(0.0)
    for i in range(5, 0, -1): # The loop goes depth -> 1
        shade_factor = 0.5 + 0.3 * (1.0 - (i / 5))
        r = min(1.0, c.r * shade_factor)
        g = min(1.0, c.g * shade_factor)
        b = min(1.0, c.b * shade_factor)
        
        # The index in rgbas is (5 - i) because i counts down
        op = rgbas[5 - i]
        assert math.isclose(op[1], r, rel_tol=1e-5)
        assert math.isclose(op[2], g, rel_tol=1e-5)
        assert math.isclose(op[3], b, rel_tol=1e-5)

def test_cast_shadow_extrusion():
    node = CastShadowExtrusion(text="SHADOW", blur_steps=3)
    ctx = MockContext()

    node.draw(ctx, time=0.0)

    shows = [op for op in ctx.ops if op[0] == 'show_text']
    assert len(shows) == 3
    assert all(show[1] == "SHADOW" for show in shows)
    
    # Check alphas and offsets
    rgba_ops = [op for op in ctx.ops if op[0] == 'set_source_rgba']
    assert len(rgba_ops) == 3
    
    # The alpha should be (shadow_color.a / blur_steps) * 0.5
    expected_alpha = (colors.BLACK.a / 3) * 0.5
    for op in rgba_ops:
        assert math.isclose(op[4], expected_alpha, rel_tol=1e-5)

def test_bevel_gleam_light():
    node = BevelGleamLight(text="GLEAM")
    ctx = MockContext()

    node.draw(ctx, time=0.0)

    assert any(op[0] == 'text_path' and op[1] == "GLEAM" for op in ctx.ops)
    assert any(op[0] == 'clip' for op in ctx.ops)
    assert any(op[0] == 'set_source' for op in ctx.ops)
    assert any(op[0] == 'paint' for op in ctx.ops)
    
    # Test a different progress
    node.progress.set(1.0)
    ctx.ops.clear()
    node.draw(ctx, time=1.0)
    
    assert any(op[0] == 'text_path' and op[1] == "GLEAM" for op in ctx.ops)
    assert any(op[0] == 'paint' for op in ctx.ops)

def test_isometric_float_idle():
    node = IsometricFloatIdle(amplitude=10.0, frequency=1.0)
    ctx = MockContext()
    
    node.draw(ctx, time=0.25)
    
    translates = [op for op in ctx.ops if op[0] == 'translate']
    assert len(translates) == 1
    
    # At time 0.25, sin(0.25 * 1.0 * 2 * pi) = sin(pi/2) = 1.0
    # y_offset should be 1.0 * amplitude = 10.0
    assert math.isclose(translates[0][2], 10.0, rel_tol=1e-5)
