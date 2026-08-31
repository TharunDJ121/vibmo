import pytest
import cairo
from vibmo.product.ai.ui_prompt_diff_suite import (
    PromptDiffCard,
    InlineDiffHighlighter,
    PromptTokenCostBadge,
    MergePromptButton,
    PromptDiffViewer,
    SideBySideDiffPane,
)

def test_inline_diff_highlighter():
    hl = InlineDiffHighlighter(v1="Old prompt text", v2="New improved prompt text")
    surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, 600, 200)
    ctx = cairo.Context(surface)
    hl.draw(ctx, time=0.0)
    assert hl.v1 == "Old prompt text"

def test_prompt_token_cost_badge():
    badge = PromptTokenCostBadge(cost_delta="+14 tokens (+$0.0002)")
    surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, 250, 50)
    ctx = cairo.Context(surface)
    badge.draw(ctx, time=0.0)
    assert "+14 tokens" in badge.cost_delta

def test_merge_prompt_button():
    btn = MergePromptButton(label="Accept Diff")
    surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, 180, 50)
    ctx = cairo.Context(surface)
    btn.draw(ctx, time=0.0)
    assert btn.label == "Accept Diff"

def test_prompt_diff_card():
    card = PromptDiffCard(v1="v1", v2="v2")
    surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, 800, 500)
    ctx = cairo.Context(surface)
    card.draw(ctx, time=0.0)
    assert card is not None
