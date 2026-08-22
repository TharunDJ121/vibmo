import pytest
import math
import cairo
from vibmo.charts.chart_bubble_scatter_suite import (
    MultiVariableBubbleScatter,
    MotionTrailBubble,
    QuadrantPartitionLines,
    BubbleScaleLegend,
)
from vibmo.core.vector import Vector2D
from vibmo.core.color import Color, colors

class MockContext:
    def __init__(self):
        self.ops = []

    def save(self):
        self.ops.append("save")

    def restore(self):
        self.ops.append("restore")

    def set_source_rgba(self, r, g, b, a):
        self.ops.append(f"set_source_rgba({r}, {g}, {b}, {a})")

    def new_path(self):
        self.ops.append("new_path")

    def move_to(self, x, y):
        self.ops.append(f"move_to({x}, {y})")

    def line_to(self, x, y):
        self.ops.append(f"line_to({x}, {y})")

    def arc(self, x, y, r, a1, a2):
        self.ops.append(f"arc({x}, {y}, {r}, {a1}, {a2})")

    def stroke(self):
        self.ops.append("stroke")

    def fill_preserve(self):
        self.ops.append("fill_preserve")

    def set_line_width(self, w):
        self.ops.append(f"set_line_width({w})")

def test_multivariable_bubble_scatter_normalization():
    data = [
        {"x": 10, "y": 20, "z": 5, "color": colors.RED},
        {"x": 30, "y": 40, "z": 15, "color": colors.BLUE},
    ]

    chart = MultiVariableBubbleScatter(width=100.0, height=200.0, data=data)

    # Check bounds
    assert chart.x_min == 10
    assert chart.x_max == 30
    assert chart.y_min == 20
    assert chart.y_max == 40
    assert chart.z_min == 5
    assert chart.z_max == 15

    # Check normalized coords
    nx, ny = chart.get_normalized_coords(20, 30, 100.0, 200.0)
    # x = (20 - 10) / 20 * 100 = 50
    # y = (1.0 - (30 - 20) / 20) * 200 = (1.0 - 0.5) * 200 = 100
    assert nx == 50.0
    assert ny == 100.0

    # Check normalized radius
    nr = chart.get_normalized_radius(10, max_radius=40, min_radius=5)
    # nz = (10 - 5) / 10 = 0.5
    # nr = 5 + 35 * sqrt(0.5)
    assert math.isclose(nr, 5 + 35 * math.sqrt(0.5))

def test_multivariable_bubble_scatter_draw():
    data = [
        {"x": 10, "y": 20, "z": 5, "color": colors.RED},
    ]
    chart = MultiVariableBubbleScatter(width=100.0, height=200.0, data=data)
    ctx = MockContext()
    chart.draw(ctx, time=0.0)

    assert "save" in ctx.ops
    assert "new_path" in ctx.ops
    # (x, y) = (0, 0), h = 200, so py = 200, px = 0
    assert "arc(0.0, 200.0, 5.0, 0, 6.283185307179586)" in ctx.ops
    assert "fill_preserve" in ctx.ops
    assert "stroke" in ctx.ops
    assert "restore" in ctx.ops

def test_motion_trail_bubble_draw():
    history = [Vector2D(10, 10), Vector2D(20, 20)]
    trail = MotionTrailBubble(history, color=colors.RED, radius=10.0)
    ctx = MockContext()
    trail.draw(ctx, time=0.0)

    assert "save" in ctx.ops
    assert "move_to(10.0, 10.0)" in ctx.ops
    assert "line_to(20.0, 20.0)" in ctx.ops
    assert "arc(20.0, 20.0, 10.0, 0, 6.283185307179586)" in ctx.ops
    assert "fill_preserve" in ctx.ops
    assert "restore" in ctx.ops

def test_quadrant_partition_lines_draw():
    lines = QuadrantPartitionLines(width=100.0, height=200.0)
    ctx = MockContext()
    lines.draw(ctx, time=0.0)

    assert "save" in ctx.ops
    assert "move_to(50.0, 0)" in ctx.ops
    assert "line_to(50.0, 200.0)" in ctx.ops
    assert "move_to(0, 100.0)" in ctx.ops
    assert "line_to(100.0, 100.0)" in ctx.ops
    assert "stroke" in ctx.ops
    assert "restore" in ctx.ops

def test_bubble_scale_legend_radius():
    legend = BubbleScaleLegend([10, 20, 30])

    assert legend.v_min == 10
    assert legend.v_max == 30

    nr = legend.get_normalized_radius(20)
    # nv = 0.5
    assert math.isclose(nr, 5.0 + 35.0 * math.sqrt(0.5))

def test_bubble_scale_legend_draw():
    legend = BubbleScaleLegend([10])
    ctx = MockContext()
    legend.draw(ctx, time=0.0)

    assert "save" in ctx.ops
    assert "new_path" in ctx.ops
    assert "arc(40.0, 75.0, 5.0, 0, 6.283185307179586)" in ctx.ops
    assert "fill_preserve" in ctx.ops
    assert "restore" in ctx.ops
