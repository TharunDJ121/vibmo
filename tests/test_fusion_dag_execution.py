"""
Tests for Fusion DAG Node Execution Engine (Topological Sort, Keying, Blur, Noise, Glow, Compositing).
"""

import pytest
import numpy as np
from vibmo.graph import (
    VibmoStateGraph,
    FusionDAGExecutor,
    FusionExecutionContext,
)


def test_topological_sort_and_execution():
    graph = VibmoStateGraph()
    fg = graph.create_fusion_graph("Test Comp")

    # Add Background node
    bg = graph.add_fusion_node(
        graph_id=fg.id,
        node_type="Background",
        name="DarkBG",
        category="generator",
        properties={"r": 10, "g": 20, "b": 30, "a": 255},
    )

    # Add Blur node
    blur = graph.add_fusion_node(
        graph_id=fg.id,
        node_type="GaussianBlur",
        name="Blur1",
        category="filter",
        properties={"radius": 8.0},
    )

    media_out_id = [nid for nid, n in fg.nodes.items() if n.node_type == "MediaOut"][0]

    # Connect: DarkBG -> Blur1 -> MediaOut
    graph.connect_fusion_nodes(fg.id, from_node_id=bg.id, to_node_id=blur.id, to_socket="input")
    graph.connect_fusion_nodes(fg.id, from_node_id=blur.id, to_node_id=media_out_id, to_socket="input")

    # Execute graph
    ctx = FusionExecutionContext(width=320, height=180, time=0.5)
    out_buffer = FusionDAGExecutor.execute_graph(fg, ctx)

    assert out_buffer is not None
    assert out_buffer.shape == (180, 320, 4)
    # Check pixels match background color
    assert out_buffer[50, 50, 0] == 10
    assert out_buffer[50, 50, 1] == 20
    assert out_buffer[50, 50, 2] == 30
    assert out_buffer[50, 50, 3] == 255


def test_fast_noise_and_glow():
    graph = VibmoStateGraph()
    fg = graph.create_fusion_graph("Noise Glow Comp")

    noise = graph.add_fusion_node(
        graph_id=fg.id,
        node_type="FastNoise",
        name="Noise1",
        category="generator",
        properties={"scale": 15.0, "seed": 42.0},
    )

    glow = graph.add_fusion_node(
        graph_id=fg.id,
        node_type="Glow",
        name="Glow1",
        category="filter",
        properties={"threshold": 0.4, "size": 10.0},
    )

    media_out_id = [nid for nid, n in fg.nodes.items() if n.node_type == "MediaOut"][0]

    graph.connect_fusion_nodes(fg.id, from_node_id=noise.id, to_node_id=glow.id, to_socket="input")
    graph.connect_fusion_nodes(fg.id, from_node_id=glow.id, to_node_id=media_out_id, to_socket="input")

    ctx = FusionExecutionContext(width=200, height=100, time=1.0)
    out_buffer = FusionDAGExecutor.execute_graph(fg, ctx)

    assert out_buffer is not None
    assert out_buffer.shape == (100, 200, 4)
    assert np.any(out_buffer > 0)


def test_chroma_keyer_delta_keyer():
    graph = VibmoStateGraph()
    fg = graph.create_fusion_graph("Green Screen Keyer")

    keyer = graph.add_fusion_node(
        graph_id=fg.id,
        node_type="DeltaKeyer",
        name="Keyer1",
        category="matte",
    )

    # Create mock green screen frame
    ctx = FusionExecutionContext(width=100, height=100, time=0.0)
    green_frame = np.zeros((100, 100, 4), dtype=np.uint8)
    green_frame[:, :, 1] = 255  # Solid pure green
    green_frame[:, :, 3] = 255  # Opaque

    ctx.buffers["green_input"] = green_frame

    # Connect to keyer
    media_out_id = [nid for nid, n in fg.nodes.items() if n.node_type == "MediaOut"][0]
    graph.connect_fusion_nodes(fg.id, from_node_id="green_input", to_node_id=keyer.id, to_socket="input")
    graph.connect_fusion_nodes(fg.id, from_node_id=keyer.id, to_node_id=media_out_id, to_socket="input")

    out_buffer = FusionDAGExecutor.execute_graph(fg, ctx)
    assert out_buffer is not None
    # Excess green should have alpha keyed out (alpha = 0)
    assert out_buffer[50, 50, 3] == 0
