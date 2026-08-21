import math
import random
from typing import Any, List, Optional, Tuple

from vibmo.core.color import Color, colors
from vibmo.core.vector import Vector2D
from vibmo.core.signal import Signal
from vibmo.scene.node import Node


class EmbeddingScatterCluster(Node):
    """Clustered point cloud of high-dimensional semantic vectors projected to 2D with distinct color groups."""

    def __init__(
        self,
        num_points: int = 100,
        num_clusters: int = 3,
        radius: float = 200.0,
        seed: int = 42,
        point_radius: float = 3.0,
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)
        self.num_points = num_points
        self.num_clusters = num_clusters
        self.radius = radius
        self.point_radius = point_radius

        rng = random.Random(seed)
        self.points: List[Tuple[Vector2D, Color]] = []
        
        cluster_centers = []
        cluster_colors = [
            colors.CYAN,
            colors.ROSE_500,
            colors.AMBER_500,
            colors.EMERALD_500,
            colors.VIOLET_500,
        ]
        
        for _ in range(num_clusters):
            angle = rng.uniform(0, 2 * math.pi)
            dist = rng.uniform(0, self.radius * 0.6)
            cluster_centers.append(Vector2D(math.cos(angle) * dist, math.sin(angle) * dist))

        for _ in range(num_points):
            cluster_idx = rng.randint(0, num_clusters - 1)
            center = cluster_centers[cluster_idx]
            color = cluster_colors[cluster_idx % len(cluster_colors)]
            
            # Scatter around the center
            angle = rng.uniform(0, 2 * math.pi)
            dist = rng.gauss(0, self.radius * 0.3)
            pt = Vector2D(center.x + math.cos(angle) * dist, center.y + math.sin(angle) * dist)
            self.points.append((pt, color))

    def draw(self, ctx: Any, time: float = 0.0) -> None:
        ctx.save()
        for pt, color in self.points:
            ctx.set_source_rgba(*color.to_cairo())
            ctx.arc(pt.x, pt.y, self.point_radius, 0, 2 * math.pi)
            ctx.fill()
        ctx.restore()


class CosineSimilarityLink(Node):
    """Glowing dashed connector line between 2 nearest neighbor points with similarity badge."""

    def __init__(
        self,
        p1: Tuple[float, float] = (0.0, 0.0),
        p2: Tuple[float, float] = (100.0, 100.0),
        similarity: float = 0.92,
        color: Color = colors.CYAN,
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)
        self.p1 = Vector2D(p1[0], p1[1])
        self.p2 = Vector2D(p2[0], p2[1])
        self.similarity = similarity
        self.color = color
        self.progress = Signal(1.0)

    def draw(self, ctx: Any, time: float = 0.0) -> None:
        ctx.save()
        
        prog = self.progress.get()
        if prog <= 0:
            ctx.restore()
            return
            
        end_pt = self.p1.lerp(self.p2, prog)
        
        # Draw glowing line
        ctx.set_source_rgba(*self.color.to_cairo())
        ctx.set_line_width(2.0)
        ctx.set_dash([5.0, 5.0], time * 20.0) # Move dashes over time
        ctx.move_to(self.p1.x, self.p1.y)
        ctx.line_to(end_pt.x, end_pt.y)
        ctx.stroke()
        ctx.set_dash([])
        
        # Draw badge
        mid_pt = self.p1.lerp(self.p2, 0.5)
        text = f"sim: {self.similarity:.2f}"
        
        ctx.select_font_face("sans-serif")
        ctx.set_font_size(12)
        extents = ctx.text_extents(text)
        
        padding = 4
        bw = extents.width + padding * 2
        bh = extents.height + padding * 2
        bx = mid_pt.x - bw / 2
        by = mid_pt.y - bh / 2 - extents.height / 2
        
        # Background
        ctx.set_source_rgba(0.1, 0.1, 0.1, 0.8)
        ctx.rectangle(bx, by, bw, bh)
        ctx.fill()
        
        # Text
        ctx.set_source_rgba(*self.color.to_cairo())
        ctx.move_to(bx + padding, by + bh - padding)
        ctx.show_text(text)
        
        ctx.restore()


class VectorDimensionBar(Node):
    """Horizontal bar breakdown of embedding dimension values."""

    def __init__(
        self,
        dimensions: List[float] = None,
        width: float = 300.0,
        height: float = 20.0,
        color_pos: Color = colors.EMERALD_500,
        color_neg: Color = colors.ROSE_500,
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)
        self.dimensions = dimensions or [random.uniform(-1.0, 1.0) for _ in range(16)]
        self.w = float(width)
        self.h = float(height)
        self.color_pos = color_pos
        self.color_neg = color_neg

    def draw(self, ctx: Any, time: float = 0.0) -> None:
        ctx.save()
        num_dims = len(self.dimensions)
        if num_dims == 0:
            ctx.restore()
            return
            
        bar_w = self.w / num_dims
        
        for i, val in enumerate(self.dimensions):
            x = i * bar_w
            
            # Normalize to 0-1 for drawing height
            h_val = abs(val) * self.h
            y = self.h / 2
            
            if val >= 0:
                ctx.set_source_rgba(*self.color_pos.to_cairo())
                ctx.rectangle(x, y - h_val, bar_w - 1, h_val)
            else:
                ctx.set_source_rgba(*self.color_neg.to_cairo())
                ctx.rectangle(x, y, bar_w - 1, h_val)
            ctx.fill()
            
        ctx.restore()


class SearchQueryProbe(Node):
    """Pulsing search query node that ripples into the cluster to highlight closest neighbors."""

    def __init__(
        self,
        radius: float = 8.0,
        color: Color = colors.WHITE,
        ripple_color: Color = colors.CYAN,
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)
        self.radius = radius
        self.color = color
        self.ripple_color = ripple_color
        self.pulse = Signal(0.0)
        
    def trigger_pulse(self):
        # In a real scenario we'd yield an animation here
        self.pulse.set(1.0)

    def draw(self, ctx: Any, time: float = 0.0) -> None:
        ctx.save()
        
        pulse_val = (math.sin(time * 5.0) + 1.0) / 2.0
        
        # Base node
        ctx.set_source_rgba(*self.color.to_cairo())
        ctx.arc(0, 0, self.radius + pulse_val * 2.0, 0, 2 * math.pi)
        ctx.fill()
        
        # Ripple
        ripple_radius = self.radius + (time % 2.0) * 50.0
        ripple_alpha = max(0.0, 1.0 - (time % 2.0) / 2.0)
        
        r, g, b, _ = self.ripple_color.to_cairo()
        ctx.set_source_rgba(r, g, b, ripple_alpha)
        ctx.arc(0, 0, ripple_radius, 0, 2 * math.pi)
        ctx.stroke()
        
        ctx.restore()
