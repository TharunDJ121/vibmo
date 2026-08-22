import pytest
from vibmo.charts.chart_treemap_market_suite import (
    PercentageDeltaColor,
    ZoomableTreemapTile,
    MarketSectorLegend,
    TreemapMarketCapGrid
)
from vibmo.core.color import Color, colors
import cairo

class MockContext:
    """A minimal mock for testing rendering logic without requiring a display."""
    def __init__(self):
        self.ops = []
    def save(self): self.ops.append('save')
    def restore(self): self.ops.append('restore')
    def clip(self): self.ops.append('clip')
    def new_path(self): self.ops.append('new_path')
    def new_sub_path(self): self.ops.append('new_sub_path')
    def rectangle(self, x, y, w, h): self.ops.append(f'rect {x},{y},{w},{h}')
    def arc(self, xc, yc, r, a1, a2): self.ops.append(f'arc {xc},{yc},{r}')
    def close_path(self): self.ops.append('close_path')
    def fill_preserve(self): self.ops.append('fill_preserve')
    def fill(self): self.ops.append('fill')
    def set_source_rgba(self, r, g, b, a): self.ops.append(f'color {r:.2f},{g:.2f},{b:.2f},{a:.2f}')
    def text_extents(self, text): return cairo.TextExtents(0, 0, 10, 10, 10, 0)
    def font_extents(self): return (10, 2, 12, 10, 0)
    def select_font_face(self, *args): pass
    def set_font_size(self, *args): pass
    def move_to(self, x, y): pass
    def show_text(self, text): pass
    def stroke(self): pass
    def set_line_width(self, w): pass
    def translate(self, tx, ty): pass
    def rotate(self, r): pass
    def scale(self, sx, sy): pass

def test_percentage_delta_color():
    # Test -5% gives ROSE
    c_red = PercentageDeltaColor.get_color(-0.05)
    assert abs(c_red.r - colors.ROSE.r) < 0.01
    assert abs(c_red.g - colors.ROSE.g) < 0.01

    # Test +5% gives Emerald
    c_green = PercentageDeltaColor.get_color(0.05)
    assert abs(c_green.r - colors.EMERALD.r) < 0.01
    assert abs(c_green.g - colors.EMERALD.g) < 0.01

    # Test 0% gives Slate 700 (Gray)
    c_gray = PercentageDeltaColor.get_color(0.0)
    assert abs(c_gray.r - colors.SLATE_700.r) < 0.01
    assert abs(c_gray.g - colors.SLATE_700.g) < 0.01

    # Test bounds capping
    c_extreme_red = PercentageDeltaColor.get_color(-0.1)
    assert abs(c_extreme_red.r - colors.ROSE.r) < 0.01

def test_zoomable_treemap_tile():
    tile = ZoomableTreemapTile("AAPL", 3.0e12, 0.02, 200, 100)
    assert tile.ticker == "AAPL"
    assert tile.market_cap == 3.0e12
    assert tile.performance == 0.02
    assert tile.width.get() == 200
    assert tile.height.get() == 100

    # Check texts are added
    texts = [child for child in tile.children]
    assert len(texts) == 3
    assert texts[0].text.get() == "AAPL"
    assert texts[1].text.get() == "$3.0T"
    assert texts[2].text.get() == "+2.00%"

def test_market_sector_legend():
    legend = MarketSectorLegend(["Tech", "Healthcare", "Finance", "Energy"])
    assert len(legend.children) == 4

def test_treemap_market_cap_grid_squarify():
    data = [
        {"ticker": "AAPL", "market_cap": 300, "performance": 0.05},
        {"ticker": "MSFT", "market_cap": 200, "performance": 0.03},
        {"ticker": "GOOGL", "market_cap": 100, "performance": -0.01},
    ]
    grid = TreemapMarketCapGrid(data, 600, 400)

    # Check layout
    assert len(grid.tiles) == 3

    # Total area should match 600 * 400 = 240000
    total_area = sum(t.width.get() * t.height.get() for t in grid.tiles)
    assert abs(total_area - 240000) < 1.0

    # AAPL is half the total market cap, so it should have half the area
    aapl_tile = next(t for t in grid.tiles if t.ticker == "AAPL")
    assert abs(aapl_tile.width.get() * aapl_tile.height.get() - 120000) < 1.0

def test_treemap_market_cap_grid_aspect_ratio_optimization():
    # A test to specifically check if squarify avoids very thin rectangles
    # compared to a simple linear partition.
    data = [
        {"ticker": "A", "market_cap": 40},
        {"ticker": "B", "market_cap": 30},
        {"ticker": "C", "market_cap": 20},
        {"ticker": "D", "market_cap": 10},
    ]

    # Width is much larger than height
    grid = TreemapMarketCapGrid(data, 1000, 100)

    # If the layout optimization works, no rectangle should have an extreme aspect ratio like 100:1
    for tile in grid.tiles:
        w = tile.width.get()
        h = tile.height.get()
        ratio = max(w/h, h/w)
        # Without optimization, ratio could be 100 (1000/10). With optimization, should be much better.
        assert ratio < 10.0 # Much better than 100.

def test_treemap_market_cap_grid_draw():
    data = [
        {"ticker": "AAPL", "market_cap": 300, "performance": 0.05},
    ]
    grid = TreemapMarketCapGrid(data, 600, 400)
    ctx = MockContext()

    # Note: TreemapMarketCapGrid is a Node, it doesn't draw itself, but its children do.
    # To test drawing we draw the children.
    # The grid calls super().draw(ctx, time) which iterates children
    grid.draw(ctx, 0.0)

    # To test drawing correctly with vibmo's architecture, we can test that calling draw on the rect itself performs operations.
    for tile in grid.tiles:
        tile.draw(ctx, 0.0)

    # Ensure some cairo ops happen
    assert "rect 0.0,0.0,600.0,400.0" in ctx.ops or any('rect' in op for op in ctx.ops) or any('new_sub_path' in op for op in ctx.ops)
    assert "restore" in ctx.ops
