from typing import Any, Dict, List, Optional, Tuple, Union
import math
from vibmo.scene.node import Node
from vibmo.core.color import Color, colors
from vibmo.core.signal import Signal, AnimationAction
from vibmo.core.vector import Vector2D
from vibmo.core.easing import Ease, EasingFunc
from vibmo.timeline.scheduler import ParallelGroup

class FlowRibbonNode(Node):
    """Vertical pillar bar representing a state or stage."""
    def __init__(
        self,
        label: str,
        value: float,
        height: float,
        width: float = 20.0,
        color: Color = colors.BLUE,
        **kwargs: Any
    ):
        super().__init__(**kwargs)
        self.label = label
        self.value = float(value)
        self.width = Signal(float(width), f"{self.name}.width")
        self.height = Signal(float(height), f"{self.name}.height")
        self.color = Signal(Color.from_any(color), f"{self.name}.color")

    def draw(self, ctx: Any, time: float = 0.0) -> None:
        w = self.width.get(time)
        h = self.height.get(time)
        c = self.color.get(time)

        ctx.save()
        ctx.set_source_rgba(*c.to_cairo())
        ctx.rectangle(0, 0, w, h)
        ctx.fill()

        # Render text
        ctx.set_source_rgba(*colors.WHITE.to_cairo())
        ctx.select_font_face("sans-serif", 0, 0)
        ctx.set_font_size(12.0)
        ctx.move_to(0, -10)
        ctx.show_text(self.label)

        val_text = f"${self.value:,.2f}"
        ctx.move_to(0, h + 15)
        ctx.show_text(val_text)

        ctx.restore()
        super().draw(ctx, time)


class ConversionDropoffIndicator(Node):
    """Downward peeling flow indicator showing lost/churned traffic."""
    def __init__(
        self,
        start_pos: Tuple[float, float],
        dropoff_value: float,
        dropoff_width: float,
        color: Color = colors.RED,
        length: float = 50.0,
        direction: str = "down",
        **kwargs: Any
    ):
        super().__init__(**kwargs)
        self.start_pos_tuple = start_pos
        self.position.set(start_pos)
        self.dropoff_value = float(dropoff_value)
        self.dropoff_width = float(dropoff_width)
        self.direction = direction
        self.color = Signal(Color.from_any(color), f"{self.name}.color")
        self.length = Signal(float(length), f"{self.name}.length")
        self.trim = Signal(1.0, f"{self.name}.trim")

    def draw(self, ctx: Any, time: float = 0.0) -> None:
        sx = float(self.start_pos_tuple[0])
        sy = float(self.start_pos_tuple[1])
        w = float(self.dropoff_width)
        l = float(self.length.get(time))
        c = self.color.get(time)
        t = max(0.0, min(1.0, float(self.trim.get(time))))

        if t <= 0:
            return

        ctx.save()
        ctx.set_source_rgba(c.r, c.g, c.b, c.a * 0.4)

        ctx.move_to(sx, sy)
        ctx.line_to(sx + w, sy)

        # Curve downward
        cp1 = (sx + w, sy + l * 0.5 * t)
        cp2 = (sx + w + l * 0.2 * t, sy + l * t)
        end_pt = (sx + w + l * 0.5 * t, sy + l * t)

        ctx.curve_to(cp1[0], cp1[1], cp2[0], cp2[1], end_pt[0], end_pt[1])
        ctx.line_to(end_pt[0], end_pt[1] + w)

        # Back up
        cp2_back = (sx + l * 0.2 * t, sy + (l + w) * t)
        cp1_back = (sx, sy + (l * 0.5 + w) * t)
        ctx.curve_to(cp2_back[0], cp2_back[1], cp1_back[0], cp1_back[1], sx, sy + w)
        ctx.close_path()
        ctx.fill()

        # Render Dropoff Label
        if t > 0.8:
            ctx.set_source_rgba(*c.to_cairo())
            ctx.select_font_face("sans-serif", 0, 0)
            ctx.set_font_size(10.0)
            val_text = f"-${self.dropoff_value:,.2f}"
            ctx.move_to(end_pt[0] + 5, end_pt[1] + w)
            ctx.show_text(val_text)

        ctx.restore()
        super().draw(ctx, time)


class RevenuePathHighlighter(Node):
    """Glow effect tracing flow from Income -> Gross Profit -> Net Margin."""
    def __init__(
        self,
        path_points: List[Tuple[float, float]],
        glow_color: Color = colors.EMERALD,
        thickness: float = 10.0,
        **kwargs: Any
    ):
        super().__init__(**kwargs)
        self.path_points = [Vector2D.from_any(p) for p in path_points]
        self.glow_color = Color.from_any(glow_color)
        self.thickness = thickness
        self.progress = Signal(0.0, f"{self.name}.progress")

    def draw(self, ctx: Any, time: float = 0.0) -> None:
        prog = self.progress.get(time)
        if prog <= 0 or len(self.path_points) < 2:
            return

        ctx.save()

        ctx.set_source_rgba(self.glow_color.r, self.glow_color.g, self.glow_color.b, self.glow_color.a * 0.5)
        ctx.set_line_width(self.thickness)
        ctx.set_line_cap(1)
        ctx.set_line_join(1)

        total_segments = len(self.path_points) - 1
        current_segment_idx = int(prog * total_segments)
        segment_prog = (prog * total_segments) - current_segment_idx

        ctx.move_to(self.path_points[0].x, self.path_points[0].y)

        for i in range(current_segment_idx):
            ctx.line_to(self.path_points[i+1].x, self.path_points[i+1].y)

        if current_segment_idx < total_segments and segment_prog > 0:
            p1 = self.path_points[current_segment_idx]
            p2 = self.path_points[current_segment_idx + 1]
            interp_x = p1.x + (p2.x - p1.x) * segment_prog
            interp_y = p1.y + (p2.y - p1.y) * segment_prog
            ctx.line_to(interp_x, interp_y)

        ctx.stroke()

        ctx.set_source_rgba(self.glow_color.r, self.glow_color.g, self.glow_color.b, self.glow_color.a * 0.9)
        ctx.set_line_width(self.thickness * 0.4)

        ctx.move_to(self.path_points[0].x, self.path_points[0].y)
        for i in range(current_segment_idx):
            ctx.line_to(self.path_points[i+1].x, self.path_points[i+1].y)

        if current_segment_idx < total_segments and segment_prog > 0:
            p1 = self.path_points[current_segment_idx]
            p2 = self.path_points[current_segment_idx + 1]
            interp_x = p1.x + (p2.x - p1.x) * segment_prog
            interp_y = p1.y + (p2.y - p1.y) * segment_prog
            ctx.line_to(interp_x, interp_y)

        ctx.stroke()

        ctx.restore()
        super().draw(ctx, time)


class BezierFlowRibbon(Node):
    """Smooth cubic Bezier ribbon connecting source and target nodes with dynamic width."""

    def __init__(
        self,
        start_pos: Tuple[float, float] = (0.0, 0.0),
        end_pos: Tuple[float, float] = (300.0, 0.0),
        width: float = 20.0,
        color: Union[Color, str] = colors.CYAN,
        **kwargs: Any
    ):
        super().__init__(**kwargs)
        self.start_pos = Signal(start_pos, f"{self.name}.start_pos")
        self.end_pos = Signal(end_pos, f"{self.name}.end_pos")
        self.ribbon_width = Signal(float(width), f"{self.name}.ribbon_width")
        self.color = Signal(Color.from_any(color), f"{self.name}.color")
        self.progress = Signal(1.0, f"{self.name}.progress")

    def draw(self, ctx: Any, time: float = 0.0) -> None:
        prog = max(0.0, min(1.0, float(self.progress.get(time))))
        if prog <= 0:
            return

        sp = self.start_pos.get(time)
        ep = self.end_pos.get(time)
        w = self.ribbon_width.get(time)
        c = self.color.get(time)

        cur_ep_x = sp[0] + (ep[0] - sp[0]) * prog
        cur_ep_y = sp[1] + (ep[1] - sp[1]) * prog

        cp1_x = sp[0] + (cur_ep_x - sp[0]) * 0.5
        cp1_y = sp[1]
        cp2_x = cur_ep_x - (cur_ep_x - sp[0]) * 0.5
        cp2_y = cur_ep_y

        ctx.save()
        ctx.set_source_rgba(c.r, c.g, c.b, c.a * 0.4)
        ctx.move_to(sp[0], sp[1])
        ctx.curve_to(cp1_x, cp1_y, cp2_x, cp2_y, cur_ep_x, cur_ep_y)
        ctx.line_to(cur_ep_x, cur_ep_y + w)
        ctx.curve_to(cp2_x, cur_ep_y + w, cp1_x, sp[1] + w, sp[0], sp[1] + w)
        ctx.close_path()
        ctx.fill()
        ctx.restore()

        super().draw(ctx, time)


class SankeyFlowDiagram(Node):
    """Multi-stage branching flow diagram with smooth Bezier ribbon paths connecting categorical nodes."""

    def __init__(
        self,
        nodes_data: Optional[Dict[str, Dict]] = None,
        links_data: Optional[List[Dict]] = None,
        links: Optional[List[Dict]] = None,
        nodes: Optional[Dict[str, Dict]] = None,
        value_scale: float = 1.0,
        **kwargs: Any
    ):
        super().__init__(**kwargs)
        self.links_data = links if links is not None else (links_data or [])
        raw_nodes = nodes if nodes is not None else nodes_data

        if raw_nodes is None:
            node_totals: Dict[str, float] = {}
            sources = set()
            targets = set()
            for l in self.links_data:
                s, t, v = l["source"], l["target"], l.get("value", 0.0)
                node_totals[s] = node_totals.get(s, 0.0) + v
                node_totals[t] = node_totals.get(t, 0.0) + v
                sources.add(s)
                targets.add(t)

            raw_nodes = {}
            src_list = sorted(list(sources - targets))
            sink_list = sorted(list(targets - sources))
            mid_list = sorted(list(sources & targets))

            y_cursor = 50.0
            for name in src_list:
                raw_nodes[name] = {"value": node_totals[name], "pos": (0.0, y_cursor), "color": colors.CYAN_500}
                y_cursor += node_totals[name] * value_scale + 40.0

            y_cursor = 50.0
            for name in mid_list:
                raw_nodes[name] = {"value": node_totals[name], "pos": (300.0, y_cursor), "color": colors.INDIGO_500}
                y_cursor += node_totals[name] * value_scale + 40.0

            y_cursor = 50.0
            for name in sink_list:
                raw_nodes[name] = {"value": node_totals[name], "pos": (600.0, y_cursor), "color": colors.EMERALD_500}
                y_cursor += node_totals[name] * value_scale + 40.0

        self.nodes_data = raw_nodes
        self.value_scale = value_scale
        self.flow_progress = Signal(1.0, f"{self.name}.flow_progress")

        self._build_diagram()

    def _build_diagram(self):
        self.clear()
        self.pillars = {}
        for node_id, data in self.nodes_data.items():
            val = data.get("value", 0)
            h = max(1.0, val * self.value_scale)
            color = data.get("color", colors.BLUE)

            pillar = FlowRibbonNode(
                label=node_id,
                value=val,
                height=h,
                color=color
            )

            pos = data.get("pos", (0, 0))
            pillar.position.set(pos)
            self.add(pillar)
            self.pillars[node_id] = pillar

        self.dropoffs = []
        self.source_offsets = {node_id: 0.0 for node_id in self.nodes_data}
        self.target_offsets = {node_id: 0.0 for node_id in self.nodes_data}

        for link in self.links_data:
            src = link["source"]
            tgt = link["target"]
            val = link.get("value", 0.0)
            drop = link.get("dropoff", 0.0)

            if src in self.pillars:
                src_pillar = self.pillars[src]
                src_pos = src_pillar.position.get()

                if drop > 0:
                    drop_w = drop * self.value_scale
                    drop_indicator = ConversionDropoffIndicator(
                        start_pos=(src_pos[0] + src_pillar.width.get(), src_pos[1] + self.source_offsets[src] + (val * self.value_scale)),
                        dropoff_value=drop,
                        dropoff_width=drop_w
                    )
                    self.add(drop_indicator)
                    self.dropoffs.append(drop_indicator)
                    self.source_offsets[src] += drop_w
                self.source_offsets[src] += val * self.value_scale

    def draw(self, ctx: Any, time: float = 0.0) -> None:
        prog = self.flow_progress.get(time)

        if prog > 0:
            ctx.save()

            src_offsets = {node_id: 0.0 for node_id in self.nodes_data}
            tgt_offsets = {node_id: 0.0 for node_id in self.nodes_data}

            for link in self.links_data:
                src = link["source"]
                tgt = link["target"]
                val = link.get("value", 0.0)
                color = link.get("color", colors.GRAY)
                drop = link.get("dropoff", 0.0)

                if src not in self.pillars or tgt not in self.pillars:
                    continue

                src_node = self.pillars[src]
                tgt_node = self.pillars[tgt]

                src_pos = src_node.position.get()
                tgt_pos = tgt_node.position.get()

                w = max(1.0, val * self.value_scale)

                start_x = src_pos[0] + src_node.width.get()
                start_y = src_pos[1] + src_offsets[src]

                end_x = tgt_pos[0]
                end_y = tgt_pos[1] + tgt_offsets[tgt]

                cur_end_x = start_x + (end_x - start_x) * prog
                cur_end_y = start_y + (end_y - start_y) * prog

                cp1_x = start_x + (cur_end_x - start_x) * 0.5
                cp1_y = start_y
                cp2_x = cur_end_x - (cur_end_x - start_x) * 0.5
                cp2_y = cur_end_y

                resolved_color = Color.from_any(color)
                ctx.set_source_rgba(resolved_color.r, resolved_color.g, resolved_color.b, resolved_color.a * 0.4)

                ctx.move_to(start_x, start_y)
                ctx.curve_to(cp1_x, cp1_y, cp2_x, cp2_y, cur_end_x, cur_end_y)
                ctx.line_to(cur_end_x, cur_end_y + w)
                ctx.curve_to(cp2_x, cur_end_y + w, cp1_x, start_y + w, start_x, start_y + w)
                ctx.close_path()
                ctx.fill()

                src_offsets[src] += w
                tgt_offsets[tgt] += w

                if drop > 0:
                    src_offsets[src] += drop * self.value_scale

            ctx.restore()

        super().draw(ctx, time)

    def trace_flow(self, duration: float = 2.0, delay: float = 0.0, ease: Optional[EasingFunc] = None) -> ParallelGroup:
        self.flow_progress.set(0.0)
        e = ease or Ease.in_out_cubic
        actions = [
            self.flow_progress.to(1.0, duration=duration, delay=delay, ease=e)
        ]

        for d in self.dropoffs:
            d.trim.set(0.0)
            actions.append(
                d.trim.to(1.0, duration=duration*0.5, delay=delay + duration*0.5, ease=Ease.out_quad)
            )

        return ParallelGroup(actions)

    def animate_flow_current(self, duration: float = 2.0, delay: float = 0.0, ease: Optional[EasingFunc] = None) -> ParallelGroup:
        """Animates energy or data currents flowing through branching Bezier ribbons."""
        return self.trace_flow(duration=duration, delay=delay, ease=ease)
