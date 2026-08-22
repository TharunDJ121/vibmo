import math
import pytest
import cairo

from vibmo.core.color import Color, colors
from vibmo.product.ai.ui_agent_team_thread_suite import (
    AgentStatusPill,
    AgentTypingWave,
    ToolCallingPayloadCard,
    AgentConversationBubble,
)
from vibmo.layout.container import FlexContainer
from vibmo.primitives.circle import Circle


def test_agent_status_pill():
    pill = AgentStatusPill(status="online")
    # Verify child construction
    assert len(pill.children) == 2
    assert isinstance(pill.children[0], Circle)
    assert pill.children[0].fill.get() == colors.EMERALD_500
    assert pill.children[1].text.get() == "Online"

    # Test cairo drawing
    surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, 200, 100)
    ctx = cairo.Context(surface)
    pill.draw(ctx, time=0.0)
    # The drawing should not raise any exceptions


def test_agent_typing_wave():
    wave = AgentTypingWave()
    assert len(wave.dots) == 3

    # Test default bounds
    bx, by, bw, bh = wave.local_bounds(time=0.0)
    assert bw >= 0
    assert bh >= 0

    # Draw to advance harmonic positions
    surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, 100, 50)
    ctx = cairo.Context(surface)

    # Save base pos. In FlexContainer, Y might start at 0 before layout.
    wave.draw(ctx, time=0.0)
    pos_before = wave.dots[0].position.get(0.0)

    # Simulate time=0.25 (to get a non-zero sine wave offset)
    wave.draw(ctx, time=0.25)

    pos_after = wave.dots[0].position.get(0.25)
    assert pos_after[1] != pos_before[1]  # Y should have changed


def test_tool_calling_payload_card():
    card = ToolCallingPayloadCard(tool_name="test_tool", payload="{'k': 'v'}")
    assert len(card.children) == 2
    header = card.children[0]
    assert len(header.children) == 2

    body = card.children[1]
    assert body.text.get() == "{'k': 'v'}"

    # Verify bounds exist
    bx, by, bw, bh = card.local_bounds(time=0.0)
    assert bw >= 0
    assert bh >= 0

    surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, 200, 100)
    ctx = cairo.Context(surface)

    # Check spinner rotation updates on draw
    rot_before = card.spinner.rotation.get(0.0)
    card.draw(ctx, time=1.0)
    rot_after = card.spinner.rotation.get(1.0)
    assert math.isclose(rot_after, math.pi)


def test_agent_conversation_bubble():
    bubble = AgentConversationBubble(
        name="AI Assistant",
        role="Coder",
        timestamp="10:42 AM",
        body="Here is the fix.",
    )

    assert len(bubble.children) == 2
    avatar = bubble.children[0]
    content_col = bubble.children[1]

    assert isinstance(avatar, Circle)
    assert isinstance(content_col, FlexContainer)

    # Header row should contain Name, Role badge, and timestamp
    header = content_col.children[0]
    assert len(header.children) == 3
    assert header.children[0].text.get() == "AI Assistant"

    # Body text
    body_text = content_col.children[1]
    assert body_text.text.get() == "Here is the fix."

    # Test auto-expansion and drawing bounds
    surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, 500, 200)
    ctx = cairo.Context(surface)
    bubble.draw(ctx, time=0.0)

    # Draw logic passes without errors
