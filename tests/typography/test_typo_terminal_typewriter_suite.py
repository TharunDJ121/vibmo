import pytest
from unittest.mock import MagicMock
import cairo

from vibmo.core.color import colors, Color
from vibmo.typography.kinetic.typo_terminal_typewriter_suite import (
    PhosphorTerminalTypewriter,
    BlinkingBlockCaret,
    CommandPromptPrefix,
    TypingAudioSyncHook
)


def test_command_prompt_prefix():
    prompt = CommandPromptPrefix(prompt="test> ", font_size=20.0, color=colors.CYAN_500)
    assert prompt.prompt == "test> "

    surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, 100, 100)
    ctx = cairo.Context(surf)
    prompt.draw(ctx, 0.0)

    w = prompt.measure_width()
    assert w > 0.0


def test_blinking_block_caret():
    caret = BlinkingBlockCaret(blink_rate=2.0)
    surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, 100, 100)
    ctx = cairo.Context(surf)

    # Initially visible
    caret.draw(ctx, 0.0)
    # At 0.25s, dt * 2 * 2 = 0.25 * 4 = 1.0 (odd -> invisible)
    caret.draw(ctx, 0.26)

    # Just checking it doesn't crash during drawing
    assert caret.blink_rate == 2.0


def test_typing_audio_sync_hook():
    calls = []

    def on_type(char: str, time: float):
        calls.append((char, time))

    hook = TypingAudioSyncHook(on_type)

    hook.trigger("a", 1.0, 0)
    hook.trigger("a", 1.1, 0) # Should ignore duplicate index
    hook.trigger("b", 1.2, 1)

    assert len(calls) == 2
    assert calls[0] == ("a", 1.0)
    assert calls[1] == ("b", 1.2)

    hook.reset()
    hook.trigger("c", 2.0, 0)
    assert len(calls) == 3


def test_phosphor_terminal_typewriter():
    calls = []
    def on_type(char: str, time: float):
        calls.append((char, time))

    term = PhosphorTerminalTypewriter(
        prompt_text="root# ",
        audio_hook=on_type
    )

    # Check hierarchy
    assert term.prompt_node is not None
    assert term.caret is not None
    assert term.audio_hook_node is not None

    # Setup animation
    action = term.typewriter("hello\nworld", speed=10.0)

    surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, 400, 200)
    ctx = cairo.Context(surf)

    # Time 0
    term.typing_progress.set(0.0)
    term.draw(ctx, 0.0)
    assert len(calls) == 0

    # Middle of typing
    term.typing_progress.set(0.5)
    term.draw(ctx, action.duration * 0.5)
    assert len(calls) > 0

    # End of typing
    term.typing_progress.set(1.0)
    term.draw(ctx, action.duration)

    assert len(calls) == len("hello\nworld")

    # Caret moved
    caret_pos = term.caret.position.get(action.duration)
    assert caret_pos[0] > 0.0 # x > 0
    assert caret_pos[1] > 0.0 # y > 0 due to newline
