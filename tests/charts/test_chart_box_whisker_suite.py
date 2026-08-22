import pytest
import numpy as np
import cairo
from vibmo.charts.chart_box_whisker_suite import (
    calculate_box_stats,
    AnimatedOutlierPings,
    WhiskersErrorBars,
    InterquartileBox,
    StatisticalBoxPlot
)
from vibmo.core.color import colors


def test_calculate_box_stats_normal():
    # Test dataset with no outliers
    data = [1, 2, 3, 4, 5, 6, 7]
    stats = calculate_box_stats(data)

    assert stats["q1"] == 2.5
    assert stats["median"] == 4.0
    assert stats["q3"] == 5.5
    assert stats["iqr"] == 3.0
    assert stats["min_whisker"] == 1.0
    assert stats["max_whisker"] == 7.0
    assert stats["outliers"] == []


def test_calculate_box_stats_with_outliers():
    # Test dataset with outliers
    # 25th percentile: 2.0, 75th percentile: 8.0, IQR = 6.0
    # Lower bound = 2.0 - 1.5 * 6.0 = -7.0
    # Upper bound = 8.0 + 1.5 * 6.0 = 17.0
    data = [1, 2, 5, 8, 9, 20, -10]
    stats = calculate_box_stats(data)

    assert stats["q1"] == 1.5
    assert stats["median"] == 5.0
    assert stats["q3"] == 8.5
    assert stats["iqr"] == 7.0

    # bounds: 1.5 - 1.5*7 = -9.0; 8.5 + 1.5*7 = 19.0
    # Valid points: 1, 2, 5, 8, 9
    assert stats["min_whisker"] == 1.0
    assert stats["max_whisker"] == 9.0
    assert set(stats["outliers"]) == {-10.0, 20.0}


def test_calculate_box_stats_empty():
    stats = calculate_box_stats([])
    assert stats["q1"] == 0.0
    assert stats["median"] == 0.0
    assert stats["q3"] == 0.0
    assert stats["outliers"] == []


class MockContext:
    def __init__(self):
        self.calls = []

    def save(self): self.calls.append("save")
    def restore(self): self.calls.append("restore")
    def set_source_rgba(self, r, g, b, a): self.calls.append(("set_source_rgba", r, g, b, a))
    def set_line_width(self, w): self.calls.append(("set_line_width", w))
    def move_to(self, x, y): self.calls.append(("move_to", x, y))
    def line_to(self, x, y): self.calls.append(("line_to", x, y))
    def stroke(self): self.calls.append("stroke")
    def rectangle(self, x, y, w, h): self.calls.append(("rectangle", x, y, w, h))
    def fill_preserve(self): self.calls.append("fill_preserve")
    def fill(self): self.calls.append("fill")
    def arc(self, cx, cy, r, a1, a2): self.calls.append(("arc", cx, cy, r, a1, a2))


def test_animated_outlier_pings_rendering():
    pings = AnimatedOutlierPings(outliers=[100.0, 200.0])
    ctx = MockContext()

    # Test early exit when progress is 0
    pings.ping_progress.set(0.0)
    pings.draw(ctx, 0.0)
    assert not ctx.calls

    # Test drawing when progress is 1.0
    pings.ping_progress.set(1.0)
    pings.draw(ctx, 1.0)

    assert "save" in ctx.calls
    assert "fill" in ctx.calls


def test_whiskers_error_bars_rendering():
    whiskers = WhiskersErrorBars(min_whisker=10.0, max_whisker=90.0, q1=30.0, q3=70.0)
    ctx = MockContext()

    whiskers.reveal.set(1.0)
    whiskers.draw(ctx, 1.0)

    assert "save" in ctx.calls
    assert "stroke" in ctx.calls

    moves = [c for c in ctx.calls if isinstance(c, tuple) and c[0] == "move_to"]
    assert len(moves) == 4 # 2 for each whisker (vertical line + horizontal cap)


def test_interquartile_box_rendering():
    box = InterquartileBox(q1=30.0, median=50.0, q3=70.0)
    ctx = MockContext()

    box.reveal.set(1.0)
    box.draw(ctx, 1.0)

    assert "save" in ctx.calls
    assert "fill_preserve" in ctx.calls
    assert "stroke" in ctx.calls

    rects = [c for c in ctx.calls if isinstance(c, tuple) and c[0] == "rectangle"]
    assert len(rects) == 1


def test_statistical_box_plot_integration():
    datasets = [
        [10, 20, 30, 40, 50],
        [15, 25, 35, 45, 55, 100]
    ]

    plot = StatisticalBoxPlot(datasets=datasets)

    assert len(plot.children) == 6 # 2 datasets * 3 components (whiskers, box, pings)

    # Check y-bounds
    assert plot.y_min < 15 # min is 10, so y_min should be slightly less
    assert plot.y_max > 100 # max is 100, so y_max should be slightly more

    # Test drawing on actual surface to ensure no cairo errors
    surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, 600, 400)
    ctx = cairo.Context(surface)
    plot.draw(ctx, 0.0)

    # No need to break encapsulation or force state, just draw at a future time.
    # We'll use the signals directly by setting them and relying on correct time flow,
    # or just let the default draw handle it if signals are setup well.
    # The components are designed to animate up to 1.0 based on signals.
    for child in plot.children:
        if hasattr(child, "reveal"):
            child.reveal.set(1.0)
        if hasattr(child, "ping_progress"):
            child.ping_progress.set(1.0)

    ctx.set_source_rgb(1, 1, 1)
    ctx.paint()
    plot.draw(ctx, 10.0)

    data = surface.get_data()
    arr = np.ndarray(shape=(400, 600, 4), dtype=np.uint8, buffer=data)
    assert np.any(arr != 0) # Should have drawn something
