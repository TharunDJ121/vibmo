"""
Native PySide6 Desktop Dialog for AI Motion Director (LangGraph).
Allows surgical scene & frame modifications and full story generation directly inside the desktop app.
"""

from __future__ import annotations
from typing import Any, Dict, Optional
from PySide6.QtCore import Qt, QThread, Signal
from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QTextEdit,
    QWidget,
    QComboBox,
    QProgressBar,
)
from PySide6.QtGui import QFont

from vibmo.ai.graph import run_motion_edit


class AiDirectorWorker(QThread):
    """Executes LangGraph Motion State Machine in a background thread."""
    step_log = Signal(str)
    finished_edit = Signal(dict)
    error_occurred = Signal(str)

    def __init__(self, prompt: str, current_code: str, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self.prompt = prompt
        self.current_code = current_code

    def run(self) -> None:
        try:
            self.step_log.emit(f"✦ LangGraph Engine: Initializing state machine for prompt: '{self.prompt}'")
            result = run_motion_edit(self.prompt, self.current_code)
            self.finished_edit.emit(result)
        except Exception as e:
            self.error_occurred.emit(str(e))


class AiDirectorDialog(QDialog):
    """CapCut-styled Native Desktop Modal for AI Motion Director (LangGraph)."""
    script_updated = Signal(str)  # Emits updated python code

    def __init__(self, current_code: str = "", parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self.current_code = current_code
        self.setWindowTitle("✨ AI Motion Director (LangGraph) — Vibmo Studio Pro")
        self.resize(680, 500)
        self.setModal(True)
        self.setStyleSheet("""
            QDialog {
                background-color: #0b0f19;
                color: #f8fafc;
                border: 1px solid #1e1b4b;
                border-radius: 12px;
            }
            QLabel {
                color: #f8fafc;
            }
            QLineEdit {
                background-color: #030712;
                color: #f8fafc;
                border: 1px solid #4338ca;
                border-radius: 8px;
                padding: 10px 14px;
                font-size: 13px;
            }
            QLineEdit:focus {
                border-color: #818cf8;
            }
            QTextEdit {
                background-color: #030712;
                color: #c084fc;
                border: 1px solid #1e293b;
                border-radius: 8px;
                font-family: ui-monospace, monospace;
                font-size: 11px;
                padding: 10px;
            }
            QPushButton {
                background-color: #1e1b4b;
                color: #e0e7ff;
                border: 1px solid #4338ca;
                border-radius: 8px;
                padding: 8px 16px;
                font-weight: bold;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #312e81;
            }
            QPushButton#ApplyBtn {
                background: linear-gradient(135deg, #7c3aed, #4f46e5);
                background-color: #7c3aed;
                color: #ffffff;
                border: none;
            }
            QPushButton#ApplyBtn:hover {
                background-color: #6d28d9;
            }
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(14)

        # Header
        header_layout = QHBoxLayout()
        icon_label = QLabel("✨")
        icon_label.setFont(QFont("Segoe UI Emoji", 20))
        header_layout.addWidget(icon_label)

        title_layout = QVBoxLayout()
        title = QLabel("AI Motion Director")
        title.setFont(QFont("Segoe UI", 15, QFont.Weight.Bold))
        subtitle = QLabel("Powered by LangGraph: Surgical scene & frame editor without code rewriting")
        subtitle.setStyleSheet("color: #a5b4fc; font-size: 11px;")
        title_layout.addWidget(title)
        title_layout.addWidget(subtitle)
        header_layout.addLayout(title_layout)
        header_layout.addStretch()
        layout.addLayout(header_layout)

        # Example Presets Selector
        preset_layout = QHBoxLayout()
        preset_label = QLabel("Quick Presets:")
        preset_label.setStyleSheet("color: #94a3b8; font-size: 11px;")
        preset_layout.addWidget(preset_label)

        self.preset_combo = QComboBox()
        self.preset_combo.setStyleSheet("background: #0f172a; color: #cbd5e1; border: 1px solid #334155; padding: 4px 8px; border-radius: 6px;")
        self.preset_combo.addItems([
            "Select an example instruction...",
            "In Scene 3, change text to 'Think Bigger' and speed up Scene 2 typing by 40%",
            "Change background in Scene 1 to Aurora gradient",
            "Set Scene 4 duration to 2.5s and enable specular shimmer",
            "In Scene 3, change word_a color to #10b981",
            "Make Scene 5 camera zoom in closer to 1.35x",
        ])
        self.preset_combo.currentIndexChanged.connect(self._on_preset_selected)
        preset_layout.addWidget(self.preset_combo, 1)
        layout.addLayout(preset_layout)

        # Prompt Input Row
        input_layout = QHBoxLayout()
        self.prompt_input = QLineEdit()
        self.prompt_input.setPlaceholderText("Type instruction in natural language (e.g. 'Make Scene 2 type faster')...")
        self.prompt_input.returnPressed.connect(self._apply_edit)
        input_layout.addWidget(self.prompt_input, 1)

        self.apply_btn = QPushButton("⚡ Apply Edit")
        self.apply_btn.setObjectName("ApplyBtn")
        self.apply_btn.clicked.connect(self._apply_edit)
        input_layout.addWidget(self.apply_btn)
        layout.addLayout(input_layout)

        # Progress Bar (Hidden by default)
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 0)
        self.progress_bar.setFixedHeight(4)
        self.progress_bar.setVisible(False)
        self.progress_bar.setStyleSheet("QProgressBar::chunk { background-color: #818cf8; }")
        layout.addWidget(self.progress_bar)

        # Console / Execution Log Box
        self.logs_box = QTextEdit()
        self.logs_box.setReadOnly(True)
        self.logs_box.setPlainText("✦ LangGraph Motion State Machine Ready.\nAwaiting instructions...")
        layout.addWidget(self.logs_box, 1)

        # Bottom Action Row
        bottom_layout = QHBoxLayout()
        self.status_label = QLabel("")
        self.status_label.setStyleSheet("color: #34d399; font-size: 12px;")
        bottom_layout.addWidget(self.status_label)
        bottom_layout.addStretch()

        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.accept)
        bottom_layout.addWidget(close_btn)
        layout.addLayout(bottom_layout)

    def _on_preset_selected(self, index: int) -> None:
        if index > 0:
            self.prompt_input.setText(self.preset_combo.currentText())

    def _apply_edit(self) -> None:
        prompt = self.prompt_input.text().strip()
        if not prompt:
            return

        self.apply_btn.setText("⏳ Applying...")
        self.apply_btn.setEnabled(False)
        self.progress_bar.setVisible(True)
        self.status_label.setText("Running LangGraph state machine...")
        self.status_label.setStyleSheet("color: #818cf8;")

        self.logs_box.append(f"\n--- Activating LangGraph for: '{prompt}' ---")

        self.worker = AiDirectorWorker(prompt, self.current_code, self)
        self.worker.step_log.connect(self._on_step_log)
        self.worker.finished_edit.connect(self._on_finished_edit)
        self.worker.error_occurred.connect(self._on_error)
        self.worker.start()

    def _on_step_log(self, text: str) -> None:
        self.logs_box.append(text)

    def _on_finished_edit(self, result: Dict[str, Any]) -> None:
        self.apply_btn.setText("⚡ Apply Edit")
        self.apply_btn.setEnabled(True)
        self.progress_bar.setVisible(False)

        logs = result.get("execution_log", [])
        for log_line in logs:
            self.logs_box.append(f"  • {log_line}")

        msg = result.get("response_message", "Edit applied successfully.")
        self.logs_box.append(f"\n✓ {msg}")

        updated_code = result.get("updated_code", "")
        if updated_code:
            self.current_code = updated_code
            self.script_updated.emit(updated_code)
            self.status_label.setText("✓ Edit applied & scene reloaded!")
            self.status_label.setStyleSheet("color: #34d399;")
        else:
            self.status_label.setText("No code changes generated.")
            self.status_label.setStyleSheet("color: #fbbf24;")

    def _on_error(self, err_msg: str) -> None:
        self.apply_btn.setText("⚡ Apply Edit")
        self.apply_btn.setEnabled(True)
        self.progress_bar.setVisible(False)
        self.logs_box.append(f"\n❌ Error: {err_msg}")
        self.status_label.setText(f"Error: {err_msg}")
        self.status_label.setStyleSheet("color: #f87171;")
