"""
Tests for ConversationMemory and Multi-turn Context in Vibmo.
"""

import pytest
from vibmo.ai.memory import ConversationMemory, get_global_memory


def test_conversation_memory_crud():
    mem = ConversationMemory(max_turns=5)
    assert len(mem.turns) == 0

    mem.add_user_turn("Make background blue")
    assert len(mem.turns) == 1
    assert mem.turns[0].role == "user"
    assert mem.turns[0].content == "Make background blue"

    mem.add_assistant_turn("Changed background to blue", code="scene.background = colors.BLUE")
    assert len(mem.turns) == 2
    assert mem.current_code == "scene.background = colors.BLUE"

    summary = mem.get_history_summary()
    assert "Make background blue" in summary
    assert "Changed background to blue" in summary

    mem.clear()
    assert len(mem.turns) == 0
    assert mem.current_code == ""


def test_conversation_memory_trim():
    mem = ConversationMemory(max_turns=3)
    for i in range(10):
        mem.add_user_turn(f"Turn {i}")
    assert len(mem.turns) == 3
    assert mem.turns[-1].content == "Turn 9"


def test_global_memory_singleton():
    gmem = get_global_memory()
    assert isinstance(gmem, ConversationMemory)
