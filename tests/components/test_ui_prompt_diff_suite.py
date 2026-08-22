import pytest
import cairo
from typing import Any

from vibmo.product.ai.ui_prompt_diff_suite import (
    PromptDiffCard,
    InlineDiffHighlighter,
    PromptTokenCostBadge,
    MergePromptButton
)


class MockContext:
    def __init__(self):
        self.calls = []
        self.matrix = cairo.Matrix()

    def __getattr__(self, name: str) -> Any:
        def stub(*args: Any, **kwargs: Any) -> Any:
            self.calls.append((name, args, kwargs))
            if name == "text_extents":
                class Extents:
                    width = 10.0
                    height = 10.0
                return Extents()
            return None
        return stub


def test_prompt_diff_card():
    card = PromptDiffCard(width=400, height=200)
    assert card.local_bounds(0.0) == (0.0, 0.0, 400.0, 200.0)
    ctx = MockContext()
    card.draw(ctx, 0.0)
    calls = [c[0] for c in ctx.calls]
    assert "save" in calls
    assert "restore" in calls
    assert "arc" in calls
    assert "fill_preserve" in calls
    assert "stroke" in calls
    assert "show_text" in calls


def test_inline_diff_highlighter():
    diff_text = " line 1\n+added line\n-deleted line"
    highlighter = InlineDiffHighlighter(text=diff_text, font_size=16.0, line_height=24.0, width=300.0)
    
    assert len(highlighter.parsed_lines) == 3
    assert highlighter.parsed_lines[0] == ("normal", " line 1")
    assert highlighter.parsed_lines[1] == ("add", "+added line")
    assert highlighter.parsed_lines[2] == ("del", "-deleted line")
    
    assert highlighter.local_bounds(0.0) == (0.0, 0.0, 300.0, 3 * 24.0)
    
    ctx = MockContext()
    highlighter.draw(ctx, 0.0)
    
    calls = [c[0] for c in ctx.calls]
    assert "save" in calls
    assert "restore" in calls
    assert "rectangle" in calls
    assert "fill" in calls
    assert "show_text" in calls


def test_prompt_token_cost_badge():
    badge = PromptTokenCostBadge(reduction_text="-25% tokens", cost_savings="$0.10 saved", width=200, height=40)
    assert badge.local_bounds(0.0) == (0.0, 0.0, 200.0, 40.0)
    
    ctx = MockContext()
    badge.draw(ctx, 0.0)
    
    calls = [c[0] for c in ctx.calls]
    assert "save" in calls
    assert "restore" in calls
    assert "arc" in calls
    assert "fill_preserve" in calls
    assert "stroke" in calls
    assert "show_text" in calls


def test_merge_prompt_button():
    btn = MergePromptButton(label="Accept", width=150, height=50)
    assert btn.local_bounds(0.0) == (0.0, 0.0, 150.0, 50.0)
    
    ctx = MockContext()
    btn.draw(ctx, 0.0)
    
    calls = [c[0] for c in ctx.calls]
    assert "save" in calls
    assert "restore" in calls
    assert "arc" in calls
    assert "fill" in calls
    assert "show_text" in calls
    
    # test scaling
    btn.scale_sig.set(1.5)
    ctx2 = MockContext()
    btn.draw(ctx2, 0.0)
    calls2 = [c[0] for c in ctx2.calls]
    assert "scale" in calls2

