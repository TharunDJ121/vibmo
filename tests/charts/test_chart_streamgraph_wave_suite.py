import pytest
from unittest.mock import MagicMock
from vibmo.charts.chart_streamgraph_wave_suite import (
    compute_streamgraph_stack,
    compute_cubic_spline_controls,
    FlowingStreamgraphArea,
    OrganicWaveBand,
    TimeAxisScrubber,
    StreamgraphLegend
)
from vibmo.core.color import colors

def test_compute_streamgraph_stack_silhouette():
    data = [[1, 2, 3], [4, 5, 6]]
    bottoms, tops = compute_streamgraph_stack(data, method="silhouette")

    # At t=0, total = 5. g0 = -2.5
    # Layer 0: bottom = -2.5, top = -1.5
    # Layer 1: bottom = -1.5, top = 2.5
    assert bottoms[0][0] == -2.5
    assert tops[0][0] == -1.5
    assert bottoms[1][0] == -1.5
    assert tops[1][0] == 2.5

    # At t=1, total = 7. g0 = -3.5
    assert bottoms[0][1] == -3.5
    assert tops[0][1] == -1.5

def test_compute_streamgraph_stack_wiggle():
    data = [[1, 2, 3], [4, 5, 6]]
    bottoms, tops = compute_streamgraph_stack(data, method="wiggle")

    # Ensure dimensions match
    assert len(bottoms) == 2
    assert len(bottoms[0]) == 3
    assert len(tops) == 2
    assert len(tops[0]) == 3

    # Top of layer i should be bottom of layer i+1
    for j in range(3):
        assert abs(tops[0][j] - bottoms[1][j]) < 1e-6

    # Stack height is equal to sum of values
    for j in range(3):
        height = tops[1][j] - bottoms[0][j]
        assert abs(height - sum(data[i][j] for i in range(2))) < 1e-6

def test_compute_cubic_spline_controls():
    pts = [(0, 0), (1, 1), (2, 0)]
    segments = compute_cubic_spline_controls(pts, tension=0.3)
    assert len(segments) == 2
    # First segment: from pt0 to pt1
    # Second segment: from pt1 to pt2
    assert segments[0][4] == 1
    assert segments[0][5] == 1
    assert segments[1][4] == 2
    assert segments[1][5] == 0

def test_organic_wave_band_draw():
    # Setup mock cairo context
    class MockContext:
        def __init__(self):
            self.calls = []
        def save(self): self.calls.append("save")
        def restore(self): self.calls.append("restore")
        def set_source_rgba(self, r, g, b, a): self.calls.append("set_source_rgba")
        def new_path(self): self.calls.append("new_path")
        def move_to(self, x, y): self.calls.append("move_to")
        def line_to(self, x, y): self.calls.append("line_to")
        def curve_to(self, c1x, c1y, c2x, c2y, x, y): self.calls.append("curve_to")
        def close_path(self): self.calls.append("close_path")
        def fill(self): self.calls.append("fill")

    bottom = [(0, 0), (10, 0), (20, 0)]
    top = [(0, 10), (10, 15), (20, 10)]
    band = OrganicWaveBand(bottom_points=bottom, top_points=top, color=colors.BLUE)

    ctx = MockContext()
    band.draw(ctx, 0.0)

    assert "save" in ctx.calls
    assert "new_path" in ctx.calls
    assert "move_to" in ctx.calls
    assert "curve_to" in ctx.calls
    assert "line_to" in ctx.calls
    assert "close_path" in ctx.calls
    assert "fill" in ctx.calls
    assert "restore" in ctx.calls

def test_flowing_streamgraph_area():
    data = [[1, 2], [3, 4]]
    chart = FlowingStreamgraphArea(data=data, width=800, height=400)
    assert len(chart.bands) == 2

def test_time_axis_scrubber():
    class MockContext:
        def __init__(self):
            self.calls = []
        def save(self): self.calls.append("save")
        def restore(self): self.calls.append("restore")
        def set_source_rgba(self, *args): pass
        def set_line_width(self, w): pass
        def new_path(self): pass
        def move_to(self, x, y): pass
        def line_to(self, x, y): pass
        def stroke(self): self.calls.append("stroke")
        def rectangle(self, *args): pass
        def clip(self): pass
        def select_font_face(self, *args): pass
        def set_font_size(self, *args): pass
        def text_extents(self, *args):
            class Extents:
                width = 10
            return Extents()
        def show_text(self, *args): pass

    scrubber = TimeAxisScrubber(x=100, height=300, label="12:00")

    ctx = MockContext()
    scrubber.draw(ctx, 0.0)

    assert "stroke" in ctx.calls
    assert scrubber.card.position.get().x == 110 # 100 + 10

def test_streamgraph_legend():
    categories = [
        ("Layer A", colors.CYAN, 15.5),
        ("Layer B", colors.EMERALD, 42.0)
    ]
    legend = StreamgraphLegend(categories=categories)
    assert len(legend.children) == 2
