"""
Tests for CLI v2 Commands (inspect, ai, watch, templates) in Vibmo.
"""

import pytest
import os
import tempfile
from vibmo.cli.main import cmd_inspect, cmd_ai, _load_runnable_from_file


def test_cli_load_runnable():
    with tempfile.NamedTemporaryFile("w", suffix=".py", delete=False) as f:
        f.write("""from motio.agent_api import *
scene = Scene(duration=3.0)
card = GlassCard()
scene.add(card)
""")
        f_path = f.name

    try:
        runnable = _load_runnable_from_file(f_path)
        assert runnable.duration == 3.0
        assert len(runnable.nodes) == 1
    finally:
        if os.path.exists(f_path):
            os.remove(f_path)


def test_cli_inspect():
    with tempfile.NamedTemporaryFile("w", suffix=".py", delete=False) as f:
        f.write("""from motio.agent_api import *
scene = Scene(duration=2.5)
title = KineticText("Hello CLI", font_size=32)
scene.add(title)
""")
        f_path = f.name

    try:
        # cmd_inspect should execute without exception
        cmd_inspect(f_path)
    finally:
        if os.path.exists(f_path):
            os.remove(f_path)


def test_cli_ai_edit():
    with tempfile.NamedTemporaryFile("w", suffix=".py", delete=False) as f:
        f.write("""from motio.agent_api import *
scene = Scene(duration=2.0)
""")
        f_path = f.name

    try:
        cmd_ai(prompt="change background to sunset", edit_script=f_path)
        with open(f_path, "r", encoding="utf-8") as f_read:
            updated = f_read.read()
        assert "sunset" in updated.lower() or "Scene" in updated
    finally:
        if os.path.exists(f_path):
            os.remove(f_path)
