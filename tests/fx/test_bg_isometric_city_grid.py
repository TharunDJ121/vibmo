import pytest
import cairo
import math
from vibmo.fx.backgrounds.bg_isometric_city_grid import (
    IsometricCityGridBackdrop,
    PulsingDataHighways,
    ServerRackMatrixBackdrop
)

def test_isometric_city_grid_backdrop():
    node = IsometricCityGridBackdrop(grid_size=5, cell_size=30)
    assert node.grid_size == 5
    assert node.cell_size == 30
    
    surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, 100, 100)
    ctx = cairo.Context(surface)
    
    # Save the original matrix to check transform later
    orig_matrix = ctx.get_matrix()
    
    node.draw(ctx, time=0.0)
    
    # Verify context state is restored correctly
    assert ctx.get_matrix() == orig_matrix

def test_pulsing_data_highways():
    node = PulsingDataHighways(grid_size=5, cell_size=30)
    assert node.grid_size == 5
    assert node.cell_size == 30
    
    surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, 100, 100)
    ctx = cairo.Context(surface)
    
    orig_matrix = ctx.get_matrix()
    
    node.draw(ctx, time=0.0)
    node.draw(ctx, time=1.0)
    
    assert ctx.get_matrix() == orig_matrix

def test_server_rack_matrix_backdrop():
    node = ServerRackMatrixBackdrop(grid_size=5, cell_size=30)
    assert node.grid_size == 5
    assert node.cell_size == 30
    
    surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, 100, 100)
    ctx = cairo.Context(surface)
    
    orig_matrix = ctx.get_matrix()
    
    node.draw(ctx, time=0.0)
    
    assert ctx.get_matrix() == orig_matrix

def test_isometric_transform_applied():
    """Verify the isometric transform is correctly generated."""
    node = IsometricCityGridBackdrop()
    surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, 100, 100)
    ctx = cairo.Context(surface)
    
    node._apply_isometric_transform(ctx)
    matrix = ctx.get_matrix()
    
    # It should have a scale of (1, 0.5) and rotation of pi/4
    # The matrix elements: [xx, yx, xy, yy, x0, y0]
    # Rotate pi/4:
    # cos(pi/4) = 0.7071
    # sin(pi/4) = 0.7071
    #
    # Matrix multiply scale and rotate:
    # [1 0]     [cos(pi/4)  sin(pi/4)]
    # [0 0.5]   [-sin(pi/4) cos(pi/4)]
    
    expected_xx = math.cos(math.pi / 4)
    expected_yx = math.sin(math.pi / 4) * 0.5
    expected_xy = -math.sin(math.pi / 4)
    expected_yy = math.cos(math.pi / 4) * 0.5
    
    assert math.isclose(matrix.xx, expected_xx, rel_tol=1e-4)
    assert math.isclose(matrix.yx, expected_yx, rel_tol=1e-4)
    assert math.isclose(matrix.xy, expected_xy, rel_tol=1e-4)
    assert math.isclose(matrix.yy, expected_yy, rel_tol=1e-4)

