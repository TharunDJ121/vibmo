import pytest
from vibmo.charts.chart_pareto_curve_suite import (
    FrequencyBarChart,
    Cumulative8020Curve,
    CriticalThresholdLine,
    ParetoAnalysisChart
)
from vibmo.core.color import colors

class MockContext:
    def __init__(self):
        self.ops = []

    def save(self):
        self.ops.append(("save",))

    def restore(self):
        self.ops.append(("restore",))

    def set_source_rgba(self, r, g, b, a):
        self.ops.append(("set_source_rgba", r, g, b, a))

    def set_line_width(self, width):
        self.ops.append(("set_line_width", width))

    def rectangle(self, x, y, width, height):
        self.ops.append(("rectangle", x, y, width, height))

    def fill(self):
        self.ops.append(("fill",))

    def move_to(self, x, y):
        self.ops.append(("move_to", x, y))

    def line_to(self, x, y):
        self.ops.append(("line_to", x, y))

    def curve_to(self, cx1, cy1, cx2, cy2, x, y):
        self.ops.append(("curve_to", cx1, cy1, cx2, cy2, x, y))

    def stroke(self):
        self.ops.append(("stroke",))

    def set_dash(self, dashes, offset):
        self.ops.append(("set_dash", dashes, offset))

def test_pareto_sorting_order():
    data = [("A", 10), ("B", 50), ("C", 20)]
    chart = ParetoAnalysisChart(data=data)

    # Must be strictly descending
    assert chart.sorted_data == [("B", 50), ("C", 20), ("A", 10)]

def test_cumulative_percentage_math():
    data = [("A", 10), ("B", 50), ("C", 40)]
    chart = ParetoAnalysisChart(data=data)

    # Sorted: B(50), C(40), A(10)
    # Total = 100
    # Cumulative: 0.5, 0.9, 1.0
    assert chart.cumulative_data == [0.5, 0.9, 1.0]

def test_frequency_bar_chart_drawing():
    data = [("B", 50), ("C", 20), ("A", 10)]
    chart = FrequencyBarChart(data=data, width=100, height=100)

    ctx = MockContext()
    chart.draw(ctx)

    # Asserting rectangles are drawn
    rect_ops = [op for op in ctx.ops if op[0] == "rectangle"]
    assert len(rect_ops) == 3

def test_cumulative_curve_drawing():
    cumulative_data = [0.5, 0.9, 1.0]
    chart = Cumulative8020Curve(cumulative_data=cumulative_data, width=100, height=100)

    ctx = MockContext()
    chart.draw(ctx)

    # Asserting curve_to is used instead of line_to for smooth bezier curves
    move_ops = [op for op in ctx.ops if op[0] == "move_to"]
    curve_ops = [op for op in ctx.ops if op[0] == "curve_to"]

    assert len(move_ops) == 1
    assert len(curve_ops) == 2

def test_critical_threshold_line_drawing():
    chart = CriticalThresholdLine(threshold=0.8, width=100, height=100)

    ctx = MockContext()
    chart.draw(ctx)

    # Glow effect has 3 layered strokes
    stroke_ops = [op for op in ctx.ops if op[0] == "stroke"]
    assert len(stroke_ops) == 3

    move_ops = [op for op in ctx.ops if op[0] == "move_to"]
    line_ops = [op for op in ctx.ops if op[0] == "line_to"]

    assert len(move_ops) == 3
    assert len(line_ops) == 3
