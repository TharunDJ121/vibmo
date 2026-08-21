"""
Motion (NLE Editorial) Workspace for Vibmo Desktop.
Features Media Pool with draggable assets, Dual Video Viewers, Transport Playback Controls,
and Interactive Multi-Track Timeline with Playhead Scrubber.
"""

from __future__ import annotations
from typing import Any, Optional
from PySide6.QtCore import Qt, Signal, QMimeData
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QSplitter,
    QTreeWidget,
    QTreeWidgetItem,
    QLabel,
    QPushButton,
    QFrame,
    QFileDialog,
    QHeaderView,
)
from PySide6.QtGui import QDrag, QPixmap

from vibmo.graph.engine import VibmoStateGraph
from vibmo.desktop.widgets.timeline_view import InteractiveTimelineWidget


class DraggableMediaTree(QTreeWidget):
    """Media Pool Tree supporting drag-and-drop to timeline."""

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self.setDragEnabled(True)
        self.setSelectionMode(QTreeWidget.SelectionMode.SingleSelection)

    def startDrag(self, supportedActions: Qt.DropAction) -> None:
        item = self.currentItem()
        if not item:
            return
        media_id = item.data(0, Qt.ItemDataRole.UserRole)
        if not media_id:
            return

        drag = QDrag(self)
        mime = QMimeData()
        mime.setText(media_id)
        drag.setMimeData(mime)

        # Create drag preview pixmap
        pix = QPixmap(120, 26)
        pix.fill(QColor("#0284C7"))
        drag.setPixmap(pix)
        drag.exec(Qt.DropAction.CopyAction)


class SingleVideoMonitor(QFrame):
    """Single Video Monitor with Timecode and Safe Margins."""

    def __init__(self, title: str, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self.setStyleSheet("background-color: #0A0B0E; border: 1px solid #27272A; border-radius: 6px;")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(6, 6, 6, 6)
        layout.setSpacing(4)

        # Header Bar
        hdr = QHBoxLayout()
        t_lbl = QLabel(f"📺 {title}")
        t_lbl.setStyleSheet("color: #94A3B8; font-weight: bold; font-size: 11px;")
        self.tc_label = QLabel("00:00:00:00")
        self.tc_label.setStyleSheet("color: #38BDF8; font-family: monospace; font-weight: bold; font-size: 11px;")

        hdr.addWidget(t_lbl)
        hdr.addStretch()
        hdr.addWidget(self.tc_label)
        layout.addLayout(hdr)

        # Video Surface Frame
        self.screen_frame = QFrame()
        self.screen_frame.setStyleSheet("background-color: #050608; border: 1px solid #18191E; border-radius: 4px;")
        s_layout = QVBoxLayout(self.screen_frame)
        
        self.display_text = QLabel("1080p @ 60.00 FPS\nACEScg Filmic Color")
        self.display_text.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.display_text.setStyleSheet("color: #3F3F46; font-size: 14px; font-weight: bold;")
        s_layout.addWidget(self.display_text)

        layout.addWidget(self.screen_frame, 1)

    def set_frame(self, frame: int, fps: float = 60.0) -> None:
        sec = int(frame / fps)
        frames_rem = int(frame % fps)
        mins = sec // 60
        secs = sec % 60
        hours = mins // 60
        mins = mins % 60
        self.tc_label.setText(f"{hours:02d}:{mins:02d}:{secs:02d}:{frames_rem:02d}")


class MotionWorkspace(QWidget):
    """Top-Level Motion (Edit / NLE) Workspace."""

    def __init__(self, state_graph: VibmoStateGraph, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self.state_graph = state_graph

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(4, 4, 4, 4)
        main_layout.setSpacing(4)

        # Master Vertical Splitter (Top Viewers / Bottom Timeline)
        v_splitter = QSplitter(Qt.Orientation.Vertical)

        # Top Horizontal Splitter: [Media Pool | Source Monitor | Master Monitor]
        top_splitter = QSplitter(Qt.Orientation.Horizontal)

        # 1. Media Pool Panel
        media_panel = QWidget()
        m_layout = QVBoxLayout(media_panel)
        m_layout.setContentsMargins(4, 4, 4, 4)
        m_layout.setSpacing(4)

        m_hdr = QHBoxLayout()
        m_title = QLabel("📂 Media Pool")
        m_title.setStyleSheet("font-weight: bold; color: #38BDF8; font-size: 13px;")
        import_btn = QPushButton("+ Import Media")
        import_btn.setObjectName("PrimaryBtn")
        import_btn.clicked.connect(self._import_media_dialog)

        m_hdr.addWidget(m_title)
        m_hdr.addStretch()
        m_hdr.addWidget(import_btn)
        m_layout.addLayout(m_hdr)

        self.tree = DraggableMediaTree(self)
        self.tree.setHeaderLabels(["Clip Name", "Type", "Resolution"])
        self.tree.header().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        m_layout.addWidget(self.tree)

        top_splitter.addWidget(media_panel)

        # 2. Dual Viewers
        self.source_monitor = SingleVideoMonitor("Source Clip Monitor")
        self.timeline_monitor = SingleVideoMonitor("Timeline Master Program")

        top_splitter.addWidget(self.source_monitor)
        top_splitter.addWidget(self.timeline_monitor)
        top_splitter.setSizes([340, 520, 520])

        v_splitter.addWidget(top_splitter)

        # Bottom Section: Timeline Toolbar + Interactive Timeline
        bottom_widget = QWidget()
        b_layout = QVBoxLayout(bottom_widget)
        b_layout.setContentsMargins(0, 0, 0, 0)
        b_layout.setSpacing(2)

        # Toolbar
        tb_layout = QHBoxLayout()
        add_v_btn = QPushButton("+ Video Track")
        add_v_btn.clicked.connect(self._add_video_track)
        add_a_btn = QPushButton("+ Audio Track")
        add_a_btn.clicked.connect(self._add_audio_track)
        razor_btn = QPushButton("✂ Razor Blade (B)")

        tb_layout.addWidget(add_v_btn)
        tb_layout.addWidget(add_a_btn)
        tb_layout.addWidget(razor_btn)
        tb_layout.addStretch()

        # Transport Buttons
        prev_btn = QPushButton("⏮")
        play_btn = QPushButton("▶ Play (Space)")
        play_btn.setObjectName("PrimaryBtn")
        next_btn = QPushButton("⏭")
        tb_layout.addWidget(prev_btn)
        tb_layout.addWidget(play_btn)
        tb_layout.addWidget(next_btn)

        b_layout.addLayout(tb_layout)

        # Interactive Timeline
        self.timeline = InteractiveTimelineWidget(self.state_graph)
        self.timeline.timecode_changed.connect(self._on_timecode_changed)
        b_layout.addWidget(self.timeline, 1)

        v_splitter.addWidget(bottom_widget)
        v_splitter.setSizes([450, 400])

        main_layout.addWidget(v_splitter)

        self.refresh_media_pool()
        self.state_graph.subscribe(self._on_state_event)

    def _import_media_dialog(self) -> None:
        files, _ = QFileDialog.getOpenFileNames(
            self,
            "Import Media Assets",
            "",
            "Media Files (*.mp4 *.mov *.webm *.png *.jpg *.jpeg *.svg *.mp3 *.wav *.cube *.ttf *.otf);;All Files (*)",
        )
        for f in files:
            self.state_graph.import_media(f)
        self.refresh_media_pool()

    def refresh_media_pool(self) -> None:
        self.tree.clear()
        for item in self.state_graph.project.media_pool:
            t_item = QTreeWidgetItem([
                item.name,
                item.kind.upper(),
                f"{item.width}x{item.height}" if item.width else "-",
            ])
            t_item.setData(0, Qt.ItemDataRole.UserRole, item.id)
            self.tree.addTopLevelItem(t_item)

    def _add_video_track(self) -> None:
        idx = len([t for t in self.state_graph.project.timeline.tracks if t.type == "video"]) + 1
        self.state_graph.add_track(f"Video {idx}", track_type="video")
        self.timeline.refresh_headers()

    def _add_audio_track(self) -> None:
        idx = len([t for t in self.state_graph.project.timeline.tracks if t.type == "audio"]) + 1
        self.state_graph.add_track(f"Audio {idx}", track_type="audio")
        self.timeline.refresh_headers()

    def _on_timecode_changed(self, frame: int) -> None:
        self.timeline_monitor.set_frame(frame, self.state_graph.project.fps)

    def _on_state_event(self, event_type: str, payload: dict) -> None:
        self.refresh_media_pool()
        self.timeline.refresh_headers()
