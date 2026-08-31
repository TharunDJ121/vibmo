from typing import Any, Dict, List, Optional, Union
from vibmo.scene.node import Node
from vibmo.core.color import colors, Color
from vibmo.core.vector import Vector2D
from vibmo.core.signal import Signal, AnimationAction
from vibmo.core.easing import Ease, EasingFunc
from vibmo.timeline.scheduler import ParallelGroup

class CumulativeBridgeConnector(Node):
    def __init__(self, start_point: Vector2D, end_point: Vector2D, **kwargs: Any):
        super().__init__(**kwargs)
        self.start_point = Signal(start_point, f"{self.name}.start_point")
        self.end_point = Signal(end_point, f"{self.name}.end_point")
        self.color = Signal(colors.SLATE_400, f"{self.name}.color")
        self.line_width = Signal(2.0, f"{self.name}.line_width")
        self.reveal = Signal(1.0, f"{self.name}.reveal")

    def draw(self, ctx: Any, time: float = 0.0) -> None:
        prog = max(0.0, min(1.0, float(self.reveal.get(time))))
        if prog <= 0.001:
            return

        start = self.start_point.get(time)
        end = self.end_point.get(time)
        color = self.color.get(time)
        lw = self.line_width.get(time)

        interp_end_x = start.x + (end.x - start.x) * prog
        interp_end_y = start.y + (end.y - start.y) * prog

        ctx.save()
        ctx.set_source_rgba(*color.to_cairo())
        ctx.set_line_width(lw)
        ctx.set_dash([5.0, 5.0], 0)

        ctx.move_to(start.x, start.y)
        ctx.line_to(interp_end_x, interp_end_y)
        ctx.stroke()
        ctx.restore()

        super().draw(ctx, time)


class FlowBarNode(Node):
    """Waterfall flow bar representing positive gain, deduction, or total pillar."""
    def __init__(self, width: float, height: float, is_gain: bool = True, color: Optional[Union[Color, str]] = None, **kwargs: Any):
        super().__init__(**kwargs)
        self.column_width = Signal(float(width), f"{self.name}.column_width")
        self.column_height = Signal(float(height), f"{self.name}.column_height")
        default_col = colors.GREEN_500 if is_gain else colors.RED_500
        self.color = Signal(Color.from_any(color) if color else default_col, f"{self.name}.color")
        self.reveal = Signal(1.0, f"{self.name}.reveal")

    def draw(self, ctx: Any, time: float = 0.0) -> None:
        prog = max(0.0, min(1.0, float(self.reveal.get(time))))
        if prog <= 0.001:
            return

        cw = self.column_width.get(time)
        ch = self.column_height.get(time) * prog
        color = self.color.get(time)

        ctx.save()
        ctx.set_source_rgba(*color.to_cairo())
        ctx.rectangle(0, 0, cw, ch)
        ctx.fill()
        ctx.restore()

        super().draw(ctx, time)


class NetGainColumn(FlowBarNode):
    def __init__(self, width: float, height: float, **kwargs: Any):
        super().__init__(width=width, height=height, is_gain=True, color=colors.GREEN_500, **kwargs)


class DeductionColumn(FlowBarNode):
    def __init__(self, width: float, height: float, **kwargs: Any):
        super().__init__(width=width, height=height, is_gain=False, color=colors.RED_500, **kwargs)


class WaterfallCostChart(Node):
    """Financial variance bridge chart decomposing gains and deductions into net totals."""

    def __init__(
        self,
        steps: Union[List[float], List[Dict[str, Any]]],
        column_width: float = 50.0,
        spacing: float = 20.0,
        **kwargs: Any
    ):
        super().__init__(**kwargs)
        # Parse numeric values from steps
        self.raw_steps = steps
        parsed_steps: List[float] = []
        for s in steps:
            if isinstance(s, dict):
                parsed_steps.append(float(s.get("value", 0.0)))
            else:
                parsed_steps.append(float(s))

        self.steps = parsed_steps
        self.column_width = Signal(float(column_width), f"{self.name}.column_width")
        self.spacing = Signal(float(spacing), f"{self.name}.spacing")

        self.columns: List[FlowBarNode] = []
        self.connectors: List[CumulativeBridgeConnector] = []

        self._build_chart()

    def _build_chart(self) -> None:
        self.clear()
        self.columns.clear()
        self.connectors.clear()

        cw = self.column_width.get()
        sp = self.spacing.get()

        current_level = 0.0
        current_x = 0.0

        all_steps = list(self.steps)
        total = sum(all_steps)

        def add_col(val: float, is_total: bool = False) -> None:
            nonlocal current_level, current_x
            if is_total:
                col = NetGainColumn(cw, abs(val)) if val >= 0 else DeductionColumn(cw, abs(val))
                y_pos = -val if val >= 0 else 0.0
                col.position.set(Vector2D(current_x, y_pos))
                self.add(col)
                self.columns.append(col)
                current_level = val
            else:
                if val >= 0:
                    col = NetGainColumn(cw, val)
                    y_pos = -current_level - val
                    col.position.set(Vector2D(current_x, y_pos))
                    current_level += val
                else:
                    col = DeductionColumn(cw, abs(val))
                    y_pos = -current_level
                    col.position.set(Vector2D(current_x, y_pos))
                    current_level += val
                self.add(col)
                self.columns.append(col)

        for i, val in enumerate(all_steps):
            is_start = (i == 0)

            if is_start:
                add_col(val, is_total=True)
            else:
                prev_x = current_x
                prev_level = current_level
                add_col(val, is_total=False)

                conn_y = -prev_level
                conn = CumulativeBridgeConnector(
                    Vector2D(prev_x + cw, conn_y),
                    Vector2D(current_x, conn_y)
                )
                self.add(conn)
                self.connectors.append(conn)

            current_x += cw + sp

        # Add Total column
        prev_x = current_x - (cw + sp)
        prev_level = current_level
        add_col(total, is_total=True)

        conn_y = -prev_level
        conn = CumulativeBridgeConnector(
            Vector2D(prev_x + cw, conn_y),
            Vector2D(current_x, conn_y)
        )
        self.add(conn)
        self.connectors.append(conn)

    def reveal_steps(
        self,
        duration: float = 1.5,
        delay: float = 0.0,
        stagger: float = 0.1,
        ease: Optional[EasingFunc] = None
    ) -> ParallelGroup:
        """Animates columns and bridge connectors stepping sequentially across the timeline."""
        e = ease or Ease.out_expo
        actions = []

        for i, col in enumerate(self.columns):
            col.reveal.set(0.0)
            actions.append(col.reveal.to(1.0, duration=duration, delay=delay + i * stagger, ease=e))

        for i, conn in enumerate(self.connectors):
            conn.reveal.set(0.0)
            actions.append(conn.reveal.to(1.0, duration=duration * 0.8, delay=delay + (i + 1) * stagger, ease=e))

        return ParallelGroup(actions)

    def draw(self, ctx: Any, time: float = 0.0) -> None:
        super().draw(ctx, time)


WaterfallFinancialChart = WaterfallCostChart
