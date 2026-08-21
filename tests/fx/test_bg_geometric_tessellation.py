import pytest
import numpy as np
import cairo

from vibmo.core.color import colors
from vibmo.fx.backgrounds.bg_geometric_tessellation import (
    VoronoiCellEvolution,
    PenroseTilingFlow,
    HexagonalHoneyGridPulse
)

def _create_mock_context():
    surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, 100, 100)
    return cairo.Context(surface)

def test_voronoi_cell_evolution_init():
    node = VoronoiCellEvolution(width=800, height=600, num_cells=10)
    assert node.width == 800
    assert node.height == 600
    assert node.num_cells == 10
    assert len(node.base_points) == 10
    assert len(node.boundary_points) == 8

def test_voronoi_cell_evolution_draw():
    node = VoronoiCellEvolution(width=800, height=600, num_cells=5)
    ctx = _create_mock_context()
    
    # Check that draw executes without exceptions
    try:
        node.draw(ctx, time=0.0)
        node.draw(ctx, time=1.5)
    except Exception as e:
        pytest.fail(f"VoronoiCellEvolution.draw raised an exception: {e}")

def test_penrose_tiling_flow_init():
    node = PenroseTilingFlow(width=800, height=600, generations=3)
    assert node.width == 800
    assert node.height == 600
    assert node.generations == 3

def test_penrose_tiling_flow_draw():
    node = PenroseTilingFlow(width=800, height=600, generations=2) # Low generations for faster test
    ctx = _create_mock_context()
    
    # Check that draw executes without exceptions
    try:
        node.draw(ctx, time=0.0)
        node.draw(ctx, time=2.0)
    except Exception as e:
        pytest.fail(f"PenroseTilingFlow.draw raised an exception: {e}")

def test_penrose_tiling_subdivide():
    node = PenroseTilingFlow(width=800, height=600, generations=1)
    
    import cmath
    # Create dummy triangles
    A, B, C = 0j, 1+0j, 0+1j
    triangles = [(0, A, B, C)]
    
    subdivided = node.subdivide(triangles)
    # A half-kite subdivides into 2 smaller triangles
    assert len(subdivided) == 2
    
    triangles = [(1, A, B, C)]
    subdivided = node.subdivide(triangles)
    # A half-dart subdivides into 3 smaller triangles
    assert len(subdivided) == 3

def test_hexagonal_honey_grid_pulse_init():
    node = HexagonalHoneyGridPulse(width=800, height=600, hex_radius=20)
    assert node.width == 800
    assert node.height == 600
    assert node.hex_radius == 20
    assert node.hex_width == pytest.approx(20 * np.sqrt(3))
    assert node.hex_height == 40

def test_hexagonal_honey_grid_pulse_draw():
    node = HexagonalHoneyGridPulse(width=200, height=200, hex_radius=50)
    ctx = _create_mock_context()
    
    # Check that draw executes without exceptions
    try:
        node.draw(ctx, time=0.0)
        node.draw(ctx, time=1.0)
    except Exception as e:
        pytest.fail(f"HexagonalHoneyGridPulse.draw raised an exception: {e}")
