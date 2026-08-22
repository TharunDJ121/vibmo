import pytest
from unittest.mock import MagicMock
from vibmo.product.ai.ui_sql_query_builder_suite import (
    VisualSqlQueryBlock,
    TableJoinConnectorCurve,
    SqlSyntaxHighlightView,
    ExecutionTimePill,
)
from vibmo.core.color import Color

class MockTextExtents:
    def __init__(self, x_advance, height):
        self.x_advance = x_advance
        self.height = height

class MockContext:
    def __init__(self):
        self.calls = []
    def __getattr__(self, name):
        def wrapper(*args, **kwargs):
            self.calls.append((name, args))
            if name == "text_extents":
                return MockTextExtents(50.0, 15.0)
            return MagicMock()
        return wrapper

def test_visual_sql_query_block():
    block = VisualSqlQueryBlock(
        table_name="orders",
        select_columns=["id", "amount"],
        where_conditions=["amount > 100"]
    )
    assert block.table_name == "orders"
    assert len(block.select_columns) == 2
    assert block.height == 40.0 + 32.0 * (2 + 1 + 2) # header + (cols + conds + headers) * row

    ctx = MockContext()
    block.draw(ctx, 0.0)
    methods_called = [call[0] for call in ctx.calls]
    assert "save" in methods_called
    assert "restore" in methods_called
    assert "show_text" in methods_called
    assert "fill_preserve" in methods_called
    assert "stroke" in methods_called

def test_table_join_connector_curve():
    conn = TableJoinConnectorCurve(
        start_pos=(10, 20),
        end_pos=(100, 50),
        color=Color.hex("#ff0000"),
        thickness=4.0
    )
    assert conn.start_pos == (10, 20)
    assert conn.end_pos == (100, 50)

    ctx = MockContext()
    conn.draw(ctx, 0.0)
    methods_called = [call[0] for call in ctx.calls]
    assert "move_to" in methods_called
    assert "curve_to" in methods_called
    assert "stroke" in methods_called

def test_sql_syntax_highlight_view():
    view = SqlSyntaxHighlightView(
        sql_query="SELECT id FROM orders",
        width=400.0,
        height=150.0
    )
    assert view.sql_query == "SELECT id FROM orders"

    ctx = MockContext()
    view.draw(ctx, 0.0)
    methods_called = [call[0] for call in ctx.calls]
    assert "fill" in methods_called
    assert "show_text" in methods_called
    assert "arc" in methods_called

def test_execution_time_pill():
    pill = ExecutionTimePill(time_ms=5.5, scan_type="Seq Scan")
    assert pill.time_ms == 5.5
    assert pill.scan_type == "Seq Scan"

    ctx = MockContext()
    pill.draw(ctx, 0.0)
    methods_called = [call[0] for call in ctx.calls]
    assert "fill" in methods_called
    assert "show_text" in methods_called
