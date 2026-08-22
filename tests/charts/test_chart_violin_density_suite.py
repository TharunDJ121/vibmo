import math
import numpy as np
import pytest
import cairo
from scipy.stats import gaussian_kde
from vibmo.core.color import Color, colors
from vibmo.charts.chart_violin_density_suite import (
    ProbabilityDensityKernel,
    MedianQuartileMarker,
    OutlierJitterDots,
    ViolinDistributionPlot,
)

class MockContext:
    def __init__(self):
        self.calls = []
        self._line_width = 1.0

    def save(self):
        self.calls.append(("save",))

    def restore(self):
        self.calls.append(("restore",))

    def new_path(self):
        self.calls.append(("new_path",))

    def move_to(self, x, y):
        self.calls.append(("move_to", x, y))

    def line_to(self, x, y):
        self.calls.append(("line_to", x, y))

    def close_path(self):
        self.calls.append(("close_path",))

    def arc(self, xc, yc, radius, angle1, angle2):
        self.calls.append(("arc", xc, yc, radius, angle1, angle2))

    def fill(self):
        self.calls.append(("fill",))

    def fill_preserve(self):
        self.calls.append(("fill_preserve",))

    def stroke(self):
        self.calls.append(("stroke",))

    def set_source_rgba(self, r, g, b, a):
        self.calls.append(("set_source_rgba", r, g, b, a))

    def set_line_width(self, width):
        self._line_width = width
        self.calls.append(("set_line_width", width))

    def clip(self):
        self.calls.append(("clip",))


def test_probability_density_kernel_math():
    data = [1.0, 2.0, 2.0, 3.0, 3.0, 3.0, 4.0, 4.0, 5.0]
    pdk = ProbabilityDensityKernel(data=data, width=100.0, height=300.0)

    assert pdk.min_val == 1.0
    assert pdk.max_val == 5.0

    # y_samples should cover the range linearly
    assert len(pdk.y_samples) == 100
    assert pdk.y_samples[0] == 1.0
    assert pdk.y_samples[-1] == 5.0

    # KDE maximum density point should be roughly at the mode (3.0)
    max_idx = np.argmax(pdk.densities)
    assert 2.5 < pdk.y_samples[max_idx] < 3.5

    # densities should be non-negative
    assert np.all(pdk.densities >= 0)

    # normalized_densities max should be exactly 1.0
    assert pytest.approx(np.max(pdk.normalized_densities)) == 1.0

def test_probability_density_kernel_cairo_drawing():
    data = [1.0, 2.0, 3.0]
    pdk = ProbabilityDensityKernel(data=data, width=100.0, height=300.0)

    ctx = MockContext()
    pdk.draw(ctx, time=0.0)

    ops = [call[0] for call in ctx.calls]
    assert "save" in ops
    assert "new_path" in ops
    assert "line_to" in ops
    assert "close_path" in ops
    assert "fill_preserve" in ops
    assert "stroke" in ops
    assert "restore" in ops

    # test symmetric math by inspecting line_to calls
    line_to_calls = [call for call in ctx.calls if call[0] == "line_to"]
    assert len(line_to_calls) == 200 # 100 right, 100 left

    # First half are right side (x > 0 or 0), second half are left side (x < 0 or 0)
    right_x_vals = [c[1] for c in line_to_calls[:100]]
    left_x_vals = [c[1] for c in line_to_calls[100:]]

    # Verify all right X are non-negative, and left X are non-positive
    assert all(x >= -1e-7 for x in right_x_vals)
    assert all(x <= 1e-7 for x in left_x_vals)


def test_median_quartile_marker():
    data = [1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0]
    mqm = MedianQuartileMarker(data=data, width=10.0, height=300.0)

    assert mqm.min_val == 1.0
    assert mqm.max_val == 7.0
    assert mqm.median == 4.0
    assert mqm.q1 == 2.5
    assert mqm.q3 == 5.5

    ctx = MockContext()
    mqm.draw(ctx, time=0.0)

    ops = [call[0] for call in ctx.calls]
    assert "save" in ops
    assert "move_to" in ops
    assert "line_to" in ops
    assert "stroke" in ops
    assert "arc" in ops
    assert "fill" in ops
    assert "restore" in ops

    # We expect an arc to be drawn for the median point
    arc_calls = [call for call in ctx.calls if call[0] == "arc"]
    assert len(arc_calls) == 1
    # Check y-coord of median arc.
    # Val range is 6.0. Median is 4.0. Fraction is (4-1)/6 = 0.5.
    # get_y(4.0) = h - 0.5 * h = 300 - 150 = 150
    assert arc_calls[0][2] == 150.0 # yc

def test_outlier_jitter_dots():
    data = [1.0, 2.0, 3.0]
    ojd = OutlierJitterDots(data=data, width=60.0, height=300.0, jitter_seed=123)

    assert len(ojd.jitters) == 3
    assert all(-0.5 <= j <= 0.5 for j in ojd.jitters)

    ctx = MockContext()
    ojd.draw(ctx, time=0.0)

    arc_calls = [call for call in ctx.calls if call[0] == "arc"]
    assert len(arc_calls) == 3 # 3 dots

def test_violin_distribution_plot_composition():
    d1 = [1.0, 2.0, 3.0]
    d2 = [2.0, 3.0, 4.0, 5.0]

    vdp = ViolinDistributionPlot(datasets=[d1, d2], category_spacing=200.0)

    # Total data range is [1.0, 5.0]
    assert vdp.global_min == 1.0
    assert vdp.global_max == 5.0

    # Check it generated 2 child violin groups
    assert len(vdp.children) == 2

    v1 = vdp.children[0]
    v2 = vdp.children[1]

    assert v1.position.get()[0] == -100.0 # start_x = - (2-1)*200 / 2 = -100.0
    assert v2.position.get()[0] == 100.0

    # Check children of violin group (PDK, Box, Jitter)
    # 3 children because show_jitter=True by default
    assert len(v1.children) == 3
    assert isinstance(v1.children[0], ProbabilityDensityKernel)
    assert isinstance(v1.children[1], OutlierJitterDots)
    assert isinstance(v1.children[2], MedianQuartileMarker)

    # Verify global bounds were passed down
    assert v1.children[0].scale_min == 1.0
    assert v1.children[0].scale_max == 5.0

    # Rendering should not crash
    surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, 400, 400)
    ctx = cairo.Context(surface)
    try:
        vdp.draw(ctx, time=0.0)
    except Exception as e:
        pytest.fail(f"draw() raised {type(e).__name__} unexpectedly: {str(e)}")

def test_pdk_empty_data():
    pdk = ProbabilityDensityKernel(data=[])
    ctx = MockContext()
    pdk.draw(ctx, time=0.0)
    ops = [call[0] for call in ctx.calls]
    # No drawing operations if data is empty (only super draw could run, but since it's an empty node, maybe no path)
    # The draw method returns early
    assert "save" not in ops

def test_violin_plot_handles_zero_variance():
    # Test identical data points
    vdp = ViolinDistributionPlot(datasets=[[2.0, 2.0, 2.0]])
    surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, 400, 400)
    ctx = cairo.Context(surface)
    # It has a val_range == 0, which gets fallback to 1.0 in components to avoid ZeroDivisionError
    vdp.draw(ctx, time=0.0)
