import pytest
import cairo
import numpy as np

from vibmo.product.ai.ui_tree_of_thought_suite import (
    TreeOfThoughtTree,
    ReasoningNodeBranch,
    ExplorationScoreBadge,
    PrunedBranchFade
)
from vibmo.core.signal import Signal

def test_exploration_score_badge():
    badge = ExplorationScoreBadge(score=0.94, is_winner=True)
    assert badge.score == 0.94
    assert badge.is_winner is True
    
    # Test drawing does not crash
    surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, 100, 100)
    ctx = cairo.Context(surface)
    badge.draw(ctx, 0.0)

def test_reasoning_node_branch():
    node = ReasoningNodeBranch(node_id="n1", thought="Let's analyze the input", status="Valid")
    assert node.node_id == "n1"
    assert node.thought == "Let's analyze the input"
    assert node.status == "Valid"
    
    # Test drawing does not crash
    surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, 200, 200)
    ctx = cairo.Context(surface)
    node.draw(ctx, 0.0)

def test_pruned_branch_fade():
    branch = PrunedBranchFade(start_pos=(0.0, 0.0), end_pos=(100.0, 100.0))
    branch.progress = Signal(0.5)
    
    # Test drawing does not crash
    surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, 200, 200)
    ctx = cairo.Context(surface)
    branch.draw(ctx, 0.0)
    
def test_tree_of_thought_tree_expansion():
    tree = TreeOfThoughtTree(root_thought="Root thought")
    
    assert "root" in tree.nodes_data
    assert tree.nodes_data["root"]["thought"] == "Root thought"
    
    # Expand node
    children_data = [
        {"id": "c1", "thought": "Option A", "status": "Valid", "score": 0.9, "is_winner": True},
        {"id": "c2", "thought": "Option B", "status": "Pruned"}
    ]
    
    action = tree.expand_node("root", children_data, duration=1.0)
    
    assert "c1" in tree.nodes_data
    assert "c2" in tree.nodes_data
    assert tree.nodes_data["root"]["children"] == ["c1", "c2"]
    assert len(tree.node_components) == 3
    assert len(tree.badges) == 1
    assert len(tree.edges) == 1 # one pruned edge
    
    # Test drawing does not crash
    surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, 500, 500)
    ctx = cairo.Context(surface)
    tree.draw(ctx, 0.0)

