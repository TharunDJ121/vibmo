"""
Fusion Node Graph Engine: Serializes Scene layers, Camera, and Post-FX into a visual Node Graph.
"""

from __future__ import annotations
from typing import Any, Dict, List


class FusionGraph:
    """Builds node-based compositing graph data for the Fusion workspace page."""

    @classmethod
    def serialize_scene(cls, scene: Any) -> Dict[str, Any]:
        nodes_graph = []
        connections = []

        # 1. Background / Canvas Node
        nodes_graph.append({
            "id": "node_background",
            "title": "Canvas Background",
            "category": "generator",
            "x": 100,
            "y": 140,
            "inputs": [],
            "outputs": ["out_bg"],
            "params": {"color": scene.background.to_hex() if hasattr(scene.background, "to_hex") else "#030712"},
        })

        # 2. Scene Layer Nodes
        prev_node_id = "node_background"
        y_offset = 240
        for i, n in enumerate(scene.nodes):
            nid = f"layer_{n.id}"
            nodes_graph.append({
                "id": nid,
                "title": n.name,
                "category": "layer",
                "type": n.__class__.__name__,
                "x": 380,
                "y": y_offset,
                "inputs": ["in_bg", "in_mask"],
                "outputs": ["out_rgb"],
                "params": {
                    "opacity": float(n.opacity.get(0.0)),
                    "rotation": float(n.rotation.get(0.0)),
                },
            })
            connections.append({"from": prev_node_id, "from_socket": "out_bg", "to": nid, "to_socket": "in_bg"})
            prev_node_id = nid
            y_offset += 120

        # 3. Post FX Pipeline Nodes
        fx_x = 720
        fx_y = 200
        for i, fx in enumerate(scene.post_fx):
            fx_id = f"fx_{i}_{fx.__class__.__name__}"
            nodes_graph.append({
                "id": fx_id,
                "title": fx.__class__.__name__,
                "category": "shader",
                "x": fx_x,
                "y": fx_y,
                "inputs": ["in_rgb"],
                "outputs": ["out_rgb"],
                "params": getattr(fx, "__dict__", {}),
            })
            connections.append({"from": prev_node_id, "from_socket": "out_rgb", "to": fx_id, "to_socket": "in_rgb"})
            prev_node_id = fx_id
            fx_x += 220

        # 4. MediaOut / Master Viewer Node
        nodes_graph.append({
            "id": "node_media_out",
            "title": "MediaOut 1",
            "category": "output",
            "x": fx_x + 80,
            "y": 200,
            "inputs": ["in_composite"],
            "outputs": [],
            "params": {"resolution": f"{scene.width}x{scene.height}", "fps": scene.fps},
        })
        connections.append({"from": prev_node_id, "from_socket": "out_rgb", "to": "node_media_out", "to_socket": "in_composite"})

        return {
            "nodes": nodes_graph,
            "connections": connections,
        }
