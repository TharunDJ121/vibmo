"""
CapCut-Style Player Viewport with 16:9 Video Canvas, Real-Time Video Decoding,
Fast Proxy Frame Rasterization, Strict LRU Frame Cache, Timecode Readout, and Async Rendering.
"""

from __future__ import annotations
import os
from typing import Any, Dict, Optional, Tuple
from collections import OrderedDict
import numpy as np
from PySide6.QtCore import Qt, Signal, QTimer, QThread
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QComboBox,
    QFrame,
)
from PySide6.QtGui import QFont, QColor, QImage, QPixmap

from vibmo.graph.engine import VibmoStateGraph


from threading import RLock


class VideoClipDecoder:
    """Fast frame decoder for video media files on the timeline with stream caching."""
    def __init__(self):
        self._caps: Dict[str, Any] = {}
        self._lock = RLock()

    def get_capture(self, file_path: str):
        with self._lock:
            if not os.path.exists(file_path):
                return None
            if file_path not in self._caps:
                try:
                    import cv2
                    cap = cv2.VideoCapture(file_path)
                    if cap.isOpened():
                        self._caps[file_path] = cap
                except Exception as e:
                    print(f"[Decoder] Failed to open video {file_path}: {e}")
                    return None
            return self._caps.get(file_path)

    def extract_frame(self, file_path: str, frame_num: int, target_w: Optional[int] = None, target_h: Optional[int] = None) -> Optional[QImage]:
        with self._lock:
            cap = self.get_capture(file_path)
            if not cap:
                return None
            try:
                import cv2
                cap.set(cv2.CAP_PROP_POS_FRAMES, max(0, frame_num))
                ret, frame = cap.read()
                if not ret or frame is None:
                    return None
                
                if target_w and target_h:
                    frame = cv2.resize(frame, (target_w, target_h))

                rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                h, w, c = rgb.shape
                return QImage(rgb.data.tobytes(), w, h, w * c, QImage.Format.Format_RGB888).copy()
            except Exception as e:
                print(f"[Decoder] Frame extract error at {frame_num}: {e}")
                return None

    def release_all(self):
        with self._lock:
            for cap in self._caps.values():
                try:
                    cap.release()
                except Exception:
                    pass
            self._caps.clear()


_GLOBAL_DECODER = VideoClipDecoder()


class RenderWorker(QThread):
    """Background thread to handle heavy rasterization and timeline clip decoding asynchronously."""
    frame_ready = Signal(int, float, QImage, int, int) # frame, scale, qimage, w, h
    error_occurred = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.state_graph = None
        self.scene = None
        self.frame = 0
        self.fps = 60.0
        self.scale = 1.0
        self.is_running = True
        self.request_pending = False

    def request_render(self, state_graph: Any, scene: Any, frame: int, fps: float, scale: float):
        self.state_graph = state_graph
        self.scene = scene
        self.frame = frame
        self.fps = fps
        self.scale = scale
        self.request_pending = True
        if not self.isRunning():
            self.start()

    def run(self):
        while self.is_running and self.request_pending:
            self.request_pending = False
            
            try:
                # 1. First priority: Render from Python scene graph if available
                if self.scene:
                    t = float(self.frame) / max(1.0, self.fps)
                    t = min(self.scene.duration, t)
                    rgba = self.scene.render_frame(time=t, scale=self.scale)
                    h, w, c = rgba.shape
                    qimg = QImage(rgba.data.tobytes(), w, h, w * 4, QImage.Format.Format_RGBA8888).copy()
                    if not self.request_pending:
                        self.frame_ready.emit(self.frame, self.scale, qimg, w, h)
                    continue

                # 2. Second priority: Evaluate NLE Timeline video clips
                if self.state_graph and hasattr(self.state_graph, "project") and self.state_graph.project.timeline.clips:
                    active_clip = None
                    # Find clip covering the current frame (reverse track order for top-layer priority)
                    for clip in sorted(self.state_graph.project.timeline.clips.values(), key=lambda c: c.start_frame):
                        if clip.start_frame <= self.frame < clip.start_frame + clip.duration_frames:
                            active_clip = clip
                            break

                    if active_clip and active_clip.media_id:
                        media = next((m for m in self.state_graph.project.media_pool if m.id == active_clip.media_id), None)
                        if media and media.file_path and os.path.exists(media.file_path):
                            if media.kind == "video":
                                src_f = int((active_clip.source_in_frame or 0) + (self.frame - active_clip.start_frame))
                                qimg = _GLOBAL_DECODER.extract_frame(media.file_path, src_f)
                                if qimg and not self.request_pending:
                                    self.frame_ready.emit(self.frame, self.scale, qimg, qimg.width(), qimg.height())
                                    continue
                            elif media.kind == "image":
                                from PySide6.QtGui import QImageReader
                                reader = QImageReader(media.file_path)
                                qimg = reader.read()
                                if not qimg.isNull() and not self.request_pending:
                                    self.frame_ready.emit(self.frame, self.scale, qimg, qimg.width(), qimg.height())
                                    continue

            except Exception as e:
                self.error_occurred.emit(str(e))
                
    def stop(self):
        self.is_running = False
        self.wait()


class CapCutPlayer(QFrame):
    """Clean 16:9 Dedicated Video Player with Fast Proxy Rasterization & Real Video Clip Decoding."""
    play_toggled = Signal(bool)
    frame_rendered = Signal(int)

    def __init__(self, state_graph: Optional[VibmoStateGraph] = None, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self.state_graph = state_graph
        self.setStyleSheet("background-color: #0E0E10; border: 1px solid #27272A; border-radius: 6px;")

        self.current_frame = 0
        self.is_playing = False
        self.proxy_scale = 0.5  # Fast 540p proxy by default for 60 FPS smooth scrubbing
        
        # Strict LRU Cache
        self._frame_cache: OrderedDict[Tuple[int, float], QPixmap] = OrderedDict()
        self._max_cache_size = 200

        # Background Worker
        self.worker = RenderWorker(self)
        self.worker.frame_ready.connect(self._on_frame_rendered)
        self.worker.error_occurred.connect(self._on_render_error)

        # Playback timer
        self.play_timer = QTimer(self)
        self.play_timer.timeout.connect(self._on_play_timer_tick)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(6, 6, 6, 6)
        layout.setSpacing(4)

        # Header Title
        hdr = QHBoxLayout()
        p_title = QLabel("Player — Program Monitor")
        p_title.setStyleSheet("font-weight: 700; color: #A1A1AA; font-size: 11px; border: none;")
        hdr.addWidget(p_title)
        hdr.addStretch()

        self.res_badge = QLabel("1080p (540p Proxy) | 60.00 FPS")
        self.res_badge.setStyleSheet("color: #71717A; font-size: 10px; font-weight: bold; border: none;")
        hdr.addWidget(self.res_badge)

        layout.addLayout(hdr)

        # 16:9 Screen Surface
        self.screen_container = QFrame()
        self.screen_container.setStyleSheet("background-color: #000000; border: 1px solid #1C1C1F; border-radius: 4px;")
        sc_layout = QVBoxLayout(self.screen_container)
        sc_layout.setContentsMargins(0, 0, 0, 0)

        self.screen_label = QLabel()
        self.screen_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.screen_label.setStyleSheet("color: #52525B; font-size: 12px; font-weight: 500; border: none;")
        self.screen_label.setText("Import media or drag video clips to timeline to preview")
        sc_layout.addWidget(self.screen_label, 1)

        layout.addWidget(self.screen_container, 1)

        # Bottom Player Transport Toolbar
        b_bar = QHBoxLayout()
        b_bar.setContentsMargins(4, 2, 4, 2)
        b_bar.setSpacing(8)

        # Timecode
        self.timecode_label = QLabel("00:00:00:00 / 00:00:10:00")
        self.timecode_label.setStyleSheet("color: #0A84FF; font-family: monospace; font-weight: bold; font-size: 11px; border: none;")
        b_bar.addWidget(self.timecode_label)

        b_bar.addStretch()

        # Center Transport
        self.prev_btn = QPushButton("Prev")
        self.prev_btn.setFixedSize(48, 26)
        self.prev_btn.clicked.connect(self._step_prev)

        self.play_btn = QPushButton("Play")
        self.play_btn.setFixedSize(58, 26)
        self.play_btn.setObjectName("PrimaryBtn")
        self.play_btn.clicked.connect(self.toggle_playback)

        self.next_btn = QPushButton("Next")
        self.next_btn.setFixedSize(48, 26)
        self.next_btn.clicked.connect(self._step_next)

        b_bar.addWidget(self.prev_btn)
        b_bar.addWidget(self.play_btn)
        b_bar.addWidget(self.next_btn)

        b_bar.addStretch()

        # Quality / Proxy Switcher
        self.qual_combo = QComboBox()
        self.qual_combo.addItems(["Half (540p Proxy)", "Draft (360p)", "Full (1080p Master)"])
        self.qual_combo.setFixedHeight(24)
        self.qual_combo.currentIndexChanged.connect(self._on_quality_changed)
        b_bar.addWidget(self.qual_combo)

        self.ratio_combo = QComboBox()
        self.ratio_combo.addItems(["Original (16:9)", "9:16 (Shorts/TikTok)", "1:1 (Square)", "4:5 (Instagram)"])
        self.ratio_combo.setFixedHeight(24)
        b_bar.addWidget(self.ratio_combo)

        fs_btn = QPushButton("Full")
        fs_btn.setFixedSize(42, 24)
        b_bar.addWidget(fs_btn)

        layout.addLayout(b_bar)

    def clear_cache(self) -> None:
        """Clears the frame rasterization cache."""
        self._frame_cache.clear()

    def _on_quality_changed(self, idx: int) -> None:
        if idx == 0:
            self.proxy_scale = 0.5
        elif idx == 1:
            self.proxy_scale = 0.333
        else:
            self.proxy_scale = 1.0
        self.clear_cache()
        self.render_frame_at(self.current_frame)

    def render_frame_at(self, frame: int) -> None:
        """Requests rendering of the frame using fast proxy cache, scene rasterization, or video clip decoder."""
        self.current_frame = max(0, frame)
        fps = self.state_graph.project.fps if self.state_graph else 60.0
        tot_f = self.state_graph.project.duration_frames if self.state_graph else 600

        self.set_timecode(self.current_frame, tot_f, fps)

        # 1. Check strict LRU Frame Cache for instant 0ms retrieval
        cache_key = (self.current_frame, self.proxy_scale)
        if cache_key in self._frame_cache:
            pix = self._frame_cache.pop(cache_key)
            self._frame_cache[cache_key] = pix
            self.screen_label.setPixmap(pix)
            self.frame_rendered.emit(self.current_frame)
            return

        # 2. Asynchronously request render from Scene or Timeline Video Clips
        scene = getattr(self.state_graph, "active_scene", None)
        self.worker.request_render(self.state_graph, scene, self.current_frame, fps, self.proxy_scale)

    def render_frame_sync(self, frame: int) -> None:
        """Synchronously renders the frame on calling thread."""
        self.current_frame = max(0, frame)
        fps = self.state_graph.project.fps if self.state_graph else 60.0
        tot_f = self.state_graph.project.duration_frames if self.state_graph else 600
        self.set_timecode(self.current_frame, tot_f, fps)

        scene = getattr(self.state_graph, "active_scene", None)
        if scene:
            t = min(scene.duration, float(self.current_frame) / max(1.0, fps))
            rgba = scene.render_frame(time=t, scale=self.proxy_scale)
            h, w, _ = rgba.shape
            qimg = QImage(rgba.data.tobytes(), w, h, w * 4, QImage.Format.Format_RGBA8888).copy()
            self._on_frame_rendered(self.current_frame, self.proxy_scale, qimg, w, h)
        elif self.state_graph and self.state_graph.project.timeline.clips:
            for clip in self.state_graph.project.timeline.clips.values():
                if clip.start_frame <= self.current_frame < clip.start_frame + clip.duration_frames:
                    if clip.media_id:
                        media = next((m for m in self.state_graph.project.media_pool if m.id == clip.media_id), None)
                        if media and media.file_path:
                            src_f = int((clip.source_in_frame or 0) + (self.current_frame - clip.start_frame))
                            qimg = _GLOBAL_DECODER.extract_frame(media.file_path, src_f)
                            if qimg:
                                self._on_frame_rendered(self.current_frame, self.proxy_scale, qimg, qimg.width(), qimg.height())
                                return

    def _on_frame_rendered(self, frame: int, scale: float, qimg: QImage, w: int, h: int) -> None:
        target_w = max(100, self.screen_container.width() - 4)
        target_h = max(60, self.screen_container.height() - 4)
        scaled = QPixmap.fromImage(qimg).scaled(
            target_w, target_h, Qt.AspectRatioMode.KeepAspectRatio, 
            Qt.TransformationMode.FastTransformation if self.is_playing else Qt.TransformationMode.SmoothTransformation
        )

        cache_key = (frame, scale)
        self._frame_cache[cache_key] = scaled
        if len(self._frame_cache) > self._max_cache_size:
            self._frame_cache.popitem(last=False)
            
        if frame == self.current_frame:
            self.screen_label.setPixmap(scaled)
            fps = self.state_graph.project.fps if self.state_graph else 60.0
            t = float(frame) / max(1.0, fps)
            
            orig_w = getattr(self.state_graph.active_scene, "width", w) if self.state_graph else w
            orig_h = getattr(self.state_graph.active_scene, "height", h) if self.state_graph else h
            self.res_badge.setText(f"{orig_w}x{orig_h} | {int(fps)} FPS • t={t:.2f}s")
            self.frame_rendered.emit(frame)

    def _on_render_error(self, err: str) -> None:
        self.screen_label.setText(f"Preview: {err}")

    def toggle_playback(self) -> None:
        """Toggles real-time video playback."""
        self.is_playing = not self.is_playing
        if self.is_playing:
            self.play_btn.setText("Pause")
            fps = self.state_graph.project.fps if self.state_graph else 60.0
            interval_ms = max(16, int(1000.0 / fps))
            self.play_timer.start(interval_ms)
        else:
            self.play_btn.setText("Play")
            self.play_timer.stop()
        self.play_toggled.emit(self.is_playing)

    def _on_play_timer_tick(self) -> None:
        tot_f = self.state_graph.project.duration_frames if self.state_graph else 600
        next_f = self.current_frame + 1
        if next_f >= tot_f:
            next_f = 0
        self.render_frame_at(next_f)

    def _step_prev(self) -> None:
        self.render_frame_at(max(0, self.current_frame - 1))

    def _step_next(self) -> None:
        tot_f = self.state_graph.project.duration_frames if self.state_graph else 600
        self.render_frame_at(min(tot_f, self.current_frame + 1))

    def set_timecode(self, current_frame: int, total_frames: int = 600, fps: float = 60.0) -> None:
        def fmt(f: int) -> str:
            sec = int(f / fps)
            fr = int(f % fps)
            mins = sec // 60
            secs = sec % 60
            hours = mins // 60
            return f"{hours:02d}:{mins % 60:02d}:{secs:02d}:{fr:02d}"

        self.timecode_label.setText(f"{fmt(current_frame)} / {fmt(total_frames)}")

    def closeEvent(self, event: Any) -> None:
        self.play_timer.stop()
        self.worker.stop()
        super().closeEvent(event)

