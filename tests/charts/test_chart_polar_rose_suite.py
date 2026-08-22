import math
import cairo
import pytest

from vibmo.charts.chart_polar_rose_suite import (
    ProportionalRadiusWedge,
    ConcentricRadiusRings,
    AngularCategoryAxis,
    PolarRoseAreaChart,
)
from vibmo.core.color import colors

class MockContext:
    def __init__(self):
        self.ops = []

    def save(self):
        self.ops.append(('save',))

    def restore(self):
        self.ops.append(('restore',))

    def set_source_rgba(self, r, g, b, a):
        self.ops.append(('set_source_rgba', r, g, b, a))

    def set_line_width(self, w):
        self.ops.append(('set_line_width', w))

    def move_to(self, x, y):
        self.ops.append(('move_to', x, y))

    def line_to(self, x, y):
        self.ops.append(('line_to', x, y))

    def arc(self, xc, yc, radius, angle1, angle2):
        self.ops.append(('arc', xc, yc, radius, angle1, angle2))

    def close_path(self):
        self.ops.append(('close_path',))

    def fill(self):
        self.ops.append(('fill',))

    def stroke(self):
        self.ops.append(('stroke',))

    def new_path(self):
        self.ops.append(('new_path',))

def test_proportional_radius_wedge():
    # Value is 50, max is 100, max_radius is 200
    # Expected ratio = 0.5, r = 200 * sqrt(0.5) = 200 * 0.7071 = 141.42
    wedge = ProportionalRadiusWedge(
        value=50,
        max_value=100,
        max_radius=200,
        start_angle=0,
        end_angle=math.pi / 2,
    )

    ctx = MockContext()
    wedge.draw(ctx)

    arcs = [op for op in ctx.ops if op[0] == 'arc']
    assert len(arcs) == 1
    op_name, xc, yc, r, a1, a2 = arcs[0]

    assert xc == 0
    assert yc == 0
    assert math.isclose(r, 200 * math.sqrt(0.5))
    assert a1 == 0
    assert a2 == math.pi / 2

def test_concentric_radius_rings():
    rings = ConcentricRadiusRings(
        max_value=100,
        max_radius=200,
        rings=4,
    )

    ctx = MockContext()
    rings.draw(ctx)

    arcs = [op for op in ctx.ops if op[0] == 'arc']
    assert len(arcs) == 4

    # Radii should be sqrt(0.25)*200, sqrt(0.5)*200, sqrt(0.75)*200, sqrt(1.0)*200
    # which is 100, 141.42, 173.2, 200
    expected_r = [
        200 * math.sqrt(0.25),
        200 * math.sqrt(0.5),
        200 * math.sqrt(0.75),
        200 * math.sqrt(1.0)
    ]

    for i, op in enumerate(arcs):
        assert math.isclose(op[3], expected_r[i])

def test_angular_category_axis():
    axis = AngularCategoryAxis(
        categories=["Jan", "Feb", "Mar", "Apr"],
        max_radius=100,
    )

    # 4 categories, expect 4 lines drawn from 0,0
    ctx = MockContext()
    axis.draw(ctx)

    moves = [op for op in ctx.ops if op[0] == 'move_to']
    lines = [op for op in ctx.ops if op[0] == 'line_to']

    assert len(moves) == 4
    assert len(lines) == 4

    # Check angles (0, pi/2, pi, 3pi/2)
    expected_angles = [0, math.pi/2, math.pi, 3*math.pi/2]
    for i, op in enumerate(lines):
        _, x, y = op
        expected_x = 100 * math.cos(expected_angles[i])
        expected_y = 100 * math.sin(expected_angles[i])
        assert math.isclose(x, expected_x, abs_tol=1e-9)
        assert math.isclose(y, expected_y, abs_tol=1e-9)

def test_polar_rose_area_chart():
    data = {
        "Army": [10, 20, 30],
        "Navy": [5, 10, 15]
    }
    categories = ["A", "B", "C"]

    chart = PolarRoseAreaChart(
        data=data,
        categories=categories,
        max_radius=300
    )

    # Max val is 30
    assert len(chart.children) == 8 # 1 ring, 1 axis, 2*3 = 6 wedges

    wedges = [c for c in chart.children if isinstance(c, ProportionalRadiusWedge)]
    assert len(wedges) == 6

    # Find the largest wedge for Army C (val=30)
    largest_wedge = next(w for w in wedges if w.value.get() == 30)
    assert largest_wedge.max_value == 30
    assert largest_wedge.max_radius == 300
    # The max radius in chart is 300, wait, it should be 300!
    assert largest_wedge.max_radius == 300
