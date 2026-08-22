import pytest
import cairo
import numpy as np
from vibmo.typography.kinetic.typo_glitch_decryptor_suite import HexMatrixCycle, LockInGlitchFlash, PasswordUnmaskEffect, GlitchDecryptorText
from vibmo.core.color import Color, colors

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
            width = 20.0
            x_advance = 22.0
            y_advance = 0.0
        return Extents()

def test_hex_matrix_cycle():
    node = HexMatrixCycle(target_char="A")
    ctx = MockContext()

    # Progress 0, should cycle
    node.draw(ctx, time=0.0)
    assert any(op[0] == 'show_text' for op in ctx.ops)

    # Progress 1, should be target_char
    node.progress.set(1.0)
    ctx.ops.clear()
    node.draw(ctx, time=1.0)
    assert any(op[0] == 'show_text' and op[1] == "A" for op in ctx.ops)

def test_lock_in_glitch_flash():
    node = LockInGlitchFlash(char="B")
    ctx = MockContext()

    # Progress 0, should not draw
    node.draw(ctx, time=0.0)
    assert not any(op[0] == 'show_text' for op in ctx.ops)

    # Progress 0.5, should draw flash effects
    node.flash_progress.set(0.5)
    node.draw(ctx, time=0.5)
    shows = [op for op in ctx.ops if op[0] == 'show_text']
    assert len(shows) == 3 # Red offset, Blue offset, Main

    # Progress 1, should not draw
    node.flash_progress.set(1.0)
    ctx.ops.clear()
    node.draw(ctx, time=1.0)
    assert not any(op[0] == 'show_text' for op in ctx.ops)

def test_password_unmask_effect():
    node = PasswordUnmaskEffect(target_text="SECRET")
    ctx = MockContext()

    # Progress 0, should be all masks
    node.draw(ctx, time=0.0)
    shows = [op for op in ctx.ops if op[0] == 'show_text']
    assert all(show[1] == "•" for show in shows)
    assert len(shows) == 6

    # Progress 1, should be all target text
    node.progress.set(1.0)
    ctx.ops.clear()
    node.draw(ctx, time=1.0)
    shows = [op for op in ctx.ops if op[0] == 'show_text']
    assert "".join(show[1] for show in shows) == "SECRET"

def test_glitch_decryptor_text():
    node = GlitchDecryptorText(text="CYBER")
    ctx = MockContext()

    # Initially children are at 0
    node.draw(ctx, time=0.0)

    # Progress 1, should set all children to 1
    node.decrypt_progress.set(1.0)
    node.draw(ctx, time=1.0)

    for cycle in node.cycles:
        assert cycle.progress.get(1.0) == 1.0
