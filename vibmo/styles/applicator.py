"""
Style Applicator: Recursively applies aesthetic themes across scene graph components and shaders.
"""

from __future__ import annotations
from typing import Any, List
from vibmo.styles.presets import StylePreset
from vibmo.fx.filters import Vignette, FilmGrain, Glow, ChromaticAberration


def apply_style_to_scene(scene: Any, style: StylePreset) -> Any:
    """Applies a StylePreset across a Scene's background, nodes, typography, and post-FX."""
    scene.background = style.background

    # Recursively update nodes
    def _apply_node(node: Any):
        cls_name = node.__class__.__name__

        # GlassCard & Containers
        if cls_name == "GlassCard":
            node.fill = style.card_fill
            node.stroke = style.card_stroke
            node.corner_radius = style.card_corner_radius

        # KineticText & Text
        elif cls_name in ("KineticText", "Text"):
            if not hasattr(node, "_custom_styled") or not node._custom_styled:
                node.color = style.text_primary
                node.font_family = style.font_family

        # MetricCounter
        elif cls_name == "MetricCounter":
            node.color = style.accent

        # Charts
        elif "Chart" in cls_name:
            if hasattr(node, "color"):
                node.color = style.accent

        # Icons
        elif cls_name == "Icon":
            if hasattr(node, "color") and node.color is not None:
                node.color = style.secondary_accent

        if hasattr(node, "children") and node.children:
            for child in node.children:
                _apply_node(child)

    for n in scene.nodes:
        _apply_node(n)

    # Post FX Shaders
    scene.post_fx.clear()
    if style.vignette_intensity > 0.01:
        scene.add_post_fx(Vignette(intensity=style.vignette_intensity))
    if style.grain_amount > 0.005:
        scene.add_post_fx(FilmGrain(amount=style.grain_amount))
    if style.name == "Cyberpunk Neon":
        scene.add_post_fx(ChromaticAberration(offset=3.0))

    return scene
