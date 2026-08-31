import pytest
import cairo
from vibmo.product.ai.ui_quota_meter_suite import (
    CircularTokenQuotaRing,
    OverLimitWarningBanner,
    UsageThresholdPill,
    UpgradeCtaButton,
    TokenQuotaMeter,
    UsageRingGauge,
)

def test_circular_token_quota_ring():
    ring = CircularTokenQuotaRing(used=750000, total=1000000)
    surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, 200, 200)
    ctx = cairo.Context(surface)
    ring.draw(ctx, time=0.0)
    assert ring.used.get() == 750000

def test_over_limit_warning_banner():
    banner = OverLimitWarningBanner(message="90% Quota Exceeded")
    surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, 400, 60)
    ctx = cairo.Context(surface)
    banner.draw(ctx, time=0.0)
    assert banner.message == "90% Quota Exceeded"

def test_usage_threshold_pill():
    pill = UsageThresholdPill(percentage=85.0)
    surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, 150, 40)
    ctx = cairo.Context(surface)
    pill.draw(ctx, time=0.0)
    assert pill.percentage == 85.0

def test_upgrade_cta_button():
    btn = UpgradeCtaButton(text="Upgrade Tier")
    surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, 180, 50)
    ctx = cairo.Context(surface)
    btn.draw(ctx, time=0.0)
    assert btn.text == "Upgrade Tier"
