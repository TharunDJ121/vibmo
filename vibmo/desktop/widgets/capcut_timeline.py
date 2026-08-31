"""
CapCut-Style Non-Linear Magnetic Timeline for Vibmo Desktop.
Features Magnetic Snap-to-Playhead & Adjacent Clips, Filmstrip Clip Rendering,
Visual Alignment Guides, Split (Ctrl+B), Ripple Delete, and Dynamic Duration Sizing.
"""

from __future__ import annotations
import math
import json
from typing import Any, Dict, List, Optional, Tuple
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
    QGraphicsLineItem,
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
    QPainterPath,
    QPixmap,
    QImage,
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
        return QRectF(-10, 0, 20, self.height)

    def paint(self, painter: QPainter, option: Any, widget: Optional[QWidget] = None) -> None:
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # White Scrubber Needle Handle
        poly = QPolygonF([
            QPointF(-7, 0),
            QPointF(7, 0),
            QPointF(7, 13),
            QPointF(0, 20),
            QPointF(-7, 13),
        ])
        painter.setBrush(QBrush(QColor("#FFFFFF")))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawPolygon(poly)

        # White vertical line spanning all tracks
        painter.setPen(QPen(QColor("#FFFFFF"), 1.8))
        painter.drawLine(0, 20, 0, int(self.height))

    def set_frame(self, frame: int) -> None:
        self.frame = max(0, frame)
        self.setPos(self.frame * self.pixels_per_frame, 0)


class CapCutVisualClip(QGraphicsRectItem):
    """Magnetic visual clip item with filmstrip look, duration tag, and drag-and-drop snapping."""

    def __init__(
        self,
        clip: TimelineClip,
        track_type: str,
        track_index: int,
        track_height: float,
        pixels_per_frame: float,
        scene_ref: CapCutTimelineScene,
        parent: Optional[QGraphicsItem] = None,
    ) -> None:
        self.clip = clip
        self.track_type = track_type
        self.track_index = track_index
        self.track_height = track_height
        self.pixels_per_frame = pixels_per_frame
        self.scene_ref = scene_ref

        w = max(24.0, clip.duration_frames * pixels_per_frame)
        h = track_height - 6.0

        super().__init__(0, 0, w, h, parent)
        self.setPos(clip.start_frame * pixels_per_frame, track_index * track_height + 26.0)
        self.setFlags(
            QGraphicsItem.GraphicsItemFlag.ItemIsMovable |
            QGraphicsItem.GraphicsItemFlag.ItemIsSelectable |
            QGraphicsItem.GraphicsItemFlag.ItemSendsGeometryChanges
        )
        self.setZValue(10)

    def paint(self, painter: QPainter, option: Any, widget: Optional[QWidget] = None) -> None:
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        rect = self.rect()
        path = QPainterPath()
        path.addRoundedRect(rect, 5.0, 5.0)

        # 1. Base Gradient & Fill
        if self.track_type == "audio":
            bg_color = QColor("#065F46")
            border_color = QColor("#10B981")
        elif "caption" in self.clip.name.lower() or self.track_type == "subtitle":
            bg_color = QColor("#9F1239")
            border_color = QColor("#F43F5E")
        else:
            bg_color = QColor("#1E1B4B") if self.clip.color_tag else QColor("#1E3A8A")
            border_color = QColor("#3B82F6")

        if self.isSelected():
            border_color = QColor("#00E5FF")

        painter.fillPath(path, QBrush(bg_color))

        # 2. Draw Filmstrip pattern for Video clips or Waveform for Audio
        if self.track_type == "video" and rect.width() > 60:
            painter.setPen(QPen(QColor(255, 255, 255, 15), 1))
            # Filmstrip sprocket dividers
            step_px = 64.0
            x = step_px
            while x < rect.width() - 20:
                painter.drawLine(int(x), 4, int(x), int(rect.height() - 4))
                x += step_px
        elif self.track_type == "audio":
            # Audio waveform peak simulation
            painter.setPen(QPen(QColor(52, 211, 153, 120), 1.5))
            cy = rect.height() / 2.0
            x = 8
            while x < rect.width() - 8:
                h = 3.0 + 8.0 * math.sin(x * 0.2) + 6.0 * math.cos(x * 0.08)
                painter.drawLine(int(x), int(cy - abs(h)), int(x), int(cy + abs(h)))
                x += 4

        # 3. Clip Header & Duration Label
        painter.setPen(QPen(QColor("#FFFFFF")))
        painter.setFont(QFont("Segoe UI", 9, QFont.Weight.Bold))
        icon = "🎬 " if self.track_type == "video" else ("🎵 " if self.track_type == "audio" else "💬 ")
        painter.drawText(QRectF(8, 4, rect.width() - 16, 18), Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter, f"{icon}{self.clip.name}")

        fps = max(1.0, self.scene_ref.state_graph.project.fps)
        dur_sec = self.clip.duration_frames / fps
        dur_text = f"{dur_sec:.2f}s"
        painter.setFont(QFont("Segoe UI", 8))
        painter.setPen(QPen(QColor("#93C5FD") if self.track_type == "video" else QColor("#A7F3D0")))
        painter.drawText(QRectF(8, rect.height() - 18, rect.width() - 16, 14), Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter, dur_text)

        # 4. Left and Right Trim Handle Bars
        if self.isSelected():
            painter.setBrush(QBrush(QColor("#00E5FF")))
            painter.setPen(Qt.PenStyle.NoPen)
            # Left pill handle
            painter.drawRoundedRect(QRectF(0, 0, 4, rect.height()), 2, 2)
            # Right pill handle
            painter.drawRoundedRect(QRectF(rect.width() - 4, 0, 4, rect.height()), 2, 2)

        # 5. Border
        pen_width = 2.0 if self.isSelected() else 1.2
        painter.setPen(QPen(border_color, pen_width, Qt.PenStyle.SolidLine if not self.isSelected() else Qt.PenStyle.DashLine))
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawPath(path)

    def mouseMoveEvent(self, event: Any) -> None:
        super().mouseMoveEvent(event)
        raw_frame = max(0, int(round(self.pos().x() / self.pixels_per_frame)))
        if self.scene_ref.snapping_enabled:
            snapped_frame, guide_x = self.scene_ref.get_snap_target(raw_frame, self.clip.duration_frames, exclude_clip_id=self.clip.id)
            if guide_x is not None:
                self.scene_ref.show_snap_guide(guide_x)
            else:
                self.scene_ref.hide_snap_guide()
        else:
            self.scene_ref.hide_snap_guide()

    def mouseReleaseEvent(self, event: Any) -> None:
        super().mouseReleaseEvent(event)
        self.scene_ref.hide_snap_guide()
        raw_frame = max(0, int(round(self.pos().x() / self.pixels_per_frame)))
        
        # Apply magnetic snapping on release
        if self.scene_ref.snapping_enabled:
            snapped_frame, _ = self.scene_ref.get_snap_target(raw_frame, self.clip.duration_frames, exclude_clip_id=self.clip.id)
            new_frame = snapped_frame
        else:
            new_frame = raw_frame

        self.setPos(new_frame * self.pixels_per_frame, self.track_index * self.track_height + 26.0)
        self.clip.start_frame = new_frame


class CapCutTimelineScene(QGraphicsScene):
    """Interactive Timeline Scene with Dynamic Sizing, Real-Time Drag Scrubbing & Magnetic Snapping."""
    timecode_changed = Signal(int)

    def __init__(self, state_graph: VibmoStateGraph, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self.state_graph = state_graph
        self.setBackgroundBrush(QBrush(QColor("#101013")))

        self.pixels_per_frame = 3.0
        self.track_height = 52.0
        self.current_frame = 0
        self.total_frames = max(300, self.state_graph.project.duration_frames)
        self.snapping_enabled = True

        # Magnetic Snap Guide Line
        self.snap_guide = QGraphicsLineItem()
        self.snap_guide.setPen(QPen(QColor("#00E5FF"), 1.5, Qt.PenStyle.DashLine))
        self.snap_guide.setZValue(150)
        self.snap_guide.setVisible(False)
        self.addItem(self.snap_guide)

        self.playhead = CapCutPlayhead(height=350.0)
        self.playhead.pixels_per_frame = self.pixels_per_frame
        self.addItem(self.playhead)

        self.refresh_scene()

    def show_snap_guide(self, x_pos: float) -> None:
        self.snap_guide.setLine(x_pos, 0, x_pos, self.sceneRect().height())
        self.snap_guide.setVisible(True)

    def hide_snap_guide(self) -> None:
        self.snap_guide.setVisible(False)

    def get_snap_target(self, target_frame: int, clip_duration: int, exclude_clip_id: Optional[str] = None) -> Tuple[int, Optional[float]]:
        """Magnetic snapping algorithm to playhead, zero point, and adjacent clip edges."""
        if not self.snapping_enabled:
            return target_frame, None

        snap_tolerance_frames = max(4, int(15.0 / max(0.5, self.pixels_per_frame)))
        candidates = [0, self.current_frame]

        for c in self.state_graph.project.timeline.clips.values():
            if c.id != exclude_clip_id:
                candidates.append(c.start_frame)
                candidates.append(c.start_frame + c.duration_frames)

        # 1. Check if clip start snaps to any candidate
        best_snap = None
        min_dist = snap_tolerance_frames + 1

        for cand in candidates:
            dist = abs(target_frame - cand)
            if dist <= snap_tolerance_frames and dist < min_dist:
                min_dist = dist
                best_snap = (cand, cand * self.pixels_per_frame)

        # 2. Check if clip end snaps to any candidate
        clip_end = target_frame + clip_duration
        for cand in candidates:
            dist = abs(clip_end - cand)
            if dist <= snap_tolerance_frames and dist < min_dist:
                min_dist = dist
                snapped_start = cand - clip_duration
                best_snap = (snapped_start, cand * self.pixels_per_frame)

        if best_snap:
            return best_snap[0], best_snap[1]

        return target_frame, None

    def refresh_scene(self) -> None:
        # Calculate maximum duration from clips or project duration
        max_clip_end = self.state_graph.project.duration_frames
        for c in self.state_graph.project.timeline.clips.values():
            max_clip_end = max(max_clip_end, c.start_frame + c.duration_frames + 60)

        self.total_frames = max(300, max_clip_end)
        self.state_graph.project.duration_frames = self.total_frames
        self.playhead.pixels_per_frame = self.pixels_per_frame

        # Clear existing items except playhead and guide
        for item in list(self.items()):
            if item not in (self.playhead, self.snap_guide):
                self.removeItem(item)

        tracks = self.state_graph.project.timeline.tracks
        total_w = self.total_frames * self.pixels_per_frame
        total_h = len(tracks) * self.track_height + 40.0

        self.setSceneRect(0, 0, total_w + 300, max(260.0, total_h))
        self.playhead.height = max(260.0, total_h)

        # Time Ruler on top (Y = 0 to 22)
        self.addRect(0, 0, total_w + 300, 22, QPen(QColor("#24242A")), QBrush(QColor("#16161A")))
        fps = max(1.0, self.state_graph.project.fps)

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
                scene_ref=self,
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
    """Complete CapCut-Style Magnetic Timeline Panel."""
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
        undo_btn.setFixedSize(50, 24)
        undo_btn.clicked.connect(self.state_graph.undo)
        
        redo_btn = QPushButton("Redo")
        redo_btn.setFixedSize(50, 24)
        redo_btn.clicked.connect(self.state_graph.redo)
        
        split_btn = QPushButton("Split (Ctrl+B)")
        split_btn.setFixedHeight(24)
        split_btn.setStyleSheet("background-color: #27272A; color: #00E5FF; font-weight: bold;")
        split_btn.clicked.connect(self.split_at_playhead)

        del_btn = QPushButton("Delete")
        del_btn.setFixedHeight(24)
        del_btn.setStyleSheet("background-color: #27272A; color: #F43F5E;")
        del_btn.clicked.connect(self.delete_selected_clip)

        tb_layout.addWidget(undo_btn)
        tb_layout.addWidget(redo_btn)
        tb_layout.addWidget(split_btn)
        tb_layout.addWidget(del_btn)
        tb_layout.addStretch()

        # Right tools: Snapping Magnet Toggle, Zoom
        self.snap_btn = QPushButton("🧲 Magnet")
        self.snap_btn.setCheckable(True)
        self.snap_btn.setChecked(True)
        self.snap_btn.setFixedSize(70, 24)
        self.snap_btn.setStyleSheet("color: #00E5FF; font-weight: bold;")
        self.snap_btn.toggled.connect(self._toggle_snapping)
        tb_layout.addWidget(self.snap_btn)

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

    def _toggle_snapping(self, checked: bool) -> None:
        self.scene.snapping_enabled = checked
        self.snap_btn.setStyleSheet(f"color: {'#00E5FF' if checked else '#71717A'}; font-weight: bold;")

    def split_at_playhead(self) -> None:
        """Splits the clip currently under playhead or selected clip."""
        cur_frame = self.scene.current_frame
        target_clip = None

        # Check selected items first
        for item in self.scene.selectedItems():
            if isinstance(item, CapCutVisualClip):
                c = item.clip
                if c.start_frame < cur_frame < c.start_frame + c.duration_frames:
                    target_clip = c
                    break

        # If none selected, find clip under playhead
        if not target_clip:
            for c in self.state_graph.project.timeline.clips.values():
                if c.start_frame < cur_frame < c.start_frame + c.duration_frames:
                    target_clip = c
                    break

        if target_clip:
            try:
                self.state_graph.split_clip(target_clip.id, cur_frame)
                self.scene.refresh_scene()
            except Exception as e:
                print(f"[Timeline] Split error: {e}")

    def delete_selected_clip(self) -> None:
        """Deletes selected clip(s) from the timeline."""
        selected_ids = []
        for item in self.scene.selectedItems():
            if isinstance(item, CapCutVisualClip):
                selected_ids.append(item.clip.id)

        if selected_ids:
            self.state_graph._push_undo_snapshot()
            for cid in selected_ids:
                if cid in self.state_graph.project.timeline.clips:
                    del self.state_graph.project.timeline.clips[cid]
            self.scene.refresh_scene()

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

        # Auto-follow playhead during playback
        x_pos = frame * self.scene.pixels_per_frame
        view_w = self.view.viewport().width()
        sb = self.view.horizontalScrollBar()
        if x_pos > sb.value() + view_w - 40 or x_pos < sb.value():
            sb.setValue(int(x_pos - 50))

    # Drop ingestion with Magnetic Snapping from Media Library
    def dragEnterEvent(self, event: QDragEnterEvent) -> None:
        if event.mimeData().hasText():
            event.acceptProposedAction()

    def dropEvent(self, event: QDropEvent) -> None:
        raw_text = event.mimeData().text()
        media_id = raw_text
        media_name = "Clip"
        clip_dur = 120

        try:
            payload = json.loads(raw_text)
            if isinstance(payload, dict):
                media_id = payload.get("media_id", raw_text)
                media_name = payload.get("name", "Clip")
                clip_dur = payload.get("duration_frames", 120)
        except Exception:
            pass

        # Look up media item
        for m in self.state_graph.project.media_pool:
            if m.id == media_id:
                media_name = m.name
                if m.duration_frames:
                    clip_dur = m.duration_frames
                break

        pos_y = event.position().y()
        track_idx = max(0, int((pos_y - 60.0) / self.scene.track_height))
        tracks = self.state_graph.project.timeline.tracks

        if track_idx < len(tracks):
            target_track = tracks[track_idx]
            
            # Magnetically snap drop position to playhead or adjacent clips
            drop_x = event.position().x() + self.view.horizontalScrollBar().value()
            target_frame = max(0, int(round(drop_x / self.scene.pixels_per_frame)))
            
            if self.scene.snapping_enabled:
                snapped_frame, _ = self.scene.get_snap_target(target_frame, clip_dur)
                final_frame = snapped_frame
            else:
                final_frame = target_frame

            self.state_graph.add_clip(
                track_id=target_track.id,
                name=media_name,
                start_frame=final_frame,
                duration_frames=clip_dur,
                media_id=media_id,
            )
            self.scene.refresh_scene()
            self.frame_changed.emit(final_frame)
            event.acceptProposedAction()
