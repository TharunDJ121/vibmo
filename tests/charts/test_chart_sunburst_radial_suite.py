import math
import pytest
from unittest.mock import MagicMock
import cairo

from vibmo.charts.chart_sunburst_radial_suite import (
    ExpandingRingArc,
    RadialSliceHighlight,
    BreadcrumbPathTrail,
    SunburstRadialHierarchy
)
from vibmo.core.color import colors


def test_expanding_ring_arc_geometry():
    arc = ExpandingRingArc(
        inner_radius=50.0,
        outer_radius=100.0,
        start_angle=0.0,
        end_angle=math.pi,
        fill=colors.CYAN
    )

    # Test local bounds
    bounds = arc.local_bounds(0.0)
    assert bounds == (-100.0, -100.0, 200.0, 200.0)

    # Test drawing
    surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, 200, 200)
    ctx = cairo.Context(surf)

    # We should intercept the paths to verify
    # A simple mock context
    class MockContext:
        def __init__(self):
            self.calls = []
        def new_path(self): self.calls.append("new_path")
        def arc(self, cx, cy, r, sa, ea): self.calls.append(("arc", cx, cy, r, sa, ea))
        def arc_negative(self, cx, cy, r, ea, sa): self.calls.append(("arc_negative", cx, cy, r, ea, sa))
        def close_path(self): self.calls.append("close_path")
        def save(self): self.calls.append("save")
        def restore(self): self.calls.append("restore")
        def set_source_rgba(self, r, g, b, a): self.calls.append(("rgba", r, g, b, a))
        def fill(self): self.calls.append("fill")
        def fill_preserve(self): self.calls.append("fill_preserve")
        def stroke(self): self.calls.append("stroke")
        def stroke_preserve(self): self.calls.append("stroke_preserve")
        def set_line_width(self, w): self.calls.append(("width", w))

    m_ctx = MockContext()
    arc.draw(m_ctx, 0.0)

    assert "new_path" in m_ctx.calls
    assert ("arc", 0, 0, 100.0, 0.0, math.pi) in m_ctx.calls
    assert ("arc_negative", 0, 0, 50.0, math.pi, 0.0) in m_ctx.calls
    assert "close_path" in m_ctx.calls


def test_expanding_ring_arc_expansion():
    arc = ExpandingRingArc(
        inner_radius=50.0,
        outer_radius=100.0,
        start_angle=0.0,
        end_angle=math.pi,
        expand_progress=0.5
    )

    class MockContext:
        def __init__(self):
            self.calls = []
        def __getattr__(self, name):
            def method(*args, **kwargs):
                self.calls.append((name, args))
            return method

    m_ctx = MockContext()
    arc.draw(m_ctx, 0.0)

    # Outer radius should be 50 + (100-50)*0.5 = 75
    arc_calls = [c for c in m_ctx.calls if c[0] == "arc"]
    assert arc_calls[0][1][2] == 75.0


def test_radial_slice_highlight():
    hl = RadialSliceHighlight(
        inner_radius=40.0,
        outer_radius=80.0,
        start_angle=0.0,
        end_angle=math.pi / 2,
        glow_width=10.0
    )

    bounds = hl.local_bounds(0.0)
    assert bounds == (-95.0, -95.0, 190.0, 190.0)

    class MockContext:
        def __init__(self):
            self.calls = []
        def __getattr__(self, name):
            def method(*args, **kwargs):
                self.calls.append((name, args))
            return method

    m_ctx = MockContext()
    hl.draw(m_ctx, 0.0)

    # Check for layered glow rendering
    stroke_calls = [c for c in m_ctx.calls if c[0] == "stroke_preserve"]
    assert len(stroke_calls) == 3


def test_breadcrumb_path_trail():
    trail = BreadcrumbPathTrail(path_items=["Company", "Engineering", "Frontend"])

    # Initial text value
    assert trail._text_node.text.get() == "Company > Engineering > Frontend"

    # Update path
    trail.update_path(["Company", "Engineering"])
    assert trail._text_node.text.get() == "Company > Engineering"


def test_sunburst_radial_hierarchy():
    data = {
        "name": "root",
        "children": [
            {
                "name": "child1",
                "value": 10,
                "children": [
                    {"name": "leaf1", "value": 4},
                    {"name": "leaf2", "value": 6}
                ]
            },
            {
                "name": "child2",
                "value": 10
            }
        ]
    }

    sunburst = SunburstRadialHierarchy(data=data, center_radius=50.0, ring_width=30.0)

    # Root has total value 20 (child1=10, child2=10)
    # Total arcs expected: child1, child2, leaf1, leaf2 => 4 arcs
    assert len(sunburst._arcs) == 4

    # check depths and radii
    # child1 and child2 are depth 1 -> inner=50, outer=80
    c1 = sunburst._arcs[0]
    c2 = sunburst._arcs[3] # Since it adds child1, then leaf1, leaf2, then child2

    assert c1.inner_radius.get() == 50.0
    assert c1.outer_radius.get() == 80.0

    leaf1 = sunburst._arcs[1]
    assert leaf1.inner_radius.get() == 80.0
    assert leaf1.outer_radius.get() == 110.0

    # Check angle splits
    # child1 value 10 -> sweep = pi
    assert math.isclose(c1.end_angle.get() - c1.start_angle.get(), math.pi, rel_tol=1e-5)

    # leaf1 value 4 -> sweep = (4/10) * pi = 0.4*pi
    assert math.isclose(leaf1.end_angle.get() - leaf1.start_angle.get(), 0.4 * math.pi, rel_tol=1e-5)
