import pytest
import cairo
from unittest.mock import MagicMock
from vibmo.typography.kinetic.typo_matrix_code_rain_suite import (
    MatrixRainTypography,
    PhosphorTrailDecay,
    HeadlineConsolidation,
    GlyphMatrixSubText,
)
from vibmo.core.color import colors, Color

def test_matrix_rain_typography():
    node = MatrixRainTypography(target_text="MATRIX", font_size=24.0, drop_speed=150.0)
    
    # Test initialization
    assert node.target_text == "MATRIX"
    assert node.font_size == 24.0
    assert len(node.drops) == len("MATRIX")
    
    # Test drawing without consolidation
    surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, 200, 200)
    ctx = cairo.Context(surface)
    
    node.draw(ctx, time=1.0)
    
    # Test drawing with consolidation
    node.consolidated.set(0.5)
    node.draw(ctx, time=2.0)
    
    node.consolidated.set(1.0)
    node.draw(ctx, time=3.0)

def test_phosphor_trail_decay():
    node = PhosphorTrailDecay(text="NEO", trail_length=3, font_size=30.0)
    
    assert node.text == "NEO"
    assert node.trail_length == 3
    
    surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, 200, 200)
    ctx = cairo.Context(surface)
    
    # Should draw leading glyph and 3 trails
    node.draw(ctx, time=1.0)

def test_headline_consolidation():
    node = HeadlineConsolidation(text="SYSTEM", font_size=40.0)
    
    assert node.text == "SYSTEM"
    
    surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, 200, 200)
    ctx = cairo.Context(surface)
    
    # Initial state, prog=0, draws nothing
    node.draw(ctx, time=0.0)
    
    # Partial progress
    node.progress.set(0.5)
    node.draw(ctx, time=1.0)
    
    # Full progress
    node.progress.set(1.0)
    node.draw(ctx, time=2.0)

def test_glyph_matrix_subtext():
    node = GlyphMatrixSubText(text="ACCESS DENIED", font_size=20.0, decode_speed=5.0)
    
    assert node.text == "ACCESS DENIED"
    assert node.decode_speed == 5.0
    
    surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, 400, 100)
    ctx = cairo.Context(surface)
    
    # t=0, fully scrambled
    node.draw(ctx, time=0.0)
    
    # t=1.0, partially decoded (5 chars)
    node.draw(ctx, time=1.0)
    
    # t=3.0, fully decoded (15 > 13 chars)
    node.draw(ctx, time=3.0)
