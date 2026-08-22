import math
import cairo
from typing import Any, List, Optional, Tuple, Union

from vibmo.scene.node import Node
from vibmo.core.color import Color
from vibmo.spatial.shadows import DropShadow


class VisualSqlQueryBlock(Node):
    """
    Visual block with SELECT columns, FROM table, and WHERE conditions.
    """

    def __init__(
        self,
        table_name: str = "users",
        select_columns: List[str] = None,
        where_conditions: List[str] = None,
        width: float = 300.0,
        x: float = 0.0,
        y: float = 0.0,
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)
        self.table_name = table_name
        self.select_columns = select_columns or ["id", "name", "email"]
        self.where_conditions = where_conditions or ["status = 'active'"]
        self.width = width
        self.x = x
        self.y = y
        # We will calculate height based on content
        self.row_height = 32.0
        self.header_height = 40.0
        self.height = self.header_height + self.row_height * (len(self.select_columns) + len(self.where_conditions) + 2) # +2 for SELECT/WHERE headers

    def draw(self, ctx: Any, time: float = 0.0) -> None:
        ctx.save()
        ctx.translate(self.x, self.y)

        # Draw block background
        r = 12.0
        ctx.new_path()
        ctx.arc(self.width - r, r, r, -math.pi * 0.5, 0)
        ctx.arc(self.width - r, self.height - r, r, 0, math.pi * 0.5)
        ctx.arc(r, self.height - r, r, math.pi * 0.5, math.pi)
        ctx.arc(r, r, r, math.pi, math.pi * 1.5)
        ctx.close_path()

        ctx.set_source_rgba(1.0, 1.0, 1.0, 1.0)
        ctx.fill_preserve()
        ctx.set_source_rgba(0.9, 0.9, 0.9, 1.0)
        ctx.set_line_width(1.0)
        ctx.stroke()

        # Header background
        ctx.save()
        ctx.new_path()
        ctx.arc(self.width - r, r, r, -math.pi * 0.5, 0)
        ctx.line_to(self.width, self.header_height)
        ctx.line_to(0, self.header_height)
        ctx.arc(r, r, r, math.pi, math.pi * 1.5)
        ctx.close_path()
        ctx.set_source_rgba(0.2, 0.6, 1.0, 0.1) # Light blue header
        ctx.fill()
        ctx.restore()

        # Table Name (Header)
        ctx.set_source_rgba(0.1, 0.1, 0.1, 1.0)
        ctx.select_font_face("Inter", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
        ctx.set_font_size(16.0)
        ctx.move_to(16.0, 26.0)
        ctx.show_text(self.table_name)

        current_y = self.header_height + 24.0

        # SELECT
        ctx.set_source_rgba(0.5, 0.5, 0.5, 1.0)
        ctx.set_font_size(12.0)
        ctx.move_to(16.0, current_y)
        ctx.show_text("SELECT")
        current_y += self.row_height

        ctx.set_source_rgba(0.2, 0.2, 0.2, 1.0)
        ctx.set_font_size(14.0)
        for col in self.select_columns:
            ctx.move_to(32.0, current_y)
            ctx.show_text(col)
            current_y += self.row_height

        # WHERE
        if self.where_conditions:
            ctx.set_source_rgba(0.5, 0.5, 0.5, 1.0)
            ctx.set_font_size(12.0)
            ctx.move_to(16.0, current_y)
            ctx.show_text("WHERE")
            current_y += self.row_height

            ctx.set_source_rgba(0.2, 0.2, 0.2, 1.0)
            ctx.set_font_size(14.0)
            for cond in self.where_conditions:
                ctx.move_to(32.0, current_y)
                ctx.show_text(cond)
                current_y += self.row_height

        ctx.restore()


class TableJoinConnectorCurve(Node):
    """
    Smooth Bézier curved link connecting foreign key column to primary key table.
    """

    def __init__(
        self,
        start_pos: Tuple[float, float] = (0.0, 0.0),
        end_pos: Tuple[float, float] = (100.0, 100.0),
        color: Color = Color.hex("#3b82f6"),
        thickness: float = 3.0,
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)
        self.start_pos = start_pos
        self.end_pos = end_pos
        self.color = color
        self.thickness = thickness

    def draw(self, ctx: Any, time: float = 0.0) -> None:
        ctx.save()
        x0, y0 = self.start_pos
        x1, y1 = self.end_pos

        # Control points for horizontal smooth curve
        cp_offset = abs(x1 - x0) * 0.5
        cx0 = x0 + cp_offset
        cy0 = y0
        cx1 = x1 - cp_offset
        cy1 = y1

        ctx.move_to(x0, y0)
        ctx.curve_to(cx0, cy0, cx1, cy1, x1, y1)

        r, g, b, a = self.color.to_tuple_rgba()
        ctx.set_source_rgba(r, g, b, a)
        ctx.set_line_width(self.thickness)
        ctx.set_line_cap(cairo.LINE_CAP_ROUND)
        ctx.stroke()
        ctx.restore()


class SqlSyntaxHighlightView(Node):
    """
    Syntax-highlighted SQL preview code window below builder.
    """

    def __init__(
        self,
        sql_query: str = "SELECT * FROM users;",
        width: float = 600.0,
        height: float = 200.0,
        x: float = 0.0,
        y: float = 0.0,
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)
        self.sql_query = sql_query
        self.width = width
        self.height = height
        self.x = x
        self.y = y
        self.shadow = DropShadow.elevated(blur=16.0, offset=(0, 8), color=Color.hex("#000000").with_alpha(0.1))

    def draw(self, ctx: Any, time: float = 0.0) -> None:
        ctx.save()
        ctx.translate(self.x, self.y)

        r = 8.0
        ctx.new_path()
        ctx.arc(self.width - r, r, r, -math.pi * 0.5, 0)
        ctx.arc(self.width - r, self.height - r, r, 0, math.pi * 0.5)
        ctx.arc(r, self.height - r, r, math.pi * 0.5, math.pi)
        ctx.arc(r, r, r, math.pi, math.pi * 1.5)
        ctx.close_path()

        ctx.set_source_rgba(0.1, 0.1, 0.12, 1.0) # Dark background
        ctx.fill()

        # Terminal dots (macOS style)
        dot_colors = [(1.0, 0.36, 0.33), (1.0, 0.76, 0.15), (0.15, 0.79, 0.25)]
        for i, color in enumerate(dot_colors):
            ctx.arc(20.0 + i * 20.0, 20.0, 6.0, 0, math.pi * 2)
            ctx.set_source_rgba(*color, 1.0)
            ctx.fill()

        # Simple Syntax Highlighting
        ctx.select_font_face("monospace", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)
        ctx.set_font_size(14.0)
        
        current_x = 20.0
        current_y = 50.0

        keywords = ["SELECT", "FROM", "WHERE", "JOIN", "ON", "AND", "OR", "ORDER BY", "GROUP BY", "LIMIT"]
        
        # Super simple tokenizer for demonstration
        tokens = self.sql_query.split()
        for token in tokens:
            if token.upper() in keywords:
                ctx.set_source_rgba(0.7, 0.3, 0.7, 1.0) # Purple for keywords
            else:
                ctx.set_source_rgba(0.9, 0.9, 0.9, 1.0) # White for other text
            
            ctx.move_to(current_x, current_y)
            ctx.show_text(token)
            
            te = ctx.text_extents(token + " ")
            current_x += te.x_advance
            if current_x > self.width - 40.0:
                current_x = 20.0
                current_y += 24.0

        ctx.restore()


class ExecutionTimePill(Node):
    """
    Badge showing query latency (⚡ 14.2ms (Index Scan)).
    """

    def __init__(
        self,
        time_ms: float = 14.2,
        scan_type: str = "Index Scan",
        x: float = 0.0,
        y: float = 0.0,
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)
        self.time_ms = time_ms
        self.scan_type = scan_type
        self.x = x
        self.y = y

    def draw(self, ctx: Any, time: float = 0.0) -> None:
        ctx.save()
        ctx.translate(self.x, self.y)

        text = f"⚡ {self.time_ms:.1f}ms ({self.scan_type})"
        
        ctx.select_font_face("Inter", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
        ctx.set_font_size(14.0)
        te = ctx.text_extents(text)
        
        padding_x = 16.0
        padding_y = 8.0
        width = te.x_advance + padding_x * 2
        height = te.height + padding_y * 2
        
        r = height / 2.0

        ctx.new_path()
        ctx.arc(width - r, r, r, -math.pi * 0.5, 0)
        ctx.arc(width - r, height - r, r, 0, math.pi * 0.5)
        ctx.arc(r, height - r, r, math.pi * 0.5, math.pi)
        ctx.arc(r, r, r, math.pi, math.pi * 1.5)
        ctx.close_path()

        ctx.set_source_rgba(0.1, 0.1, 0.1, 0.8) # Dark pill
        ctx.fill()

        ctx.set_source_rgba(1.0, 0.8, 0.2, 1.0) # Yellow/Orange text
        ctx.move_to(padding_x, padding_y + te.height)
        ctx.show_text(text)

        ctx.restore()
