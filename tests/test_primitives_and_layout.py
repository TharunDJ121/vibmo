"""
Unit tests for vector primitives, SVG paths, trim paths, gradients, and flexbox auto-layout.
"""

import pytest
from vibmo.primitives.rect import Rect, RoundedRect
from vibmo.primitives.circle import Circle, Ellipse
from vibmo.primitives.polygon import Polygon, Star, Line
from vibmo.primitives.path import Path
from vibmo.layout.container import FlexContainer, AutoResizeBox
from vibmo.core.color import Color, LinearGradient, RadialGradient, ColorStop, colors


def test_rect_and_rounded_rect():
    r = Rect(width=200, height=100, corner_radius=12.0, fill=colors.INDIGO)
    bx, by, bw, bh = r.local_bounds(0.0)
    assert bw == 200
    assert bh == 100

    rr = RoundedRect(width=150, height=80, corner_radius=20.0)
    assert float(rr.corner_radius.get(0.0)) == 20.0


def test_circle_and_ellipse():
    c = Circle(radius=50.0, fill=colors.CYAN)
    bx, by, bw, bh = c.local_bounds(0.0)
    assert bw == 100
    assert bh == 100

    el = Ellipse(radius_x=80.0, radius_y=40.0)
    _, _, ew, eh = el.local_bounds(0.0)
    assert ew == 160
    assert eh == 80


def test_polygon_star_and_line():
    poly = Polygon(points=[(0, 0), (100, 0), (50, 80)], fill=colors.AMBER)
    bx, by, bw, bh = poly.local_bounds(0.0)
    assert bw > 0 and bh > 0

    star = Star(points=5, outer_radius=50, inner_radius=20)
    _, _, sw, sh = star.local_bounds(0.0)
    assert sw > 0 and sh > 0

    line = Line(start=(0, 0), end=(200, 100), stroke_width=4.0)
    _, _, lw, lh = line.local_bounds(0.0)
    assert lw >= 200
    assert lh >= 100


def test_svg_path_and_trim():
    svg_d = "M 10 10 C 20 20, 40 20, 50 10"
    path = Path(d=svg_d, stroke=colors.WHITE, stroke_width=2.0)
    assert path.d == svg_d

    # Animate trim_end
    action = path.trim_end.to(1.0, duration=1.0)
    assert action is not None


def test_flex_container_row_column():
    # Row layout
    row = FlexContainer(direction="row", gap=10.0, padding=20.0)
    c1 = Rect(width=50, height=50)
    c2 = Rect(width=50, height=50)
    row.add(c1, c2)

    # Compute layout
    w, h = row.compute_layout(0.0)
    assert w > 100
    assert h > 50



def test_gradients_linear_and_radial():
    lin = LinearGradient(
        start=(0.0, 0.0),
        end=(1.0, 1.0),
        stops=[
            ColorStop(0.0, colors.INDIGO),
            ColorStop(1.0, colors.CYAN),
        ],
    )
    assert len(lin.stops) == 2

    rad = RadialGradient(
        center=(0.5, 0.5),
        radius=0.5,
        stops=[
            ColorStop(0.0, colors.WHITE),
            ColorStop(1.0, colors.TRANSPARENT),
        ],
    )
    assert rad.radius == 0.5
