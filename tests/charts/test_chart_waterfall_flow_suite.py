import pytest
from vibmo.charts.chart_waterfall_flow_suite import (
    WaterfallCostChart,
    NetGainColumn,
    DeductionColumn,
    CumulativeBridgeConnector
)
from vibmo.core.color import colors
from vibmo.core.vector import Vector2D
import cairo

class MockContext:
    def __init__(self):
        self.ops = []
        self.fills = 0
        self.strokes = 0
        self.moves = []
        self.lines = []
        self.rects = []
        self.colors = []
    def save(self): self.ops.append('save')
    def restore(self): self.ops.append('restore')
    def set_source_rgba(self, r, g, b, a):
        self.ops.append('set_source_rgba')
        self.colors.append((r,g,b,a))
    def rectangle(self, x, y, w, h):
        self.ops.append('rectangle')
        self.rects.append((x,y,w,h))
    def fill(self):
        self.ops.append('fill')
        self.fills += 1
    def move_to(self, x, y):
        self.ops.append('move_to')
        self.moves.append((x,y))
    def line_to(self, x, y):
        self.ops.append('line_to')
        self.lines.append((x,y))
    def stroke(self):
        self.ops.append('stroke')
        self.strokes += 1
    def set_line_width(self, w): self.ops.append('set_line_width')
    def set_dash(self, dashes, offset): self.ops.append('set_dash')

def test_cumulative_bridge_connector():
    ctx = MockContext()
    c = CumulativeBridgeConnector(Vector2D(10, 20), Vector2D(30, 40))
    c.draw(ctx)
    assert ctx.strokes == 1
    assert ctx.moves == [(10, 20)]
    assert ctx.lines == [(30, 40)]

def test_columns():
    ctx = MockContext()
    ngc = NetGainColumn(10, 20)
    ngc.draw(ctx)
    assert ctx.fills == 1
    assert ctx.rects == [(0, 0, 10, 20)]
    assert ctx.colors[-1] == colors.GREEN_500.to_cairo()

    ctx = MockContext()
    dc = DeductionColumn(15, 25)
    dc.draw(ctx)
    assert ctx.fills == 1
    assert ctx.rects == [(0, 0, 15, 25)]
    assert ctx.colors[-1] == colors.RED_500.to_cairo()

def test_waterfall_chart():
    chart = WaterfallCostChart([100, 50, -30, -20])

    assert len(chart.columns) == 5
    assert len(chart.connectors) == 4

    # 0: 100
    assert isinstance(chart.columns[0], NetGainColumn)
    assert chart.columns[0].position.get() == Vector2D(0, -100)

    # 1: 50
    assert isinstance(chart.columns[1], NetGainColumn)
    assert chart.columns[1].position.get() == Vector2D(70, -150)

    # 2: -30
    assert isinstance(chart.columns[2], DeductionColumn)
    assert chart.columns[2].position.get() == Vector2D(140, -150)

    # 3: -20
    assert isinstance(chart.columns[3], DeductionColumn)
    assert chart.columns[3].position.get() == Vector2D(210, -120)

    # 4: 100 (total)
    assert isinstance(chart.columns[4], NetGainColumn)
    assert chart.columns[4].position.get() == Vector2D(280, -100)
