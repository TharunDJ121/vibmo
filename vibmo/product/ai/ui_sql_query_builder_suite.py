"""
Visual SQL Query Builder UI Suite for Vibmo / Motio.
Components:
- VisualSqlQueryBuilder
- SchemaTableNode (VisualSqlQueryBlock)
- TableJoinConnectorCurve
- SqlSyntaxHighlightView
- ExecutionTimePill
"""

from __future__ import annotations
import math
from typing import Any, Dict, List, Optional, Sequence, Tuple, Union
import cairo

from vibmo.core.color import Color, colors
from vibmo.core.vector import Vector2D
from vibmo.core.signal import Signal, AnimationAction
from vibmo.core.easing import Ease, EasingFunc
from vibmo.scene.node import Node
from vibmo.spatial.shadows import DropShadow


class SchemaTableNode(Node):
    """Visual table schema block with column names, data types, and primary key badges."""

    def __init__(
        self,
        table_name: str = "users",
        columns: Optional[List[Tuple[str, str, bool]]] = None,
        select_columns: Optional[List[str]] = None,
        where_conditions: Optional[List[str]] = None,
        tables: Optional[Union[List[str], List[Dict[str, Any]]]] = None,
        query: Optional[str] = None,
        width: float = 230.0,
        height: Optional[float] = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)
        self.table_name = table_name
        self.select_columns = list(select_columns) if select_columns is not None else []
        self.where_conditions = list(where_conditions) if where_conditions is not None else []
        self.tables = list(tables) if tables is not None else []
        self.query = query

        if columns is not None:
            self.columns = columns
        elif self.select_columns:
            self.columns = [(c, "VARCHAR", i == 0) for i, c in enumerate(self.select_columns)]
        else:
            self.columns = [("id", "BIGINT", True), ("name", "VARCHAR", False), ("email", "VARCHAR", False), ("created_at", "TIMESTAMP", False)]

        self.width_val = float(width)
        if height is not None:
            self.height_val = float(height)
            self.height = self.height_val
        elif select_columns is not None and where_conditions is not None:
            self.height = 40.0 + 32.0 * (len(self.select_columns) + len(self.where_conditions) + 2)
            self.height_val = self.height
        else:
            self.height_val = 40.0 + len(self.columns) * 26.0
            self.height = self.height_val

        self.join_curve = TableJoinConnectorCurve(p1=(260.0, 134.0), p2=(460.0, 160.0), color=colors.CYAN)
        self.add(self.join_curve)

    def draw_join_relation(
        self,
        table_a: Optional[str] = None,
        table_b: Optional[str] = None,
        table1: Optional[str] = None,
        table2: Optional[str] = None,
        duration: float = 1.2,
        ease: EasingFunc = Ease.out_quad,
    ) -> AnimationAction:
        self.join_curve.progress.set(0.0)
        return self.join_curve.progress.to(1.0, duration=duration, ease=ease)

    def local_bounds(self, time: float = 0.0) -> Tuple[float, float, float, float]:
        return (0.0, 0.0, self.width_val, self.height_val)

    def draw(self, ctx: Any, time: float = 0.0) -> None:
        w, h = self.width_val, self.height_val
        ctx.save()

        # Box
        r = 10.0
        if hasattr(ctx, "new_path"):
            ctx.new_path()
        if hasattr(ctx, "arc"):
            ctx.arc(w - r, r, r, -math.pi * 0.5, 0)
            ctx.arc(w - r, h - r, r, 0, math.pi * 0.5)
            ctx.arc(r, h - r, r, math.pi * 0.5, math.pi)
            ctx.arc(r, r, r, math.pi, math.pi * 1.5)
        if hasattr(ctx, "close_path"):
            ctx.close_path()

        ctx.set_source_rgba(0.06, 0.09, 0.15, 0.95)
        if hasattr(ctx, "fill_preserve"):
            ctx.fill_preserve()
        else:
            ctx.fill()
        ctx.set_source_rgba(0.2, 0.3, 0.45, 0.7)
        if hasattr(ctx, "set_line_width"):
            ctx.set_line_width(1.0)
        ctx.stroke()

        # Header background
        if hasattr(ctx, "new_path"):
            ctx.new_path()
        if hasattr(ctx, "arc"):
            ctx.arc(w - r, r, r, -math.pi * 0.5, 0)
        if hasattr(ctx, "line_to"):
            ctx.line_to(w, 34.0)
            ctx.line_to(0, 34.0)
        if hasattr(ctx, "arc"):
            ctx.arc(r, r, r, math.pi, math.pi * 1.5)
        if hasattr(ctx, "close_path"):
            ctx.close_path()
        ctx.set_source_rgba(0.1, 0.15, 0.25, 0.9)
        ctx.fill()

        # Table Name
        if hasattr(ctx, "select_font_face"):
            ctx.select_font_face("Inter", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
        if hasattr(ctx, "set_font_size"):
            ctx.set_font_size(12.0)
        ctx.set_source_rgba(0.95, 0.98, 1.0, 0.95)
        ctx.move_to(12.0, 22.0)
        if hasattr(ctx, "show_text"):
            ctx.show_text(f"Table: {self.table_name}")

        # Columns
        for i, (col_name, col_type, is_pk) in enumerate(self.columns):
            cy = 54.0 + i * 26.0
            if is_pk:
                ctx.set_source_rgba(0.95, 0.75, 0.2, 0.95)
                if hasattr(ctx, "select_font_face"):
                    ctx.select_font_face("Inter", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
                if hasattr(ctx, "set_font_size"):
                    ctx.set_font_size(10.0)
                ctx.move_to(12.0, cy)
                if hasattr(ctx, "show_text"):
                    ctx.show_text("PK")
            else:
                ctx.set_source_rgba(0.4, 0.5, 0.65, 0.7)
                if hasattr(ctx, "arc"):
                    ctx.arc(16.0, cy - 3.0, 2.5, 0, 2 * math.pi)
                ctx.fill()

            # Column Name
            if hasattr(ctx, "select_font_face"):
                ctx.select_font_face("Consolas", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)
            if hasattr(ctx, "set_font_size"):
                ctx.set_font_size(11.0)
            ctx.set_source_rgba(0.9, 0.95, 1.0, 0.9)
            ctx.move_to(28.0, cy)
            if hasattr(ctx, "show_text"):
                ctx.show_text(col_name)

            # Column Type
            if hasattr(ctx, "set_font_size"):
                ctx.set_font_size(9.0)
            ctx.set_source_rgba(0.45, 0.55, 0.7, 0.8)
            ext = ctx.text_extents(col_type) if hasattr(ctx, "text_extents") else None
            ext_w = ext.width if ext and hasattr(ext, "width") else 30.0
            ctx.move_to(w - ext_w - 12.0, cy)
            if hasattr(ctx, "show_text"):
                ctx.show_text(col_type)

        super().draw(ctx, time)
        ctx.restore()


VisualSqlQueryBlock = SchemaTableNode


class TableJoinConnectorCurve(Node):
    """Dynamic bezier curve connecting foreign key columns between 2 tables."""

    def __init__(
        self,
        p1: Optional[Tuple[float, float]] = None,
        p2: Optional[Tuple[float, float]] = None,
        start_pos: Tuple[float, float] = (240.0, 160.0),
        end_pos: Tuple[float, float] = (420.0, 160.0),
        color: Union[Color, str] = colors.CYAN,
        thickness: float = 2.5,
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)
        self.start_pos = p1 if p1 is not None else start_pos
        self.end_pos = p2 if p2 is not None else end_pos
        self.p1 = self.start_pos
        self.p2 = self.end_pos
        self.color = Color.from_any(color)
        self.thickness = float(thickness)
        self.progress = Signal(1.0, f"{self.name}.progress")

    def draw(self, ctx: Any, time: float = 0.0) -> None:
        prog = max(0.0, min(1.0, self.progress.get(time)))
        if prog <= 0.0:
            return

        ctx.save()
        x1, y1 = self.start_pos
        x2, y2 = self.end_pos
        dx = (x2 - x1) * prog
        dy = (y2 - y1) * prog

        ctx.set_source_rgba(*self.color.to_cairo())
        if hasattr(ctx, "set_line_width"):
            ctx.set_line_width(self.thickness)
        ctx.move_to(x1, y1)
        if hasattr(ctx, "curve_to"):
            ctx.curve_to(x1 + dx * 0.5, y1, x1 + dx * 0.5, y1 + dy, x1 + dx, y1 + dy)
        elif hasattr(ctx, "line_to"):
            ctx.line_to(x1 + dx, y1 + dy)
        ctx.stroke()
        ctx.restore()


class SqlSyntaxHighlightView(Node):
    """Generated SQL syntax highlighted text card."""

    def __init__(
        self,
        sql_query: Optional[str] = None,
        sql_text: Optional[str] = None,
        width: float = 680.0,
        height: float = 90.0,
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)
        self.sql_query = sql_query or sql_text or "SELECT u.id, u.name, o.total_usd\nFROM users u\nJOIN orders o ON u.id = o.user_id\nWHERE o.status = 'completed';"
        self.sql_text = Signal(self.sql_query, f"{self.name}.sql_text")
        self.width_val = float(width)
        self.height_val = float(height)

    def draw(self, ctx: Any, time: float = 0.0) -> None:
        w, h = self.width_val, self.height_val
        text = self.sql_text.get(time)

        ctx.save()
        r = 8.0
        if hasattr(ctx, "new_path"):
            ctx.new_path()
        if hasattr(ctx, "arc"):
            ctx.arc(w - r, r, r, -math.pi * 0.5, 0)
            ctx.arc(w - r, h - r, r, 0, math.pi * 0.5)
            ctx.arc(r, h - r, r, math.pi * 0.5, math.pi)
            ctx.arc(r, r, r, math.pi, math.pi * 1.5)
        if hasattr(ctx, "close_path"):
            ctx.close_path()

        ctx.set_source_rgba(0.04, 0.06, 0.1, 0.9)
        ctx.fill()
        ctx.set_source_rgba(0.18, 0.25, 0.35, 0.6)
        if hasattr(ctx, "set_line_width"):
            ctx.set_line_width(1.0)
        ctx.stroke()

        # SQL lines
        if hasattr(ctx, "select_font_face"):
            ctx.select_font_face("Consolas", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)
        if hasattr(ctx, "set_font_size"):
            ctx.set_font_size(12.0)

        lines = text.split("\n")
        for i, line in enumerate(lines[:4]):
            ctx.set_source_rgba(0.2, 0.85, 1.0, 0.95)
            ctx.move_to(16.0, 24.0 + i * 18.0)
            if hasattr(ctx, "show_text"):
                ctx.show_text(line)

        ctx.restore()


class ExecutionTimePill(Node):
    """Badge indicating SQL query execution time (`2.4 ms (Index Scan)`)."""

    def __init__(
        self,
        time_ms: float = 2.4,
        scan_type: str = "Index Scan",
        width: float = 160.0,
        height: float = 26.0,
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)
        self.time_ms = float(time_ms)
        self.scan_type = str(scan_type)
        self.width_val = float(width)
        self.height_val = float(height)

    def draw(self, ctx: Any, time: float = 0.0) -> None:
        w, h = self.width_val, self.height_val
        ctx.save()
        r = 6.0
        if hasattr(ctx, "new_path"):
            ctx.new_path()
        if hasattr(ctx, "arc"):
            ctx.arc(w - r, r, r, -math.pi * 0.5, 0)
            ctx.arc(w - r, h - r, r, 0, math.pi * 0.5)
            ctx.arc(r, h - r, r, math.pi * 0.5, math.pi)
            ctx.arc(r, r, r, math.pi, math.pi * 1.5)
        if hasattr(ctx, "close_path"):
            ctx.close_path()

        ctx.set_source_rgba(0.06, 0.18, 0.12, 0.85)
        ctx.fill()
        ctx.set_source_rgba(0.1, 0.85, 0.45, 0.7)
        if hasattr(ctx, "set_line_width"):
            ctx.set_line_width(1.0)
        ctx.stroke()

        if hasattr(ctx, "select_font_face"):
            ctx.select_font_face("Inter", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
        if hasattr(ctx, "set_font_size"):
            ctx.set_font_size(10.0)
        ctx.set_source_rgba(0.2, 0.95, 0.55, 0.95)
        ctx.move_to(12.0, 16.0)
        if hasattr(ctx, "show_text"):
            ctx.show_text(f"{self.time_ms:.1f} ms ({self.scan_type})")
        ctx.restore()


class VisualSqlQueryBuilder(Node):
    """
    Visual SQL Query Builder Suite.
    Renders relational table schema entities, animated bezier JOIN connectors,
    interactive query syntax preview, and execution planning pills.
    """

    def __init__(
        self,
        tables: Optional[List[Dict[str, Any]]] = None,
        width: float = 780.0,
        height: float = 480.0,
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)
        self.width_val = float(width)
        self.height_val = float(height)
        self.shadow = DropShadow(color=Color(0.0, 0.0, 0.0, 0.5), blur=32.0, offset=(0.0, 16.0))

        # Schema Table 1 (users)
        self.table_users = SchemaTableNode(
            table_name="users",
            columns=[("id", "BIGINT", True), ("name", "VARCHAR", False), ("email", "VARCHAR", False), ("created_at", "TIMESTAMP", False)],
            width=230.0,
        )
        self.table_users.position.set(Vector2D(30.0, 80.0))

        # Schema Table 2 (orders)
        self.table_orders = SchemaTableNode(
            table_name="orders",
            columns=[("id", "BIGINT", True), ("user_id", "BIGINT", False), ("total_usd", "NUMERIC", False), ("status", "VARCHAR", False)],
            width=230.0,
        )
        self.table_orders.position.set(Vector2D(460.0, 80.0))

        # JOIN Connector curve
        self.join_curve = TableJoinConnectorCurve(p1=(260.0, 134.0), p2=(460.0, 160.0), color=colors.CYAN)
        self.join_curve.progress.set(1.0)

        # SQL Syntax View at bottom
        self.sql_view = SqlSyntaxHighlightView(
            sql_text="SELECT u.id, u.name, o.total_usd\nFROM users u\nJOIN orders o ON u.id = o.user_id\nWHERE o.status = 'completed';",
            width=self.width_val - 48.0,
            height=92.0,
        )
        self.sql_view.position.set(Vector2D(24.0, 360.0))

        # Execution time pill
        self.exec_pill = ExecutionTimePill(time_ms=2.4)
        self.exec_pill.position.set(Vector2D(self.width_val - 190.0, 24.0))

        self.add(self.table_users, self.table_orders, self.join_curve, self.sql_view, self.exec_pill)

    def draw_join_relation(
        self,
        table_a: Optional[str] = None,
        table_b: Optional[str] = None,
        table1: Optional[str] = None,
        table2: Optional[str] = None,
        duration: float = 1.2,
        ease: EasingFunc = Ease.out_quad,
    ) -> AnimationAction:
        """
        Fluent generator animation verb to draw bezier JOIN relationship between schema tables.
        """
        self.join_curve.progress.set(0.0)
        return self.join_curve.progress.to(1.0, duration=duration, ease=ease)

    def local_bounds(self, time: float = 0.0) -> Tuple[float, float, float, float]:
        return (0.0, 0.0, self.width_val, self.height_val)

    def draw(self, ctx: Any, time: float = 0.0) -> None:
        w, h = self.width_val, self.height_val
        ctx.save()

        # Canvas card
        r = 16.0
        ctx.new_path()
        ctx.arc(w - r, r, r, -math.pi * 0.5, 0)
        ctx.arc(w - r, h - r, r, 0, math.pi * 0.5)
        ctx.arc(r, h - r, r, math.pi * 0.5, math.pi)
        ctx.arc(r, r, r, math.pi, math.pi * 1.5)
        ctx.close_path()

        ctx.set_source_rgba(0.04, 0.06, 0.1, 0.95)
        ctx.fill_preserve()
        ctx.set_source_rgba(0.18, 0.25, 0.38, 0.8)
        ctx.set_line_width(1.5)
        ctx.stroke()

        # Title
        ctx.select_font_face("Inter", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
        ctx.set_font_size(15.0)
        ctx.set_source_rgba(0.95, 0.98, 1.0, 0.95)
        ctx.move_to(24.0, 42.0)
        ctx.show_text("Visual Relational SQL Query Builder")

        super().draw(ctx, time)
        ctx.restore()
