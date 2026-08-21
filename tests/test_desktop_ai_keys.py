"""
Tests for Desktop App AI Director and API Keys Dialogs.
"""

import os
import pytest
from PySide6.QtWidgets import QApplication
from vibmo.desktop.main_window import VibmoMainWindow
from vibmo.desktop.dialogs.api_keys_dialog import ApiKeysDialog
from vibmo.desktop.dialogs.ai_director_dialog import AiDirectorDialog


@pytest.fixture(scope="session")
def qapp():
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


def test_api_keys_dialog_initialization(qapp):
    dlg = ApiKeysDialog()
    assert dlg is not None
    assert "openai" in dlg.inputs
    assert "anthropic" in dlg.inputs
    dlg.close()


def test_ai_director_dialog_initialization(qapp):
    dlg = AiDirectorDialog(current_code="from motio.agent_api import *\ns1 = Scene()")
    assert dlg is not None
    assert dlg.prompt_input is not None
    assert dlg.logs_box is not None
    dlg.close()


def test_main_window_has_ai_actions(qapp):
    win = VibmoMainWindow()
    assert win is not None
    assert hasattr(win, "_open_ai_director")
    assert hasattr(win, "_open_api_keys")
    win.close()
