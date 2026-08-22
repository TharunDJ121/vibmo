import pytest
import cairo
from vibmo.core.color import colors
from vibmo.typography.kinetic.typo_elastic_squash_bounce_suite import (
    ElasticSquashBounceTitle,
    RhythmicImpactPumping,
    JellyMorphTypography,
    ComicSpeedLines,
)
from unittest.mock import MagicMock


def create_cairo_context():
    surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, 100, 100)
    return cairo.Context(surface)


class TestElasticSquashBounceTitle:
    def test_volume_conservation(self):
        title = ElasticSquashBounceTitle(text="BOUNCE", font_size=50)
        title.bounce_progress.set(0.6) # First impact wobble
        
        mock_ctx = MagicMock()
        title.draw(mock_ctx, time=0.6)
        
        # Check that scale was called.
        scale_calls = [call for call in mock_ctx.mock_calls if call[0] == 'scale']
        assert len(scale_calls) > 0
        scale_args = scale_calls[0][1]
        scale_x, scale_y = scale_args
        
        # Check volume conservation ScaleX * ScaleY == 1.0 (with slight tolerance)
        assert abs(scale_x * scale_y - 1.0) < 1e-5

    def test_cairo_drawing(self):
        title = ElasticSquashBounceTitle(text="BOUNCE", font_size=50)
        ctx = create_cairo_context()
        title.draw(ctx, time=0.5)
        # Verify no exceptions during real cairo draw

    def test_bounce_in_generator(self):
        title = ElasticSquashBounceTitle(text="BOUNCE")
        action = title.bounce_in(duration=1.0)
        assert action is not None
        assert title.bounce_progress.get(0.0) == 0.0


class TestRhythmicImpactPumping:
    def test_cairo_drawing(self):
        title = RhythmicImpactPumping(text="PUMP", bpm=120)
        ctx = create_cairo_context()
        title.draw(ctx, time=0.5)


class TestJellyMorphTypography:
    def test_volume_conservation(self):
        title = JellyMorphTypography(text="JELLY")
        title.progress.set(0.5)
        
        mock_ctx = MagicMock()
        title.draw(mock_ctx, time=0.5)
        
        scale_calls = [call for call in mock_ctx.mock_calls if call[0] == 'scale']
        assert len(scale_calls) > 0
        scale_args = scale_calls[0][1]
        scale_x, scale_y = scale_args
        
        assert abs(scale_x * scale_y - 1.0) < 1e-5

    def test_cairo_drawing(self):
        title = JellyMorphTypography(text="JELLY")
        ctx = create_cairo_context()
        title.draw(ctx, time=0.5)


class TestComicSpeedLines:
    def test_cairo_drawing(self):
        lines = ComicSpeedLines(radius=50, line_count=10)
        ctx = create_cairo_context()
        # Progress 0 won't draw anything, so set to 0.5
        lines.progress.set(0.5)
        lines.draw(ctx, time=0.5)
        
    def test_burst_generator(self):
        lines = ComicSpeedLines()
        action = lines.burst(duration=0.5)
        assert action is not None
