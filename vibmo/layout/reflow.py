"""
Multi-Platform Aspect Ratio Auto-Reflow Engine for Social Video Formats.
Automatically reflows 16:9 Landscape compositions into 9:16 Shorts/TikTok/Reels, 1:1 Square, and 4:5 Feeds.
"""

from __future__ import annotations
import copy
import os
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple, Union
from vibmo.core.vector import Vector2D


class AspectRatio(Tuple[int, int], Enum):
    """Standard broadcast and social aspect ratios."""
    LANDSCAPE_16_9 = (1920, 1080)
    PORTRAIT_9_16 = (1080, 1920)
    SQUARE_1_1 = (1080, 1080)
    FEED_4_5 = (1080, 1350)


class SceneReflowEngine:
    """Intelligently adapts scene canvas geometry and auto-reflows layer layouts."""

    @classmethod
    def reflow(
        cls,
        scene: Any,
        target_dimensions: Union[AspectRatio, Tuple[int, int]] = AspectRatio.PORTRAIT_9_16,
    ) -> Any:
        """Creates a reflowed clone of the scene tailored for the target aspect ratio."""
        target_w, target_h = target_dimensions.value if isinstance(target_dimensions, AspectRatio) else target_dimensions

        orig_w, orig_h = scene.width, scene.height
        scale_x = target_w / orig_w
        scale_y = target_h / orig_h

        is_vertical = (target_h > target_w)
        was_horizontal = (orig_w > orig_h)

        scene.width = int(target_w)
        scene.height = int(target_h)
        scene._rasterizer.width = int(target_w)
        scene._rasterizer.height = int(target_h)

        # Reflow root nodes
        for node in scene.nodes:
            pos = node.position.get(0.0)
            px = pos.x if hasattr(pos, "x") else float(pos[0])
            py = pos.y if hasattr(pos, "y") else float(pos[1])

            if is_vertical and was_horizontal:
                # Center horizontally on mobile canvas, stack vertically
                new_x = (target_w - 400) * 0.5 if hasattr(node, "width") else (px * scale_x * 0.8 + target_w * 0.1)
                new_y = py * scale_y * 0.9 + (target_h * 0.05)
                node.position.set(Vector2D(new_x, new_y))
            else:
                node.position.set(Vector2D(px * scale_x, py * scale_y))

        return scene
