import pytest
import cairo
from vibmo.product.ai.ui_tree_of_thought_suite import (
    TreeOfThoughtTree,
    ReasoningNodeBranch,
    ExplorationScoreBadge,
    PrunedBranchFade,
    ReasoningBranchNode,
)

def test_exploration_score_badge():
    badge = ExplorationScoreBadge(score=0.94, is_winner=True)
    assert badge.score.get() == 0.94
    assert badge.is_winner is True
    surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, 100, 50)
    ctx = cairo.Context(surface)
    badge.draw(ctx, time=0.0)

def test_tree_of_thought_tree_expansion():
    tree = TreeOfThoughtTree()
    action = tree.expand_branch(0)
    assert action is not None
    surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, 800, 600)
    ctx = cairo.Context(surface)
    tree.draw(ctx, time=0.0)

def test_reasoning_node_branch():
    branch = ReasoningNodeBranch(thought="Evaluating hypothesis Alpha", score=0.88)
    surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, 300, 80)
    ctx = cairo.Context(surface)
    branch.draw(ctx, time=0.0)
    assert branch.thought == "Evaluating hypothesis Alpha"

def test_pruned_branch_fade():
    fade = PrunedBranchFade(start_pos=(0.0, 0.0), end_pos=(100.0, 100.0))
    surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, 300, 80)
    ctx = cairo.Context(surface)
    fade.draw(ctx, time=0.0)
    assert fade is not None
