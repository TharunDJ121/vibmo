"""
Unit tests for Scene to StateGraph bidirectional synchronization and live desktop rendering.
"""

import pytest
from PySide6.QtWidgets import QApplication

from vibmo.agent_api import Scene, GlassCard, KineticText, MetricCounter, Vignette, FilmGrain, colors
from vibmo.graph.engine import VibmoStateGraph
from vibmo.graph.scene_sync import SceneGraphSyncEngine
from vibmo.desktop.workspaces.scripting import ScriptingWorkspace
from vibmo.desktop.widgets.capcut_player import CapCutPlayer


@pytest.fixture(scope="session")
def qapp():
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


def test_scene_to_state_graph_synchronization():
    state_graph = VibmoStateGraph()

    scene = Scene(width=1920, height=1080, fps=60.0, duration=4.0, background=colors.DARK_NAVY)
    card = GlassCard(position=(400, 300))
    title = KineticText("Live Sync Test", font_size=32)
    counter = MetricCounter(start_val=0, end_val=1000)
    card.add(title, counter)
    scene.add(card)

    scene.add_post_fx(Vignette(0.3), FilmGrain(0.01))

    # Sync
    SceneGraphSyncEngine.sync_scene_to_state_graph(scene, state_graph)

    # Assertions
    assert state_graph.project.width == 1920
    assert state_graph.project.height == 1080
    assert state_graph.project.fps == 60.0
    assert state_graph.project.duration_seconds == 4.0
    assert state_graph.project.duration_frames == 240

    # Check tracks and clips
    assert len(state_graph.project.timeline.tracks) >= 1
    assert len(state_graph.project.timeline.clips) >= 1

    # Check Fusion graph sync
    fg = list(state_graph.project.fusion_graphs.values())[0]
    assert len(fg.nodes) >= 3  # MediaIn, Glow/Vignette, MediaOut


def test_script_execution_and_player_frame_render(qapp):
    state_graph = VibmoStateGraph()
    scripting = ScriptingWorkspace(state_graph=state_graph)

    code = """
from vibmo.agent_api import *
scene = Scene(width=640, height=360, fps=30.0, duration=2.0)
text = KineticText("Hello Vibmo", font_size=24)
scene.add(text)
"""
    scripting.editor.setPlainText(code)
    scripting.run_script()

    assert state_graph.active_scene is not None
    assert state_graph.project.width == 640
    assert state_graph.project.height == 360

    # Test Player live frame rendering
    player = CapCutPlayer(state_graph=state_graph)
    player.render_frame_sync(15)  # t = 0.5s

    # Pixmap should be successfully painted
    assert player.screen_label.pixmap() is not None
    assert not player.screen_label.pixmap().isNull()


def test_multi_scene_sequence_sync(qapp):
    state_graph = VibmoStateGraph()
    scripting = ScriptingWorkspace(state_graph=state_graph)

    from vibmo.desktop.workspaces.scripting import SHOWCASE_SEQUENCE_CODE
    scripting.editor.setPlainText(SHOWCASE_SEQUENCE_CODE)
    scripting.run_script()

    # Verify state graph synced with 4 scenes
    assert state_graph.active_scene is not None
    assert state_graph.project.duration_seconds > 10.0
    assert len(state_graph.project.timeline.tracks) >= 2
    assert len(state_graph.project.timeline.clips) >= 4

    # Verify player renders sequence frame
    player = CapCutPlayer(state_graph=state_graph)
    player.render_frame_sync(120)  # t = 2.0s
    assert player.screen_label.pixmap() is not None
    assert not player.screen_label.pixmap().isNull()

