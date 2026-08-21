"""
Fusion Shift+Space Command Palette (Select Tool Dialog) for Vibmo Desktop.
Opens a sleek Spotlight-style search modal to quickly insert Fusion VFX nodes at cursor position.
"""

from __future__ import annotations
from typing import Any, List, Optional, Tuple
from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QLabel,
    QGraphicsDropShadowEffect,
)
from PySide6.QtGui import QFont, QColor, QKeyEvent


FUSION_TOOLS: List[Tuple[str, str, str]] = [
    ("GaussianBlur", "filter", "Smooth optical Gaussian blur with adjustable radius"),
    ("DirectionalBlur", "filter", "Linear motion blur along angle vector"),
    ("OpticalGlow", "filter", "High-pass threshold bloom and atmospheric glow"),
    ("DropShadow", "filter", "Custom elevation drop shadow with blur and tint"),
    ("FastNoise", "generator", "Procedural animated Perlin/Simplex noise field"),
    ("Background", "generator", "Solid color or 4-corner gradient canvas"),
    ("Text3D", "generator", "Extruded 3D kinetic typography with bevel"),
    ("Shape2D", "generator", "Parametric vector geometric shapes and paths"),
    ("DeltaKeyer", "matte", "Advanced green/blue screen chroma keyer with despill"),
    ("PolygonMask", "matte", "Bézier spline rotoscoping and garbage matte"),
    ("LumaKeyer", "matte", "Luminance-based alpha isolation keyer"),
    ("ColorCorrector", "color", "Primary Lift/Gamma/Gain, contrast, saturation grade"),
    ("Merge", "color", "Multi-layer alpha compositing with 17 blend modes"),
    ("OCIOColorspace", "color", "OpenColorIO ACEScg to Rec.709 color transform"),
    ("Transform2D", "transform", "2D scale, rotation, translation, pivot, and skew"),
    ("GridWarp", "transform", "Mesh grid distortion and perspective pin"),
    ("PlanarTracker", "tracking", "4-point corner pin and planar surface tracking"),
    ("Displace", "transform", "Luminance map coordinate displacement"),
    ("FilmGrain", "filter", "Organic cinematic 35mm film grain emulation"),
    ("Vignette", "filter", "Customizable radial optical falloff shading"),
    ("MediaIn", "io", "Source video or image stream input socket"),
    ("MediaOut", "io", "Master composited output frame buffer"),
]


class FusionCommandPalette(QDialog):
    """Shift+Space Select Tool Command Palette Dialog."""
    tool_selected = Signal(str, str)  # (node_type, category)

    def __init__(self, parent: Optional[Any] = None) -> None:
        super().__init__(parent, Qt.WindowType.Popup | Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.setFixedSize(460, 360)

        # Drop shadow for floating spotlight feel
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(24)
        shadow.setColor(QColor(0, 0, 0, 180))
        shadow.setOffset(0, 8)
        self.setGraphicsEffect(shadow)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)

        container = QDialog()
        container.setStyleSheet("""
            QDialog {
                background-color: #16161B;
                border: 1px solid #00E5FF;
                border-radius: 8px;
            }
        """)
        c_layout = QVBoxLayout(container)
        c_layout.setContentsMargins(10, 10, 10, 10)
        c_layout.setSpacing(8)

        # Header Title
        hdr = QHBoxLayout()
        title = QLabel("Select Tool (Shift + Space)")
        title.setStyleSheet("color: #00E5FF; font-weight: 800; font-size: 12px;")
        hdr.addWidget(title)
        hdr.addStretch()
        hint = QLabel("↑/↓ Navigate • Enter Insert • Esc Close")
        hint.setStyleSheet("color: #71717A; font-size: 10px;")
        hdr.addWidget(hint)
        c_layout.addLayout(hdr)

        # Search Bar
        self.search_bar = QLineEdit()
        self.search_bar.setPlaceholderText("Search tools (e.g. Blur, Noise, Glow, DeltaKeyer)...")
        self.search_bar.setFixedHeight(34)
        self.search_bar.setStyleSheet("""
            QLineEdit {
                background-color: #1F1F26;
                border: 1px solid #2E2E38;
                border-radius: 6px;
                padding: 6px 12px;
                color: #FFFFFF;
                font-size: 13px;
                font-weight: 500;
            }
            QLineEdit:focus {
                border: 1px solid #00E5FF;
            }
        """)
        self.search_bar.textChanged.connect(self._filter_tools)
        c_layout.addWidget(self.search_bar)

        # Results List
        self.results_list = QListWidget()
        self.results_list.setStyleSheet("""
            QListWidget {
                background-color: #121215;
                border: 1px solid #26262E;
                border-radius: 6px;
                color: #ECECED;
                font-size: 12px;
                padding: 4px;
            }
            QListWidget::item {
                padding: 6px 10px;
                border-radius: 4px;
                margin-bottom: 2px;
            }
            QListWidget::item:selected {
                background-color: #00E5FF;
                color: #09090B;
                font-weight: bold;
            }
        """)
        self.results_list.itemDoubleClicked.connect(self._on_item_activated)
        c_layout.addWidget(self.results_list)

        layout.addWidget(container)
        self._populate_list(FUSION_TOOLS)

    def _populate_list(self, tools: List[Tuple[str, str, str]]) -> None:
        self.results_list.clear()
        for name, cat, desc in tools:
            item = QListWidgetItem(f"[{cat.upper()}]  {name} — {desc}")
            item.setData(Qt.ItemDataRole.UserRole, (name, cat))
            self.results_list.addItem(item)
        if self.results_list.count() > 0:
            self.results_list.setCurrentRow(0)

    def _filter_tools(self, query: str) -> None:
        q = query.strip().lower()
        if not q:
            self._populate_list(FUSION_TOOLS)
            return

        filtered = [
            (name, cat, desc) for name, cat, desc in FUSION_TOOLS
            if q in name.lower() or q in cat.lower() or q in desc.lower()
        ]
        self._populate_list(filtered)

    def keyPressEvent(self, event: QKeyEvent) -> None:
        if event.key() in (Qt.Key.Key_Return, Qt.Key.Key_Enter):
            self._on_item_activated(self.results_list.currentItem())
        elif event.key() == Qt.Key.Key_Down:
            curr = self.results_list.currentRow()
            if curr < self.results_list.count() - 1:
                self.results_list.setCurrentRow(curr + 1)
        elif event.key() == Qt.Key.Key_Up:
            curr = self.results_list.currentRow()
            if curr > 0:
                self.results_list.setCurrentRow(curr - 1)
        elif event.key() == Qt.Key.Key_Escape:
            self.reject()
        else:
            super().keyPressEvent(event)

    def _on_item_activated(self, item: Optional[QListWidgetItem]) -> None:
        if not item:
            return
        node_type, category = item.data(Qt.ItemDataRole.UserRole)
        self.tool_selected.emit(node_type, category)
        self.accept()
