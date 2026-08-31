import pytest
import cairo
from vibmo.product.ai.ui_matrix_comparison_suite import (
    InteractiveFeatureMatrix,
    CompetitorComparisonRow,
    TooltipFeatureExplanation,
    StickyHeaderColumn,
    FeatureComparisonMatrix,
    CheckmarkCell,
)

def test_interactive_feature_matrix():
    matrix = InteractiveFeatureMatrix(features=[{"name": "Fast", "values": [True, True, False, False]}])
    surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, 800, 500)
    ctx = cairo.Context(surface)
    matrix.draw(ctx, time=0.0)
    assert len(matrix.rows) == 1

def test_competitor_comparison_row_striped():
    row = CompetitorComparisonRow(feature="SSO Auth", values=[True, True, False])
    surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, 600, 50)
    ctx = cairo.Context(surface)
    row.draw(ctx, time=0.0)
    assert row.feature == "SSO Auth"

def test_tooltip_feature_explanation():
    tip = TooltipFeatureExplanation(text="Enterprise single sign-on integration")
    surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, 300, 100)
    ctx = cairo.Context(surface)
    tip.draw(ctx, time=0.0)
    assert tip.text == "Enterprise single sign-on integration"

def test_sticky_header_column():
    col = StickyHeaderColumn(headers=["Feature", "Starter", "Pro", "Enterprise"])
    surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, 800, 60)
    ctx = cairo.Context(surface)
    col.draw(ctx, time=0.0)
    assert len(col.headers) == 4
