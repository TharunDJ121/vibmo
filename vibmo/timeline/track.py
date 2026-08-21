"""
NLE Timeline Tracks for Visual Layer Management and Audio Grouping.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Set, Union
from vibmo.core.color import Color, colors
from vibmo.scene.node import Node


@dataclass
class LayerTrack:
    """
    An explicit NLE visual layer track (e.g. 'V1 - Graphics', 'V2 - Titles').
    Allows soloing, muting, locking, opacity scaling, and blend mode propagation.
    """

    name: str
    kind: str = "video"  # "video" | "audio" | "adjustment"
    index: int = 0
    visible: bool = True
    locked: bool = False
    solo: bool = False
    muted: bool = False
    opacity: float = 1.0
    blend_mode: str = "normal"
    nodes: List[Node] = field(default_factory=list)

    def add(self, *nodes: Node) -> LayerTrack:
        """Assigns nodes to this track."""
        for n in nodes:
            if n not in self.nodes:
                self.nodes.append(n)
                n.track_name = self.name
        return self

    def remove(self, node: Node) -> None:
        if node in self.nodes:
            self.nodes.remove(node)
            if getattr(node, "track_name", None) == self.name:
                node.track_name = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "kind": self.kind,
            "index": self.index,
            "visible": self.visible,
            "locked": self.locked,
            "solo": self.solo,
            "muted": self.muted,
            "opacity": self.opacity,
            "blend_mode": self.blend_mode,
            "node_ids": [n.id for n in self.nodes],
            "node_count": len(self.nodes),
        }
