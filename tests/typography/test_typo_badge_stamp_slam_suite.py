import pytest
import cairo
import math

from vibmo.typography.kinetic.typo_badge_stamp_slam_suite import (
    RubberStampTitleSlam,
    DustPuffShockwave,
    InkedTextureMask,
    SpringReboundSettling
)
from vibmo.core.color import colors


def test_slam_physics_scale_curve():
    # Test slam scale curve
    slam_node = RubberStampTitleSlam(text="REJECTED")
    
    assert slam_node.scale.get(0.0) == (3.0, 3.0)
    
    # Run animation
    slam_node.slam(delay=0.1, duration=0.6)
    
    # At t=0.0, scale is still 3.0
    assert slam_node.scale.get(0.0) == (3.0, 3.0)
    
    # At t=0.1 (delay over), scale should just start to move or be 3.0
    assert slam_node.scale.get(0.1) == (3.0, 3.0)
    
    # At t=0.4 (delay 0.1 + duration 0.3), scale should be 1.0 (since we animate for duration*0.5 in the code, which is 0.3s)
    assert slam_node.scale.get(0.4) == (1.0, 1.0)
    
    # Scale should be smoothly interpolating
    mid_scale = slam_node.scale.get(0.25)
    assert 1.0 < mid_scale[0] < 3.0


def test_particle_burst_logic():
    shockwave = DustPuffShockwave(particle_count=10)
    
    assert shockwave.progress.get(0.0) == 0.0
    
    shockwave.burst(duration=0.5, delay=0.1)
    
    assert shockwave.progress.get(0.0) == 0.0
    assert shockwave.progress.get(0.1) == 0.0
    assert shockwave.progress.get(0.6) == 1.0
    
    prog_mid = shockwave.progress.get(0.35)
    assert 0.0 < prog_mid < 1.0
    
    assert len(shockwave.particles) == 10


def test_cairo_drawing_without_errors():
    surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, 200, 200)
    ctx = cairo.Context(surface)
    
    # Setup node and start animation
    slam_node = RubberStampTitleSlam(text="TESTING")
    slam_node.slam(delay=0.0, duration=0.5)
    
    # Draw at start
    slam_node.draw(ctx, 0.0)
    
    # Draw at mid point
    slam_node.draw(ctx, 0.25)
    
    # Draw at end
    slam_node.draw(ctx, 1.0)

    # If we get here without exceptions, drawing is fundamentally sound

