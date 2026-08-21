"""
Native PySide6 Desktop Dialog for API Key Attachment & Verification.
Supports OpenAI, Anthropic, Gemini, Groq, and OpenRouter with secure local persistence in .env.
"""

from __future__ import annotations
from typing import Dict, Optional
from PySide6.QtCore import Qt, QThread, Signal
from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QFrame,
    QWidget,
    QScrollArea,
    QMessageBox,
)
from PySide6.QtGui import QFont

from vibmo.ai.keys import (
    PROVIDERS,
    get_all_keys,
    save_key,
    verify_key_connection,
    mask_key,
)


class KeyVerificationWorker(QThread):
    """Background worker to test key connectivity without blocking GUI."""
    result_ready = Signal(str, bool, str)  # provider_id, success, message

    def __init__(self, provider_id: str, key_val: str, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self.provider_id = provider_id
        self.key_val = key_val

    def run(self) -> None:
        success, msg = verify_key_connection(self.provider_id, self.key_val)
        self.result_ready.emit(self.provider_id, success, msg)


class ApiKeysDialog(QDialog):
    """CapCut-styled Native Desktop Modal for Managing LLM API Keys."""

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self.setWindowTitle("AI Provider API Keys — Vibmo Studio Pro")
        self.resize(580, 520)
        self.setModal(True)
        self.setStyleSheet("""
            QDialog {
                background-color: #0d1117;
                color: #f0f6fc;
                border: 1px solid #30363d;
                border-radius: 12px;
            }
            QLabel {
                color: #f0f6fc;
            }
            QLineEdit {
                background-color: #161b22;
                color: #f0f6fc;
                border: 1px solid #30363d;
                border-radius: 6px;
                padding: 8px 10px;
                font-family: ui-monospace, monospace;
                font-size: 12px;
            }
            QLineEdit:focus {
                border-color: #58a6ff;
            }
            QPushButton {
                background-color: #21262d;
                color: #c9d1d9;
                border: 1px solid #30363d;
                border-radius: 6px;
                padding: 6px 12px;
                font-weight: bold;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #30363d;
                color: #f0f6fc;
            }
            QPushButton#SaveBtn {
                background-color: #238636;
                color: #ffffff;
                border: 1px solid #2ea043;
            }
            QPushButton#SaveBtn:hover {
                background-color: #2ea043;
            }
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(16)

        # Header
        header_layout = QHBoxLayout()
        icon_label = QLabel("🔑")
        icon_label.setFont(QFont("Segoe UI Emoji", 20))
        header_layout.addWidget(icon_label)

        title_layout = QVBoxLayout()
        title = QLabel("AI Provider API Keys")
        title.setFont(QFont("Segoe UI", 15, QFont.Weight.Bold))
        subtitle = QLabel("Keys are tested live and stored in your project's .env file")
        subtitle.setStyleSheet("color: #8b949e; font-size: 11px;")
        title_layout.addWidget(title)
        title_layout.addWidget(subtitle)
        header_layout.addLayout(title_layout)
        header_layout.addStretch()
        layout.addLayout(header_layout)

        # Providers List
        self.inputs: Dict[str, QLineEdit] = {}
        self.status_labels: Dict[str, QLabel] = {}
        self.save_buttons: Dict[str, QPushButton] = {}

        scroll = QScrollArea(self)
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")
        container = QWidget()
        container_layout = QVBoxLayout(container)
        container_layout.setContentsMargins(0, 0, 0, 0)
        container_layout.setSpacing(12)

        providers_data = get_all_keys()

        for p_id, meta in providers_data.items():
            card = QFrame()
            card.setStyleSheet("""
                QFrame {
                    background-color: #161b22;
                    border: 1px solid #30363d;
                    border-radius: 8px;
                    padding: 10px;
                }
            """)
            card_layout = QVBoxLayout(card)
            card_layout.setContentsMargins(12, 10, 12, 10)
            card_layout.setSpacing(8)

            # Title row
            row1 = QHBoxLayout()
            p_name = QLabel(meta["name"])
            p_name.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
            row1.addWidget(p_name)

            status = QLabel()
            if meta["is_configured"]:
                status.setText(f"✓ Configured ({meta['masked_key']})")
                status.setStyleSheet("color: #3fb950; font-size: 11px; font-weight: bold;")
            else:
                status.setText("Not Configured")
                status.setStyleSheet("color: #f85149; font-size: 11px;")
            self.status_labels[p_id] = status
            row1.addWidget(status)
            row1.addStretch()

            env_hint = QLabel(meta["env_var"])
            env_hint.setStyleSheet("color: #8b949e; font-size: 10px; font-family: monospace;")
            row1.addWidget(env_hint)
            card_layout.addLayout(row1)

            # Input row
            row2 = QHBoxLayout()
            line_edit = QLineEdit()
            line_edit.setEchoMode(QLineEdit.EchoMode.Password)
            line_edit.setPlaceholderText("Enter new API key (e.g. sk-...)...")
            self.inputs[p_id] = line_edit
            row2.addWidget(line_edit, 1)

            save_btn = QPushButton("Save & Test")
            save_btn.setObjectName("SaveBtn")
            save_btn.clicked.connect(lambda _, pid=p_id: self._test_and_save(pid))
            self.save_buttons[p_id] = save_btn
            row2.addWidget(save_btn)

            card_layout.addLayout(row2)
            container_layout.addWidget(card)

        container_layout.addStretch()
        scroll.setWidget(container)
        layout.addWidget(scroll, 1)

        # Global Status Message
        self.global_status = QLabel("")
        self.global_status.setStyleSheet("font-size: 12px; min-height: 18px;")
        layout.addWidget(self.global_status)

        # Bottom Close Button
        bottom_layout = QHBoxLayout()
        bottom_layout.addStretch()
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.accept)
        bottom_layout.addWidget(close_btn)
        layout.addLayout(bottom_layout)

    def _test_and_save(self, provider_id: str) -> None:
        key_val = self.inputs[provider_id].text().strip()
        if not key_val:
            QMessageBox.warning(self, "Empty Key", "Please enter an API key before saving.")
            return

        self.save_buttons[provider_id].setText("Testing...")
        self.save_buttons[provider_id].setEnabled(False)
        self.global_status.setText(f"Verifying connectivity with {PROVIDERS[provider_id]['name']}...")
        self.global_status.setStyleSheet("color: #58a6ff;")

        self.worker = KeyVerificationWorker(provider_id, key_val, self)
        self.worker.result_ready.connect(self._on_verification_result)
        self.worker.start()

    def _on_verification_result(self, provider_id: str, success: bool, message: str) -> None:
        self.save_buttons[provider_id].setText("Save & Test")
        self.save_buttons[provider_id].setEnabled(True)

        key_val = self.inputs[provider_id].text().strip()
        save_key(provider_id, key_val)

        if success:
            self.status_labels[provider_id].setText(f"✓ Configured ({mask_key(key_val)})")
            self.status_labels[provider_id].setStyleSheet("color: #3fb950; font-size: 11px; font-weight: bold;")
            self.global_status.setText(f"✓ {message}")
            self.global_status.setStyleSheet("color: #3fb950;")
            self.inputs[provider_id].clear()
        else:
            self.status_labels[provider_id].setText(f"⚠️ Saved ({mask_key(key_val)})")
            self.status_labels[provider_id].setStyleSheet("color: #d29922; font-size: 11px;")
            self.global_status.setText(f"Warning: {message}")
            self.global_status.setStyleSheet("color: #d29922;")
