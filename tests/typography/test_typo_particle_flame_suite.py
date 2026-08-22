import pytest
import cairo
import math

from vibmo.typography.kinetic.typo_particle_flame_suite import (
    _extract_text_points,
    ParticleFlameText,
    DisintegratingEmbers,
    IgnitionSparkBurst,
    SmokeDissipateHeading
)
from vibmo.core.vector import Vector2D

def test_extract_text_points():
    surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, 100, 100)
    ctx = cairo.Context(surface)
    
    # Use density=1 to get maximum points for testing
    points = _extract_text_points(ctx, "Test", 0, 50, "sans-serif", 32, density=1)
    
    # We should get a list of points representing the text outline
    assert isinstance(points, list)
    if len(points) > 0:
        assert isinstance(points[0], tuple)
        assert len(points[0]) == 2
        assert isinstance(points[0][0], float)

def test_particle_flame_text():
    node = ParticleFlameText("FIRE")
    surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, 100, 100)
    ctx = cairo.Context(surface)

    # Initially draw, should extract points
    node.draw(ctx, 0.0)
    assert node._initialized is True
    
    # Progress > 0 should draw flames
    node.progress.set(0.5)
    node.draw(ctx, 0.5)

def test_disintegrating_embers():
    node = DisintegratingEmbers("ASH", wind_dir=Vector2D(10, 0))
    surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, 100, 100)
    ctx = cairo.Context(surface)

    node.draw(ctx, 0.0)
    assert node._initialized is True
    assert len(node._ember_speeds) == len(node._embers)

    node.disintegrate_progress.set(0.5)
    node.draw(ctx, 0.5)
    
    node.disintegrate_progress.set(1.0)
    node.draw(ctx, 1.0)

def test_ignition_spark_burst():
    node = IgnitionSparkBurst("SPARK")
    surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, 100, 100)
    ctx = cairo.Context(surface)

    node.draw(ctx, 0.0)
    assert node._initialized is True
    assert len(node._spark_dirs) == len(node._sparks) * 2

    node.burst_progress.set(0.5)
    node.draw(ctx, 0.5)

def test_smoke_dissipate_heading():
    node = SmokeDissipateHeading("SMOKE")
    surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, 100, 100)
    ctx = cairo.Context(surface)

    node.draw(ctx, 0.0)
    assert node._initialized is True
    assert len(node._smoke_params) == len(node._smoke_points)

    node.dissipate_progress.set(0.5)
    node.draw(ctx, 0.5)
    
    node.dissipate_progress.set(1.0)
    node.draw(ctx, 1.0)
