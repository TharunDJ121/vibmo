"""
Unit tests for Vibmo PySide6 Desktop Workstations and UI panels.
"""

import os
import pytest
from PySide6.QtWidgets import QApplication, QWidget

from vibmo.graph.engine import VibmoStateGraph
from vibmo.desktop.main_window import VibmoMainWindow
from vibmo.desktop.workspaces import (
    MotionWorkspace,
    FusionWorkspace,
    ColorWorkspace,
    FairlightWorkspace,
    DeliveryWorkspace,
)


@pytest.fixture(scope="session")
def qapp():
    """Ensure a single QApplication instance exists for GUI tests."""
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


def test_main_window_and_workspaces_creation(qapp):
    state_graph = VibmoStateGraph()
    window = VibmoMainWindow(state_graph=state_graph)

    # Check window and stack properties
    assert window.stack.count() == 6
    assert isinstance(window.motion_ws, QWidget)
    assert isinstance(window.fusion_ws, (FusionWorkspace, QWidget))
    assert isinstance(window.color_ws, ColorWorkspace)
    assert isinstance(window.fairlight_ws, FairlightWorkspace)
    assert isinstance(window.delivery_ws, DeliveryWorkspace)


def test_workspace_switching(qapp):
    state_graph = VibmoStateGraph()
    window = VibmoMainWindow(state_graph=state_graph)

    # Switch to Fusion
    window.stack.setCurrentIndex(1)
    assert window.stack.currentIndex() == 1

    # Switch to Color
    window.stack.setCurrentIndex(2)
    assert window.stack.currentIndex() == 2

    # Switch to Fairlight
    window.stack.setCurrentIndex(3)
    assert window.stack.currentIndex() == 3

    # Switch to Delivery
    window.stack.setCurrentIndex(4)
    assert window.stack.currentIndex() == 4


def test_delivery_queue_interaction(qapp):
    state_graph = VibmoStateGraph()
    window = VibmoMainWindow(state_graph=state_graph)

    delivery_ws = window.delivery_ws
    delivery_ws.path_input.setText("output/test_export.mp4")
    delivery_ws._add_to_queue()

    assert len(state_graph.project.render_queue) == 1
    assert delivery_ws.queue_table.rowCount() == 1
