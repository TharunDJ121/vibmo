import cairo
import numpy as np
from vibmo.charts.chart_choropleth_map_suite import (
    RegionalHeatPolygon,
    GeoDataTooltip,
    CountryRankLeaderboard,
    ChoroplethWorldMiniMap
)
from vibmo.core.color import colors


class MockContext:
    def __init__(self):
        self.paths = []
        self.sources = []
        self.clips = []
        self.transforms = []
        self.saves = 0
        self.restores = 0

    def save(self):
        self.saves += 1

    def restore(self):
        self.restores += 1

    def set_source_rgba(self, r, g, b, a):
        self.sources.append((r, g, b, a))

    def move_to(self, x, y):
        self.paths.append(('move', x, y))

    def line_to(self, x, y):
        self.paths.append(('line', x, y))

    def close_path(self):
        self.paths.append(('close',))

    def fill(self):
        self.paths.append(('fill',))

    def clip(self):
        self.clips.append(('clip',))

    def fill_preserve(self):
        self.paths.append(('fill_preserve',))

    def rectangle(self, x, y, w, h):
        self.paths.append(('rect', x, y, w, h))

    def new_path(self):
        self.paths.append(('new_path',))

    def new_sub_path(self):
        self.paths.append(('new_sub_path',))

    def arc(self, xc, yc, radius, angle1, angle2):
        self.paths.append(('arc', xc, yc, radius, angle1, angle2))

    def text_extents(self, text):
        class Extents:
            def __init__(self):
                self.x_bearing = 0
                self.y_bearing = 0
                self.width = 10 * len(text)
                self.height = 10
                self.x_advance = 10 * len(text)
                self.y_advance = 0
        return Extents()

    def show_text(self, text):
        self.paths.append(('show_text', text))

    def translate(self, x, y):
        self.transforms.append(('translate', x, y))

    def scale(self, x, y):
        self.transforms.append(('scale', x, y))


def test_regional_heat_polygon_coords_and_color():
    coords = [(0, 0), (10, 0), (10, 10), (0, 10)]
    poly = RegionalHeatPolygon(coordinates=coords, value=0.5)

    ctx = MockContext()
    poly.draw(ctx, 0.0)

    assert ctx.saves == 1
    assert ctx.restores == 1

    assert ('move', 0, 0) in ctx.paths
    assert ('line', 10, 0) in ctx.paths
    assert ('line', 10, 10) in ctx.paths
    assert ('line', 0, 10) in ctx.paths
    assert ('close',) in ctx.paths
    assert ('fill',) in ctx.paths

    assert len(ctx.sources) > 0
    # At value 0.5, it should be a mix of SLATE_800 and EMERALD
    # Just checking it calls set_source_rgba
    assert len(ctx.sources[-1]) == 4


def test_geo_data_tooltip_content():
    tooltip = GeoDataTooltip(country_name="United States", user_count=1000000, revenue=50000.5)

    # We can inspect the children structure to ensure text nodes exist
    children_texts = [child.text.get() for child in tooltip.children if hasattr(child, 'text')]
    assert "United States" in children_texts
    assert "Users: 1,000,000" in children_texts
    assert "Revenue: $50,000.50" in children_texts


def test_country_rank_leaderboard_content():
    rankings = [
        {"country": "USA", "score": 95},
        {"country": "UK", "score": 85}
    ]
    board = CountryRankLeaderboard(rankings=rankings)

    # Verify the structure recursively
    def get_all_texts(node):
        texts = []
        if hasattr(node, 'text'):
            texts.append(node.text.get())
        for child in node.children:
            texts.extend(get_all_texts(child))
        return texts

    all_texts = get_all_texts(board)
    assert "#1" in all_texts
    assert "USA" in all_texts
    assert "95" in all_texts
    assert "#2" in all_texts
    assert "UK" in all_texts
    assert "85" in all_texts


def test_choropleth_world_mini_map():
    regions = {
        "us": {"coordinates": [(0, 0), (1, 0), (1, 1), (0, 1)], "value": 0.8},
        "uk": {"coordinates": [(2, 0), (3, 0), (3, 1), (2, 1)], "value": 0.3}
    }
    map_node = ChoroplethWorldMiniMap(regions_data=regions)

    assert "us" in map_node.polygons
    assert "uk" in map_node.polygons

    assert map_node.polygons["us"].heat_value.get() == 0.8
    assert map_node.polygons["uk"].heat_value.get() == 0.3

    # In scene graph children are implicitly drawn, we will explicitly test the polygons themselves
    ctx = MockContext()
    for poly in map_node.polygons.values():
        poly.draw(ctx, 0.0)

    # Expect that at least polygons were drawn
    assert ('move', 0, 0) in ctx.paths
    assert ('move', 2, 0) in ctx.paths
