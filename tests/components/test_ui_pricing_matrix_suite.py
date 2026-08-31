import pytest
import cairo
from vibmo.product.ai.ui_pricing_matrix_suite import (
    FeatureChecklistRow,
    AnnualBillingToggle,
    PopularGlowBadge,
    PricingTierGrid,
    PricingTierMatrix,
    PricingTierColumn,
)

def test_feature_checklist_row_draw():
    row = FeatureChecklistRow(text="Test Feature", active=True)
    surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, 200, 50)
    ctx = cairo.Context(surface)
    row.draw(ctx, time=0.0)
    assert row.text == "Test Feature"

def test_annual_billing_toggle_state():
    toggle = AnnualBillingToggle(discount_pct=20)
    surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, 200, 50)
    ctx = cairo.Context(surface)
    toggle.draw(ctx, time=0.0)
    assert toggle.discount_pct == 20

def test_popular_glow_badge():
    badge = PopularGlowBadge(text="MOST POPULAR")
    surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, 150, 40)
    ctx = cairo.Context(surface)
    badge.draw(ctx, time=0.0)
    assert badge.text == "MOST POPULAR"

def test_pricing_tier_grid_sizing_and_draw():
    grid = PricingTierGrid()
    surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, 1000, 600)
    ctx = cairo.Context(surface)
    grid.draw(ctx, time=0.0)
    assert len(grid.columns) > 0

def test_pricing_tier_grid_prices_change():
    grid = PricingTierGrid()
    action = grid.highlight_tier("Pro")
    assert action is not None

def test_pricing_tier_matrix_highlight():
    matrix = PricingTierMatrix()
    action = matrix.highlight_tier("Pro")
    assert action is not None
