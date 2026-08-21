"""
Interactive 6-Band Parametric EQ Curve Widget for Vibmo Fairlight Workspace.
Allows dragging frequency (Hz) and gain (dB) control points directly on an animated audio spectrum curve.
"""

from __future__ import annotations
import math
from typing import Any, List, Optional
from PySide6.QtCore import Qt, Signal, QPointF, QRectF
from PySide6.QtWidgets import QWidget
from PySide6.QtGui import QPainter, QColor, QBrush, QPen, QFont, QPainterPath, QMouseEvent

from vibmo.graph.schema import EQBand


class InteractiveEQCurveWidget(QWidget):
    """Interactive 6-Band Parametric Equalizer Visualizer."""
    band_changed = Signal(int, float, float)  # band_index, freq_hz, gain_db

    def __init__(self, bands: Optional[List[EQBand]] = None, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self.setFixedHeight(180)
        self.setStyleSheet("background-color: #0F1014; border: 1px solid #27272A; border-radius: 6px;")

        # 6 Default EQ control points (Freq, Gain)
        self.control_points = [
            {"freq": 80.0, "gain": 0.0, "color": QColor("#EF4444")},    # High Pass / Sub
            {"freq": 200.0, "gain": 1.5, "color": QColor("#F59E0B")},   # Low Shelf
            {"freq": 800.0, "gain": -2.0, "color": QColor("#10B981")},  # Low Mid
            {"freq": 2500.0, "gain": 3.0, "color": QColor("#06B6D4")},  # High Mid
            {"freq": 8000.0, "gain": 1.0, "color": QColor("#3B82F6")},  # High Shelf
            {"freq": 16000.0, "gain": 0.0, "color": QColor("#8B5CF6")}, # Air / Low Pass
        ]
        self.selected_point_idx: Optional[int] = None

    def _freq_to_x(self, freq: float) -> float:
        """Converts logarithmic frequency (20Hz - 20kHz) to pixel X coordinate."""
        min_f = math.log10(20.0)
        max_f = math.log10(20000.0)
        cur_f = math.log10(max(20.0, min(20000.0, freq)))
        ratio = (cur_f - min_f) / (max_f - min_f)
        return ratio * (self.width() - 40) + 20

    def _x_to_freq(self, x: float) -> float:
        """Converts pixel X to frequency Hz."""
        ratio = max(0.0, min(1.0, (x - 20) / max(1.0, self.width() - 40)))
        min_f = math.log10(20.0)
        max_f = math.log10(20000.0)
        return 10 ** (min_f + ratio * (max_f - min_f))

    def _gain_to_y(self, gain: float) -> float:
        """Converts gain in dB (-18dB to +18dB) to pixel Y coordinate."""
        cy = self.height() / 2.0
        scale = (self.height() - 30) / 36.0
        return cy - gain * scale

    def _y_to_gain(self, y: float) -> float:
        """Converts pixel Y to gain in dB."""
        cy = self.height() / 2.0
        scale = (self.height() - 30) / 36.0
        return max(-18.0, min(18.0, (cy - y) / scale))

    def paintEvent(self, event: Any) -> None:
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        w = self.width()
        h = self.height()
        cy = h / 2.0

        # Background Grid Lines
        painter.setPen(QPen(QColor("#1F222C"), 1, Qt.PenStyle.DashLine))
        # Center 0dB Line
        painter.drawLine(0, int(cy), w, int(cy))
        # +6dB and -6dB lines
        painter.drawLine(0, int(self._gain_to_y(6.0)), w, int(self._gain_to_y(6.0)))
        painter.drawLine(0, int(self._gain_to_y(-6.0)), w, int(self._gain_to_y(-6.0)))

        # Frequency Grid Lines (100Hz, 1kHz, 10kHz)
        for f in [100.0, 1000.0, 10000.0]:
            x = self._freq_to_x(f)
            painter.drawLine(int(x), 0, int(x), h)
            painter.setPen(QPen(QColor("#64748B")))
            painter.setFont(QFont("Segoe UI", 7))
            painter.drawText(int(x) + 4, h - 6, f"{int(f)}Hz" if f < 1000 else f"{int(f/1000)}kHz")
            painter.setPen(QPen(QColor("#1F222C"), 1, Qt.PenStyle.DashLine))

        # Draw Smooth Parametric Filter Response Curve (Cyan Glow)
        curve_path = QPainterPath()
        points = [(self._freq_to_x(p["freq"]), self._gain_to_y(p["gain"])) for p in self.control_points]
        curve_path.moveTo(0, cy)
        curve_path.lineTo(points[0][0], points[0][1])

        for i in range(len(points) - 1):
            p1 = points[i]
            p2 = points[i + 1]
            cx1 = (p1[0] + p2[0]) / 2.0
            curve_path.cubicTo(QPointF(cx1, p1[1]), QPointF(cx1, p2[1]), QPointF(p2[0], p2[1]))

        curve_path.lineTo(w, cy)

        # Draw filled gradient below curve
        fill_path = QPainterPath(curve_path)
        fill_path.lineTo(w, h)
        fill_path.lineTo(0, h)
        fill_path.closeSubpath()

        painter.fillPath(fill_path, QBrush(QColor(56, 189, 248, 25)))
        painter.strokePath(curve_path, QPen(QColor("#38BDF8"), 2.2))

        # Draw 6 Draggable Frequency/Gain Handles
        for i, p in enumerate(self.control_points):
            px = self._freq_to_x(p["freq"])
            py = self._gain_to_y(p["gain"])

            painter.setBrush(QBrush(p["color"]))
            painter.setPen(QPen(QColor("#FFFFFF"), 2 if i == self.selected_point_idx else 1))
            painter.drawEllipse(QPointF(px, py), 6, 6)

            # Draw band number
            painter.setPen(QPen(QColor("#FFFFFF")))
            painter.setFont(QFont("Segoe UI", 7, QFont.Weight.Bold))
            painter.drawText(QRectF(px - 10, py - 18, 20, 12), Qt.AlignmentFlag.AlignCenter, str(i + 1))

    def mousePressEvent(self, event: QMouseEvent) -> None:
        if event.button() == Qt.MouseButton.LeftButton:
            pos = event.position()
            # Find nearest control point
            for i, p in enumerate(self.control_points):
                px = self._freq_to_x(p["freq"])
                py = self._gain_to_y(p["gain"])
                if math.sqrt((pos.x() - px) ** 2 + (pos.y() - py) ** 2) < 14:
                    self.selected_point_idx = i
                    self.update()
                    break

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        if self.selected_point_idx is not None:
            pos = event.position()
            new_freq = self._x_to_freq(pos.x())
            new_gain = self._y_to_gain(pos.y())

            self.control_points[self.selected_point_idx]["freq"] = new_freq
            self.control_points[self.selected_point_idx]["gain"] = new_gain
            self.update()

            self.band_changed.emit(self.selected_point_idx, new_freq, new_gain)

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        if event.button() == Qt.MouseButton.LeftButton:
            self.selected_point_idx = None
            self.update()
