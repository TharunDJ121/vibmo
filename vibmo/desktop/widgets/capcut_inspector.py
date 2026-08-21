"""
CapCut-Style Tabbed Property Inspector for Vibmo Desktop.
Features Video Transform, Speed Ramping, Spring Animations, Audio Controls, and Color Grading Tabs.
"""

from __future__ import annotations
from typing import Any, Optional
from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QGridLayout,
    QLabel,
    QPushButton,
    QSlider,
    QDoubleSpinBox,
    QComboBox,
    QTabWidget,
    QGroupBox,
    QFormLayout,
    QLineEdit,
)

from vibmo.graph.engine import VibmoStateGraph


class CapCutInspector(QWidget):
    """Right-Hand CapCut Inspector & Details Panel."""
    property_changed = Signal(str, Any)

    def __init__(self, state_graph: VibmoStateGraph, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self.state_graph = state_graph

        layout = QVBoxLayout(self)
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(4)

        # Header Title
        i_title = QLabel("Details / Inspector")
        i_title.setStyleSheet("font-weight: 700; color: #A1A1AA; font-size: 11px; margin-bottom: 2px;")
        layout.addWidget(i_title)

        # Tab Widget
        self.tabs = QTabWidget()

        # 1. Tab: Basic (Transform & Opacity)
        basic_tab = QWidget()
        b_layout = QVBoxLayout(basic_tab)
        
        form = QFormLayout()
        self.pos_x_spin = QDoubleSpinBox()
        self.pos_x_spin.setRange(-2000.0, 2000.0)
        self.pos_y_spin = QDoubleSpinBox()
        self.pos_y_spin.setRange(-2000.0, 2000.0)
        form.addRow("Position X:", self.pos_x_spin)
        form.addRow("Position Y:", self.pos_y_spin)

        self.scale_spin = QDoubleSpinBox()
        self.scale_spin.setRange(0.01, 10.0)
        self.scale_spin.setValue(1.0)
        self.scale_spin.setSingleStep(0.05)
        form.addRow("Scale:", self.scale_spin)

        self.rot_spin = QDoubleSpinBox()
        self.rot_spin.setRange(-360.0, 360.0)
        form.addRow("Rotation (°):", self.rot_spin)

        self.opacity_slider = QSlider(Qt.Orientation.Horizontal)
        self.opacity_slider.setRange(0, 100)
        self.opacity_slider.setValue(100)
        form.addRow("Opacity (%):", self.opacity_slider)

        self.blend_combo = QComboBox()
        self.blend_combo.addItems(["Normal / Over", "Multiply", "Screen", "Overlay", "Add", "Soft Light"])
        form.addRow("Blend Mode:", self.blend_combo)

        b_layout.addLayout(form)
        b_layout.addStretch()
        self.tabs.addTab(basic_tab, "Basic")

        # 2. Tab: Speed
        speed_tab = QWidget()
        s_layout = QVBoxLayout(speed_tab)
        s_form = QFormLayout()
        
        self.speed_spin = QDoubleSpinBox()
        self.speed_spin.setRange(0.1, 10.0)
        self.speed_spin.setValue(1.0)
        self.speed_spin.setSingleStep(0.1)
        s_form.addRow("Speed (x):", self.speed_spin)

        self.reverse_btn = QPushButton("Reverse Clip")
        s_form.addRow("Direction:", self.reverse_btn)

        s_layout.addLayout(s_form)
        s_layout.addStretch()
        self.tabs.addTab(speed_tab, "Speed")

        # 3. Tab: Animation (Motion Verbs)
        anim_tab = QWidget()
        a_layout = QVBoxLayout(anim_tab)
        
        pop_btn = QPushButton("✨ Pop In (Spring)")
        fade_btn = QPushButton("⬆ Fade Up (Cubic)")
        bounce_btn = QPushButton("🏀 Elastic Bounce")
        float_btn = QPushButton("🌊 Float Idle")

        a_layout.addWidget(pop_btn)
        a_layout.addWidget(fade_btn)
        a_layout.addWidget(bounce_btn)
        a_layout.addWidget(float_btn)
        a_layout.addStretch()
        self.tabs.addTab(anim_tab, "Animation")

        # 4. Tab: Color
        color_tab = QWidget()
        c_layout = QVBoxLayout(color_tab)
        c_form = QFormLayout()

        self.temp_slider = QSlider(Qt.Orientation.Horizontal)
        self.temp_slider.setRange(-50, 50)
        c_form.addRow("Temp:", self.temp_slider)

        self.sat_slider = QSlider(Qt.Orientation.Horizontal)
        self.sat_slider.setRange(0, 200)
        self.sat_slider.setValue(100)
        c_form.addRow("Saturation:", self.sat_slider)

        self.contrast_slider = QSlider(Qt.Orientation.Horizontal)
        self.contrast_slider.setRange(0, 200)
        self.contrast_slider.setValue(100)
        c_form.addRow("Contrast:", self.contrast_slider)

        lut_combo = QComboBox()
        lut_combo.addItems(["None", "Kodak_2383.cube", "Teal_Orange.cube"])
        c_form.addRow("LUT:", lut_combo)

        c_layout.addLayout(c_form)
        c_layout.addStretch()
        self.tabs.addTab(color_tab, "Color")

        layout.addWidget(self.tabs)
