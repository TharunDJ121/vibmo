import pytest
import cairo
import numpy as np

from vibmo.typography.kinetic.typo_neon_strobe_suite import (
    RealisticNeonStrobeSign,
    BallastFlickerFailure,
    GasIgnitionSurge,
    NeonTubeConnectors,
)
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

    def line_to(self, x, y):
        self.ops.append(('line_to', x, y))

    def text_path(self, text):
        self.ops.append(('text_path', text))

    def stroke(self):
        self.ops.append(('stroke',))

    def fill(self):
        self.ops.append(('fill',))

    def translate(self, x, y):
        self.ops.append(('translate', x, y))

    def arc(self, x, y, radius, angle1, angle2):
        self.ops.append(('arc', x, y, radius, angle1, angle2))

    def set_line_width(self, w):
        self.ops.append(('set_line_width', w))

    def set_line_join(self, j):
        self.ops.append(('set_line_join', j))

    def set_line_cap(self, c):
        self.ops.append(('set_line_cap', c))

    def set_source(self, pat):
        self.ops.append(('set_source', pat))

def test_ballast_flicker_failure_timing():
    node = BallastFlickerFailure()

    # Check start and end explicitly
    assert node.get_flicker_intensity(0.0) == 0.0

    node.progress.set(1.0)
    assert node.get_flicker_intensity(1.0) == 1.0

    # Pattern check
    node.progress.set(0.05)
    assert node.get_flicker_intensity(0.0) == 1.0

    node.progress.set(0.12)
    assert node.get_flicker_intensity(0.0) == 0.0

    node.progress.set(0.2)
    assert node.get_flicker_intensity(0.0) == 1.0

    node.progress.set(0.3)
    assert node.get_flicker_intensity(0.0) == 0.0

    node.progress.set(0.42)
    assert node.get_flicker_intensity(0.0) == 1.0

def test_gas_ignition_surge_radius_math():
    node = GasIgnitionSurge(max_radius=100.0)
    ctx = MockContext()

    node.draw(ctx, time=0.0)
    assert not any(op[0] == 'arc' for op in ctx.ops)

    ctx.ops.clear()
    node.progress.set(0.5)
    node.draw(ctx, time=0.0)

    # Calculate expected radius for prog 0.5: 100.0 * (0.2 + 0.8 * 0.5) = 100.0 * 0.6 = 60.0
    arc_ops = [op for op in ctx.ops if op[0] == 'arc']
    assert len(arc_ops) == 1
    assert pytest.approx(arc_ops[0][3], 0.001) == 60.0

    # Pattern stop alpha at 0.5: 1.0 - (0.5 ** 0.5)

def test_neon_tube_connectors():
    node = NeonTubeConnectors(points=[Vector2D(10, 10), Vector2D(50, 10), Vector2D(50, 50)])
    ctx = MockContext()

    node.draw(ctx, time=0.0)

    lines = [op for op in ctx.ops if op[0] == 'line_to']
    assert len(lines) == 2
    assert lines[0][1:] == (50, 10)
    assert lines[1][1:] == (50, 50)

    arcs = [op for op in ctx.ops if op[0] == 'arc']
    assert len(arcs) == 3

def test_realistic_neon_strobe_sign_bloom():
    node = RealisticNeonStrobeSign(text="OPEN", font_size=50.0)
    ctx = MockContext()

    node.draw(ctx, time=0.0)

    # When off (flicker intensity = 0, node intensity = 0), only the base tube should be drawn
    # (NeonTubeConnectors doesn't draw here because MockContext doesn't propagate child draws properly in our simplified test)
    strokes = [op for op in ctx.ops if op[0] == 'stroke']
    assert len(strokes) == 1

    # Ignite turns on sign
    node.flicker.progress.set(1.0) # forces intensity to 1.0
    ctx.ops.clear()

    node.draw(ctx, time=0.0)

    # Base off tube + 4 layers + 1 core = 6 strokes
    strokes = [op for op in ctx.ops if op[0] == 'stroke']
    assert len(strokes) == 6

    # Check widths of the strokes
    widths = [op[1] for op in ctx.ops if op[0] == 'set_line_width']

    # Base tube width is fs * 0.05
    assert widths[0] == 50.0 * 0.05

    # Bloom widths:
    assert widths[1] == 50.0 * 0.4
    assert widths[2] == 50.0 * 0.2
    assert widths[3] == 50.0 * 0.1
    assert widths[4] == 50.0 * 0.05

    # Core width
    assert widths[5] == 50.0 * 0.02
