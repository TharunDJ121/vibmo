"""
Interactive Color Wheel Widget for Vibmo Color Workspace.
Features a 2D Chrominance disk with a draggable color puck, RGB readouts, and Master luminance slider.
"""

from __future__ import annotations
import math
from typing import Optional, Tuple
from PySide6.QtCore import Qt, Signal, QPointF, QRectF
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QGridLayout,
    QLabel,
    QSlider,
    QDoubleSpinBox,
    QFrame,
    QGroupBox,
)
from PySide6.QtGui import QPainter, QColor, QBrush, QPen, QRadialGradient, QMouseEvent


class ChrominanceWheel(QWidget):
    """Circular Chrominance wheel with a draggable puck for tint/hue adjustments."""
    color_changed = Signal(float, float, float)  # red, green, blue offsets [-1.0, 1.0]

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self.setFixedSize(140, 140)
        self.puck_pos = QPointF(70.0, 70.0)  # Center (0, 0 offset)
        self.is_dragging = False

    def paintEvent(self, event: Any) -> None:
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        w = self.width()
        h = self.height()
        cx = w / 2.0
        cy = h / 2.0
        radius = min(w, h) / 2.0 - 4.0

        # Outer ring
        painter.setPen(QPen(QColor("#3F3F46"), 2))
        painter.setBrush(QBrush(QColor("#18191E")))
        painter.drawEllipse(QPointF(cx, cy), radius, radius)

        # Crosshairs
        painter.setPen(QPen(QColor("#27272A"), 1, Qt.PenStyle.DashLine))
        painter.drawLine(int(cx - radius + 4), int(cy), int(cx + radius - 4), int(cy))
        painter.drawLine(int(cx), int(cy - radius + 4), int(cx), int(cy + radius - 4))

        # Draggable Puck
        painter.setBrush(QBrush(QColor("#38BDF8")))
        painter.setPen(QPen(QColor("#FFFFFF"), 2))
        painter.drawEllipse(self.puck_pos, 6, 6)

    def mousePressEvent(self, event: QMouseEvent) -> None:
        if event.button() == Qt.MouseButton.LeftButton:
            self.is_dragging = True
            self._update_puck_position(event.position())

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        if self.is_dragging:
            self._update_puck_position(event.position())

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        if event.button() == Qt.MouseButton.LeftButton:
            self.is_dragging = False

    def mouseDoubleClickEvent(self, event: QMouseEvent) -> None:
        # Reset to center on double click
        self.puck_pos = QPointF(self.width() / 2.0, self.height() / 2.0)
        self.update()
        self.color_changed.emit(0.0, 0.0, 0.0)

    def _update_puck_position(self, pos: QPointF) -> None:
        cx = self.width() / 2.0
        cy = self.height() / 2.0
        radius = min(self.width(), self.height()) / 2.0 - 6.0

        dx = pos.x() - cx
        dy = pos.y() - cy
        dist = math.sqrt(dx * dx + dy * dy)

        if dist > radius:
            dx = (dx / dist) * radius
            dy = (dy / dist) * radius

        self.puck_pos = QPointF(cx + dx, cy + dy)
        self.update()

        # Normalized coordinates [-1.0, 1.0]
        norm_x = dx / radius
        norm_y = -dy / radius  # Invert Y so up is positive

        # Calculate approximate RGB offsets
        r_offset = max(-1.0, min(1.0, norm_x * 0.8 + norm_y * 0.5))
        g_offset = max(-1.0, min(1.0, -norm_x * 0.5 + norm_y * 0.8))
        b_offset = max(-1.0, min(1.0, -norm_x * 0.6 - norm_y * 0.6))

        self.color_changed.emit(r_offset, g_offset, b_offset)


class InteractiveColorWheel(QGroupBox):
    """Full Color Wheel group with chrominance disk, master slider, and RGB spinboxes."""
    values_changed = Signal(float, float, float, float)  # r, g, b, master

    def __init__(self, title: str, parent: Optional[QWidget] = None) -> None:
        super().__init__(title, parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(6, 8, 6, 6)
        layout.setSpacing(6)

        # 1. Interactive Chrominance Wheel
        self.wheel = ChrominanceWheel(self)
        self.wheel.color_changed.connect(self._on_wheel_moved)
        layout.addWidget(self.wheel, alignment=Qt.AlignmentFlag.AlignCenter)

        # 2. Master Luminance Slider (Bottom Dial)
        master_layout = QHBoxLayout()
        master_layout.addWidget(QLabel("Y:"))
        self.master_slider = QSlider(Qt.Orientation.Horizontal)
        self.master_slider.setRange(-100, 100)
        self.master_slider.setValue(0)
        self.master_slider.valueChanged.connect(self._on_master_slider_changed)
        master_layout.addWidget(self.master_slider)
        layout.addLayout(master_layout)

        # 3. Numerical Spinboxes
        grid = QGridLayout()
        grid.setSpacing(4)

        self.r_spin = QDoubleSpinBox()
        self.r_spin.setRange(-1.0, 1.0)
        self.r_spin.setSingleStep(0.01)
        self.r_spin.valueChanged.connect(self._emit_change)

        self.g_spin = QDoubleSpinBox()
        self.g_spin.setRange(-1.0, 1.0)
        self.g_spin.setSingleStep(0.01)
        self.g_spin.valueChanged.connect(self._emit_change)

        self.b_spin = QDoubleSpinBox()
        self.b_spin.setRange(-1.0, 1.0)
        self.b_spin.setSingleStep(0.01)
        self.b_spin.valueChanged.connect(self._emit_change)

        grid.addWidget(QLabel("R:"), 0, 0)
        grid.addWidget(self.r_spin, 0, 1)
        grid.addWidget(QLabel("G:"), 0, 2)
        grid.addWidget(self.g_spin, 0, 3)
        grid.addWidget(QLabel("B:"), 0, 4)
        grid.addWidget(self.b_spin, 0, 5)

        layout.addLayout(grid)

    def _on_wheel_moved(self, r: float, g: float, b: float) -> None:
        self.r_spin.blockSignals(True)
        self.g_spin.blockSignals(True)
        self.b_spin.blockSignals(True)

        self.r_spin.setValue(r)
        self.g_spin.setValue(g)
        self.b_spin.setValue(b)

        self.r_spin.blockSignals(False)
        self.g_spin.blockSignals(False)
        self.b_spin.blockSignals(False)

        self._emit_change()

    def _on_master_slider_changed(self, val: int) -> None:
        self._emit_change()

    def _emit_change(self) -> None:
        r = self.r_spin.value()
        g = self.g_spin.value()
        b = self.b_spin.value()
        master = self.master_slider.value() / 100.0
        self.values_changed.emit(r, g, b, master)

    def get_values(self) -> Tuple[float, float, float, float]:
        return (
            self.r_spin.value(),
            self.g_spin.value(),
            self.b_spin.value(),
            self.master_slider.value() / 100.0,
        )
