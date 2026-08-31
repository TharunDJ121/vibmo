"""
Unit tests for TerminalWindow, CodeCard, and DiagramNode.
"""

import pytest
import cairo
from vibmo.components.terminal_session import TerminalWindow, TerminalStep
from vibmo.components.code_card import CodeCard
from vibmo.components.diagram_node import DiagramNode, DiagramBox
from vibmo.core.color import colors


def test_terminal_window_creation_and_steps():
    term = TerminalWindow(title="bash", prompt="$ ")
    term.add_command("pip install vibmo", type_speed=0.01, hold_seconds=0.1)
    term.add_output("Successfully installed vibmo", hold_seconds=0.2)
    term.add_pause(0.1)
    term.add_pill("Ready", color=colors.EMERALD, duration=1.0)
    assert len(term.steps) == 4


def test_terminal_window_cairo_render():
    surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, 1920, 1080)
    ctx = cairo.Context(surface)

    term = TerminalWindow(position=(960, 540))
    term.add_command("echo 'hello'", type_speed=0.01, hold_seconds=0.1)
    term.add_output("hello", hold_seconds=0.2)
    term.add_pill("Active", duration=1.0)

    # Render at t=0.05, t=0.5, t=1.0
    term._render_self(ctx, t=0.05)
    term._render_self(ctx, t=0.5)
    term._render_self(ctx, t=1.0)


def test_code_card_cairo_render():
    surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, 1920, 1080)
    ctx = cairo.Context(surface)

    code = """def animate():\n    yield card.pop_in()\n    return True"""
    card = CodeCard(code=code, language="python", filename="demo.py", theme="dracula")
    card._render_self(ctx, t=1.0)


def test_diagram_node_cairo_render():
    surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, 1920, 1080)
    ctx = cairo.Context(surface)

    diag = DiagramNode()
    diag.add_box("1", "Client", subtext="Web/App", x=400, y=540, color=colors.CYAN)
    diag.add_box("2", "Vibmo Engine", subtext="GPU Rasterizer", x=960, y=540, color=colors.EMERALD)
    diag.connect("1", "2", label="JSON Request", color=colors.CYAN)

    diag._render_self(ctx, t=0.5)
