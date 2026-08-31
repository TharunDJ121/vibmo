"""
CapCut-Style Media & Asset Library Browser for Vibmo Desktop.
Features Ingestion Pills, Media Card Bins with Duration Badges, and Drag-and-Drop to Timeline.
"""

from __future__ import annotations
from typing import Any, Optional
from PySide6.QtCore import Qt, Signal, QMimeData
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QGridLayout,
    QLabel,
    QPushButton,
    QLineEdit,
    QScrollArea,
    QFrame,
    QFileDialog,
)
from PySide6.QtGui import QDrag, QPixmap, QColor, QFont, QMouseEvent

from vibmo.graph.engine import VibmoStateGraph
from vibmo.graph.schema import MediaItem


class MediaCardWidget(QFrame):
    """Visual media asset card with video thumbnail, duration badge, and draggable MIME data."""

    def __init__(self, media_item: MediaItem, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self.media_item = media_item
        self.setFixedSize(130, 95)
        self.setStyleSheet("""
            QFrame {
                background-color: #1A1A1E;
                border: 1px solid #28282D;
                border-radius: 6px;
            }
            QFrame:hover {
                border: 1px solid #00E5FF;
                background-color: #222228;
            }
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(2)

        # Thumbnail Surface
        thumb = QFrame()
        thumb.setStyleSheet("background-color: #0D0D10; border-radius: 4px;")
        t_layout = QVBoxLayout(thumb)
        t_layout.setContentsMargins(0, 0, 0, 0)
        t_layout.setSpacing(0)

        thumb_b64 = media_item.metadata.get("thumbnail_b64") if media_item.metadata else None
        if thumb_b64:
            import base64
            from PySide6.QtGui import QImage
            img_data = base64.b64decode(thumb_b64)
            qimg = QImage.fromData(img_data)
            thumb_pix = QPixmap.fromImage(qimg).scaled(120, 60, Qt.AspectRatioMode.KeepAspectRatioByExpanding, Qt.TransformationMode.SmoothTransformation)
            thumb_lbl = QLabel()
            thumb_lbl.setPixmap(thumb_pix)
            thumb_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            thumb_lbl.setStyleSheet("border-radius: 4px; border: none;")
            t_layout.addWidget(thumb_lbl)
        else:
            # Icon / Badge based on kind
            icons = {"video": "🎬", "audio": "🎵", "image": "🖼", "font": "🔤", "lut": "🎨"}
            icon_lbl = QLabel(icons.get(media_item.kind, "📁"))
            icon_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            icon_lbl.setStyleSheet("font-size: 18px; border: none;")
            t_layout.addWidget(icon_lbl)

        # Duration / Kind badge
        dur_str = media_item.metadata.get("duration_formatted") if media_item.metadata else None
        if not dur_str:
            dur_str = "VIDEO" if media_item.kind == "video" else media_item.kind.upper()
            
        dur_lbl = QLabel(dur_str)
        dur_lbl.setAlignment(Qt.AlignmentFlag.AlignRight)
        dur_lbl.setStyleSheet("color: #00E5FF; font-size: 9px; font-weight: bold; background: rgba(0,0,0,0.7); border-radius: 2px; padding: 1px 4px; margin: 2px;")
        t_layout.addWidget(dur_lbl)

        layout.addWidget(thumb, 1)

        # Name label
        name_lbl = QLabel(media_item.name)
        name_lbl.setStyleSheet("color: #ECECED; font-size: 10px; font-weight: 500;")
        layout.addWidget(name_lbl)

    def mousePressEvent(self, event: QMouseEvent) -> None:
        if event.button() == Qt.MouseButton.LeftButton:
            import json
            drag = QDrag(self)
            mime = QMimeData()
            payload = {
                "media_id": self.media_item.id,
                "name": self.media_item.name,
                "duration_frames": self.media_item.duration_frames or 120,
                "kind": self.media_item.kind,
            }
            mime.setText(json.dumps(payload))
            drag.setMimeData(mime)

            pix = QPixmap(100, 24)
            pix.fill(QColor("#00E5FF"))
            drag.setPixmap(pix)
            drag.exec(Qt.DropAction.CopyAction)


class CapCutMediaLibrary(QWidget):
    """Media Library & Category Browser Widget."""
    category_changed = Signal(str)

    def __init__(self, state_graph: VibmoStateGraph, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self.state_graph = state_graph

        layout = QVBoxLayout(self)
        layout.setContentsMargins(6, 6, 6, 6)
        layout.setSpacing(6)

        # Top Action Bar: [+ Import] [Record] [Search]
        top_bar = QHBoxLayout()
        top_bar.setSpacing(6)

        import_btn = QPushButton("+ Import")
        import_btn.setObjectName("PrimaryAction")
        import_btn.setFixedHeight(28)
        import_btn.clicked.connect(self._import_files)
        top_bar.addWidget(import_btn)

        record_btn = QPushButton("🎙 Record")
        record_btn.setFixedHeight(28)
        top_bar.addWidget(record_btn)

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("🔍 Search media...")
        self.search_input.setFixedHeight(28)
        top_bar.addWidget(self.search_input)

        layout.addLayout(top_bar)

        # Scrollable Cards Grid Area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("background: transparent; border: none;")

        self.grid_container = QWidget()
        self.grid_layout = QGridLayout(self.grid_container)
        self.grid_layout.setContentsMargins(2, 2, 2, 2)
        self.grid_layout.setSpacing(8)

        scroll.setWidget(self.grid_container)
        layout.addWidget(scroll, 1)

        self.refresh_cards()

    def _import_files(self) -> None:
        files, _ = QFileDialog.getOpenFileNames(
            self,
            "Import Media Assets",
            "",
            "Media Files (*.mp4 *.mov *.webm *.png *.jpg *.jpeg *.svg *.mp3 *.wav *.cube *.ttf *.otf);;All Files (*)",
        )
        for f in files:
            self.state_graph.import_media(f)
        self.refresh_cards()

    def refresh_cards(self) -> None:
        # Clear grid
        while self.grid_layout.count():
            item = self.grid_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        items = self.state_graph.project.media_pool
        cols = 2
        for idx, m in enumerate(items):
            card = MediaCardWidget(m, self)
            row = idx // cols
            col = idx % cols
            self.grid_layout.addWidget(card, row, col)

        self.grid_layout.setRowStretch(len(items) // cols + 1, 1)
