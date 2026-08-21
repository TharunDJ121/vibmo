"""
Delivery (Export & Render Queue) Workspace for Vibmo Desktop.
Features Presets (YouTube 4K, ProRes 4444, WebM Transparent), Custom Codec Settings, and Render Queue.
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
    QLineEdit,
    QComboBox,
    QSpinBox,
    QTableWidget,
    QTableWidgetItem,
    QGroupBox,
    QFileDialog,
    QProgressBar,
)

from vibmo.graph.engine import VibmoStateGraph


class DeliveryWorkspace(QWidget):
    """Top-level Delivery (Export & Ingestion) Workspace."""

    def __init__(self, state_graph: VibmoStateGraph, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self.state_graph = state_graph

        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(8, 8, 8, 8)
        main_layout.setSpacing(10)

        # Left Column: Render Settings & Presets
        settings_box = QGroupBox("🚀 Render Settings")
        s_layout = QVBoxLayout(settings_box)
        s_layout.setSpacing(8)

        # Presets Bar
        preset_layout = QHBoxLayout()
        preset_layout.addWidget(QLabel("Preset:"))
        self.preset_combo = QComboBox()
        self.preset_combo.addItems([
            "YouTube 4K Master (H.264 / 3840x2160)",
            "Apple ProRes 4444 (Master with Alpha / 1080p)",
            "WebM Transparent Overlay (VP9)",
            "Discord / Twitter Fast Share (1080p 60fps)",
            "Lossless PNG / EXR Image Sequence",
        ])
        preset_layout.addWidget(self.preset_combo)
        s_layout.addLayout(preset_layout)

        # Output File Name & Destination
        grid = QGridLayout()
        grid.addWidget(QLabel("File Name:"), 0, 0)
        self.filename_input = QLineEdit("Vibmo_Master_Render.mp4")
        grid.addWidget(self.filename_input, 0, 1)

        grid.addWidget(QLabel("Export Path:"), 1, 0)
        path_layout = QHBoxLayout()
        self.path_input = QLineEdit("output/Vibmo_Master_Render.mp4")
        browse_btn = QPushButton("Browse...")
        browse_btn.clicked.connect(self._browse_path)
        path_layout.addWidget(self.path_input)
        path_layout.addWidget(browse_btn)
        grid.addLayout(path_layout, 1, 1)

        grid.addWidget(QLabel("Format:"), 2, 0)
        self.format_combo = QComboBox()
        self.format_combo.addItems(["MP4 (H.264/AAC)", "QuickTime (ProRes)", "WebM (VP9/Opus)", "GIF", "WAV Stems"])
        grid.addWidget(self.format_combo, 2, 1)

        grid.addWidget(QLabel("Resolution:"), 3, 0)
        res_layout = QHBoxLayout()
        self.w_spin = QSpinBox()
        self.w_spin.setRange(240, 7680)
        self.w_spin.setValue(1920)
        self.h_spin = QSpinBox()
        self.h_spin.setRange(240, 4320)
        self.h_spin.setValue(1080)
        res_layout.addWidget(self.w_spin)
        res_layout.addWidget(QLabel("x"))
        res_layout.addWidget(self.h_spin)
        grid.addLayout(res_layout, 3, 1)

        grid.addWidget(QLabel("Frame Rate:"), 4, 0)
        self.fps_combo = QComboBox()
        self.fps_combo.addItems(["60.00 fps", "30.00 fps", "24.00 fps", "120.00 fps"])
        grid.addWidget(self.fps_combo, 4, 1)

        s_layout.addLayout(grid)
        s_layout.addStretch()

        add_queue_btn = QPushButton("+ Add to Render Queue")
        add_queue_btn.setObjectName("PrimaryBtn")
        add_queue_btn.setFixedHeight(36)
        add_queue_btn.clicked.connect(self._add_to_queue)
        s_layout.addWidget(add_queue_btn)

        main_layout.addWidget(settings_box, 1)

        # Right Column: Render Queue
        queue_box = QGroupBox("📋 Render Queue")
        q_layout = QVBoxLayout(queue_box)
        q_layout.setSpacing(8)

        self.queue_table = QTableWidget(0, 5)
        self.queue_table.setHorizontalHeaderLabels(["Job Name", "Format", "Resolution", "Status", "Progress"])
        self.queue_table.horizontalHeader().setStretchLastSection(True)
        q_layout.addWidget(self.queue_table)

        # Progress bar
        self.overall_progress = QProgressBar()
        self.overall_progress.setValue(0)
        q_layout.addWidget(self.overall_progress)

        # Queue Actions
        q_actions = QHBoxLayout()
        render_all_btn = QPushButton("▶ Render All Jobs")
        render_all_btn.setObjectName("PrimaryBtn")
        render_all_btn.setFixedHeight(34)
        clear_queue_btn = QPushButton("Clear Completed")
        q_actions.addWidget(render_all_btn)
        q_actions.addWidget(clear_queue_btn)
        q_layout.addLayout(q_actions)

        main_layout.addWidget(queue_box, 2)
        self.refresh_queue()

    def _browse_path(self) -> None:
        file_path, _ = QFileDialog.getSaveFileName(self, "Select Render Output", self.path_input.text(), "Video Files (*.mp4 *.mov *.webm)")
        if file_path:
            self.path_input.setText(file_path)

    def _add_to_queue(self) -> None:
        self.state_graph.queue_render_job(
            output_path=self.path_input.text(),
            preset_name=self.preset_combo.currentText(),
            format_name="mp4",
            width=self.w_spin.value(),
            height=self.h_spin.value(),
            fps=60.0,
        )
        self.refresh_queue()

    def refresh_queue(self) -> None:
        jobs = self.state_graph.project.render_queue
        self.queue_table.setRowCount(len(jobs))
        for row, job in enumerate(jobs):
            self.queue_table.setItem(row, 0, QTableWidgetItem(job.preset_name))
            self.queue_table.setItem(row, 1, QTableWidgetItem(job.format.upper()))
            self.queue_table.setItem(row, 2, QTableWidgetItem(f"{job.width}x{job.height}"))
            self.queue_table.setItem(row, 3, QTableWidgetItem(job.status.upper()))
            self.queue_table.setItem(row, 4, QTableWidgetItem(f"{int(job.progress * 100)}%"))
