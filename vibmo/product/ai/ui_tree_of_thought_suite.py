"""
Tree-of-Thought AI UI Suite for Vibmo / Motio.
Components:
- TreeOfThoughtTree
- ReasoningBranchNode (ReasoningNodeBranch)
- ExplorationScoreBadge
- PrunedBranchFade
"""

from __future__ import annotations
import math
from typing import Any, Dict, List, Optional, Sequence, Tuple, Union
import cairo

from vibmo.core.color import Color, colors
from vibmo.core.vector import Vector2D
from vibmo.core.signal import Signal, AnimationAction
from vibmo.core.easing import Ease, EasingFunc
from vibmo.scene.node import Node
from vibmo.spatial.shadows import DropShadow


class ExplorationScoreBadge(Node):
    """Evaluation score badge with glowing green border for best candidate branch."""

    def __init__(self, score: float = 0.94, is_winner: bool = False, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.score = Signal(float(score), f"{self.name}.score")
        self.is_winner = is_winner
        self.width = 68.0
        self.height = 24.0
        self.opacity = Signal(1.0, f"{self.name}.opacity")
        self.scale_sig = Signal(1.0, f"{self.name}.scale_sig")

    def draw(self, ctx: Any, time: float = 0.0) -> None:
        op = self.opacity.get(time)
        sc = self.scale_sig.get(time)
        if op <= 0.0 or sc <= 0.0:
            return

        ctx.save()
        ctx.translate(self.width * 0.5, self.height * 0.5)
        ctx.scale(sc, sc)
        ctx.translate(-self.width * 0.5, -self.height * 0.5)

        r = 12.0
        w, h = self.width, self.height
        ctx.new_path()
        ctx.arc(w - r, r, r, -math.pi * 0.5, 0)
        ctx.arc(w - r, h - r, r, 0, math.pi * 0.5)
        ctx.arc(r, h - r, r, math.pi * 0.5, math.pi)
        ctx.arc(r, r, r, math.pi, math.pi * 1.5)
        ctx.close_path()

        if self.is_winner:
            ctx.set_source_rgba(0.05, 0.25, 0.15, 0.9 * op)
            ctx.fill_preserve()
            ctx.set_source_rgba(0.1, 0.9, 0.4, 0.9 * op)
            ctx.set_line_width(1.5)
            ctx.stroke()
            text_color = (0.2, 1.0, 0.5, op)
        else:
            ctx.set_source_rgba(0.1, 0.12, 0.18, 0.9 * op)
            ctx.fill_preserve()
            ctx.set_source_rgba(0.3, 0.4, 0.5, 0.6 * op)
            ctx.set_line_width(1.0)
            ctx.stroke()
            text_color = (0.7, 0.8, 0.9, op)

        ctx.select_font_face("Inter", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
        ctx.set_font_size(10.0)
        ctx.set_source_rgba(*text_color)
        score_val = self.score.get(time)
        text = f"{score_val:.2f}"
        ext = ctx.text_extents(text)
        ctx.move_to((w - ext.width) * 0.5, h * 0.5 + ext.height * 0.35)
        ctx.show_text(text)
        ctx.restore()


class ReasoningBranchNode(Node):
    """Reasoning node card displaying thought text, evaluation status, and glowing border."""

    def __init__(
        self,
        node_id: str = "node_0",
        thought: str = "Decompose into subproblems",
        status: str = "Evaluating",
        width: float = 200.0,
        height: float = 72.0,
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)
        self.node_id = node_id
        self.thought = thought
        self.status = status
        self.width_val = float(width)
        self.height_val = float(height)
        self.opacity = Signal(1.0, f"{self.name}.opacity")
        self.scale_sig = Signal(1.0, f"{self.name}.scale_sig")
        self.highlight = Signal(0.0, f"{self.name}.highlight")

    def local_bounds(self, time: float = 0.0) -> Tuple[float, float, float, float]:
        return (0.0, 0.0, self.width_val, self.height_val)

    def draw(self, ctx: Any, time: float = 0.0) -> None:
        op = max(0.0, min(1.0, self.opacity.get(time)))
        sc = self.scale_sig.get(time)
        if op <= 0.0 or sc <= 0.0:
            return

        w, h = self.width_val, self.height_val
        ctx.save()
        ctx.translate(w * 0.5, h * 0.5)
        ctx.scale(sc, sc)
        ctx.translate(-w * 0.5, -h * 0.5)

        r = 10.0
        ctx.new_path()
        ctx.arc(w - r, r, r, -math.pi * 0.5, 0)
        ctx.arc(w - r, h - r, r, 0, math.pi * 0.5)
        ctx.arc(r, h - r, r, math.pi * 0.5, math.pi)
        ctx.arc(r, r, r, math.pi, math.pi * 1.5)
        ctx.close_path()

        if self.status.lower() in ("valid", "winner"):
            bg_rgba = (0.06, 0.15, 0.12, 0.95 * op)
            border_rgba = (0.1, 0.85, 0.45, 0.9 * op)
        elif self.status.lower() in ("pruned", "rejected"):
            bg_rgba = (0.18, 0.06, 0.08, 0.85 * op)
            border_rgba = (0.9, 0.2, 0.3, 0.7 * op)
        else:
            bg_rgba = (0.08, 0.12, 0.18, 0.9 * op)
            border_rgba = (0.25, 0.4, 0.6, 0.7 * op)

        ctx.set_source_rgba(*bg_rgba)
        ctx.fill_preserve()

        ctx.set_source_rgba(*border_rgba)
        ctx.set_line_width(1.5)
        ctx.stroke()

        # Status badge dot
        ctx.arc(16.0, 18.0, 4.0, 0, 2 * math.pi)
        ctx.set_source_rgba(*border_rgba)
        ctx.fill()

        # Status label
        ctx.select_font_face("Inter", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
        ctx.set_font_size(10.0)
        ctx.set_source_rgba(0.7, 0.8, 0.9, 0.9 * op)
        ctx.move_to(26.0, 22.0)
        ctx.show_text(self.status.upper())

        # Thought text
        ctx.select_font_face("Inter", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)
        ctx.set_font_size(11.0)
        ctx.set_source_rgba(0.9, 0.95, 1.0, 0.95 * op)
        ctx.move_to(14.0, 42.0)
        thought_line = self.thought[:28] + ("..." if len(self.thought) > 28 else "")
        ctx.show_text(thought_line)

        super().draw(ctx, time)
        ctx.restore()


ReasoningNodeBranch = ReasoningBranchNode


class PrunedBranchFade(Node):
    """Red-tinted fading dashed branch indicating rejected reasoning path."""

    def __init__(self, start_pos: Tuple[float, float], end_pos: Tuple[float, float], **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.start_pos = start_pos
        self.end_pos = end_pos
        self.progress = Signal(1.0, f"{self.name}.progress")
        self.opacity = Signal(1.0, f"{self.name}.opacity")

    def draw(self, ctx: Any, time: float = 0.0) -> None:
        op = self.opacity.get(time)
        prog = self.progress.get(time)
        if op <= 0.0 or prog <= 0.0:
            return

        ctx.save()
        ctx.set_source_rgba(0.9, 0.25, 0.35, 0.7 * op)
        ctx.set_line_width(2.0)
        ctx.set_dash([6.0, 4.0], 0)

        x1, y1 = self.start_pos
        x2, y2 = self.end_pos
        dx = (x2 - x1) * prog
        dy = (y2 - y1) * prog

        ctx.move_to(x1, y1)
        ctx.curve_to(x1 + dx * 0.5, y1, x1 + dx * 0.5, y1 + dy, x1 + dx, y1 + dy)
        ctx.stroke()
        ctx.restore()


class TreeOfThoughtTree(Node):
    """
    Tree-of-Thought AI Graph Suite.
    Visualizes hierarchical node-link branching exploration, evaluation scores,
    and pruning dynamics with smooth spring transitions.
    """

    def __init__(
        self,
        root_thought: str = "Plan: Optimize LLM inference latency",
        branches: Optional[List[Dict[str, Any]]] = None,
        width: float = 850.0,
        height: float = 520.0,
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)
        self.width_val = float(width)
        self.height_val = float(height)
        self.root_thought = root_thought
        self.shadow = DropShadow(color=Color(0.0, 0.0, 0.0, 0.5), blur=32.0, offset=(0.0, 16.0))

        self.nodes_data: Dict[str, Dict[str, Any]] = {
            "root": {"thought": root_thought, "status": "Valid", "parent": None, "children": []}
        }
        self.node_components: Dict[str, ReasoningBranchNode] = {}
        self.badges: Dict[str, ExplorationScoreBadge] = {}
        self.edges: List[Any] = []

        # Create root component
        root_node = ReasoningBranchNode("root", root_thought, status="Valid", width=220.0)
        root_node.position.set(Vector2D(40.0, self.height_val * 0.5 - 36.0))
        self.add(root_node)
        self.node_components["root"] = root_node

        # Seed initial branches if provided
        initial_branches = branches or [
            {"id": "b1", "thought": "Speculative Decoding (Draft Model)", "status": "Valid", "score": 0.96, "is_winner": True},
            {"id": "b2", "thought": "INT4 Weight-Only Quantization", "status": "Evaluating", "score": 0.82, "is_winner": False},
            {"id": "b3", "thought": "Direct KV Cache Eviction", "status": "Pruned", "score": 0.41, "is_winner": False},
        ]
        self._seed_branches("root", initial_branches)

    def _seed_branches(self, parent_id: str, branches: List[Dict[str, Any]]) -> None:
        parent_node = self.node_components[parent_id]
        px, py = parent_node.position.get(0.0).x, parent_node.position.get(0.0).y
        n = len(branches)
        spacing = 110.0
        start_y = py - (n - 1) * spacing * 0.5

        for i, b in enumerate(branches):
            b_id = b.get("id", f"b_{i}")
            thought = b.get("thought", f"Branch {i+1}")
            status = b.get("status", "Evaluating")
            score = b.get("score", 0.75)
            is_winner = b.get("is_winner", False)

            self.nodes_data[parent_id]["children"].append(b_id)
            self.nodes_data[b_id] = {"thought": thought, "status": status, "parent": parent_id, "children": []}

            tx = px + 280.0
            ty = start_y + i * spacing

            node_comp = ReasoningBranchNode(b_id, thought, status=status, width=220.0)
            node_comp.position.set(Vector2D(tx, ty))
            self.add(node_comp)
            self.node_components[b_id] = node_comp

            badge = ExplorationScoreBadge(score=score, is_winner=is_winner)
            badge.position.set(Vector2D(tx + 220.0 - 72.0, ty - 12.0))
            self.add(badge)
            self.badges[b_id] = badge

    def expand_branch(
        self,
        index: Union[int, str] = 0,
        duration: float = 1.0,
        child_nodes: Optional[List[Dict[str, Any]]] = None,
    ) -> List[AnimationAction]:
        """
        Fluent generator animation verb to expand a branch with spring reveals.
        """
        parent_id = "root" if index == 0 or index == "root" else f"b{index+1}" if isinstance(index, int) else str(index)
        if parent_id not in self.node_components:
            # Fallback to first available child or root
            keys = list(self.node_components.keys())
            parent_id = keys[index] if isinstance(index, int) and index < len(keys) else keys[0]

        actions: List[AnimationAction] = []
        children = self.nodes_data.get(parent_id, {}).get("children", [])

        # If existing children, animate their pop in and score badges
        for c_id in children:
            comp = self.node_components.get(c_id)
            if comp:
                comp.scale_sig.set(0.6)
                comp.opacity.set(0.2)
                actions.append(comp.scale_sig.to(1.0, duration=duration, ease=Ease.out_back))
                actions.append(comp.opacity.to(1.0, duration=duration, ease=Ease.out_quad))
            badge = self.badges.get(c_id)
            if badge:
                badge.scale_sig.set(0.5)
                badge.opacity.set(0.0)
                actions.append(badge.scale_sig.to(1.0, duration=duration, ease=Ease.out_back))
                actions.append(badge.opacity.to(1.0, duration=duration, ease=Ease.out_quad))

        # Highlight parent node
        parent_comp = self.node_components.get(parent_id)
        if parent_comp:
            actions.append(parent_comp.scale_sig.to(1.08, duration=duration * 0.4, ease=Ease.out_quad))
            actions.append(parent_comp.scale_sig.to(1.0, duration=duration * 0.6, delay=duration * 0.4, ease=Ease.out_quad))

        return actions

    def expand_node(self, parent_id: str, child_nodes: List[Dict[str, Any]], duration: float = 1.0) -> Any:
        return self.expand_branch(index=parent_id, duration=duration, child_nodes=child_nodes)

    def local_bounds(self, time: float = 0.0) -> Tuple[float, float, float, float]:
        return (0.0, 0.0, self.width_val, self.height_val)

    def draw(self, ctx: Any, time: float = 0.0) -> None:
        w, h = self.width_val, self.height_val
        ctx.save()

        # Canvas card container
        r = 16.0
        ctx.new_path()
        ctx.arc(w - r, r, r, -math.pi * 0.5, 0)
        ctx.arc(w - r, h - r, r, 0, math.pi * 0.5)
        ctx.arc(r, h - r, r, math.pi * 0.5, math.pi)
        ctx.arc(r, r, r, math.pi, math.pi * 1.5)
        ctx.close_path()

        ctx.set_source_rgba(0.04, 0.06, 0.1, 0.95)
        ctx.fill_preserve()
        ctx.set_source_rgba(0.15, 0.22, 0.32, 0.8)
        ctx.set_line_width(1.5)
        ctx.stroke()

        # Header Title
        ctx.select_font_face("Inter", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
        ctx.set_font_size(14.0)
        ctx.set_source_rgba(0.9, 0.95, 1.0, 0.9)
        ctx.move_to(24.0, 36.0)
        ctx.show_text("Tree-of-Thought Exploration Graph")

        # Draw connecting branch bezier ribbons
        for p_id, p_info in self.nodes_data.items():
            p_comp = self.node_components.get(p_id)
            if not p_comp:
                continue
            px = p_comp.position.get(time).x + p_comp.width_val
            py = p_comp.position.get(time).y + p_comp.height_val * 0.5

            for c_id in p_info.get("children", []):
                c_comp = self.node_components.get(c_id)
                if not c_comp:
                    continue
                cx = c_comp.position.get(time).x
                cy = c_comp.position.get(time).y + c_comp.height_val * 0.5
                op = c_comp.opacity.get(time)

                dx = cx - px
                ctx.new_path()
                ctx.move_to(px, py)
                ctx.curve_to(px + dx * 0.5, py, px + dx * 0.5, cy, cx, cy)

                if self.nodes_data.get(c_id, {}).get("status") == "Pruned":
                    ctx.set_source_rgba(0.9, 0.2, 0.3, 0.5 * op)
                    ctx.set_line_width(2.0)
                    ctx.set_dash([6.0, 4.0], 0)
                    ctx.stroke()
                    ctx.set_dash([])
                elif self.nodes_data.get(c_id, {}).get("status") in ("Valid", "winner"):
                    ctx.set_source_rgba(0.1, 0.85, 0.45, 0.7 * op)
                    ctx.set_line_width(2.5)
                    ctx.stroke()
                else:
                    ctx.set_source_rgba(0.3, 0.45, 0.65, 0.6 * op)
                    ctx.set_line_width(2.0)
                    ctx.stroke()

        # Draw children nodes & badges
        super().draw(ctx, time)
        ctx.restore()
