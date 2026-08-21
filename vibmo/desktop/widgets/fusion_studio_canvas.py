"""
Motio Studio-Style Fusion Node Graph Canvas for Vibmo Desktop.
Features DaVinci/Motio Node Cards, Glowing Sockets, Interactive Bézier Cables,
Canvas Grid, Shift+Space Command Palette, Drag-and-Drop Node Ingestion, and Real-Time Inspector.
"""

from __future__ import annotations
import math
from typing import Any, Dict, List, Optional, Tuple
from PySide6.QtCore import Qt, Signal, QPointF, QRectF, QMimeData
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QSplitter,
    QListWidget,
    QListWidgetItem,
    QLabel,
    QPushButton,
    QGraphicsView,
    QGraphicsScene,
    QGraphicsItem,
    QGraphicsPathItem,
    QGroupBox,
    QFormLayout,
    QLineEdit,
    QDoubleSpinBox,
    QSlider,
    QMenu,
    QFrame,
)
from PySide6.QtGui import (
    QPainter,
    QColor,
    QBrush,
    QPen,
    QFont,
    QPainterPath,
    QMouseEvent,
    QWheelEvent,
    QKeyEvent,
    QDrag,
    QPixmap,
    QDragEnterEvent,
    QDropEvent,
    QLinearGradient,
    QShortcut,
    QKeySequence,
)

from vibmo.graph.engine import VibmoStateGraph
from vibmo.graph.schema import FusionGraph, FusionNode, AnimatableProperty
from vibmo.desktop.widgets.fusion_command_palette import FusionCommandPalette


class DraggableNodeList(QListWidget):
    """Fusion Node Library List supporting drag-and-drop directly onto DAG canvas."""

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self.setDragEnabled(True)
        self.setSelectionMode(QListWidget.SelectionMode.SingleSelection)

    def startDrag(self, supportedActions: Qt.DropAction) -> None:
        item = self.currentItem()
        if not item:
            return
        node_type, category = item.data(Qt.ItemDataRole.UserRole)
        drag = QDrag(self)
        mime = QMimeData()
        mime.setText(f"{node_type}:{category}")
        drag.setMimeData(mime)

        pix = QPixmap(140, 30)
        pix.fill(QColor("#0284C7"))
        drag.setPixmap(pix)
        drag.exec(Qt.DropAction.CopyAction)


class StudioNodeCardItem(QGraphicsItem):
    """Motio Studio-Style Fusion Node Card with Category Header and Sockets."""

    def __init__(self, node: FusionNode, parent: Optional[QGraphicsItem] = None) -> None:
        super().__init__(parent)
        self.node = node
        self.setPos(node.pos_x, node.pos_y)
        self.setFlags(
            QGraphicsItem.GraphicsItemFlag.ItemIsMovable |
            QGraphicsItem.GraphicsItemFlag.ItemIsSelectable |
            QGraphicsItem.GraphicsItemFlag.ItemSendsGeometryChanges
        )
        self.width = 170.0
        self.height = 68.0

    def boundingRect(self) -> QRectF:
        return QRectF(-12, -12, self.width + 24, self.height + 24)

    def paint(self, painter: QPainter, option: Any, widget: Optional[QWidget] = None) -> None:
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        cat_colors = {
            "generator": (QColor("#0284C7"), QColor("#0369A1")),
            "filter": (QColor("#8B5CF6"), QColor("#6D28D9")),
            "color": (QColor("#10B981"), QColor("#047857")),
            "matte": (QColor("#F59E0B"), QColor("#D97706")),
            "io": (QColor("#EF4444"), QColor("#B91C1C")),
            "transform": (QColor("#EC4899"), QColor("#BE185D")),
            "tracking": (QColor("#6366F1"), QColor("#4338CA")),
        }
        c_top, c_bot = cat_colors.get(self.node.category, (QColor("#64748B"), QColor("#475569")))

        # 1. Main Card Shadow & Body
        is_sel = self.isSelected()
        border_pen = QPen(QColor("#00E5FF") if is_sel else QColor("#2D2D36"), 2.2 if is_sel else 1.2)
        painter.setPen(border_pen)
        painter.setBrush(QBrush(QColor("#18181F")))
        painter.drawRoundedRect(0, 0, self.width, self.height, 8, 8)

        # 2. Gradient Category Header
        header_grad = QLinearGradient(0, 0, self.width, 0)
        header_grad.setColorAt(0.0, c_top)
        header_grad.setColorAt(1.0, c_bot)
        painter.setBrush(QBrush(header_grad))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRoundedRect(0, 0, self.width, 22, 5, 5)

        # 3. Header Text
        painter.setPen(QPen(QColor("#FFFFFF")))
        painter.setFont(QFont("Segoe UI", 9, QFont.Weight.Bold))
        painter.drawText(QRectF(10, 2, self.width - 20, 18), Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter, self.node.name)

        painter.setFont(QFont("Segoe UI", 7))
        painter.setPen(QPen(QColor(255, 255, 255, 180)))
        painter.drawText(QRectF(10, 2, self.width - 20, 18), Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter, self.node.category.upper())

        # 4. Body Content
        painter.setFont(QFont("Segoe UI", 9))
        painter.setPen(QPen(QColor("#ECECED")))
        painter.drawText(QRectF(12, 28, self.width - 24, 20), Qt.AlignmentFlag.AlignLeft, self.node.node_type)

        painter.setFont(QFont("Segoe UI", 7))
        painter.setPen(QPen(QColor("#71717A")))
        painter.drawText(QRectF(12, 48, self.width - 24, 16), Qt.AlignmentFlag.AlignLeft, f"Active • {len(self.node.properties)} Props")

        # 5. Input Socket (Left Amber Circle)
        if self.node.inputs:
            painter.setBrush(QBrush(QColor("#F59E0B")))
            painter.setPen(QPen(QColor("#FFFFFF"), 2.0))
            painter.drawEllipse(-7, int(self.height / 2) - 7, 14, 14)

        # 6. Output Socket (Right Cyan Circle)
        if self.node.outputs:
            painter.setBrush(QBrush(QColor("#00E5FF")))
            painter.setPen(QPen(QColor("#FFFFFF"), 2.0))
            painter.drawEllipse(int(self.width) - 7, int(self.height / 2) - 7, 14, 14)

    def itemChange(self, change: Any, value: Any) -> Any:
        if change == QGraphicsItem.GraphicsItemChange.ItemPositionHasChanged:
            self.node.pos_x = self.pos().x()
            self.node.pos_y = self.pos().y()
            if self.scene() and hasattr(self.scene(), "update_wires"):
                self.scene().update_wires()
        return super().itemChange(change, value)


class FusionStudioScene(QGraphicsScene):
    """Interactive DAG Scene with Grid, Wire Dragging, and Connection Management."""
    node_selected = Signal(str)

    def __init__(self, state_graph: VibmoStateGraph, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self.state_graph = state_graph
        self.setBackgroundBrush(QBrush(QColor("#0D0D10")))
        self.setSceneRect(0, 0, 3000, 2000)

        self.node_items: Dict[str, StudioNodeCardItem] = {}
        self.wire_items: List[QGraphicsPathItem] = []

        self.is_dragging_wire = False
        self.wire_start_node: Optional[str] = None
        self.temp_wire: Optional[QGraphicsPathItem] = None

    def drawBackground(self, painter: QPainter, rect: QRectF) -> None:
        super().drawBackground(painter, rect)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, False)

        grid_size = 30
        left = int(rect.left()) - (int(rect.left()) % grid_size)
        top = int(rect.top()) - (int(rect.top()) % grid_size)

        painter.setPen(QPen(QColor("#1A1A22"), 2))
        for x in range(left, int(rect.right()), grid_size):
            for y in range(top, int(rect.bottom()), grid_size):
                painter.drawPoint(x, y)

    def _get_active_graph(self) -> Optional[FusionGraph]:
        if not self.state_graph.project.fusion_graphs:
            return None
        return list(self.state_graph.project.fusion_graphs.values())[0]

    def refresh_graph(self) -> None:
        self.clear()
        self.node_items.clear()
        self.wire_items.clear()

        fg = self._get_active_graph()
        if not fg:
            return

        for node in fg.nodes.values():
            item = StudioNodeCardItem(node)
            self.addItem(item)
            self.node_items[node.id] = item

        self.update_wires()

    def update_wires(self) -> None:
        for w in self.wire_items:
            self.removeItem(w)
        self.wire_items.clear()

        fg = self._get_active_graph()
        if not fg:
            return

        for conn in fg.connections:
            if conn.from_node in self.node_items and conn.to_node in self.node_items:
                n_from = self.node_items[conn.from_node]
                n_to = self.node_items[conn.to_node]

                p1 = QPointF(n_from.pos().x() + n_from.width, n_from.pos().y() + n_from.height / 2)
                p2 = QPointF(n_to.pos().x(), n_to.pos().y() + n_to.height / 2)

                path = QPainterPath(p1)
                dx = max(50.0, abs(p2.x() - p1.x()) * 0.5)
                path.cubicTo(QPointF(p1.x() + dx, p1.y()), QPointF(p2.x() - dx, p2.y()), p2)

                wire = self.addPath(path, QPen(QColor("#00E5FF"), 2.8))
                self.wire_items.append(wire)

    def mousePressEvent(self, event: Any) -> None:
        item = self.itemAt(event.scenePos(), self.views()[0].transform() if self.views() else None)
        if isinstance(item, StudioNodeCardItem):
            self.node_selected.emit(item.node.id)
            local_pos = item.mapFromScene(event.scenePos())
            if local_pos.x() >= item.width - 16:
                self.is_dragging_wire = True
                self.wire_start_node = item.node.id
                return

        super().mousePressEvent(event)

    def mouseMoveEvent(self, event: Any) -> None:
        if self.is_dragging_wire and self.wire_start_node in self.node_items:
            n_from = self.node_items[self.wire_start_node]
            p1 = QPointF(n_from.pos().x() + n_from.width, n_from.pos().y() + n_from.height / 2)
            p2 = event.scenePos()

            path = QPainterPath(p1)
            dx = max(40.0, abs(p2.x() - p1.x()) * 0.5)
            path.cubicTo(QPointF(p1.x() + dx, p1.y()), QPointF(p2.x() - dx, p2.y()), p2)

            if not self.temp_wire:
                self.temp_wire = self.addPath(path, QPen(QColor("#F59E0B"), 2.2, Qt.PenStyle.DashLine))
            else:
                self.temp_wire.setPath(path)

        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event: Any) -> None:
        if self.is_dragging_wire:
            self.is_dragging_wire = False
            if self.temp_wire:
                self.removeItem(self.temp_wire)
                self.temp_wire = None

            item = self.itemAt(event.scenePos(), self.views()[0].transform() if self.views() else None)
            if isinstance(item, StudioNodeCardItem) and item.node.id != self.wire_start_node:
                fg = self._get_active_graph()
                if fg and self.wire_start_node:
                    self.state_graph.connect_fusion_nodes(
                        graph_id=fg.id,
                        from_node_id=self.wire_start_node,
                        to_node_id=item.node.id,
                    )
                    self.update_wires()

            self.wire_start_node = None

        super().mouseReleaseEvent(event)


class FusionStudioCanvas(QWidget):
    """Complete Motio Studio-Style Fusion Workspace with Shift+Space Select Tool and Drag-and-Drop."""

    def __init__(self, state_graph: VibmoStateGraph, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self.state_graph = state_graph
        self.selected_node_id: Optional[str] = None
        self.setAcceptDrops(True)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(4)

        splitter = QSplitter(Qt.Orientation.Horizontal)

        # 1. Left: Node Library Palette
        palette = QWidget()
        palette.setFixedWidth(210)
        p_layout = QVBoxLayout(palette)
        p_layout.setContentsMargins(4, 4, 4, 4)
        p_layout.setSpacing(6)

        p_lbl = QLabel("🧬 Fusion VFX Library")
        p_lbl.setStyleSheet("font-weight: 800; color: #00E5FF; font-size: 12px;")
        p_layout.addWidget(p_lbl)

        p_hint = QLabel("Drag to canvas or Shift+Space")
        p_hint.setStyleSheet("color: #71717A; font-size: 10px; margin-bottom: 2px;")
        p_layout.addWidget(p_hint)

        self.node_list = DraggableNodeList(self)
        nodes = [
            ("Background", "generator"),
            ("FastNoise", "generator"),
            ("Text3D", "generator"),
            ("Shape2D", "generator"),
            ("GaussianBlur", "filter"),
            ("OpticalGlow", "filter"),
            ("DropShadow", "filter"),
            ("DeltaKeyer", "matte"),
            ("PolygonMask", "matte"),
            ("ColorCorrector", "color"),
            ("Merge", "color"),
            ("Transform2D", "transform"),
            ("GridWarp", "transform"),
            ("PlanarTracker", "tracking"),
        ]
        for n_name, cat in nodes:
            item = QListWidgetItem(f"+ {n_name}")
            item.setData(Qt.ItemDataRole.UserRole, (n_name, cat))
            self.node_list.addItem(item)
        p_layout.addWidget(self.node_list)

        add_btn = QPushButton("+ Add Node to Graph")
        add_btn.setObjectName("PrimaryAction")
        add_btn.setFixedHeight(30)
        add_btn.clicked.connect(self._add_node)
        p_layout.addWidget(add_btn)

        splitter.addWidget(palette)

        # 2. Center: DAG Viewport Canvas
        canvas_container = QWidget()
        cc_layout = QVBoxLayout(canvas_container)
        cc_layout.setContentsMargins(0, 0, 0, 0)
        cc_layout.setSpacing(2)

        # Canvas Header Toolbar
        ch_bar = QHBoxLayout()
        ch_bar.setContentsMargins(6, 2, 6, 2)
        ch_lbl = QLabel("VFX Node Graph (Shift+Space: Select Tool)")
        ch_lbl.setStyleSheet("color: #71717A; font-weight: bold; font-size: 11px;")
        ch_bar.addWidget(ch_lbl)
        ch_bar.addStretch()

        palette_btn = QPushButton("🔍 Tool Palette (Shift+Space)")
        palette_btn.setFixedHeight(22)
        palette_btn.clicked.connect(self.open_command_palette)
        ch_bar.addWidget(palette_btn)

        zoom_in_btn = QPushButton("+ Zoom")
        zoom_in_btn.setFixedHeight(22)
        zoom_in_btn.clicked.connect(lambda: self.view.scale(1.2, 1.2))
        zoom_out_btn = QPushButton("- Zoom")
        zoom_out_btn.setFixedHeight(22)
        zoom_out_btn.clicked.connect(lambda: self.view.scale(0.8, 0.8))
        reset_view_btn = QPushButton("Reset View")
        reset_view_btn.setFixedHeight(22)
        reset_view_btn.clicked.connect(self._reset_viewport)

        ch_bar.addWidget(zoom_in_btn)
        ch_bar.addWidget(zoom_out_btn)
        ch_bar.addWidget(reset_view_btn)
        cc_layout.addLayout(ch_bar)

        self.scene = FusionStudioScene(self.state_graph, self)
        self.scene.node_selected.connect(self._on_node_selected)

        self.view = QGraphicsView(self.scene)
        self.view.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.view.setStyleSheet("border: 1px solid #28282D; border-radius: 6px; background-color: #0D0D10;")
        self.view.setDragMode(QGraphicsView.DragMode.RubberBandDrag)
        self.view.setAcceptDrops(True)
        cc_layout.addWidget(self.view, 1)

        splitter.addWidget(canvas_container)

        # 3. Right: Node Parameter Inspector
        inspector = QWidget()
        inspector.setFixedWidth(280)
        i_layout = QVBoxLayout(inspector)
        i_layout.setContentsMargins(6, 6, 6, 6)
        i_layout.setSpacing(6)

        i_lbl = QLabel("🎛 Node Inspector")
        i_lbl.setStyleSheet("font-weight: 800; color: #00E5FF; font-size: 12px;")
        i_layout.addWidget(i_lbl)

        self.prop_box = QGroupBox("Selected Node Properties")
        self.form_layout = QFormLayout(self.prop_box)

        self.node_name_edit = QLineEdit("No Node Selected")
        self.node_name_edit.textChanged.connect(self._on_name_edited)
        self.form_layout.addRow("Node Name:", self.node_name_edit)

        self.p1_lbl = QLabel("Radius / Size:")
        self.p1_spin = QDoubleSpinBox()
        self.p1_spin.setRange(0.0, 500.0)
        self.p1_spin.setValue(10.0)
        self.p1_spin.valueChanged.connect(self._on_prop_changed)
        self.form_layout.addRow(self.p1_lbl, self.p1_spin)

        self.p2_lbl = QLabel("Gain / Blend:")
        self.p2_spin = QDoubleSpinBox()
        self.p2_spin.setRange(0.0, 500.0)
        self.p2_spin.setValue(1.0)
        self.p2_spin.valueChanged.connect(self._on_prop_changed)
        self.form_layout.addRow(self.p2_lbl, self.p2_spin)

        i_layout.addWidget(self.prop_box)
        i_layout.addStretch()

        splitter.addWidget(inspector)
        splitter.setSizes([210, 840, 280])

        layout.addWidget(splitter)

        # Keyboard Shortcut: Shift + Space for Tool Palette
        self.palette_shortcut = QShortcut(QKeySequence("Shift+Space"), self, self.open_command_palette)

        self._ensure_starter_composition()
        self.refresh_graph()
        self._reset_viewport()

    def open_command_palette(self) -> None:
        dialog = FusionCommandPalette(self)
        dialog.tool_selected.connect(self._on_palette_tool_selected)
        dialog.exec()

    def _on_palette_tool_selected(self, node_type: str, category: str) -> None:
        fg = self._get_active_graph()
        if not fg:
            return

        # Insert near viewport center or offset from selected node
        prev_sel = self.selected_node_id
        if prev_sel and prev_sel in fg.nodes:
            prev_node = fg.nodes[prev_sel]
            pos_x = prev_node.pos_x + 210.0
            pos_y = prev_node.pos_y
        else:
            pos_x = 450.0 + len(fg.nodes) * 20
            pos_y = 180.0

        new_node = self.state_graph.add_fusion_node(
            graph_id=fg.id,
            node_type=node_type,
            category=category,
            pos_x=pos_x,
            pos_y=pos_y,
        )

        # Auto-connect if a node was selected
        if prev_sel and prev_sel in fg.nodes:
            self.state_graph.connect_fusion_nodes(
                graph_id=fg.id,
                from_node_id=prev_sel,
                to_node_id=new_node.id,
            )

        self.refresh_graph()
        self._on_node_selected(new_node.id)

    def _ensure_starter_composition(self) -> None:
        if not self.state_graph.project.fusion_graphs:
            fg = self.state_graph.create_fusion_graph("Main VFX Graph")
        else:
            fg = list(self.state_graph.project.fusion_graphs.values())[0]

        if not fg.nodes or len(fg.nodes) <= 1:
            fg.nodes.clear()
            fg.connections.clear()

            n_in = self.state_graph.add_fusion_node(fg.id, "MediaIn", "io", pos_x=60, pos_y=160)
            n_noise = self.state_graph.add_fusion_node(fg.id, "FastNoise", "generator", pos_x=270, pos_y=100)
            n_glow = self.state_graph.add_fusion_node(fg.id, "Glow", "filter", pos_x=480, pos_y=160)
            n_keyer = self.state_graph.add_fusion_node(fg.id, "DeltaKeyer", "matte", pos_x=690, pos_y=160)
            n_out = self.state_graph.add_fusion_node(fg.id, "MediaOut", "io", pos_x=900, pos_y=160)

            self.state_graph.connect_fusion_nodes(fg.id, n_in.id, n_noise.id)
            self.state_graph.connect_fusion_nodes(fg.id, n_noise.id, n_glow.id)
            self.state_graph.connect_fusion_nodes(fg.id, n_glow.id, n_keyer.id)
            self.state_graph.connect_fusion_nodes(fg.id, n_keyer.id, n_out.id)

    def _get_active_graph(self) -> Optional[FusionGraph]:
        if not self.state_graph.project.fusion_graphs:
            return None
        return list(self.state_graph.project.fusion_graphs.values())[0]

    def _add_node(self) -> None:
        sel = self.node_list.currentItem()
        if not sel:
            return
        n_type, cat = sel.data(Qt.ItemDataRole.UserRole)
        fg = self._get_active_graph()
        if fg:
            offset_x = 100 + len(fg.nodes) * 50
            offset_y = 120 + (len(fg.nodes) % 3) * 60
            new_node = self.state_graph.add_fusion_node(
                graph_id=fg.id,
                node_type=n_type,
                category=cat,
                pos_x=offset_x,
                pos_y=offset_y,
            )
            self.refresh_graph()
            self._on_node_selected(new_node.id)

    def refresh_graph(self) -> None:
        self.scene.refresh_graph()

    def _on_node_selected(self, node_id: str) -> None:
        self.selected_node_id = node_id
        fg = self._get_active_graph()
        if not fg or node_id not in fg.nodes:
            return

        node = fg.nodes[node_id]
        self.prop_box.setTitle(f"Properties: {node.name} ({node.category.upper()})")
        self.node_name_edit.blockSignals(True)
        self.node_name_edit.setText(node.name)
        self.node_name_edit.blockSignals(False)

        for nid, item in self.scene.node_items.items():
            item.setSelected(nid == node_id)

    def _on_name_edited(self, text: str) -> None:
        if not self.selected_node_id:
            return
        fg = self._get_active_graph()
        if fg and self.selected_node_id in fg.nodes:
            fg.nodes[self.selected_node_id].name = text
            self.scene.update()

    def _on_prop_changed(self) -> None:
        if not self.selected_node_id:
            return
        fg = self._get_active_graph()
        if fg and self.selected_node_id in fg.nodes:
            node = fg.nodes[self.selected_node_id]
            node.properties["val1"] = AnimatableProperty(name="val1", value=self.p1_spin.value())
            node.properties["val2"] = AnimatableProperty(name="val2", value=self.p2_spin.value())

    def _reset_viewport(self) -> None:
        self.view.resetTransform()
        self.view.centerOn(500, 200)

    # Drag & Drop Support
    def dragEnterEvent(self, event: QDragEnterEvent) -> None:
        if event.mimeData().hasText():
            event.acceptProposedAction()

    def dropEvent(self, event: QDropEvent) -> None:
        txt = event.mimeData().text()
        if ":" in txt:
            n_type, cat = txt.split(":", 1)
            fg = self._get_active_graph()
            if fg:
                view_pos = self.view.mapFrom(self, event.position().toPoint())
                scene_pos = self.view.mapToScene(view_pos)
                new_node = self.state_graph.add_fusion_node(
                    graph_id=fg.id,
                    node_type=n_type,
                    category=cat,
                    pos_x=scene_pos.x(),
                    pos_y=scene_pos.y(),
                )
                self.refresh_graph()
                self._on_node_selected(new_node.id)
                event.acceptProposedAction()
