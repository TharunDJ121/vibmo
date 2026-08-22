import math
import pytest
from vibmo.product.ai.ui_matrix_comparison_suite import (
    InteractiveFeatureMatrix,
    CompetitorComparisonRow,
    TooltipFeatureExplanation,
    StickyHeaderColumn
)


class MockContext:
    def __init__(self):
        self.calls = []

    def save(self):
        self.calls.append("save")

    def restore(self):
        self.calls.append("restore")

    def clip(self):
        self.calls.append("clip")

    def new_path(self):
        self.calls.append("new_path")

    def new_sub_path(self):
        self.calls.append("new_sub_path")

    def rectangle(self, x, y, w, h):
        self.calls.append(("rectangle", x, y, w, h))

    def arc(self, xc, yc, radius, angle1, angle2):
        self.calls.append(("arc", xc, yc, radius, angle1, angle2))

    def set_source_rgba(self, r, g, b, a=1.0):
        self.calls.append(("set_source_rgba", r, g, b, a))

    def set_line_width(self, width):
        self.calls.append(("set_line_width", width))

    def move_to(self, x, y):
        self.calls.append(("move_to", x, y))

    def line_to(self, x, y):
        self.calls.append(("line_to", x, y))

    def stroke(self):
        self.calls.append("stroke")

    def fill(self):
        self.calls.append("fill")

    def has_call(self, name):
        for call in self.calls:
            if isinstance(call, tuple) and call[0] == name:
                return True
            if call == name:
                return True
        return False


def test_interactive_feature_matrix():
    ctx = MockContext()
    matrix = InteractiveFeatureMatrix()
    matrix.draw(ctx)

    assert ctx.has_call("save")
    assert ctx.has_call("restore")
    assert ctx.has_call("rectangle")
    assert ctx.has_call("fill")
    assert ctx.has_call("stroke")
    assert ctx.has_call("move_to")
    assert ctx.has_call("line_to")


def test_competitor_comparison_row_striped():
    ctx = MockContext()
    row = CompetitorComparisonRow(is_striped=True)
    row.draw(ctx)

    assert ctx.has_call("save")
    assert ctx.has_call("restore")
    assert ctx.has_call("rectangle")
    assert ctx.has_call("fill")
    assert ctx.has_call("arc") # Checkmark
    assert ctx.has_call("stroke") # Cross


def test_tooltip_feature_explanation():
    ctx = MockContext()
    tooltip = TooltipFeatureExplanation()
    tooltip.draw(ctx)

    assert ctx.has_call("save")
    assert ctx.has_call("restore")
    assert ctx.has_call("rectangle")
    assert ctx.has_call("fill")
    assert ctx.has_call("stroke")


def test_sticky_header_column():
    ctx = MockContext()
    col = StickyHeaderColumn()
    col.draw(ctx)

    assert ctx.has_call("save")
    assert ctx.has_call("restore")
    assert ctx.has_call("rectangle")
    assert ctx.has_call("fill")
    assert ctx.has_call("stroke")
    assert ctx.has_call("set_line_width")
