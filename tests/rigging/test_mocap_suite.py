"""
Unit tests for 2D FABRIK IK and MocapStickFigure character puppetry.
"""

import pytest
import cairo
from vibmo.rigging.mocap import FabrikSolver2D, MocapStickFigure, MocapLibrary
from vibmo.core.color import colors


def test_fabrik_solver_2d():
    origin = (0.0, 0.0)
    target = (80.0, 60.0)
    l1 = 50.0
    l2 = 60.0

    j0, j1, j2 = FabrikSolver2D.solve_2segment(origin, target, l1, l2)
    assert j0 == (0.0, 0.0)
    assert j2 == (80.0, 60.0)

    # Verify bone lengths
    d1 = (j1[0] - j0[0]) ** 2 + (j1[1] - j0[1]) ** 2
    assert abs(d1 - l1 * l1) < 1.0


def test_mocap_stick_figure_render():
    surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, 1920, 1080)
    ctx = cairo.Context(surface)

    char = MocapStickFigure(action="walk", action_speed=1.2, boil=True)
    char._render_self(ctx, t=0.5)

    char_dance = MocapStickFigure(action="dance", action_speed=1.0)
    char_dance._render_self(ctx, t=1.2)

    char_ik = MocapStickFigure(action="wave")
    char_ik.reach_left((120.0, -40.0))
    char_ik._render_self(ctx, t=0.8)
