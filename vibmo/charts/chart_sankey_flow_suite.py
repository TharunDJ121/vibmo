from typing import Any, List, Optional, Tuple, Dict
from vibmo.scene.node import Node
from vibmo.core.signal import Signal
from vibmo.core.vector import Vector2D
from vibmo.core.color import Color, colors
from vibmo.core.easing import Ease

class FlowRibbonNode(Node):
    """Vertical node pillar with label and total monetary value."""
    def __init__(
        self,
        label: str,
        value: float,
        width: float = 20.0,
        height: float = 100.0,
        color: Color = colors.BLUE,
        **kwargs: Any
    ):
        super().__init__(**kwargs)
        self.label = label
        self.value = value
        self.width = Signal(float(width), f"{self.name}.width")
        self.height = Signal(float(height), f"{self.name}.height")
        self.color = color

    def draw(self, ctx: Any, time: float = 0.0) -> None:
        w = self.width.get(time)
        h = self.height.get(time)

        ctx.save()

        # Draw node pillar
        ctx.set_source_rgba(*self.color.to_cairo())
        ctx.rectangle(0, 0, w, h)
        ctx.fill()

        # Draw text labels
        ctx.set_source_rgba(1.0, 1.0, 1.0, 1.0)
        ctx.select_font_face("sans-serif", 0, 1) # Normal weight
        ctx.set_font_size(14)

        # Label
        text = self.label
        extents = ctx.text_extents(text)
        ctx.move_to(w / 2 - extents.width / 2, -10)
        ctx.show_text(text)

        # Monetary Value
        val_text = f"${self.value:,.2f}"
        val_extents = ctx.text_extents(val_text)
        ctx.move_to(w / 2 - val_extents.width / 2, h + 20)
        ctx.show_text(val_text)

        ctx.restore()
        super().draw(ctx, time)

class ConversionDropoffIndicator(Node):
    """Red branch highlighting customer/traffic drop-off."""
    def __init__(
        self,
        start_pos: Tuple[float, float],
        dropoff_value: float,
        dropoff_width: float,
        direction: str = "down", # "up" or "down"
        **kwargs: Any
    ):
        super().__init__(**kwargs)
        self.start_pos = Vector2D.from_any(start_pos)
        self.dropoff_value = dropoff_value
        self.dropoff_width = dropoff_width
        self.direction = direction
        self.color = colors.RED
        self.trim = Signal(1.0, f"{self.name}.trim")

    def draw(self, ctx: Any, time: float = 0.0) -> None:
        ctx.save()

        trim_val = self.trim.get(time)

        if trim_val > 0:
            ctx.set_source_rgba(self.color.r, self.color.g, self.color.b, self.color.a * 0.7)

            # Simple curving dropoff path
            dropoff_len = 50.0 * trim_val
            dir_mult = 1.0 if self.direction == "down" else -1.0

            ctx.move_to(self.start_pos.x, self.start_pos.y)
            ctx.line_to(self.start_pos.x + self.dropoff_width, self.start_pos.y)

            # Curve down/up and thin out
            ctx.curve_to(
                self.start_pos.x + self.dropoff_width, self.start_pos.y + 20 * dir_mult,
                self.start_pos.x + self.dropoff_width/2, self.start_pos.y + dropoff_len * dir_mult,
                self.start_pos.x + self.dropoff_width/2, self.start_pos.y + dropoff_len * dir_mult
            )

            ctx.curve_to(
                self.start_pos.x + self.dropoff_width/2, self.start_pos.y + dropoff_len * dir_mult,
                self.start_pos.x, self.start_pos.y + 20 * dir_mult,
                self.start_pos.x, self.start_pos.y
            )

            ctx.fill()

            # Value label
            ctx.set_source_rgba(1.0, 0.0, 0.0, trim_val)
            ctx.select_font_face("sans-serif", 0, 1)
            ctx.set_font_size(12)
            val_text = f"-${self.dropoff_value:,.2f}"
            extents = ctx.text_extents(val_text)
            ctx.move_to(self.start_pos.x + self.dropoff_width/2 - extents.width/2, self.start_pos.y + (dropoff_len + 15) * dir_mult)
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
        self.glow_color = glow_color
        self.thickness = thickness
        self.progress = Signal(0.0, f"{self.name}.progress")

    def draw(self, ctx: Any, time: float = 0.0) -> None:
        prog = self.progress.get(time)
        if prog <= 0 or len(self.path_points) < 2:
            return

        ctx.save()

        ctx.set_source_rgba(self.glow_color.r, self.glow_color.g, self.glow_color.b, self.glow_color.a * 0.5)
        ctx.set_line_width(self.thickness)
        ctx.set_line_cap(1) # ROUND
        ctx.set_line_join(1) # ROUND

        # Draw path up to progress
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

        # Add a brighter core glow
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

class SankeyFlowDiagram(Node):
    """Multi-stage branching flow diagram with smooth Bezier ribbon paths connecting categorical nodes."""
    def __init__(
        self,
        nodes_data: Dict[str, Dict], # Format: {"NodeA": {"value": 1000, "pos": (x,y), "color": Color}, ...}
        links_data: List[Dict], # Format: [{"source": "NodeA", "target": "NodeB", "value": 500, "color": Color, "dropoff": 100}, ...]
        value_scale: float = 1.0, # pixels per unit value
        **kwargs: Any
    ):
        super().__init__(**kwargs)
        self.nodes_data = nodes_data
        self.links_data = links_data
        self.value_scale = value_scale

        self.flow_progress = Signal(1.0, f"{self.name}.flow_progress")

        self._build_diagram()

    def _build_diagram(self):
        # Instantiate node pillars
        self.pillars = {}
        for node_id, data in self.nodes_data.items():
            val = data.get("value", 0)
            h = val * self.value_scale
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

        # Add dropoffs if needed
        self.dropoffs = []
        # Calculate Y offsets for source and target connections
        self.source_offsets = {node_id: 0.0 for node_id in self.nodes_data}
        self.target_offsets = {node_id: 0.0 for node_id in self.nodes_data}

        for link in self.links_data:
            src = link["source"]
            tgt = link["target"]
            val = link["value"]
            drop = link.get("dropoff", 0.0)

            # Simple math: sum of inputs - dropoff = sum of outputs (checked in tests)

            src_pillar = self.pillars[src]
            src_pos = src_pillar.position.get()

            if drop > 0:
                drop_w = drop * self.value_scale
                drop_indicator = ConversionDropoffIndicator(
                    start_pos=(src_pos[0], src_pos[1] + self.source_offsets[src] + (val * self.value_scale)),
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

            # Reset offsets for drawing
            src_offsets = {node_id: 0.0 for node_id in self.nodes_data}
            tgt_offsets = {node_id: 0.0 for node_id in self.nodes_data}

            for link in self.links_data:
                src = link["source"]
                tgt = link["target"]
                val = link["value"]
                color = link.get("color", colors.GRAY)
                drop = link.get("dropoff", 0.0)

                src_node = self.pillars[src]
                tgt_node = self.pillars[tgt]

                src_pos = src_node.position.get()
                tgt_pos = tgt_node.position.get()

                w = val * self.value_scale

                start_x = src_pos[0] + src_node.width.get()
                start_y = src_pos[1] + src_offsets[src]

                end_x = tgt_pos[0]
                end_y = tgt_pos[1] + tgt_offsets[tgt]

                cur_end_x = start_x + (end_x - start_x) * prog
                cur_end_y = start_y + (end_y - start_y) * prog

                # Bezier control points for smooth S-curve ribbon
                cp1_x = start_x + (cur_end_x - start_x) * 0.5
                cp1_y = start_y
                cp2_x = cur_end_x - (cur_end_x - start_x) * 0.5
                cp2_y = cur_end_y

                # Draw the ribbon path
                ctx.set_source_rgba(color.r, color.g, color.b, color.a * 0.4)

                ctx.move_to(start_x, start_y)

                # Top curve
                ctx.curve_to(cp1_x, cp1_y, cp2_x, cp2_y, cur_end_x, cur_end_y)

                # Right edge (down)
                ctx.line_to(cur_end_x, cur_end_y + w)

                # Bottom curve (backwards)
                ctx.curve_to(
                    cp2_x, cur_end_y + w,
                    cp1_x, cp1_y + w,
                    start_x, start_y + w
                )

                ctx.close_path()
                ctx.fill()

                src_offsets[src] += w
                tgt_offsets[tgt] += w

                if drop > 0:
                     src_offsets[src] += drop * self.value_scale

            ctx.restore()

        super().draw(ctx, time)

    def trace_flow(self, duration: float = 2.0) -> Any:
        self.flow_progress.set(0.0)
        from vibmo.timeline.scheduler import ParallelGroup
        actions = [
            self.flow_progress.to(1.0, duration=duration, ease=Ease.in_out_cubic)
        ]

        for d in self.dropoffs:
            d.trim.set(0.0)
            actions.append(
                d.trim.to(1.0, duration=duration*0.5, delay=duration*0.5, ease=Ease.out_quad)
            )

        return ParallelGroup(actions)
