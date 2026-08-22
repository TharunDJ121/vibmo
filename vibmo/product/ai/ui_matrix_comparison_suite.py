import math
from typing import Any

from vibmo.scene.node import Node
from vibmo.core.color import Color
from vibmo.core.signal import Signal


class InteractiveFeatureMatrix(Node):
    """
    Table comparing "Our Product" vs 3 competitors across 10 feature categories.
    """
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.width = Signal(800.0)
        self.height = Signal(600.0)

    def draw(self, ctx: Any, time: float = 0.0) -> None:
        ctx.save()
        width = self.width.get(time)
        height = self.height.get(time)

        # Background
        ctx.set_source_rgba(*Color.hex("#ffffff").to_tuple_rgba())
        ctx.rectangle(0, 0, width, height)
        ctx.fill()

        # Grid lines
        ctx.set_line_width(1.0)
        ctx.set_source_rgba(*Color.hex("#e2e8f0").to_tuple_rgba())

        cols = 5 # 1 feature column + 4 competitors
        rows = 11 # 1 header + 10 features

        col_width = width / cols
        row_height = height / rows

        for i in range(cols + 1):
            x = i * col_width
            ctx.move_to(x, 0)
            ctx.line_to(x, height)
            ctx.stroke()

        for i in range(rows + 1):
            y = i * row_height
            ctx.move_to(0, y)
            ctx.line_to(width, y)
            ctx.stroke()

        super().draw(ctx, time)
        ctx.restore()


class CompetitorComparisonRow(Node):
    """
    Alternating striped table row with green checkmarks, red crosses, and partial score badges.
    """
    def __init__(self, is_striped: bool = False, **kwargs):
        super().__init__(**kwargs)
        self.width = Signal(800.0)
        self.height = Signal(50.0)
        self.is_striped = is_striped

    def draw(self, ctx: Any, time: float = 0.0) -> None:
        ctx.save()
        width = self.width.get(time)
        height = self.height.get(time)

        # Background stripe
        if self.is_striped:
            ctx.set_source_rgba(*Color.hex("#f8fafc").to_tuple_rgba())
        else:
            ctx.set_source_rgba(*Color.hex("#ffffff").to_tuple_rgba())

        ctx.rectangle(0, 0, width, height)
        ctx.fill()

        # Draw some icons (checkmarks, crosses)
        cols = 5
        col_width = width / cols

        for i in range(1, cols):
            center_x = i * col_width + col_width / 2
            center_y = height / 2

            if i == 1: # "Our Product" - always green check
                ctx.set_source_rgba(*Color.hex("#22c55e").to_tuple_rgba()) # Green
                ctx.arc(center_x, center_y, 10, 0, 2 * math.pi)
                ctx.fill()
            elif i % 2 == 0: # Red cross
                ctx.set_source_rgba(*Color.hex("#ef4444").to_tuple_rgba()) # Red
                ctx.set_line_width(2.0)
                ctx.move_to(center_x - 8, center_y - 8)
                ctx.line_to(center_x + 8, center_y + 8)
                ctx.move_to(center_x + 8, center_y - 8)
                ctx.line_to(center_x - 8, center_y + 8)
                ctx.stroke()
            else: # Partial score badge
                ctx.set_source_rgba(*Color.hex("#eab308").to_tuple_rgba()) # Yellow
                ctx.rectangle(center_x - 12, center_y - 8, 24, 16)
                ctx.fill()

        super().draw(ctx, time)
        ctx.restore()


class TooltipFeatureExplanation(Node):
    """
    Popover card detailing feature specifications.
    """
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.width = Signal(200.0)
        self.height = Signal(100.0)

    def draw(self, ctx: Any, time: float = 0.0) -> None:
        ctx.save()
        width = self.width.get(time)
        height = self.height.get(time)

        # Shadow
        ctx.set_source_rgba(*Color.hex("#000000").to_tuple_rgba()[:3], 0.1)
        ctx.rectangle(4, 4, width, height)
        ctx.fill()

        # Card background
        ctx.set_source_rgba(*Color.hex("#ffffff").to_tuple_rgba())
        ctx.rectangle(0, 0, width, height)
        ctx.fill()

        # Border
        ctx.set_source_rgba(*Color.hex("#cbd5e1").to_tuple_rgba())
        ctx.set_line_width(1.0)
        ctx.rectangle(0, 0, width, height)
        ctx.stroke()

        super().draw(ctx, time)
        ctx.restore()


class StickyHeaderColumn(Node):
    """
    Highlighted column for "Our Product" with cyan glowing border.
    """
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.width = Signal(160.0)
        self.height = Signal(600.0)

    def draw(self, ctx: Any, time: float = 0.0) -> None:
        ctx.save()
        width = self.width.get(time)
        height = self.height.get(time)

        # Base background
        ctx.set_source_rgba(*Color.hex("#f0fdfa").to_tuple_rgba())
        ctx.rectangle(0, 0, width, height)
        ctx.fill()

        # Cyan glowing border
        ctx.set_source_rgba(*Color.hex("#06b6d4").to_tuple_rgba())
        ctx.set_line_width(4.0)
        ctx.rectangle(0, 0, width, height)
        ctx.stroke()

        # Inner subtle glow (simplified)
        ctx.set_source_rgba(*Color.hex("#22d3ee").to_tuple_rgba()[:3], 0.3)
        ctx.set_line_width(8.0)
        ctx.rectangle(0, 0, width, height)
        ctx.stroke()

        super().draw(ctx, time)
        ctx.restore()
