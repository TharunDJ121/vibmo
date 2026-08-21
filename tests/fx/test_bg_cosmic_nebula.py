import pytest
import math
from unittest.mock import MagicMock
from vibmo.fx.backgrounds.bg_cosmic_nebula import (
    CosmicNebulaBackdrop,
    StarfieldWarpDrift,
    ConstellationGrid
)

def test_cosmic_nebula_instantiation():
    node = CosmicNebulaBackdrop(width=800, height=600, seed=1)
    assert node.width == 800
    assert node.height == 600
    assert len(node.clouds) == 12

def test_cosmic_nebula_drawing():
    node = CosmicNebulaBackdrop(width=100, height=100)
    mock_ctx = MagicMock()
    # Test 100% opacity
    node.draw(mock_ctx, time=0.0)
    assert mock_ctx.save.called
    assert mock_ctx.restore.called
    assert mock_ctx.fill.called

    # Test 0% opacity (no drawing)
    mock_ctx.reset_mock()
    node.opacity.set(0.0)
    node.draw(mock_ctx, time=0.0)
    assert not mock_ctx.save.called

def test_starfield_warp_drift_instantiation():
    node = StarfieldWarpDrift(width=800, height=600, num_stars=50, seed=2)
    assert node.width == 800
    assert node.height == 600
    assert len(node.stars) == 50

def test_starfield_warp_drift_drawing():
    node = StarfieldWarpDrift(width=100, height=100, num_stars=10)
    mock_ctx = MagicMock()
    node.draw(mock_ctx, time=1.0)
    assert mock_ctx.save.called
    assert mock_ctx.restore.called
    assert mock_ctx.stroke.called

def test_starfield_warp_drift_time_dependency():
    node = StarfieldWarpDrift(width=100, height=100, num_stars=10, seed=1)
    
    mock_ctx_1 = MagicMock()
    node.draw(mock_ctx_1, time=0.0)
    call_args_1 = mock_ctx_1.line_to.call_args_list
    
    mock_ctx_2 = MagicMock()
    node.draw(mock_ctx_2, time=1.0)
    call_args_2 = mock_ctx_2.line_to.call_args_list
    
    assert call_args_1 != call_args_2, "Star positions should change over time"


def test_constellation_grid_instantiation():
    node = ConstellationGrid(width=800, height=600, num_points=25, max_distance=100.0, seed=3)
    assert node.width == 800
    assert node.height == 600
    assert node.max_distance == 100.0
    assert len(node.points) == 25

def test_constellation_grid_drawing():
    node = ConstellationGrid(width=100, height=100, num_points=10)
    mock_ctx = MagicMock()
    node.draw(mock_ctx, time=2.0)
    assert mock_ctx.save.called
    assert mock_ctx.restore.called
    assert mock_ctx.fill.called

def test_constellation_grid_time_dependency():
    node = ConstellationGrid(width=100, height=100, num_points=10, seed=1)
    
    mock_ctx_1 = MagicMock()
    node.draw(mock_ctx_1, time=0.0)
    call_args_1 = mock_ctx_1.arc.call_args_list
    
    mock_ctx_2 = MagicMock()
    node.draw(mock_ctx_2, time=1.0)
    call_args_2 = mock_ctx_2.arc.call_args_list
    
    assert call_args_1 != call_args_2, "Constellation points should change over time"

