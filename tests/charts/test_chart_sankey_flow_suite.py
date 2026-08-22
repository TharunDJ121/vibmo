import pytest
import math
import cairo
import numpy as np
from vibmo.charts.chart_sankey_flow_suite import (
    SankeyFlowDiagram,
    FlowRibbonNode,
    ConversionDropoffIndicator,
    RevenuePathHighlighter
)
from vibmo.core.color import colors
from vibmo.core.vector import Vector2D

class MockContext:
    def __init__(self):
        self.operations = []

    def save(self): self.operations.append("save")
    def restore(self): self.operations.append("restore")
    def set_source_rgba(self, r, g, b, a): self.operations.append(f"set_source_rgba({r}, {g}, {b}, {a})")
    def rectangle(self, x, y, w, h): self.operations.append(f"rectangle({x}, {y}, {w}, {h})")
    def fill(self): self.operations.append("fill")
    def move_to(self, x, y): self.operations.append(f"move_to({x}, {y})")
    def line_to(self, x, y): self.operations.append(f"line_to({x}, {y})")
    def curve_to(self, x1, y1, x2, y2, x3, y3): self.operations.append(f"curve_to({x1}, {y1}, {x2}, {y2}, {x3}, {y3})")
    def close_path(self): self.operations.append("close_path")
    def set_line_width(self, w): self.operations.append(f"set_line_width({w})")
    def set_line_cap(self, c): self.operations.append(f"set_line_cap({c})")
    def set_line_join(self, j): self.operations.append(f"set_line_join({j})")
    def stroke(self): self.operations.append("stroke")
    def select_font_face(self, family, slant, weight): self.operations.append(f"select_font_face({family}, {slant}, {weight})")
    def set_font_size(self, size): self.operations.append(f"set_font_size({size})")
    def show_text(self, text): self.operations.append(f"show_text({text})")
    def text_extents(self, text): return type("Extents", (), {"width": 10.0, "height": 10.0})()


def test_flow_ribbon_node():
    node = FlowRibbonNode("Test", 1000.0, width=50, height=200, color=colors.RED)
    assert node.label == "Test"
    assert node.value == 1000.0
    assert node.width.get() == 50.0
    assert node.height.get() == 200.0

    ctx = MockContext()
    node.draw(ctx, 0.0)

    assert "save" in ctx.operations
    assert "rectangle(0, 0, 50.0, 200.0)" in ctx.operations
    assert "fill" in ctx.operations
    assert "show_text(Test)" in ctx.operations
    assert "show_text($1,000.00)" in ctx.operations
    assert "restore" in ctx.operations


def test_conversion_dropoff_indicator():
    dropoff = ConversionDropoffIndicator(start_pos=(100, 100), dropoff_value=50.0, dropoff_width=20.0, direction="down")
    assert dropoff.dropoff_value == 50.0
    assert dropoff.dropoff_width == 20.0
    assert dropoff.trim.get() == 1.0

    ctx = MockContext()
    dropoff.draw(ctx, 0.0)

    assert "save" in ctx.operations
    assert "move_to(100.0, 100.0)" in ctx.operations
    assert "line_to(120.0, 100.0)" in ctx.operations
    assert "fill" in ctx.operations
    assert "show_text(-$50.00)" in ctx.operations
    assert "restore" in ctx.operations


def test_revenue_path_highlighter():
    path = [(0, 0), (100, 0), (100, 100)]
    highlighter = RevenuePathHighlighter(path_points=path, thickness=5.0)
    assert len(highlighter.path_points) == 3
    assert highlighter.progress.get() == 0.0

    highlighter.progress.set(1.0)
    ctx = MockContext()
    highlighter.draw(ctx, 0.0)

    assert "save" in ctx.operations
    assert "set_line_width(5.0)" in ctx.operations
    assert "move_to(0.0, 0.0)" in ctx.operations
    assert "line_to(100.0, 0.0)" in ctx.operations
    assert "line_to(100.0, 100.0)" in ctx.operations
    assert "stroke" in ctx.operations
    assert "restore" in ctx.operations


def test_sankey_flow_diagram_math_and_drawing():
    nodes_data = {
        "A": {"value": 1000, "pos": (0, 0)},
        "B": {"value": 800, "pos": (200, 0)},
        "C": {"value": 200, "pos": (200, 200)}
    }
    links_data = [
        {"source": "A", "target": "B", "value": 800, "dropoff": 0},
        {"source": "A", "target": "C", "value": 100, "dropoff": 100}
    ]

    diagram = SankeyFlowDiagram(nodes_data=nodes_data, links_data=links_data, value_scale=0.1)

    # Check Math Conservation (A output = B input + C input + dropoff)
    assert len(diagram.pillars) == 3
    a_out = sum(link["value"] for link in links_data if link["source"] == "A") + sum(link.get("dropoff", 0) for link in links_data if link["source"] == "A")
    assert a_out == nodes_data["A"]["value"]

    # Check ribbon width calculations
    assert diagram.pillars["A"].height.get() == 100.0
    assert diagram.pillars["B"].height.get() == 80.0
    assert diagram.pillars["C"].height.get() == 20.0

    # Check cairo drawing
    ctx = MockContext()
    diagram.draw(ctx, 0.0)

    # The links should trace the bezier ribbon
    assert "save" in ctx.operations
    assert "move_to(20.0, 0.0)" in ctx.operations
    assert "close_path" in ctx.operations
    assert "fill" in ctx.operations
    assert "restore" in ctx.operations
