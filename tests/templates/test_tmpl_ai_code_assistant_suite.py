import pytest
from vibmo.templates.turnkey.tmpl_ai_code_assistant_suite import AiCodeAssistantTemplate
from vibmo.product.mockups import BrowserWindow
from vibmo.components.code import CodeWindow
from vibmo.components.glass import GlassCard
from vibmo.product.ai.ui_token_streamer_suite import TokenStreamerBox
from vibmo.components.counter import MetricCounter

def _walk_scene(node):
    yield node
    if hasattr(node, "nodes"):
        for child in node.nodes:
            yield from _walk_scene(child)
    if hasattr(node, "children"):
        for child in node.children:
            yield from _walk_scene(child)
    if hasattr(node, "_content") and node._content:
        yield from _walk_scene(node._content)
    if hasattr(node, "content") and node.content:
        yield from _walk_scene(node.content)

def test_ai_code_assistant_scene_duration_and_hierarchy():
    scene = AiCodeAssistantTemplate.create_scene(
        title="Agent.ai IDE",
        code_snippet="def stream():\n    yield tokens",
        duration=7.5
    )

    assert scene.duration == 7.5

    nodes = list(_walk_scene(scene))

    browser_nodes = [n for n in nodes if isinstance(n, BrowserWindow)]
    assert len(browser_nodes) > 0, "BrowserWindow should be in scene"

    code_win_nodes = [n for n in nodes if isinstance(n, CodeWindow)]
    assert len(code_win_nodes) > 0, "CodeWindow should be in scene"

    glass_card_nodes = [n for n in nodes if isinstance(n, GlassCard)]
    assert len(glass_card_nodes) > 0, "GlassCard should be in scene"

    token_box_nodes = [n for n in nodes if isinstance(n, TokenStreamerBox)]
    assert len(token_box_nodes) > 0, "TokenStreamerBox should be in scene"

    counter_nodes = [n for n in nodes if isinstance(n, MetricCounter)]
    assert len(counter_nodes) > 0, "MetricCounter should be in scene"

def test_ai_code_assistant_scene_storyboard_and_actions():
    scene = AiCodeAssistantTemplate.create_scene(
        title="Agent.ai IDE",
        code_snippet="def stream():\n    yield tokens",
        duration=6.0
    )

    # Validation passes without error
    assert len(scene.validate()) == 0

    # Test storyboard generation
    storyboard = scene.storyboard(rows=1, cols=3)
    assert storyboard is not None
