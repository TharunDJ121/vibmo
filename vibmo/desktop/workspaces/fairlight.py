"""
Fairlight (Audio DAW & Mixing) Workspace for Vibmo Desktop.
Features Multi-Track Mixer Strips with Volume Faders, dB Meters, and Interactive 6-Band Parametric EQ Graph.
"""

from __future__ import annotations
from typing import Any, Optional
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSlider,
    QFrame,
    QGroupBox,
    QScrollArea,
    QSplitter,
)

from vibmo.graph.engine import VibmoStateGraph
from vibmo.desktop.widgets.eq_curve import InteractiveEQCurveWidget


class FairlightChannelStrip(QFrame):
    """Vertical Audio Track Channel Strip."""

    def __init__(self, track_name: str, track_id: str, state_graph: VibmoStateGraph, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self.track_name = track_name
        self.track_id = track_id
        self.state_graph = state_graph

        self.setFixedWidth(120)
        self.setStyleSheet("background-color: #181920; border: 1px solid #27272A; border-radius: 6px;")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(6, 6, 6, 6)
        layout.setSpacing(4)

        # Track Title
        lbl = QLabel(track_name)
        lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl.setStyleSheet("font-weight: bold; color: #38BDF8; font-size: 11px;")
        layout.addWidget(lbl)

        # Pan Slider
        pan_layout = QHBoxLayout()
        pan_layout.addWidget(QLabel("Pan:"))
        pan_slider = QSlider(Qt.Orientation.Horizontal)
        pan_slider.setRange(-50, 50)
        pan_slider.setValue(0)
        pan_layout.addWidget(pan_slider)
        layout.addLayout(pan_layout)

        # Fader + Meter
        fader_layout = QHBoxLayout()
        self.fader = QSlider(Qt.Orientation.Vertical)
        self.fader.setRange(-60, 12)
        self.fader.setValue(0)
        self.fader.setFixedHeight(180)
        self.fader.valueChanged.connect(self._on_fader_changed)
        fader_layout.addWidget(self.fader)

        meter = QFrame()
        meter.setFixedWidth(12)
        meter.setFixedHeight(180)
        meter.setStyleSheet("background: qlineargradient(x1:0, y1:1, x2:0, y2:0, stop:0 #10B981, stop:0.75 #F59E0B, stop:1 #EF4444); border-radius: 2px;")
        fader_layout.addWidget(meter)
        layout.addLayout(fader_layout)

        # dB Text
        self.db_lbl = QLabel("0.0 dB")
        self.db_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.db_lbl.setStyleSheet("color: #94A3B8; font-size: 11px;")
        layout.addWidget(self.db_lbl)

        # Mute / Solo
        btn_layout = QHBoxLayout()
        m_btn = QPushButton("M")
        m_btn.setCheckable(True)
        m_btn.setFixedSize(22, 22)
        s_btn = QPushButton("S")
        s_btn.setCheckable(True)
        s_btn.setFixedSize(22, 22)
        btn_layout.addWidget(m_btn)
        btn_layout.addWidget(s_btn)
        layout.addLayout(btn_layout)

    def _on_fader_changed(self, val: int) -> None:
        self.db_lbl.setText(f"{val:+.1f} dB")
        self.state_graph.configure_track_strip(self.track_id, fader_gain_db=float(val))


class FairlightWorkspace(QWidget):
    """Top-level Fairlight (Audio DAW) Workspace."""

    def __init__(self, state_graph: VibmoStateGraph, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self.state_graph = state_graph

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(6, 6, 6, 6)
        main_layout.setSpacing(6)

        v_splitter = QSplitter(Qt.Orientation.Vertical)

        # Top Section: Interactive 6-Band Parametric EQ Graph
        eq_box = QGroupBox("🎛 Master 6-Band Parametric Equalizer (Drag control points to sculpt sound)")
        eq_layout = QVBoxLayout(eq_box)
        self.eq_widget = InteractiveEQCurveWidget(parent=self)
        eq_layout.addWidget(self.eq_widget)
        v_splitter.addWidget(eq_box)

        # Bottom Section: Scrollable Mixer Strips
        mixer_box = QGroupBox("Fairlight Mixing Console & Busses")
        m_layout = QHBoxLayout(mixer_box)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("background: transparent; border: none;")

        strips_container = QWidget()
        self.strips_layout = QHBoxLayout(strips_container)
        self.strips_layout.setSpacing(10)

        self.refresh_strips()

        # Add Master Strip
        master_strip = FairlightChannelStrip("MASTER BUS", "master", self.state_graph)
        master_strip.setStyleSheet("background-color: #1E2028; border: 2px solid #38BDF8; border-radius: 6px;")
        self.strips_layout.addWidget(master_strip)
        self.strips_layout.addStretch()

        scroll.setWidget(strips_container)
        m_layout.addWidget(scroll)

        v_splitter.addWidget(mixer_box)
        v_splitter.setSizes([260, 450])

        main_layout.addWidget(v_splitter)

    def refresh_strips(self) -> None:
        for t in self.state_graph.project.timeline.tracks:
            if t.type == "audio":
                strip = FairlightChannelStrip(t.name, t.id, self.state_graph)
                self.strips_layout.addWidget(strip)
