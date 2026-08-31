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
    window.close()


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
    window.close()


def test_magnetic_timeline_and_snapping(qapp):
    state_graph = VibmoStateGraph()
    window = VibmoMainWindow(state_graph=state_graph)

    # 1. Import sample video
    if os.path.exists("Video-45138.mp4"):
        media = state_graph.import_media("Video-45138.mp4")
        assert media.kind == "video"
        assert media.duration_frames is not None
        assert media.duration_frames > 100
        assert "thumbnail_b64" in media.metadata

        # Add clip to timeline
        track = state_graph.project.timeline.tracks[0]
        clip1 = state_graph.add_clip(
            track_id=track.id,
            name="Video-45138",
            start_frame=0,
            duration_frames=180,
            media_id=media.id,
        )

        window.timeline.scene.refresh_scene()
        assert len(state_graph.project.timeline.clips) == 1

        # 2. Test Magnetic Snapping Calculation
        # Snapping near playhead (frame 0 or playhead)
        snapped_frame, guide = window.timeline.scene.get_snap_target(target_frame=3, clip_duration=60)
        assert snapped_frame == 0  # Snapped magnetically to 0!

        # 3. Test Video Frame Rendering in Player
        window.timeline.set_playhead_frame(30)
        window.player.render_frame_sync(30)
        assert window.player.screen_label.pixmap() is not None
        assert not window.player.screen_label.pixmap().isNull()

        # 4. Test Split at Playhead (Ctrl+B)
        window.timeline.scene.current_frame = 60
        window.timeline.split_at_playhead()
        assert len(state_graph.project.timeline.clips) == 2

        # 5. Test Delete
        # Select first clip and delete
        for item in window.timeline.scene.items():
            if hasattr(item, "clip"):
                item.setSelected(True)
                break
        window.timeline.delete_selected_clip()
        assert len(state_graph.project.timeline.clips) == 1
    window.close()


def test_delivery_queue_interaction(qapp):
    state_graph = VibmoStateGraph()
    window = VibmoMainWindow(state_graph=state_graph)

    delivery_ws = window.delivery_ws
    delivery_ws.path_input.setText("output/test_export.mp4")
    delivery_ws._add_to_queue()

    assert len(state_graph.project.render_queue) == 1
    assert delivery_ws.queue_table.rowCount() == 1
    window.close()

