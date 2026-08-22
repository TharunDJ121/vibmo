import math
import pytest
from vibmo.core.color import Color, colors
from vibmo.core.vector import Vector2D
from vibmo.product.ai.ui_embeddings_space_suite import (
    EmbeddingScatterCluster,
    CosineSimilarityLink,
    VectorDimensionBar,
    SearchQueryProbe,
)

class MockContext:
    def __init__(self):
        self.calls = []

    def save(self):
        self.calls.append(("save",))

    def restore(self):
        self.calls.append(("restore",))

    def set_source_rgba(self, r, g, b, a):
        self.calls.append(("set_source_rgba", r, g, b, a))

    def arc(self, x, y, radius, angle1, angle2):
        self.calls.append(("arc", x, y, radius, angle1, angle2))

    def fill(self):
        self.calls.append(("fill",))

    def stroke(self):
        self.calls.append(("stroke",))

    def move_to(self, x, y):
        self.calls.append(("move_to", x, y))

    def line_to(self, x, y):
        self.calls.append(("line_to", x, y))

    def set_line_width(self, w):
        self.calls.append(("set_line_width", w))

    def set_dash(self, dashes, offset=0):
        self.calls.append(("set_dash", dashes, offset))

    def select_font_face(self, family, slant=0, weight=0):
        self.calls.append(("select_font_face", family, slant, weight))

    def set_font_size(self, size):
        self.calls.append(("set_font_size", size))

    def text_extents(self, text):
        self.calls.append(("text_extents", text))
        class Extents:
            width = 50
            height = 10
        return Extents()

    def rectangle(self, x, y, w, h):
        self.calls.append(("rectangle", x, y, w, h))

    def show_text(self, text):
        self.calls.append(("show_text", text))

def test_embedding_scatter_cluster():
    cluster = EmbeddingScatterCluster(num_points=10, num_clusters=2, seed=42)
    assert len(cluster.points) == 10
    ctx = MockContext()
    cluster.draw(ctx, 0.0)

    arcs = [c for c in ctx.calls if c[0] == "arc"]
    assert len(arcs) == 10

def test_cosine_similarity_link():
    link = CosineSimilarityLink(p1=(0, 0), p2=(100, 100), similarity=0.99)
    ctx = MockContext()
    link.draw(ctx, 1.0)

    # Text badge was rendered
    texts = [c for c in ctx.calls if c[0] == "show_text"]
    assert len(texts) == 1
    assert texts[0][1] == "sim: 0.99"

    # Line was rendered
    moves = [c for c in ctx.calls if c[0] == "move_to"]
    assert len(moves) >= 1
    assert moves[0][1] == 0.0 and moves[0][2] == 0.0
    lines = [c for c in ctx.calls if c[0] == "line_to"]
    assert len(lines) >= 1
    assert lines[0][1] == 100.0 and lines[0][2] == 100.0

def test_vector_dimension_bar():
    bar = VectorDimensionBar(dimensions=[0.5, -0.5], width=100, height=20)
    ctx = MockContext()
    bar.draw(ctx, 0.0)

    rects = [c for c in ctx.calls if c[0] == "rectangle"]
    assert len(rects) == 2
    # Check width (100 / 2 - 1 = 49.0)
    assert rects[0][3] == 49.0
    assert rects[1][3] == 49.0

def test_search_query_probe():
    probe = SearchQueryProbe(radius=10.0)
    ctx = MockContext()
    probe.draw(ctx, 1.0)

    arcs = [c for c in ctx.calls if c[0] == "arc"]
    # Base node and ripple
    assert len(arcs) == 2
