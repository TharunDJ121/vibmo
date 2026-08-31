import math
import pytest
import cairo
from vibmo.core.color import Color, colors
from vibmo.product.ai.ui_embeddings_space_suite import (
    EmbeddingScatterCluster,
    CosineSimilarityLink,
    VectorDimensionBar,
    SearchQueryProbe,
    VectorEmbeddingsVisualizer,
    ClusterPoint,
)

def test_embedding_scatter_cluster():
    cluster = EmbeddingScatterCluster(point_count=30)
    surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, 600, 600)
    ctx = cairo.Context(surface)
    cluster.draw(ctx, time=0.0)
    assert cluster is not None

def test_cosine_similarity_link():
    link = CosineSimilarityLink(p1=(50.0, 50.0), p2=(150.0, 150.0), similarity=0.99)
    surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, 400, 400)
    ctx = cairo.Context(surface)
    link.draw(ctx, time=0.0)
    assert link.similarity == 0.99

def test_vector_dimension_bar():
    bar = VectorDimensionBar(dimension=512, active_dims=128)
    surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, 300, 40)
    ctx = cairo.Context(surface)
    bar.draw(ctx, time=0.0)
    assert bar.dimension == 512

def test_search_query_probe():
    probe = SearchQueryProbe(position=(100.0, 100.0), query="vibmo motion")
    surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, 400, 400)
    ctx = cairo.Context(surface)
    probe.draw(ctx, time=0.0)
    assert probe.query == "vibmo motion"
