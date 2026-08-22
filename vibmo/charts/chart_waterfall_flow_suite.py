from typing import Any, List
from vibmo.scene.node import Node
from vibmo.core.color import colors, Color
from vibmo.core.vector import Vector2D
from vibmo.core.signal import Signal

class CumulativeBridgeConnector(Node):
    def __init__(self, start_point: Vector2D, end_point: Vector2D, **kwargs):
        super().__init__(**kwargs)
        self.start_point = Signal(start_point)
        self.end_point = Signal(end_point)
        self.color = Signal(colors.SLATE_400)
        self.line_width = Signal(2.0)

    def draw(self, ctx: Any, time: float = 0.0) -> None:
        start = self.start_point.get(time)
        end = self.end_point.get(time)
        color = self.color.get(time)
        lw = self.line_width.get(time)

        ctx.save()
        ctx.set_source_rgba(*color.to_cairo())
        ctx.set_line_width(lw)
        ctx.set_dash([5.0, 5.0], 0)

        ctx.move_to(start.x, start.y)
        ctx.line_to(end.x, end.y)
        ctx.stroke()
        ctx.restore()

        super().draw(ctx, time)

class NetGainColumn(Node):
    def __init__(self, width: float, height: float, **kwargs):
        super().__init__(**kwargs)
        self.column_width = Signal(float(width))
        self.column_height = Signal(float(height))
        self.color = Signal(colors.GREEN_500)

    def draw(self, ctx: Any, time: float = 0.0) -> None:
        cw = self.column_width.get(time)
        ch = self.column_height.get(time)
        color = self.color.get(time)

        ctx.save()
        ctx.set_source_rgba(*color.to_cairo())
        ctx.rectangle(0, 0, cw, ch)
        ctx.fill()
        ctx.restore()

        super().draw(ctx, time)


class DeductionColumn(Node):
    def __init__(self, width: float, height: float, **kwargs):
        super().__init__(**kwargs)
        self.column_width = Signal(float(width))
        self.column_height = Signal(float(height))
        self.color = Signal(colors.RED_500)

    def draw(self, ctx: Any, time: float = 0.0) -> None:
        cw = self.column_width.get(time)
        ch = self.column_height.get(time)
        color = self.color.get(time)

        ctx.save()
        ctx.set_source_rgba(*color.to_cairo())
        ctx.rectangle(0, 0, cw, ch)
        ctx.fill()
        ctx.restore()

        super().draw(ctx, time)


class WaterfallCostChart(Node):
    def __init__(self, steps: List[float], column_width: float = 50.0, spacing: float = 20.0, **kwargs):
        super().__init__(**kwargs)
        self.steps = steps
        self.column_width = Signal(float(column_width))
        self.spacing = Signal(float(spacing))

        self.columns: List[Node] = []
        self.connectors: List[Node] = []

        self._build_chart()

    def _build_chart(self) -> None:
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

    def draw(self, ctx: Any, time: float = 0.0) -> None:
        super().draw(ctx, time)
