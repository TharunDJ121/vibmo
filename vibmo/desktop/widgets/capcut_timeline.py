"""
CapCut-Style Non-Linear Timeline for Vibmo Desktop.
Features Top Editing Toolbar (Undo, Split, Snapping, Zoom), CapCut-Style Track Icons,
Filmstrip Video Clips, Coral Caption Badges, Dynamic Duration Sizing, and Continuous Drag-Scrub Playhead.
"""

from __future__ import annotations
import math
from typing import Any, Dict, List, Optional
from PySide6.QtCore import Qt, Signal, QPointF, QRectF
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSlider,
    QGraphicsView,
    QGraphicsScene,
    QGraphicsItem,
    QGraphicsRectItem,
    QGraphicsTextItem,
    QFrame,
)
from PySide6.QtGui import (
    QPainter,
    QColor,
    QBrush,
    QPen,
    QFont,
    QPolygonF,
    QDragEnterEvent,
    QDropEvent,
)

from vibmo.graph.engine import VibmoStateGraph
from vibmo.graph.schema import TimelineClip, TimelineTrack


class CapCutPlayhead(QGraphicsItem):
    """CapCut clean vertical playhead with top scrubber handle."""

    def __init__(self, height: float = 300.0, parent: Optional[QGraphicsItem] = None) -> None:
        super().__init__(parent)
        self.height = height
        self.frame = 0
        self.pixels_per_frame = 3.0
        self.setZValue(200)

    def boundingRect(self) -> QRectF:
        return QRectF(-8, 0, 16, self.height)

    def paint(self, painter: QPainter, option: Any, widget: Optional[QWidget] = None) -> None:
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # White Scrubber Needle Handle
        poly = QPolygonF([
            QPointF(-6, 0),
            QPointF(6, 0),
            QPointF(6, 12),
            QPointF(0, 18),
            QPointF(-6, 12),
        ])
        painter.setBrush(QBrush(QColor("#FFFFFF")))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawPolygon(poly)

        # White vertical line spanning all tracks
        painter.setPen(QPen(QColor("#FFFFFF"), 1.5))
        painter.drawLine(0, 18, 0, int(self.height))

    def set_frame(self, frame: int) -> None:
        self.frame = max(0, frame)
        self.setPos(self.frame * self.pixels_per_frame, 0)


class CapCutVisualClip(QGraphicsRectItem):
    """CapCut visual clip item: Filmstrip style for video, coral badge for captions."""

    def __init__(
        self,
        clip: TimelineClip,
        track_type: str,
        track_index: int,
        track_height: float,
        pixels_per_frame: float,
        parent: Optional[QGraphicsItem] = None,
    ) -> None:
        self.clip = clip
        self.track_type = track_type
        self.track_index = track_index
        self.track_height = track_height
        self.pixels_per_frame = pixels_per_frame

        w = max(20.0, clip.duration_frames * pixels_per_frame)
        h = track_height - 6.0

        super().__init__(0, 0, w, h, parent)
        self.setPos(clip.start_frame * pixels_per_frame, track_index * track_height + 26.0)
        self.setFlags(
            QGraphicsItem.GraphicsItemFlag.ItemIsMovable |
            QGraphicsItem.GraphicsItemFlag.ItemIsSelectable |
            QGraphicsItem.GraphicsItemFlag.ItemSendsGeometryChanges
        )

        # Style based on clip color_tag or track type
        if clip.color_tag and clip.color_tag.startswith("#"):
            c = QColor(clip.color_tag)
            self.setBrush(QBrush(c))
            self.setPen(QPen(c.lighter(130), 1.2))
        elif "caption" in clip.name.lower() or track_type == "subtitle":
            self.setBrush(QBrush(QColor("#FF5A5F")))
            self.setPen(QPen(QColor("#FFA0A4"), 1.2))
        elif track_type == "audio":
            self.setBrush(QBrush(QColor("#059669")))
            self.setPen(QPen(QColor("#34D399"), 1.2))
        else:
            self.setBrush(QBrush(QColor("#0E7490")))
            self.setPen(QPen(QColor("#22D3EE"), 1.2))

        # Title Text Label
        prefix = "[A] " if "caption" in clip.name.lower() or track_type == "subtitle" else ""
        self.text_label = QGraphicsTextItem(f"{prefix}{clip.name}", self)
        self.text_label.setFont(QFont("Segoe UI", 9, QFont.Weight.Bold))
        self.text_label.setDefaultTextColor(QColor("#FFFFFF"))
        self.text_label.setPos(4, 4)

    def mouseReleaseEvent(self, event: Any) -> None:
        super().mouseReleaseEvent(event)
        new_frame = max(0, int(round(self.pos().x() / self.pixels_per_frame)))
        self.setPos(new_frame * self.pixels_per_frame, self.pos().y())
        self.clip.start_frame = new_frame


class CapCutTimelineScene(QGraphicsScene):
    """Interactive Timeline Scene with Dynamic Sizing and Real-Time Drag Scrubbing."""
    timecode_changed = Signal(int)

    def __init__(self, state_graph: VibmoStateGraph, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self.state_graph = state_graph
        self.setBackgroundBrush(QBrush(QColor("#101013")))

        self.pixels_per_frame = 3.0
        self.track_height = 48.0
        self.current_frame = 0
        self.total_frames = max(300, self.state_graph.project.duration_frames)

        self.playhead = CapCutPlayhead(height=350.0)
        self.playhead.pixels_per_frame = self.pixels_per_frame
        self.addItem(self.playhead)

        self.refresh_scene()

    def refresh_scene(self) -> None:
        self.total_frames = max(300, self.state_graph.project.duration_frames)
        self.playhead.pixels_per_frame = self.pixels_per_frame

        for item in list(self.items()):
            if item != self.playhead:
                self.removeItem(item)

        tracks = self.state_graph.project.timeline.tracks
        total_w = self.total_frames * self.pixels_per_frame
        total_h = len(tracks) * self.track_height + 40.0

        self.setSceneRect(0, 0, total_w + 300, max(260.0, total_h))
        self.playhead.height = max(260.0, total_h)

        # Time Ruler on top (Y = 0 to 22)
        self.addRect(0, 0, total_w + 300, 22, QPen(QColor("#24242A")), QBrush(QColor("#16161A")))
        fps = max(1.0, self.state_graph.project.fps)

        # Dynamic ruler interval based on zoom
        step_sec = 1 if self.pixels_per_frame >= 4.0 else (2 if self.pixels_per_frame >= 2.0 else 5)
        step_frames = max(1, int(fps * step_sec))

        for f in range(0, self.total_frames + step_frames, step_frames):
            x = f * self.pixels_per_frame
            self.addLine(x, 10, x, 22, QPen(QColor("#52525B"), 1))
            sec = int(f / fps)
            tc = f"00:{sec // 60:02d}:{sec % 60:02d}"
            lbl = self.addText(tc, QFont("Segoe UI", 7))
            lbl.setDefaultTextColor(QColor("#71717A"))
            lbl.setPos(x + 2, -1)

        # Tracks Background
        y_pos = 24.0
        for i, track in enumerate(tracks):
            bg = QColor("#17171C") if i % 2 == 0 else QColor("#131317")
            self.addRect(0, y_pos, total_w + 300, self.track_height, QPen(QColor("#24242A")), QBrush(bg))
            y_pos += self.track_height

        # Visual Clips
        for clip in self.state_graph.project.timeline.clips.values():
            track_idx = 0
            t_type = "video"
            for idx, t in enumerate(tracks):
                if t.id == clip.track_id:
                    track_idx = idx
                    t_type = t.type
                    break

            clip_item = CapCutVisualClip(
                clip=clip,
                track_type=t_type,
                track_index=track_idx,
                track_height=self.track_height,
                pixels_per_frame=self.pixels_per_frame,
            )
            self.addItem(clip_item)

        self.playhead.set_frame(self.current_frame)

    def mousePressEvent(self, event: Any) -> None:
        super().mousePressEvent(event)
        scene_pos = event.scenePos()
        frame = max(0, min(self.total_frames, int(round(scene_pos.x() / self.pixels_per_frame))))
        self.current_frame = frame
        self.playhead.set_frame(frame)
        self.timecode_changed.emit(frame)

    def mouseMoveEvent(self, event: Any) -> None:
        if event.buttons() & Qt.MouseButton.LeftButton:
            scene_pos = event.scenePos()
            frame = max(0, min(self.total_frames, int(round(scene_pos.x() / self.pixels_per_frame))))
            self.current_frame = frame
            self.playhead.set_frame(frame)
            self.timecode_changed.emit(frame)
        super().mouseMoveEvent(event)


class CapCutTimeline(QWidget):
    """Complete CapCut-Style Timeline Panel."""
    frame_changed = Signal(int)

    def __init__(self, state_graph: VibmoStateGraph, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self.state_graph = state_graph
        self.setAcceptDrops(True)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # 1. Top Action Toolbar (Undo, Redo, Split, Delete, Snapping, Zoom)
        toolbar = QFrame()
        toolbar.setFixedHeight(34)
        toolbar.setStyleSheet("background-color: #16161A; border-top: 1px solid #27272A; border-bottom: 1px solid #27272A;")
        tb_layout = QHBoxLayout(toolbar)
        tb_layout.setContentsMargins(8, 2, 8, 2)
        tb_layout.setSpacing(6)

        undo_btn = QPushButton("Undo")
        undo_btn.setFixedSize(46, 24)
        undo_btn.clicked.connect(self.state_graph.undo)
        redo_btn = QPushButton("Redo")
        redo_btn.setFixedSize(46, 24)
        redo_btn.clicked.connect(self.state_graph.redo)
        split_btn = QPushButton("Split (Ctrl+B)")
        split_btn.setFixedHeight(24)
        del_btn = QPushButton("Delete")
        del_btn.setFixedHeight(24)

        tb_layout.addWidget(undo_btn)
        tb_layout.addWidget(redo_btn)
        tb_layout.addWidget(split_btn)
        tb_layout.addWidget(del_btn)
        tb_layout.addStretch()

        # Right tools: Snapping, Auto-ripple, Zoom
        snap_btn = QPushButton("Snap")
        snap_btn.setCheckable(True)
        snap_btn.setChecked(True)
        snap_btn.setFixedSize(46, 24)
        tb_layout.addWidget(snap_btn)

        tb_layout.addWidget(QLabel("-"))
        self.zoom_slider = QSlider(Qt.Orientation.Horizontal)
        self.zoom_slider.setRange(1, 8)
        self.zoom_slider.setValue(3)
        self.zoom_slider.setFixedWidth(80)
        self.zoom_slider.valueChanged.connect(self._on_zoom_changed)
        tb_layout.addWidget(self.zoom_slider)
        tb_layout.addWidget(QLabel("+"))

        layout.addWidget(toolbar)

        # 2. Main Timeline Split: Left Track Headers & Right Graphic Canvas
        content_widget = QWidget()
        c_layout = QHBoxLayout(content_widget)
        c_layout.setContentsMargins(0, 0, 0, 0)
        c_layout.setSpacing(0)

        # Left Track Headers Sidebar
        self.headers_bar = QWidget()
        self.headers_bar.setFixedWidth(84)
        self.headers_bar.setStyleSheet("background-color: #141417; border-right: 1px solid #27272A;")
        self.headers_layout = QVBoxLayout(self.headers_bar)
        self.headers_layout.setContentsMargins(4, 26, 4, 4)
        self.headers_layout.setSpacing(4)
        c_layout.addWidget(self.headers_bar)

        # Right Graphics View
        self.scene = CapCutTimelineScene(self.state_graph, self)
        self.scene.timecode_changed.connect(self.frame_changed.emit)

        self.view = QGraphicsView(self.scene)
        self.view.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        self.view.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.view.setStyleSheet("background-color: #0E0E11; border: none;")
        self.view.setRenderHint(QPainter.RenderHint.Antialiasing)
        c_layout.addWidget(self.view, 1)

        layout.addWidget(content_widget, 1)

        self.refresh_headers()

    def refresh_headers(self) -> None:
        while self.headers_layout.count():
            item = self.headers_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        tracks = self.state_graph.project.timeline.tracks
        for track in tracks:
            t_frame = QFrame()
            t_frame.setFixedHeight(int(self.scene.track_height - 4))
            t_frame.setStyleSheet("background-color: #1B1B20; border-radius: 4px;")
            
            tf_layout = QHBoxLayout(t_frame)
            tf_layout.setContentsMargins(4, 2, 4, 2)
            tf_layout.setSpacing(2)

            icon = "[V]" if track.type == "video" else ("[A]" if track.type == "audio" else "[T]")
            lbl = QLabel(f"{icon} {track.name[:4]}")
            lbl.setStyleSheet("color: #0A84FF; font-weight: bold; font-size: 10px; border: none;")
            tf_layout.addWidget(lbl)

            lock_btn = QPushButton("L")
            lock_btn.setFixedSize(18, 18)
            lock_btn.setStyleSheet("border: 1px solid #2C2C30; font-size: 9px; padding: 0;")
            tf_layout.addWidget(lock_btn)

            self.headers_layout.addWidget(t_frame)

        self.headers_layout.addStretch()
        self.scene.refresh_scene()

    def _on_zoom_changed(self, val: int) -> None:
        self.scene.pixels_per_frame = float(val)
        self.scene.playhead.pixels_per_frame = float(val)
        self.scene.refresh_scene()

    def set_playhead_frame(self, frame: int) -> None:
        self.scene.current_frame = frame
        self.scene.playhead.set_frame(frame)

        # Auto-center / follow playhead during playback
        x_pos = frame * self.scene.pixels_per_frame
        view_w = self.view.viewport().width()
        sb = self.view.horizontalScrollBar()
        if x_pos > sb.value() + view_w - 40 or x_pos < sb.value():
            sb.setValue(int(x_pos - 50))

    # Drop ingestion from Media Library
    def dragEnterEvent(self, event: QDragEnterEvent) -> None:
        if event.mimeData().hasText():
            event.acceptProposedAction()

    def dropEvent(self, event: QDropEvent) -> None:
        media_id = event.mimeData().text()
        pos_y = event.position().y()
        track_idx = max(0, int((pos_y - 60.0) / self.scene.track_height))
        tracks = self.state_graph.project.timeline.tracks

        if track_idx < len(tracks):
            target_track = tracks[track_idx]
            media_name = "Clip"
            for m in self.state_graph.project.media_pool:
                if m.id == media_id:
                    media_name = m.name
                    break

            self.state_graph.add_clip(
                track_id=target_track.id,
                name=media_name,
                start_frame=self.scene.current_frame,
                duration_frames=120,
                media_id=media_id,
            )
            self.scene.refresh_scene()
            event.acceptProposedAction()
