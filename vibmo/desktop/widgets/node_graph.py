"""
Interactive Fusion Node Graph Canvas for Vibmo Desktop.
Features Draggable Nodes, Sockets, Interactive Bézier Wire Dragging, and Live State Graph Sync.
"""

from __future__ import annotations
import math
from typing import Any, Dict, List, Optional, Tuple
from PySide6.QtCore import Qt, Signal, QPointF, QRectF
from PySide6.QtWidgets import (
    QWidget,
    QGraphicsView,
    QGraphicsScene,
    QGraphicsItem,
    QGraphicsPathItem,
)
from PySide6.QtGui import (
    QPainter,
    QColor,
    QBrush,
    QPen,
    QFont,
    QPainterPath,
    QMouseEvent,
    QKeyEvent,
)

from vibmo.graph.engine import VibmoStateGraph
from vibmo.graph.schema import FusionGraph, FusionNode


class InteractiveVisualNode(QGraphicsItem):
    """Visual Node Item in the DAG with input and output sockets."""

    def __init__(self, node: FusionNode, parent: Optional[QGraphicsItem] = None) -> None:
        super().__init__(parent)
        self.node = node
        self.setPos(node.pos_x, node.pos_y)
        self.setFlags(
            QGraphicsItem.GraphicsItemFlag.ItemIsMovable |
            QGraphicsItem.GraphicsItemFlag.ItemIsSelectable |
            QGraphicsItem.GraphicsItemFlag.ItemSendsGeometryChanges
        )
        self.width = 150.0
        self.height = 54.0

    def boundingRect(self) -> QRectF:
        return QRectF(-8, -8, self.width + 16, self.height + 16)

    def paint(self, painter: QPainter, option: Any, widget: Optional[QWidget] = None) -> None:
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Header category colors
        cat_colors = {
            "generator": QColor("#0284C7"),
            "filter": QColor("#8B5CF6"),
            "color": QColor("#10B981"),
            "matte": QColor("#F59E0B"),
            "io": QColor("#EF4444"),
            "transform": QColor("#EC4899"),
        }
        accent = cat_colors.get(self.node.category, QColor("#64748B"))

        # Main Body
        painter.setBrush(QBrush(QColor("#1A1B22")))
        painter.setPen(QPen(QColor("#38BDF8") if self.isSelected() else QColor("#27272A"), 1.8))
        painter.drawRoundedRect(0, 0, self.width, self.height, 6, 6)

        # Top Accent Header Bar
        painter.setBrush(QBrush(accent))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRoundedRect(0, 0, self.width, 8, 3, 3)

        # Node Title
        painter.setPen(QPen(QColor("#F8FAFC")))
        painter.setFont(QFont("Segoe UI", 9, QFont.Weight.Bold))
        painter.drawText(QRectF(10, 12, self.width - 20, 20), Qt.AlignmentFlag.AlignLeft, self.node.name)

        # Node Type subtitle
        painter.setPen(QPen(QColor("#94A3B8")))
        painter.setFont(QFont("Segoe UI", 7))
        painter.drawText(QRectF(10, 32, self.width - 20, 16), Qt.AlignmentFlag.AlignLeft, self.node.node_type)

        # Input Socket (Left Orange Circle)
        if self.node.inputs:
            painter.setBrush(QBrush(QColor("#F59E0B")))
            painter.setPen(QPen(QColor("#FFFFFF"), 1.5))
            painter.drawEllipse(-5, int(self.height / 2) - 5, 10, 10)

        # Output Socket (Right Cyan Circle)
        if self.node.outputs:
            painter.setBrush(QBrush(QColor("#38BDF8")))
            painter.setPen(QPen(QColor("#FFFFFF"), 1.5))
            painter.drawEllipse(int(self.width) - 5, int(self.height / 2) - 5, 10, 10)

    def itemChange(self, change: Any, value: Any) -> Any:
        if change == QGraphicsItem.GraphicsItemChange.ItemPositionHasChanged:
            self.node.pos_x = self.pos().x()
            self.node.pos_y = self.pos().y()
            if self.scene() and hasattr(self.scene(), "update_wires"):
                self.scene().update_wires()
        return super().itemChange(change, value)


class InteractiveNodeScene(QGraphicsScene):
    """QGraphicsScene with dynamic Bézier wire rendering and interactive connection dragging."""
    node_selected = Signal(str)

    def __init__(self, state_graph: VibmoStateGraph, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self.state_graph = state_graph
        self.setBackgroundBrush(QBrush(QColor("#101114")))
        self.setSceneRect(0, 0, 3000, 2000)

        self.node_items: Dict[str, InteractiveVisualNode] = {}
        self.wire_items: List[QGraphicsPathItem] = []

        # Wire dragging state
        self.is_dragging_wire = False
        self.wire_start_node: Optional[str] = None
        self.temp_wire: Optional[QGraphicsPathItem] = None

        self.refresh_graph()

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

        # Add Nodes
        for node in fg.nodes.values():
            item = InteractiveVisualNode(node)
            self.addItem(item)
            self.node_items[node.id] = item

        self.update_wires()

    def update_wires(self) -> None:
        # Remove old wires
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
                dx = max(40.0, abs(p2.x() - p1.x()) * 0.5)
                c1 = QPointF(p1.x() + dx, p1.y())
                c2 = QPointF(p2.x() - dx, p2.y())
                path.cubicTo(c1, c2, p2)

                wire = self.addPath(path, QPen(QColor("#38BDF8"), 2.5))
                self.wire_items.append(wire)

    def mousePressEvent(self, event: Any) -> None:
        item = self.itemAt(event.scenePos(), self.views()[0].transform() if self.views() else None)
        if isinstance(item, InteractiveVisualNode):
            self.node_selected.emit(item.node.id)
            # Check if clicked on right output socket to start wire dragging
            local_pos = item.mapFromScene(event.scenePos())
            if local_pos.x() >= item.width - 15:
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
            dx = max(30.0, abs(p2.x() - p1.x()) * 0.5)
            path.cubicTo(QPointF(p1.x() + dx, p1.y()), QPointF(p2.x() - dx, p2.y()), p2)

            if not self.temp_wire:
                self.temp_wire = self.addPath(path, QPen(QColor("#F59E0B"), 2.0, Qt.PenStyle.DashLine))
            else:
                self.temp_wire.setPath(path)

        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event: Any) -> None:
        if self.is_dragging_wire:
            self.is_dragging_wire = False
            if self.temp_wire:
                self.removeItem(self.temp_wire)
                self.temp_wire = None

            # Check if dropped onto a node's input socket
            item = self.itemAt(event.scenePos(), self.views()[0].transform() if self.views() else None)
            if isinstance(item, InteractiveVisualNode) and item.node.id != self.wire_start_node:
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


class InteractiveNodeGraphWidget(QGraphicsView):
    """Complete Node Graph Viewport widget with smooth pan and zoom."""

    def __init__(self, state_graph: VibmoStateGraph, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self.state_graph = state_graph
        self.scene = InteractiveNodeScene(state_graph, self)
        self.setScene(self.scene)
        self.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.setStyleSheet("border: 1px solid #27272A; border-radius: 6px;")
        self.setDragMode(QGraphicsView.DragMode.RubberBandDrag)
