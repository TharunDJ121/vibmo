import math
import pytest
import cairo

from vibmo.core.color import colors, Color
from vibmo.product.ai.ui_quota_meter_suite import (
    CircularTokenQuotaRing,
    OverLimitWarningBanner,
    UsageThresholdPill,
    UpgradeCtaButton
)

class MockContext:
    def __init__(self):
        self.paths = []
        self.arcs = []
        self.fills = 0
        self.strokes = 0
        self.saves = 0
        self.restores = 0
        self.scales = []
        self.sources = []
        self.line_widths = []

    def save(self):
        self.saves += 1

    def restore(self):
        self.restores += 1

    def scale(self, sx, sy):
        self.scales.append((sx, sy))

    def new_path(self):
        self.paths.append("new")

    def close_path(self):
        self.paths.append("close")

    def arc(self, xc, yc, radius, angle1, angle2):
        self.arcs.append((xc, yc, radius, angle1, angle2))

    def fill(self):
        self.fills += 1

    def stroke(self):
        self.strokes += 1

    def set_source_rgba(self, r, g, b, a):
        self.sources.append((r, g, b, a))

    def set_source(self, pattern):
        self.sources.append(pattern)

    def set_line_width(self, w):
        self.line_widths.append(w)

    def set_line_cap(self, cap):
        pass


def test_circular_token_quota_ring():
    node = CircularTokenQuotaRing(used=500, total=1000, radius=50, thickness=10)
    ctx = MockContext()

    node.draw(ctx, 0.0)

    assert ctx.saves == 1
    assert ctx.restores == 1
    assert ctx.strokes == 2  # Track + Fill

    assert ctx.line_widths[-1] == 10

    # Check arcs
    assert len(ctx.arcs) == 2

    # First arc is track
    track_arc = ctx.arcs[0]
    assert track_arc[2] == 50  # radius
    assert track_arc[3] == 0  # start angle
    assert track_arc[4] == 2 * math.pi  # end angle

    # Second arc is fill
    fill_arc = ctx.arcs[1]
    assert fill_arc[2] == 50
    assert fill_arc[3] == -math.pi / 2
    # 50% fill
    assert fill_arc[4] == -math.pi / 2 + (0.5 * 2 * math.pi)


def test_over_limit_warning_banner():
    # Test under limit
    node_safe = OverLimitWarningBanner(ratio=0.5)
    ctx_safe = MockContext()
    node_safe.draw(ctx_safe, 0.0)
    assert ctx_safe.fills == 0

    # Test over limit
    node_warn = OverLimitWarningBanner(ratio=0.95)
    ctx_warn = MockContext()
    node_warn.draw(ctx_warn, 0.0)
    assert ctx_warn.fills == 1
    assert ctx_warn.saves == 1

    # Check bounds
    assert len(ctx_warn.arcs) == 4

    # Test pulse animation over 95%
    node_crit = OverLimitWarningBanner(ratio=0.99, color=colors.RED)
    ctx_crit = MockContext()
    node_crit.draw(ctx_crit, 0.25)  # sin(0.25 * 2 * pi) = sin(pi/2) = 1.0

    c = colors.RED
    c_rgba = c.to_tuple_rgba() if hasattr(c, "to_tuple_rgba") else (c.r, c.g, c.b, c.a)

    assert ctx_crit.fills == 1
    source = ctx_crit.sources[-1]
    # opacity should be 0.7 + 0.3 * 1.0 = 1.0
    assert abs(source[3] - 1.0) < 1e-5


def test_usage_threshold_pill():
    node = UsageThresholdPill(days_left=5)
    ctx = MockContext()

    node.draw(ctx, 0.0)

    assert ctx.saves == 1
    assert ctx.restores == 1
    assert ctx.fills == 1
    assert len(ctx.arcs) == 4


def test_upgrade_cta_button():
    node = UpgradeCtaButton(width=100, height=40)
    ctx = MockContext()

    node.draw(ctx, 0.0)

    assert ctx.saves == 1
    assert ctx.restores == 1
    assert ctx.fills == 1
    assert len(ctx.arcs) == 4
    assert ctx.scales[0] == (1.0, 1.0)

    # Test hover
    node.hover_progress.set(1.0)
    ctx2 = MockContext()
    node.draw(ctx2, 0.0)
    assert ctx2.scales[0] == (1.05, 1.05)
