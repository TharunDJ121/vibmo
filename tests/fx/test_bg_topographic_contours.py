import pytest
import cairo
import numpy as np
from vibmo.fx.backgrounds.bg_topographic_contours import AnimatedTopographicContours, BathymetricMapBackdrop, RadarElevationSweep

def _create_mock_context():
    surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, 100, 100)
    return cairo.Context(surface), surface

def test_animated_topographic_contours():
    node = AnimatedTopographicContours(width=100, height=100, levels=3, grid_resolution=10)
    ctx, surface = _create_mock_context()
    
    # Test drawing at time 0
    node.draw(ctx, time=0.0)
    data_t0 = np.ndarray(shape=(100, 100, 4), dtype=np.uint8, buffer=surface.get_data()).copy()
    
    # Assert something was drawn
    assert np.any(data_t0 > 0)
    
    # Clear and test at time 1.0
    ctx.set_operator(cairo.Operator.CLEAR)
    ctx.paint()
    ctx.set_operator(cairo.Operator.OVER)
    
    node.draw(ctx, time=10.0)
    data_t1 = np.ndarray(shape=(100, 100, 4), dtype=np.uint8, buffer=surface.get_data()).copy()
    
    # Assert state has progressed (time difference causes visual change)
    assert not np.array_equal(data_t0, data_t1)

def test_bathymetric_map_backdrop():
    node = BathymetricMapBackdrop(width=100, height=100, levels=2, grid_resolution=10)
    ctx, surface = _create_mock_context()
    
    node.draw(ctx, time=0.0)
    data = np.ndarray(shape=(100, 100, 4), dtype=np.uint8, buffer=surface.get_data()).copy()
    
    # Assert it filled something (the base bg covers everything)
    assert np.any(data > 0)

def test_radar_elevation_sweep():
    node = RadarElevationSweep(width=100, height=100, levels=2, grid_resolution=10, rpm=60)
    ctx, surface = _create_mock_context()
    
    # Render at t=0
    node.draw(ctx, time=0.0)
    data_t0 = np.ndarray(shape=(100, 100, 4), dtype=np.uint8, buffer=surface.get_data()).copy()
    assert np.any(data_t0 > 0)
    
    # Render at t=0.25 (1/4 rotation since rpm is 60 -> 1 rev/sec)
    ctx.set_operator(cairo.Operator.CLEAR)
    ctx.paint()
    ctx.set_operator(cairo.Operator.OVER)
    
    node.draw(ctx, time=0.25)
    data_t025 = np.ndarray(shape=(100, 100, 4), dtype=np.uint8, buffer=surface.get_data()).copy()
    
    # Due to sweep rotation, frames should not be identical
    assert not np.array_equal(data_t0, data_t025)

