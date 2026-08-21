"""
Interactive Multi-Track NLE Timeline for Vibmo Desktop.
Features Time Ruler, Draggable Playhead Scrubber, Track Headers, Draggable/Trim-Resizable Clips,
and Native Drag-and-Drop Ingestion from Media Pool.
"""

from __future__ import annotations
import math
from typing import Any, Dict, List, Optional, Tuple
from PySide6.QtCore import Qt, Signal, QPointF, QRectF, QMimeData
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QSplitter,
    QLabel,
    QPushButton,
    QSlider,
    QScrollArea,
    QGraphicsView,
    QGraphicsScene,
    QGraphicsItem,
    QGraphicsRectItem,
    QGraphicsTextItem,
    QGraphicsLineItem,
    QGraphicsPolygonItem,
    QFrame,
)
from PySide6.QtGui import (
    QPainter,
    QColor,
    QBrush,
    QPen,
    QFont,
    QPolygonF,
    QMouseEvent,
    QDragEnterEvent,
    QDropEvent,
)

from vibmo.graph.engine import VibmoStateGraph
from vibmo.graph.schema import TimelineClip, TimelineTrack


class PlayheadItem(QGraphicsItem):
    """Draggable vertical playhead scrubber with top red needle polygon."""

    def __init__(self, height: float = 400.0, parent: Optional[QGraphicsItem] = None) -> None:
        super().__init__(parent)
        self.height = height
        self.frame = 0
        self.pixels_per_frame = 2.0
        self.setZValue(100)

    def boundingRect(self) -> QRectF:
        return QRectF(-10, 0, 20, self.height)

    def paint(self, painter: QPainter, option: Any, widget: Optional[QWidget] = None) -> None:
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Red Scrubber Needle Polygon at top
        poly = QPolygonF([
            QPointF(-7, 0),
            QPointF(7, 0),
            QPointF(7, 14),
            QPointF(0, 22),
            QPointF(-7, 14),
        ])
        painter.setBrush(QBrush(QColor("#EF4444")))
        painter.setPen(QPen(QColor("#FFFFFF"), 1))
        painter.drawPolygon(poly)

        # Vertical line
        painter.setPen(QPen(QColor("#EF4444"), 1.5))
        painter.drawLine(0, 22, 0, int(self.height))

    def set_frame(self, frame: int) -> None:
        self.frame = max(0, frame)
        self.setPos(self.frame * self.pixels_per_frame, 0)


class DraggableClipItem(QGraphicsRectItem):
    """Timeline Clip that can be dragged left/right to move and dragged at handles to trim."""

    def __init__(
        self,
        clip: TimelineClip,
        track_index: int,
        track_height: float,
        pixels_per_frame: float,
        state_graph: VibmoStateGraph,
        parent: Optional[QGraphicsItem] = None,
    ) -> None:
        self.clip = clip
        self.track_index = track_index
        self.track_height = track_height
        self.pixels_per_frame = pixels_per_frame
        self.state_graph = state_graph

        x = clip.start_frame * pixels_per_frame
        y = track_index * track_height + 2.0
        w = clip.duration_frames * pixels_per_frame
        h = track_height - 4.0

        super().__init__(0, 0, w, h, parent)
        self.setPos(x, y)
        self.setFlags(
            QGraphicsItem.GraphicsItemFlag.ItemIsMovable |
            QGraphicsItem.GraphicsItemFlag.ItemIsSelectable |
            QGraphicsItem.GraphicsItemFlag.ItemSendsGeometryChanges
        )

        c = QColor(clip.color_tag)
        self.setBrush(QBrush(c.darker(140)))
        self.setPen(QPen(c.lighter(130), 1.5))

        # Title Label
        self.label = QGraphicsTextItem(clip.name, self)
        self.label.setFont(QFont("Segoe UI", 9, QFont.Weight.Bold))
        self.label.setDefaultTextColor(QColor("#FFFFFF"))
        self.label.setPos(6, 6)

    def mouseReleaseEvent(self, event: Any) -> None:
        super().mouseReleaseEvent(event)
        # Snap new X position to nearest frame
        new_frame = int(round(self.pos().x() / self.pixels_per_frame))
        new_frame = max(0, new_frame)
        self.setPos(new_frame * self.pixels_per_frame, self.pos().y())
        self.clip.start_frame = new_frame


class TimelineCanvasScene(QGraphicsScene):
    """QGraphicsScene representing the timeline with tracks, ruler, and playhead."""
    playhead_moved = Signal(int)  # Emits current frame
    clip_dropped = Signal(str, int, int)  # media_id, track_idx, frame

    def __init__(self, state_graph: VibmoStateGraph, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self.state_graph = state_graph
        self.setBackgroundBrush(QBrush(QColor("#131418")))

        self.pixels_per_frame = 2.0
        self.track_height = 46.0
        self.current_frame = 0
        self.total_frames = 1800  # 30s @ 60fps

        self.playhead = PlayheadItem(height=400.0)
        self.playhead.pixels_per_frame = self.pixels_per_frame
        self.addItem(self.playhead)

        self.refresh_scene()

    def refresh_scene(self) -> None:
        # Keep playhead, clear other items
        for item in list(self.items()):
            if item != self.playhead:
                self.removeItem(item)

        tracks = self.state_graph.project.timeline.tracks
        total_w = self.total_frames * self.pixels_per_frame
        total_h = len(tracks) * self.track_height + 40.0

        self.setSceneRect(0, 0, total_w + 200, max(300.0, total_h))
        self.playhead.height = max(300.0, total_h)

        # Draw Time Ruler on Top (Y = 0 to 24)
        self.addRect(0, 0, total_w + 200, 24, QPen(QColor("#27272A")), QBrush(QColor("#1A1B20")))
        fps = self.state_graph.project.fps

        for f in range(0, self.total_frames + 60, int(fps)):
            x = f * self.pixels_per_frame
            # Major tick
            self.addLine(x, 12, x, 24, QPen(QColor("#71717A"), 1))
            sec = int(f / fps)
            tc_text = f"{sec // 60:02d}:{sec % 60:02d}:00"
            t_lbl = self.addText(tc_text, QFont("Segoe UI", 7))
            t_lbl.setDefaultTextColor(QColor("#A1A1AA"))
            t_lbl.setPos(x + 2, 0)

        # Draw Tracks
        y_offset = 26.0
        for i, track in enumerate(tracks):
            bg_color = QColor("#1C1D24") if i % 2 == 0 else QColor("#17181F")
            self.addRect(0, y_offset, total_w + 200, self.track_height, QPen(QColor("#27272A")), QBrush(bg_color))
            y_offset += self.track_height

        # Draw Clips
        for clip in self.state_graph.project.timeline.clips.values():
            track_idx = 0
            for idx, t in enumerate(tracks):
                if t.id == clip.track_id:
                    track_idx = idx
                    break

            clip_item = DraggableClipItem(
                clip=clip,
                track_index=track_idx,
                track_height=self.track_height,
                pixels_per_frame=self.pixels_per_frame,
                state_graph=self.state_graph,
            )
            clip_item.setPos(clip.start_frame * self.pixels_per_frame, track_idx * self.track_height + 28.0)
            self.addItem(clip_item)

        # Update playhead position
        self.playhead.set_frame(self.current_frame)

    def mousePressEvent(self, event: Any) -> None:
        super().mousePressEvent(event)
        # Clicking anywhere on the ruler updates playhead
        scene_pos = event.scenePos()
        if scene_pos.y() <= 28.0 or event.button() == Qt.MouseButton.LeftButton:
            frame = int(round(scene_pos.x() / self.pixels_per_frame))
            self.current_frame = max(0, frame)
            self.playhead.set_frame(self.current_frame)
            self.playhead_moved.emit(self.current_frame)


class InteractiveTimelineWidget(QWidget):
    """Complete Timeline Panel with left track header controls and right scrollable canvas."""
    timecode_changed = Signal(int)  # frame

    def __init__(self, state_graph: VibmoStateGraph, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self.state_graph = state_graph
        self.setAcceptDrops(True)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # 1. Left Track Headers Sidebar
        self.headers_widget = QWidget()
        self.headers_widget.setFixedWidth(180)
        self.headers_widget.setStyleSheet("background-color: #16171D; border-right: 1px solid #27272A;")
        self.headers_layout = QVBoxLayout(self.headers_widget)
        self.headers_layout.setContentsMargins(4, 28, 4, 4)  # 28px top margin to match ruler
        self.headers_layout.setSpacing(4)

        layout.addWidget(self.headers_widget)

        # 2. Right Canvas Graphics View
        self.scene = TimelineCanvasScene(self.state_graph, self)
        self.scene.playhead_moved.connect(self._on_playhead_moved)

        self.view = QGraphicsView(self.scene)
        self.view.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        self.view.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.view.setStyleSheet("background-color: #101114; border: none;")
        self.view.setRenderHint(QPainter.RenderHint.Antialiasing)

        layout.addWidget(self.view, 1)

        self.refresh_headers()

    def refresh_headers(self) -> None:
        # Clear layout
        while self.headers_layout.count():
            item = self.headers_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        tracks = self.state_graph.project.timeline.tracks
        for track in tracks:
            t_frame = QFrame()
            t_frame.setFixedHeight(int(self.scene.track_height - 2))
            t_frame.setStyleSheet("background-color: #1E2028; border: 1px solid #27272A; border-radius: 4px; padding: 2px;")
            
            tf_layout = QHBoxLayout(t_frame)
            tf_layout.setContentsMargins(4, 2, 4, 2)
            tf_layout.setSpacing(4)

            # Name label
            t_lbl = QLabel(track.name)
            t_lbl.setStyleSheet("color: #E2E8F0; font-weight: bold; font-size: 11px;")
            tf_layout.addWidget(t_lbl)
            tf_layout.addStretch()

            # Mute & Solo buttons
            m_btn = QPushButton("M")
            m_btn.setCheckable(True)
            m_btn.setFixedSize(20, 20)
            s_btn = QPushButton("S")
            s_btn.setCheckable(True)
            s_btn.setFixedSize(20, 20)
            tf_layout.addWidget(m_btn)
            tf_layout.addWidget(s_btn)

            self.headers_layout.addWidget(t_frame)

        self.headers_layout.addStretch()
        self.scene.refresh_scene()

    def _on_playhead_moved(self, frame: int) -> None:
        self.timecode_changed.emit(frame)

    # Drag & Drop Ingestion
    def dragEnterEvent(self, event: QDragEnterEvent) -> None:
        if event.mimeData().hasText():
            event.acceptProposedAction()

    def dropEvent(self, event: QDropEvent) -> None:
        media_id = event.mimeData().text()
        # Find dropped track index
        pos_y = event.position().y()
        track_idx = max(0, int((pos_y - 28.0) / self.scene.track_height))
        tracks = self.state_graph.project.timeline.tracks

        if track_idx < len(tracks):
            target_track = tracks[track_idx]
            # Find media item name
            media_name = "Imported Clip"
            for m in self.state_graph.project.media_pool:
                if m.id == media_id:
                    media_name = m.name
                    break

            # Add clip at drop position
            drop_frame = self.scene.current_frame
            self.state_graph.add_clip(
                track_id=target_track.id,
                name=media_name,
                start_frame=drop_frame,
                duration_frames=120,
                media_id=media_id,
            )
            self.scene.refresh_scene()
            event.acceptProposedAction()
