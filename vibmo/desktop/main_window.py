"""
CapCut-Style Workstation Main Window for Vibmo Desktop Pro.
Features Top Category Tabs (Media, Audio, Text, Captions, Fusion, Color), 3-Column Studio Layout,
Motio Studio Fusion Node Graph, and Full Multi-Track CapCut Timeline.
"""

from __future__ import annotations
from typing import Any, Optional, List
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QStackedWidget,
    QPushButton,
    QLabel,
    QFileDialog,
    QMessageBox,
    QButtonGroup,
    QSplitter,
    QMenu,
)
from PySide6.QtGui import QFont, QShortcut, QKeySequence

from vibmo.graph.engine import VibmoStateGraph
from vibmo.desktop.capcut_theme import CAPCUT_STYLESHEET
from vibmo.desktop.widgets.capcut_player import CapCutPlayer
from vibmo.desktop.widgets.capcut_inspector import CapCutInspector
from vibmo.desktop.widgets.capcut_media_library import CapCutMediaLibrary
from vibmo.desktop.widgets.capcut_timeline import CapCutTimeline
from vibmo.desktop.widgets.fusion_studio_canvas import FusionStudioCanvas
from vibmo.desktop.workspaces.color import ColorWorkspace
from vibmo.desktop.workspaces.fairlight import FairlightWorkspace
from vibmo.desktop.workspaces.delivery import DeliveryWorkspace


class VibmoMainWindow(QMainWindow):
    """CapCut-Style Flagship Desktop Application."""

    def __init__(self, state_graph: Optional[VibmoStateGraph] = None, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self.state_graph = state_graph or VibmoStateGraph()
        self.setWindowTitle(f"Vibmo Studio Pro — {self.state_graph.project.name}")
        self.resize(1560, 920)
        self.setMinimumSize(1100, 700)
        self.setStyleSheet(CAPCUT_STYLESHEET)

        # Central Root Container
        root = QWidget(self)
        self.setCentralWidget(root)
        root_layout = QVBoxLayout(root)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)

        # 1. Top Header Bar (CapCut Style with Logo, Menu, Categories, Project Name, Export)
        self.top_bar = self._create_top_bar()
        root_layout.addWidget(self.top_bar)

        # Master Vertical Splitter (Top Panels / Bottom Timeline)
        v_splitter = QSplitter(Qt.Orientation.Vertical)

        # 2. Main Center Stacked Views
        self.center_stack = QStackedWidget()

        # View 0: CapCut Standard 3-Column Layout [Media Library | Player | Inspector]
        self.standard_edit_view = self._create_standard_edit_view()
        self.center_stack.addWidget(self.standard_edit_view)  # Index 0

        # View 1: Motio Studio Fusion Node Graph Canvas
        self.fusion_canvas = FusionStudioCanvas(self.state_graph, self)
        self.center_stack.addWidget(self.fusion_canvas)        # Index 1

        # View 2: Color Grading Page
        self.color_page = ColorWorkspace(self.state_graph, self)
        self.center_stack.addWidget(self.color_page)           # Index 2

        # View 3: Fairlight Audio Mixer & EQ
        self.fairlight_page = FairlightWorkspace(self.state_graph, self)
        self.center_stack.addWidget(self.fairlight_page)       # Index 3

        # View 4: Delivery / Export Queue
        self.delivery_page = DeliveryWorkspace(self.state_graph, self)
        self.center_stack.addWidget(self.delivery_page)        # Index 4

        # View 5: Python Scripting & REPL Console
        from vibmo.desktop.workspaces.scripting import ScriptingWorkspace
        self.scripting_page = ScriptingWorkspace(self.state_graph, self)
        self.center_stack.addWidget(self.scripting_page)       # Index 5

        # Workspaces and Compatibility Aliases (No dangling unmanaged widgets!)
        self.motion_ws = self.standard_edit_view
        self.fusion_ws = self.fusion_canvas
        self.color_ws = self.color_page
        self.fairlight_ws = self.fairlight_page
        self.delivery_ws = self.delivery_page
        self.scripting_ws = self.scripting_page
        self.stack = self.center_stack

        v_splitter.addWidget(self.center_stack)

        # 3. Bottom CapCut Multi-Track Timeline (Always Visible)
        self.timeline = CapCutTimeline(self.state_graph, self)
        self.timeline.frame_changed.connect(self._on_timeline_frame_changed)
        self.player.frame_rendered.connect(self.timeline.set_playhead_frame)
        v_splitter.addWidget(self.timeline)

        v_splitter.setSizes([520, 360])
        root_layout.addWidget(v_splitter, 1)

        # Shortcuts & Event Listeners
        self._setup_shortcuts()
        self.state_graph.subscribe(self._on_state_changed)

    def _create_top_bar(self) -> QWidget:
        bar = QWidget()
        bar.setObjectName("TopBar")
        bar.setFixedHeight(44)
        layout = QHBoxLayout(bar)
        layout.setContentsMargins(14, 4, 14, 4)
        layout.setSpacing(10)

        # Logo
        logo = QLabel("Vibmo Studio")
        logo.setObjectName("BrandLogo")
        layout.addWidget(logo)

        # Menu Button
        menu_btn = QPushButton("Menu ▾")
        menu = QMenu(self)
        menu.addAction("New Project", lambda: None)
        menu.addAction("Open Project...", self._open_project)
        menu.addAction("Save Project (Ctrl+S)", self._save_project)
        menu.addSeparator()
        menu.addAction("✨ AI Motion Director (Ctrl+K)...", self._open_ai_director)
        menu.addAction("🔑 API Key Settings...", self._open_api_keys)
        menu.addSeparator()
        menu.addAction("Export Video...", self._on_export_clicked)
        menu_btn.setMenu(menu)
        layout.addWidget(menu_btn)

        layout.addSpacing(14)

        # CapCut Category Navigation Tabs
        self.nav_btn_group = QButtonGroup(self)
        self.nav_btn_group.setExclusive(True)

        categories = [
            ("Media", 0),
            ("Audio", 0),
            ("Text", 0),
            ("Captions", 0),
            ("Fusion", 1),
            ("Color", 2),
            ("Fairlight", 3),
            ("Scripting", 5),
        ]

        self.tab_buttons: List[QPushButton] = []
        for title, view_idx in categories:
            btn = QPushButton(title)
            btn.setObjectName("NavTabBtn")
            btn.setCheckable(True)
            if title == "Media":
                btn.setChecked(True)

            def make_handler(idx: int):
                def handler():
                    self.center_stack.setCurrentIndex(idx)
                    if idx == 1:
                        self.fusion_canvas.refresh_graph()
                        self.fusion_canvas._reset_viewport()
                return handler

            btn.clicked.connect(make_handler(view_idx))
            self.nav_btn_group.addButton(btn)
            self.tab_buttons.append(btn)
            layout.addWidget(btn)

        layout.addStretch()

        # Center Project Title
        proj_title = QLabel(self.state_graph.project.name)
        proj_title.setObjectName("ProjectTitle")
        layout.addWidget(proj_title)

        layout.addStretch()

        # AI Motion Director Button (Glowing Purple)
        ai_btn = QPushButton("✨ AI Director")
        ai_btn.setStyleSheet("""
            QPushButton {
                background: linear-gradient(135deg, #7c3aed, #4f46e5);
                background-color: #6366f1;
                color: #ffffff;
                border: 1px solid #818cf8;
                border-radius: 6px;
                padding: 4px 12px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #4f46e5;
            }
        """)
        ai_btn.clicked.connect(self._open_ai_director)
        layout.addWidget(ai_btn)

        # API Keys Button (Emerald Green)
        keys_btn = QPushButton("🔑 API Keys")
        keys_btn.setStyleSheet("""
            QPushButton {
                background-color: #064e3b;
                color: #a7f3d0;
                border: 1px solid #059669;
                border-radius: 6px;
                padding: 4px 10px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #047857;
            }
        """)
        keys_btn.clicked.connect(self._open_api_keys)
        layout.addWidget(keys_btn)

        # Export Button (Glowing Cyan Top Right)
        export_btn = QPushButton("Export")
        export_btn.setObjectName("ExportBtn")
        export_btn.clicked.connect(self._on_export_clicked)
        layout.addWidget(export_btn)

        return bar

    def _create_standard_edit_view(self) -> QWidget:
        """3-Column CapCut Layout [Media Library | Player | Inspector]."""
        w = QWidget()
        layout = QHBoxLayout(w)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(8)

        splitter = QSplitter(Qt.Orientation.Horizontal)

        # 1. Left: Media Library
        self.media_library = CapCutMediaLibrary(self.state_graph, self)
        splitter.addWidget(self.media_library)

        # 2. Center: 16:9 Dedicated Player
        self.player = CapCutPlayer(self.state_graph, self)
        splitter.addWidget(self.player)

        # 3. Right: Properties & Details Inspector
        self.inspector = CapCutInspector(self.state_graph, self)
        splitter.addWidget(self.inspector)

        splitter.setSizes([340, 720, 320])
        layout.addWidget(splitter)
        return w

    def _on_timeline_frame_changed(self, frame: int) -> None:
        self.player.render_frame_at(frame)

    def _on_export_clicked(self) -> None:
        self.center_stack.setCurrentIndex(4)

    def _open_project(self) -> None:
        file_path, _ = QFileDialog.getOpenFileName(self, "Open Vibmo Project", "", "Vibmo Project (*.vibmo *.json)")
        if file_path:
            self.state_graph = VibmoStateGraph.load_from_file(file_path)
            self.player.clear_cache()
            self.media_library.refresh_cards()
            self.timeline.refresh_headers()
            self.fusion_canvas.refresh_graph()

    def _save_project(self) -> None:
        file_path, _ = QFileDialog.getSaveFileName(self, "Save Vibmo Project", f"{self.state_graph.project.name}.vibmo", "Vibmo Project (*.vibmo *.json)")
        if file_path:
            self.state_graph.save_to_file(file_path)
            QMessageBox.information(self, "Project Saved", f"Project successfully saved to:\n{file_path}")

    def _open_ai_director(self) -> None:
        """Opens the native LangGraph AI Motion Director dialog."""
        from vibmo.desktop.dialogs.ai_director_dialog import AiDirectorDialog
        current_code = getattr(self.scripting_page, "code_edit", None)
        code_str = current_code.toPlainText() if current_code else ""
        dlg = AiDirectorDialog(current_code=code_str, parent=self)
        dlg.script_updated.connect(self._on_script_updated_from_ai)
        dlg.exec()

    def _open_api_keys(self) -> None:
        """Opens the native API Keys settings dialog."""
        from vibmo.desktop.dialogs.api_keys_dialog import ApiKeysDialog
        dlg = ApiKeysDialog(parent=self)
        dlg.exec()

    def _on_script_updated_from_ai(self, new_code: str) -> None:
        """Applies updated script from AI Director to Scripting workspace and reloads."""
        if hasattr(self.scripting_page, "code_edit"):
            self.scripting_page.code_edit.setPlainText(new_code)
            if hasattr(self.scripting_page, "_run_script"):
                self.scripting_page._run_script()
        self.player.clear_cache()
        self.timeline.refresh_headers()
        self.player.render_frame_at(self.timeline.scene.current_frame)

    def _setup_shortcuts(self) -> None:
        QShortcut(QKeySequence("Ctrl+S"), self, self._save_project)
        QShortcut(QKeySequence("Ctrl+O"), self, self._open_project)
        QShortcut(QKeySequence("Ctrl+K"), self, self._open_ai_director)
        QShortcut(QKeySequence("Ctrl+B"), self, self.timeline.split_at_playhead)
        QShortcut(QKeySequence("Delete"), self, self.timeline.delete_selected_clip)
        QShortcut(QKeySequence("Space"), self, self.player.toggle_playback)

    def _on_state_changed(self, event_type: str, payload: dict) -> None:
        self.player.clear_cache()
        self.media_library.refresh_cards()
        self.timeline.refresh_headers()
        self.fusion_canvas.refresh_graph()
        self.player.render_frame_at(self.timeline.scene.current_frame)

    def closeEvent(self, event: Any) -> None:
        if hasattr(self, "player") and self.player:
            self.player.play_timer.stop()
            self.player.worker.stop()
        super().closeEvent(event)
