"""
Fusion (VFX & Node-Based Compositing) Workspace for Vibmo Desktop.
Features Node Library Palette, Interactive DAG Canvas with Wire Routing, and Dynamic Parameter Inspector.
"""

from __future__ import annotations
from typing import Any, Optional, Dict
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QSplitter,
    QListWidget,
    QListWidgetItem,
    QLabel,
    QPushButton,
    QLineEdit,
    QDoubleSpinBox,
    QFormLayout,
    QGroupBox,
)

from vibmo.graph.engine import VibmoStateGraph
from vibmo.desktop.widgets.node_graph import InteractiveNodeGraphWidget


class FusionWorkspace(QWidget):
    """Top-level Fusion (Node-Based Compositing & VFX) Workspace."""

    def __init__(self, state_graph: VibmoStateGraph, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self.state_graph = state_graph

        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(4, 4, 4, 4)
        main_layout.setSpacing(4)

        splitter = QSplitter(Qt.Orientation.Horizontal)

        # 1. Left: Node Library / Palette
        palette_widget = QWidget()
        p_layout = QVBoxLayout(palette_widget)
        p_layout.setContentsMargins(4, 4, 4, 4)

        p_title = QLabel("🧬 Node Library")
        p_title.setStyleSheet("font-weight: bold; font-size: 13px; color: #38BDF8;")
        p_layout.addWidget(p_title)

        self.node_list = QListWidget()
        available_nodes = [
            ("Background", "generator"),
            ("FastNoise", "generator"),
            ("Text3D", "generator"),
            ("Shape2D", "generator"),
            ("GaussianBlur", "filter"),
            ("DirectionalBlur", "filter"),
            ("Glow", "filter"),
            ("Transform2D", "transform"),
            ("GridWarp", "transform"),
            ("DeltaKeyer", "matte"),
            ("PolygonMask", "matte"),
            ("ColorCorrector", "color"),
            ("Merge", "color"),
            ("PlanarTracker", "tracking"),
        ]
        for n_type, cat in available_nodes:
            item = QListWidgetItem(f"+ {n_type}")
            item.setData(Qt.ItemDataRole.UserRole, (n_type, cat))
            self.node_list.addItem(item)

        p_layout.addWidget(self.node_list)

        add_node_btn = QPushButton("+ Add Node to Graph")
        add_node_btn.setObjectName("PrimaryBtn")
        add_node_btn.clicked.connect(self._on_add_node_clicked)
        p_layout.addWidget(add_node_btn)

        splitter.addWidget(palette_widget)

        # 2. Center: Interactive Node Graph Viewport
        self.graph_view = InteractiveNodeGraphWidget(self.state_graph, self)
        self.graph_view.scene.node_selected.connect(self._on_node_selected)
        splitter.addWidget(self.graph_view)

        # 3. Right: Parameter Inspector
        inspector_widget = QWidget()
        i_layout = QVBoxLayout(inspector_widget)
        i_layout.setContentsMargins(4, 4, 4, 4)

        i_title = QLabel("🎛 Node Inspector")
        i_title.setStyleSheet("font-weight: bold; font-size: 13px; color: #38BDF8;")
        i_layout.addWidget(i_title)

        self.inspector_group = QGroupBox("Selected Node Properties")
        self.form_layout = QFormLayout(self.inspector_group)
        
        self.name_edit = QLineEdit("No Node Selected")
        self.val1_spin = QDoubleSpinBox()
        self.val1_spin.setRange(-1000.0, 1000.0)
        self.val2_spin = QDoubleSpinBox()
        self.val2_spin.setRange(-1000.0, 1000.0)

        self.form_layout.addRow("Name:", self.name_edit)
        self.form_layout.addRow("Param 1 (Size/Rad):", self.val1_spin)
        self.form_layout.addRow("Param 2 (Gain/Blend):", self.val2_spin)

        i_layout.addWidget(self.inspector_group)
        i_layout.addStretch()

        splitter.addWidget(inspector_widget)
        splitter.setSizes([200, 750, 300])

        main_layout.addWidget(splitter)

        # Ensure active graph exists
        if not self.state_graph.project.fusion_graphs:
            self.state_graph.create_fusion_graph("Main VFX Graph")
        self.graph_view.scene.refresh_graph()

    def _on_add_node_clicked(self) -> None:
        sel = self.node_list.currentItem()
        if not sel:
            return
        node_type, category = sel.data(Qt.ItemDataRole.UserRole)
        fg = list(self.state_graph.project.fusion_graphs.values())[0]
        self.state_graph.add_fusion_node(
            graph_id=fg.id,
            node_type=node_type,
            category=category,
            pos_x=300.0 + len(fg.nodes) * 30,
            pos_y=200.0 + len(fg.nodes) * 20,
        )
        self.graph_view.scene.refresh_graph()

    def _on_node_selected(self, node_id: str) -> None:
        fg = list(self.state_graph.project.fusion_graphs.values())[0]
        node = fg.nodes.get(node_id)
        if node:
            self.name_edit.setText(node.name)
