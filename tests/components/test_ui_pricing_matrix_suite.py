import pytest
import cairo
import math

from vibmo.product.ai.ui_pricing_matrix_suite import (
    FeatureChecklistRow,
    AnnualBillingToggle,
    PopularGlowBadge,
    PricingTierGrid,
)
from vibmo.core.signal import Signal

def test_feature_checklist_row_draw():
    row = FeatureChecklistRow(text="Test Feature", active=True)
    surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, 200, 50)
    ctx = cairo.Context(surface)
    row.draw(ctx, time=0.0)
    
    row_inactive = FeatureChecklistRow(text="Test Feature", active=False)
    ctx2 = cairo.Context(cairo.ImageSurface(cairo.FORMAT_ARGB32, 200, 50))
    row_inactive.draw(ctx2, time=0.0)

def test_annual_billing_toggle_state():
    # Test toggle with static boolean
    toggle = AnnualBillingToggle(is_annual=False)
    assert toggle.get_price(100.0) == 100.0
    
    toggle_annual = AnnualBillingToggle(is_annual=True)
    assert toggle_annual.get_price(100.0) == 80.0
    
    # Test toggle with Signal
    sig = Signal(False)
    toggle_sig = AnnualBillingToggle(is_annual=sig)
    assert toggle_sig.get_price(100.0) == 100.0
    
    sig.set(True)
    assert toggle_sig.get_price(100.0) == 80.0

def test_annual_billing_toggle_draw():
    toggle = AnnualBillingToggle(is_annual=True)
    surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, 200, 50)
    ctx = cairo.Context(surface)
    toggle.draw(ctx, time=0.0)

def test_popular_glow_badge_draw():
    badge = PopularGlowBadge()
    surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, 200, 50)
    ctx = cairo.Context(surface)
    badge.draw(ctx, time=1.0) # Test with some time for glow

def test_pricing_tier_grid_sizing_and_draw():
    # Test drawing
    grid = PricingTierGrid()
    surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, 1200, 800)
    ctx = cairo.Context(surface)
    grid.draw(ctx, time=0.0)
    
    # Test 3-column sizing
    # 3 cards * 300 width + 2 gaps * 40 width = 900 + 80 = 980
    bounds = grid.local_bounds()
    assert bounds[2] == 980 # width
    assert bounds[3] == 500 # height

def test_pricing_tier_grid_prices_change():
    # Sizing and toggle state are verified
    toggle = AnnualBillingToggle(is_annual=True)
    grid = PricingTierGrid(toggle=toggle)
    
    # Render with toggle True
    surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, 1200, 800)
    ctx = cairo.Context(surface)
    grid.draw(ctx, time=0.0)
    
    # We can verify it manually through toggle
    assert grid.toggle.get_price(grid.tiers[1]["price"]) == 40.0
    
