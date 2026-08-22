from typing import List, Tuple, Any, Dict, Optional
import math
from vibmo.scene.node import Node
from vibmo.core.signal import Signal
from vibmo.core.vector import Vector2D
from vibmo.core.color import Color

class MultiVariableBubbleScatter(Node):
    def __init__(self, width: float, height: float, data: List[Dict[str, Any]]):
        super().__init__()
        self.width = Signal(float(width))
        self.height = Signal(float(height))
        self.data = data

        # Calculate bounds for normalization
        if not self.data:
            self.x_min, self.x_max = 0.0, 1.0
            self.y_min, self.y_max = 0.0, 1.0
            self.z_min, self.z_max = 0.0, 1.0
        else:
            self.x_min = min(d.get("x", 0.0) for d in self.data)
            self.x_max = max(d.get("x", 1.0) for d in self.data)
            self.y_min = min(d.get("y", 0.0) for d in self.data)
            self.y_max = max(d.get("y", 1.0) for d in self.data)
            self.z_min = min(d.get("z", 0.0) for d in self.data)
            self.z_max = max(d.get("z", 1.0) for d in self.data)

            if self.x_max == self.x_min:
                self.x_max = self.x_min + 1.0
            if self.y_max == self.y_min:
                self.y_max = self.y_min + 1.0
            if self.z_max == self.z_min:
                self.z_max = self.z_min + 1.0

    def get_normalized_coords(self, x: float, y: float, w: float, h: float) -> Tuple[float, float]:
        nx = (x - self.x_min) / (self.x_max - self.x_min)
        ny = (y - self.y_min) / (self.y_max - self.y_min)
        # Flip Y axis for rendering (standard chart coords)
        return nx * w, (1.0 - ny) * h

    def get_normalized_radius(self, z: float, max_radius: float = 40.0, min_radius: float = 5.0) -> float:
        nz = (z - self.z_min) / (self.z_max - self.z_min)
        # Size by area, not radius
        return min_radius + (max_radius - min_radius) * math.sqrt(max(0, nz))

    def draw(self, ctx: Any, time: float = 0.0) -> None:
        w = self.width.get(time)
        h = self.height.get(time)

        ctx.save()

        for d in self.data:
            x = d.get("x", 0.0)
            y = d.get("y", 0.0)
            z = d.get("z", 0.0)
            color_val = d.get("color", Color.WHITE)
            c = Color.from_any(color_val)

            px, py = self.get_normalized_coords(x, y, w, h)
            r = self.get_normalized_radius(z)

            ctx.new_path()
            ctx.arc(px, py, r, 0, 2 * math.pi)
            ctx.set_source_rgba(*c.to_cairo())
            ctx.fill_preserve()

            # Stroke
            ctx.set_line_width(2.0)
            ctx.set_source_rgba(1.0, 1.0, 1.0, 0.8)
            ctx.stroke()

        super().draw(ctx, time)
        ctx.restore()

class MotionTrailBubble(Node):
    def __init__(self, history: List[Vector2D], color: Any, radius: float = 15.0):
        super().__init__()
        self.history = history
        self.color = Color.from_any(color)
        self.radius = Signal(float(radius))

    def draw(self, ctx: Any, time: float = 0.0) -> None:
        if not self.history:
            return

        r = self.radius.get(time)
        c = self.color

        ctx.save()

        # Draw trail
        if len(self.history) > 1:
            ctx.new_path()
            ctx.move_to(self.history[0].x, self.history[0].y)
            for pt in self.history[1:]:
                ctx.line_to(pt.x, pt.y)

            ctx.set_line_width(r * 0.5)
            # Fading trail effect, simple linear gradient not explicitly supported by cairo here easily without complex setup,
            # so we'll just draw a solid line with lower opacity
            ctx.set_source_rgba(c.r, c.g, c.b, c.a * 0.3)
            ctx.stroke()

        # Draw current bubble
        last_pt = self.history[-1]
        ctx.new_path()
        ctx.arc(last_pt.x, last_pt.y, r, 0, 2 * math.pi)
        ctx.set_source_rgba(*c.to_cairo())
        ctx.fill_preserve()

        ctx.set_line_width(2.0)
        ctx.set_source_rgba(1.0, 1.0, 1.0, 0.8)
        ctx.stroke()

        super().draw(ctx, time)
        ctx.restore()

class QuadrantPartitionLines(Node):
    def __init__(self, width: float, height: float, center_x_ratio: float = 0.5, center_y_ratio: float = 0.5):
        super().__init__()
        self.width = Signal(float(width))
        self.height = Signal(float(height))
        self.center_x_ratio = Signal(float(center_x_ratio))
        self.center_y_ratio = Signal(float(center_y_ratio))
        self.color = Color(1.0, 1.0, 1.0, 0.3)
        self.line_width = Signal(2.0)

    def draw(self, ctx: Any, time: float = 0.0) -> None:
        w = self.width.get(time)
        h = self.height.get(time)
        cx = self.center_x_ratio.get(time) * w
        cy = self.center_y_ratio.get(time) * h

        ctx.save()
        ctx.set_line_width(self.line_width.get(time))
        ctx.set_source_rgba(*self.color.to_cairo())

        # Vertical line
        ctx.new_path()
        ctx.move_to(cx, 0)
        ctx.line_to(cx, h)
        ctx.stroke()

        # Horizontal line
        ctx.new_path()
        ctx.move_to(0, cy)
        ctx.line_to(w, cy)
        ctx.stroke()

        super().draw(ctx, time)
        ctx.restore()

class BubbleScaleLegend(Node):
    def __init__(self, values: List[float], max_radius: float = 40.0, min_radius: float = 5.0):
        super().__init__()
        self.values = sorted(values)
        self.max_radius = Signal(float(max_radius))
        self.min_radius = Signal(float(min_radius))
        self.color = Color(0.5, 0.5, 0.5, 0.5)

        if not self.values:
            self.v_min, self.v_max = 0.0, 1.0
        else:
            self.v_min = min(self.values)
            self.v_max = max(self.values)
            if self.v_max == self.v_min:
                self.v_max = self.v_min + 1.0

    def get_normalized_radius(self, v: float, time: float = 0.0) -> float:
        nv = (v - self.v_min) / (self.v_max - self.v_min)
        mr = self.max_radius.get(time)
        mir = self.min_radius.get(time)
        return mir + (mr - mir) * math.sqrt(max(0, nv))

    def draw(self, ctx: Any, time: float = 0.0) -> None:
        if not self.values:
            return

        ctx.save()

        # Draw nested circles at the bottom center of the legend's local origin
        mr = self.max_radius.get(time)
        base_y = mr * 2

        for v in reversed(self.values): # Draw largest first
            r = self.get_normalized_radius(v, time)

            ctx.new_path()
            # Tangent at the bottom
            ctx.arc(mr, base_y - r, r, 0, 2 * math.pi)
            ctx.set_source_rgba(*self.color.to_cairo())
            ctx.fill_preserve()

            ctx.set_line_width(1.0)
            ctx.set_source_rgba(1.0, 1.0, 1.0, 0.8)
            ctx.stroke()

        super().draw(ctx, time)
        ctx.restore()
