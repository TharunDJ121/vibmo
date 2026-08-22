"""
AI Reasoning Tree-of-Thought (ToT) Visualizer suite.
"""

from __future__ import annotations
import math
from typing import Any, Dict, List, Optional, Sequence, Tuple, Union
import cairo

from vibmo.core.vector import Vector2D
from vibmo.core.color import Color, colors
from vibmo.core.signal import Signal, AnimationAction
from vibmo.core.easing import Ease, EasingFunc
from vibmo.timeline.scheduler import all as parallel_all
from vibmo.scene.node import Node


class ExplorationScoreBadge(Node):
    """
    Numeric evaluation score pill (`Score: 0.94`) with emerald fill for winner.
    """
    def __init__(self, score: float = 0.0, is_winner: bool = False, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.score = score
        self.is_winner = is_winner
        self.opacity = Signal(1.0)
        self.width = 80.0
        self.height = 24.0

    def draw(self, ctx: Any, time: float = 0.0) -> None:
        ctx.save()
        op = self.opacity.get(time)
        ctx.set_line_width(1.0)

        # Pill background
        radius = self.height / 2.0
        ctx.arc(radius, radius, radius, math.pi / 2, 3 * math.pi / 2)
        ctx.arc(self.width - radius, radius, radius, -math.pi / 2, math.pi / 2)
        ctx.close_path()

        if self.is_winner:
            bg_color = colors.EMERALD_500.to_tuple_rgba()
            text_color = (1.0, 1.0, 1.0, op)
        else:
            bg_color = colors.SLATE_800.to_tuple_rgba()
            text_color = colors.SLATE_300.to_tuple_rgba()

        ctx.set_source_rgba(bg_color[0], bg_color[1], bg_color[2], bg_color[3] * op)
        ctx.fill_preserve()

        ctx.set_source_rgba(text_color[0], text_color[1], text_color[2], op * 0.2)
        ctx.stroke()

        # Text
        ctx.set_source_rgba(text_color[0], text_color[1], text_color[2], text_color[3] * op)
        ctx.select_font_face("sans-serif", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
        ctx.set_font_size(12)
        text = f"Score: {self.score:.2f}"
        extents = ctx.text_extents(text)
        x = (self.width - extents.width) / 2.0 - extents.x_bearing
        y = (self.height - extents.height) / 2.0 - extents.y_bearing
        ctx.move_to(x, y)
        ctx.show_text(text)

        ctx.restore()


class ReasoningNodeBranch(Node):
    """
    Individual thought bubble card with status state (Evaluating, Valid, Pruned).
    """
    def __init__(self, node_id: str, thought: str, status: str = "Evaluating", **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.node_id = node_id
        self.thought = thought
        self.status = status # "Evaluating", "Valid", "Pruned"
        self.width = 160.0
        self.height = 60.0
        self.opacity = Signal(1.0)
        self.scale_sig = Signal(1.0)

    def draw(self, ctx: Any, time: float = 0.0) -> None:
        ctx.save()
        op = self.opacity.get(time)
        scale = self.scale_sig.get(time)

        ctx.translate(self.width / 2.0, self.height / 2.0)
        ctx.scale(scale, scale)
        ctx.translate(-self.width / 2.0, -self.height / 2.0)

        radius = 8.0
        ctx.arc(self.width - radius, radius, radius, -math.pi / 2, 0)
        ctx.arc(self.width - radius, self.height - radius, radius, 0, math.pi / 2)
        ctx.arc(radius, self.height - radius, radius, math.pi / 2, math.pi)
        ctx.arc(radius, radius, radius, math.pi, 3 * math.pi / 2)
        ctx.close_path()

        if self.status == "Evaluating":
            bg_color = colors.SLATE_800.to_tuple_rgba()
            border_color = colors.BLUE_500.to_tuple_rgba()
        elif self.status == "Valid":
            bg_color = colors.EMERALD.to_tuple_rgba() # using EMERALD directly instead of EMERALD_900
            bg_color = (bg_color[0]*0.3, bg_color[1]*0.3, bg_color[2]*0.3, bg_color[3])
            border_color = colors.EMERALD.to_tuple_rgba()
        elif self.status == "Pruned":
            bg_color = colors.ROSE.to_tuple_rgba() # using ROSE directly
            bg_color = (bg_color[0]*0.3, bg_color[1]*0.3, bg_color[2]*0.3, bg_color[3])
            border_color = colors.ROSE.to_tuple_rgba()
        else:
            bg_color = colors.SLATE_800.to_tuple_rgba()
            border_color = colors.SLATE_500.to_tuple_rgba()

        ctx.set_source_rgba(bg_color[0], bg_color[1], bg_color[2], bg_color[3] * op)
        ctx.fill_preserve()

        ctx.set_source_rgba(border_color[0], border_color[1], border_color[2], border_color[3] * op)
        ctx.set_line_width(2.0)
        ctx.stroke()

        # Text
        ctx.set_source_rgba(1.0, 1.0, 1.0, op)
        ctx.select_font_face("sans-serif", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)
        ctx.set_font_size(11)

        # Simple text wrapping for thought
        words = self.thought.split()
        lines = []
        current_line = ""
        for word in words:
            if ctx.text_extents(current_line + word).width > self.width - 20:
                lines.append(current_line)
                current_line = word + " "
            else:
                current_line += word + " "
        lines.append(current_line)

        y = 20.0
        for line in lines[:3]: # max 3 lines
            extents = ctx.text_extents(line)
            ctx.move_to(10.0, y)
            ctx.show_text(line)
            y += 14.0

        super().draw(ctx, time)
        ctx.restore()


class PrunedBranchFade(Node):
    """
    Red-tinted fading dashed branch indicating rejected reasoning path.
    """
    def __init__(self, start_pos: Tuple[float, float], end_pos: Tuple[float, float], **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.start_pos = start_pos
        self.end_pos = end_pos
        self.progress = Signal(1.0)
        self.opacity = Signal(1.0)

    def draw(self, ctx: Any, time: float = 0.0) -> None:
        ctx.save()
        op = self.opacity.get(time)
        prog = self.progress.get(time)

        if prog <= 0 or op <= 0:
            ctx.restore()
            return

        color = colors.ROSE_500.to_tuple_rgba()
        ctx.set_source_rgba(color[0], color[1], color[2], color[3] * op)
        ctx.set_line_width(2.0)

        # Dashed line
        ctx.set_dash([6.0, 4.0], 0)

        x1, y1 = self.start_pos
        x2, y2 = self.end_pos

        dx = x2 - x1
        dy = y2 - y1

        # Draw a cubic bezier curve for the branch
        ctrl_x1 = x1 + dx * 0.5
        ctrl_y1 = y1
        ctrl_x2 = x1 + dx * 0.5
        ctrl_y2 = y2

        # If we want to animate drawing the path, we'd need to interpolate.
        # For simplicity, just fade it or scale it.
        # Since cairo path interpolation is complex without MorphPath, we just draw full path and fade.

        ctx.move_to(x1, y1)
        ctx.curve_to(ctrl_x1, ctrl_y1, ctrl_x2, ctrl_y2, x1 + dx * prog, y1 + dy * prog)
        ctx.stroke()

        ctx.restore()


class TreeOfThoughtTree(Node):
    """
    Hierarchical node-link graph showing branching exploration of thought paths.
    """
    def __init__(self, root_thought: str = "Root", **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.nodes_data = {"root": {"thought": root_thought, "status": "Valid", "parent": None, "children": []}}

        self.node_components = {}
        self.badges = {}
        self.edges = []

        root_comp = ReasoningNodeBranch("root", root_thought, "Valid")
        root_comp.position = Signal((50.0, 300.0))
        self.add(root_comp)
        self.node_components["root"] = root_comp

    def expand_node(self, parent_id: str, child_nodes: List[Dict[str, Any]], duration: float = 1.0) -> Any:
        """
        Expands a node, creating child branches with animation.
        child_nodes: List of dicts with 'id', 'thought', 'status', 'score', 'is_winner'
        """
        if parent_id not in self.nodes_data:
            return parallel_all()

        parent_comp = self.node_components[parent_id]
        parent_x, parent_y = parent_comp.position.get(0.0)

        num_children = len(child_nodes)
        y_spacing = 100.0
        start_y = parent_y - (num_children - 1) * y_spacing / 2.0

        actions = []

        for i, child_data in enumerate(child_nodes):
            c_id = child_data['id']
            c_thought = child_data['thought']
            c_status = child_data.get('status', 'Evaluating')
            c_score = child_data.get('score', None)
            c_winner = child_data.get('is_winner', False)

            self.nodes_data[parent_id]['children'].append(c_id)
            self.nodes_data[c_id] = {
                "thought": c_thought,
                "status": c_status,
                "parent": parent_id,
                "children": []
            }

            target_x = parent_x + 250.0
            target_y = start_y + i * y_spacing

            # Add branch edge
            if c_status == "Pruned":
                edge = PrunedBranchFade((parent_x + 160.0, parent_y + 30.0), (target_x, target_y + 30.0))
                edge.progress = Signal(0.0)
                self.add(edge)
                self.edges.append(edge)
                actions.append(edge.progress.to(1.0, duration=duration, ease=Ease.out_cubic))

            # Add node component
            child_comp = ReasoningNodeBranch(c_id, c_thought, c_status)
            child_comp.position = Signal((target_x, target_y))
            child_comp.opacity = Signal(0.0)
            child_comp.scale_sig = Signal(0.5)
            self.add(child_comp)
            self.node_components[c_id] = child_comp

            actions.append(child_comp.opacity.to(1.0, duration=duration, ease=Ease.out_quad))
            actions.append(child_comp.scale_sig.to(1.0, duration=duration, ease=Ease.out_back))

            # Add badge if score exists
            if c_score is not None:
                badge = ExplorationScoreBadge(c_score, c_winner)
                badge.position = Signal((target_x + 40.0, target_y - 12.0))
                badge.opacity = Signal(0.0)
                self.add(badge)
                self.badges[c_id] = badge
                actions.append(badge.opacity.to(1.0, duration=duration, ease=Ease.out_quad))

        return parallel_all(*actions)

    def draw(self, ctx: Any, time: float = 0.0) -> None:
        ctx.save()

        # Draw edges for Valid/Evaluating nodes
        ctx.set_line_width(2.0)
        ctx.set_source_rgba(0.4, 0.4, 0.5, 0.5) # Slate color for standard edges

        for p_id, data in self.nodes_data.items():
            if not data['children']:
                continue

            p_comp = self.node_components.get(p_id)
            if not p_comp:
                continue

            px, py = p_comp.position.get(time)
            px += 160.0 # width of node
            py += 30.0 # half height

            for c_id in data['children']:
                c_comp = self.node_components.get(c_id)
                if not c_comp:
                    continue

                # Skip pruned as they have custom PrunedBranchFade components
                if self.nodes_data[c_id]['status'] == "Pruned":
                    continue

                cx, cy = c_comp.position.get(time)
                cy += 30.0 # half height

                op = c_comp.opacity.get(time)
                if op <= 0:
                    continue

                ctx.set_source_rgba(0.4, 0.4, 0.5, 0.5 * op)

                # Cubic bezier connector
                dx = cx - px
                ctx.move_to(px, py)
                ctx.curve_to(px + dx * 0.5, py, px + dx * 0.5, cy, cx, cy)
                ctx.stroke()

        # Draw children nodes
        super().draw(ctx, time)

        ctx.restore()
