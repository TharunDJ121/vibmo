"""
Color Grading Workspace for Vibmo Desktop.
Features Interactive Color Wheels (Lift, Gamma, Gain, Offset), Contrast/Saturation Controls, and LUT Selector.
"""

from __future__ import annotations
from typing import Any, Optional
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QGridLayout,
    QLabel,
    QPushButton,
    QDoubleSpinBox,
    QFrame,
    QGroupBox,
    QComboBox,
    QSplitter,
)

from vibmo.graph.engine import VibmoStateGraph
from vibmo.desktop.widgets.color_wheel import InteractiveColorWheel


class ColorWorkspace(QWidget):
    """Top-level Color Grading Workspace."""

    def __init__(self, state_graph: VibmoStateGraph, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self.state_graph = state_graph

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(6, 6, 6, 6)
        main_layout.setSpacing(6)

        v_splitter = QSplitter(Qt.Orientation.Vertical)

        # Top Section: Reference Monitor + Node Tree
        top_splitter = QSplitter(Qt.Orientation.Horizontal)

        # Color Monitor
        monitor = QFrame()
        monitor.setStyleSheet("background-color: #050608; border: 1px solid #27272A; border-radius: 6px;")
        m_layout = QVBoxLayout(monitor)
        m_lbl = QLabel("Color Grade Reference Monitor\nACEScg Wide Gamut")
        m_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        m_lbl.setStyleSheet("color: #64748B; font-size: 15px; font-weight: bold;")
        m_layout.addWidget(m_lbl)
        top_splitter.addWidget(monitor)

        # Node Grading Tree Panel
        node_tree_box = QGroupBox("Color Grading Nodes")
        nt_layout = QVBoxLayout(node_tree_box)
        node_btn1 = QPushButton("01: Primary Wheels")
        node_btn1.setObjectName("PrimaryBtn")
        node_btn2 = QPushButton("+ Add Serial Node (Alt+S)")
        node_btn3 = QPushButton("+ Add Parallel Node (Alt+P)")
        nt_layout.addWidget(node_btn1)
        nt_layout.addWidget(node_btn2)
        nt_layout.addWidget(node_btn3)
        nt_layout.addStretch()
        top_splitter.addWidget(node_tree_box)
        top_splitter.setSizes([850, 350])

        v_splitter.addWidget(top_splitter)

        # Bottom Section: Primary Wheels & Global Adjustments
        bottom_widget = QWidget()
        b_layout = QHBoxLayout(bottom_widget)
        b_layout.setContentsMargins(0, 0, 0, 0)
        b_layout.setSpacing(6)

        wheels_box = QGroupBox("Primary Color Grading Wheels (Lift / Gamma / Gain / Offset)")
        w_layout = QHBoxLayout(wheels_box)
        w_layout.setContentsMargins(4, 8, 4, 4)
        w_layout.setSpacing(6)

        self.lift_wheel = InteractiveColorWheel("Lift (Shadows)", self)
        self.gamma_wheel = InteractiveColorWheel("Gamma (Midtones)", self)
        self.gain_wheel = InteractiveColorWheel("Gain (Highlights)", self)
        self.offset_wheel = InteractiveColorWheel("Offset (Global)", self)

        self.lift_wheel.values_changed.connect(self._apply_grade)
        self.gamma_wheel.values_changed.connect(self._apply_grade)
        self.gain_wheel.values_changed.connect(self._apply_grade)
        self.offset_wheel.values_changed.connect(self._apply_grade)

        w_layout.addWidget(self.lift_wheel)
        w_layout.addWidget(self.gamma_wheel)
        w_layout.addWidget(self.gain_wheel)
        w_layout.addWidget(self.offset_wheel)

        b_layout.addWidget(wheels_box, 3)

        # Global Adjustments (Contrast, Saturation, LUT)
        adj_box = QGroupBox("Adjustments & LUTs")
        adj_layout = QVBoxLayout(adj_box)
        adj_layout.setSpacing(6)

        c_layout = QHBoxLayout()
        c_layout.addWidget(QLabel("Contrast:"))
        self.contrast_spin = QDoubleSpinBox()
        self.contrast_spin.setValue(1.0)
        self.contrast_spin.setRange(0.0, 3.0)
        self.contrast_spin.setSingleStep(0.05)
        self.contrast_spin.valueChanged.connect(self._apply_grade)
        c_layout.addWidget(self.contrast_spin)
        adj_layout.addLayout(c_layout)

        s_layout = QHBoxLayout()
        s_layout.addWidget(QLabel("Saturation:"))
        self.sat_spin = QDoubleSpinBox()
        self.sat_spin.setValue(1.0)
        self.sat_spin.setRange(0.0, 3.0)
        self.sat_spin.setSingleStep(0.05)
        self.sat_spin.valueChanged.connect(self._apply_grade)
        s_layout.addWidget(self.sat_spin)
        adj_layout.addLayout(s_layout)

        lut_layout = QHBoxLayout()
        lut_layout.addWidget(QLabel("3D LUT:"))
        self.lut_combo = QComboBox()
        self.lut_combo.addItems(["None", "Kodak_2383.cube", "Teal_Orange.cube", "Alexa_LogC.cube"])
        lut_layout.addWidget(self.lut_combo)
        adj_layout.addLayout(lut_layout)

        adj_layout.addStretch()
        b_layout.addWidget(adj_box, 1)

        v_splitter.addWidget(bottom_widget)
        v_splitter.setSizes([450, 350])

        main_layout.addWidget(v_splitter)

    def _apply_grade(self, *args: Any) -> None:
        lift = self.lift_wheel.get_values()
        gamma = self.gamma_wheel.get_values()
        gain = self.gain_wheel.get_values()
        self.state_graph.set_primary_grade(
            lift=lift,
            gamma=gamma,
            gain=gain,
            contrast=self.contrast_spin.value(),
            saturation=self.sat_spin.value(),
        )
