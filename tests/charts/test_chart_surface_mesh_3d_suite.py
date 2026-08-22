import math
import pytest
from unittest.mock import MagicMock
from vibmo.core.color import Color
from vibmo.charts.chart_surface_mesh_3d_suite import ElevationColorGradient, CameraRotationRig, WireframeContourGrid, Animated3DSurfaceMesh

def test_elevation_color_gradient():
    valley = Color(0, 0, 1)
    plains = Color(0, 1, 0)
    peaks = Color(1, 1, 1)

    grad = ElevationColorGradient(valley=valley, plains=plains, peaks=peaks, min_z=-1.0, max_z=1.0)

    c_valley = grad.get_color(-1.0)
    # Check if valley is close
    assert abs(c_valley.b - 1.0) < 0.05
    assert abs(c_valley.r - 0.0) < 0.05
    assert abs(c_valley.g - 0.0) < 0.05

    c_plains = grad.get_color(0.0)
    assert abs(c_plains.g - 1.0) < 0.05
    assert abs(c_plains.r - 0.0) < 0.05
    assert abs(c_plains.b - 0.0) < 0.05

    c_peaks = grad.get_color(1.0)
    assert abs(c_peaks.r - 1.0) < 0.05
    assert abs(c_peaks.g - 1.0) < 0.05
    assert abs(c_peaks.b - 1.0) < 0.05

    # Check out of bounds clamping
    c_under = grad.get_color(-2.0)
    assert abs(c_under.b - 1.0) < 0.05

def test_camera_rotation_rig():
    rig = CameraRotationRig(azimuth=0.0, elevation=0.0, scale=1.0)
    # Looking down Z axis? If el=0, az=0:
    # x_rot = x, y_rot = y
    # y_rot2 = y, z_rot2 = z
    # screen_x = x, screen_y = -y

    x, y, z = rig.project(1.0, 2.0, 3.0)
    assert pytest.approx(x) == 1.0
    assert pytest.approx(y) == -2.0
    assert pytest.approx(z) == 3.0

    rig.elevation.set(math.pi/2) # 90 degrees
    # y_rot2 = y*0 - z*1 = -3.0
    # screen_y = 3.0
    # z_rot2 = y*1 + z*0 = 2.0
    x, y, z = rig.project(1.0, 2.0, 3.0)
    assert pytest.approx(x) == 1.0
    assert pytest.approx(y) == 3.0
    assert pytest.approx(z) == 2.0

class MockCairoContext(MagicMock):
    pass

def test_animated_3d_surface_mesh():
    rig = CameraRotationRig(azimuth=math.pi/4, elevation=math.pi/6, scale=10.0)
    mesh = Animated3DSurfaceMesh(rig=rig, resolution=2)
    ctx = MockCairoContext()

    mesh.draw(ctx, 0.0)

    # 2x2 resolution means 2*2=4 faces
    # Each face calls fill_preserve and stroke
    assert ctx.fill_preserve.call_count == 4
    assert ctx.stroke.call_count == 4

def test_wireframe_contour_grid():
    rig = CameraRotationRig(azimuth=math.pi/4, elevation=math.pi/6, scale=10.0)
    grid = WireframeContourGrid(rig=rig, grid_steps=2)
    ctx = MockCairoContext()

    grid.draw(ctx, 0.0)
    # 2 z-levels, each level has (steps+1) X lines and (steps+1) Y lines
    # 2 * (3 + 3) = 12 lines total, so 12 move_to/line_to pairs
    # One stroke per z-level? No, the code does one stroke at the end.
    assert ctx.stroke.call_count == 1
    assert ctx.move_to.call_count == 12
    assert ctx.line_to.call_count == 12
