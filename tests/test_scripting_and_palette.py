"""
Unit tests for Fusion Shift+Space Command Palette and Python Scripting REPL Workspace.
"""

import pytest
from PySide6.QtWidgets import QApplication

from vibmo.graph.engine import VibmoStateGraph
from vibmo.desktop.widgets.fusion_command_palette import FusionCommandPalette, FUSION_TOOLS
from vibmo.desktop.workspaces.scripting import ScriptingWorkspace
from vibmo.desktop.main_window import VibmoMainWindow


@pytest.fixture(scope="session")
def qapp():
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


def test_fusion_command_palette_filtering(qapp):
    palette = FusionCommandPalette()
    assert len(FUSION_TOOLS) >= 20

    # Test search filter
    palette._filter_tools("glow")
    assert palette.results_list.count() >= 1

    palette._filter_tools("noise")
    assert palette.results_list.count() >= 1


def test_scripting_workspace_execution(qapp):
    state_graph = VibmoStateGraph()
    scripting = ScriptingWorkspace(state_graph=state_graph)

    # Test code execution
    scripting.editor.setPlainText("a = 10 + 20\nprint('Computed sum:', a)")
    scripting.run_script()

    console_text = scripting.console.toPlainText()
    assert "Computed sum: 30" in console_text
    assert "Execution & State Graph Sync Completed" in console_text


def test_main_window_with_scripting_and_fusion_palette(qapp):
    state_graph = VibmoStateGraph()
    window = VibmoMainWindow(state_graph=state_graph)

    # Check 6 workspace views
    assert window.stack.count() == 6
    assert hasattr(window, "scripting_ws")

    # Open palette from fusion canvas
    assert hasattr(window.fusion_canvas, "open_command_palette")
