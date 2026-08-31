"""
Vector Embeddings & Semantic Search UI Suite for Vibmo / Motio.
Components:
- VectorEmbeddingsVisualizer
- ClusterPoint
- EmbeddingScatterCluster
- CosineSimilarityLink
- VectorDimensionBar
- SearchQueryProbe
"""

from __future__ import annotations
import math
import random
from typing import Any, Dict, List, Optional, Sequence, Tuple, Union
import cairo

from vibmo.core.color import Color, colors
from vibmo.core.vector import Vector2D
from vibmo.core.signal import Signal, AnimationAction
from vibmo.core.easing import Ease, EasingFunc
from vibmo.scene.node import Node
from vibmo.spatial.shadows import DropShadow


class ClusterPoint:
    """Dataclass / state container for a single embedding point in 3D/2D space."""

    def __init__(
        self,
        x: float,
        y: float,
        z: float = 0.0,
        cluster_id: int = 0,
        color: Optional[Color] = None,
        radius: float = 4.0,
        label: str = "",
    ) -> None:
        self.x = float(x)
        self.y = float(y)
        self.z = float(z)
        self.cluster_id = cluster_id
        self.color = color or colors.CYAN
        self.radius = float(radius)
        self.label = label


class EmbeddingScatterCluster(Node):
    """Clustered point cloud of high-dimensional semantic vectors projected to 2D/3D."""

    def __init__(
        self,
        num_points: int = 100,
        num_clusters: int = 3,
        radius: float = 160.0,
        seed: int = 42,
        point_radius: float = 3.5,
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)
        self.num_points = num_points
        self.num_clusters = num_clusters
        self.radius = radius
        self.point_radius = point_radius

        rng = random.Random(seed)
        self.points: List[ClusterPoint] = []
        cluster_colors = [colors.CYAN, colors.ROSE_500, colors.EMERALD, colors.AMBER, colors.VIOLET]

        centers = []
        for i in range(num_clusters):
            angle = (i / num_clusters) * 2.0 * math.pi
            dist = self.radius * 0.55
            centers.append((math.cos(angle) * dist, math.sin(angle) * dist, rng.uniform(-40, 40)))

        for i in range(num_points):
            c_idx = i % num_clusters
            cx, cy, cz = centers[c_idx]
            col = cluster_colors[c_idx % len(cluster_colors)]
            px = cx + rng.gauss(0, self.radius * 0.22)
            py = cy + rng.gauss(0, self.radius * 0.22)
            pz = cz + rng.gauss(0, self.radius * 0.22)
            self.points.append(ClusterPoint(px, py, pz, cluster_id=c_idx, color=col, radius=point_radius))

    def draw(self, ctx: Any, time: float = 0.0) -> None:
        ctx.save()
        for pt in self.points:
            ctx.set_source_rgba(*pt.color.to_cairo())
            ctx.arc(pt.x, pt.y, pt.radius, 0, 2 * math.pi)
            ctx.fill()
        ctx.restore()


class CosineSimilarityLink(Node):
    """Glowing dashed connector line between 2 nearest neighbor points with similarity badge."""

    def __init__(
        self,
        p1: Tuple[float, float] = (-60.0, -40.0),
        p2: Tuple[float, float] = (80.0, 50.0),
        similarity: float = 0.94,
        color: Union[Color, str] = colors.CYAN,
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)
        self.p1 = p1
        self.p2 = p2
        self.similarity = similarity
        self.color = Color.from_any(color)
        self.progress = Signal(1.0, f"{self.name}.progress")

    def draw(self, ctx: Any, time: float = 0.0) -> None:
        prog = max(0.0, min(1.0, self.progress.get(time)))
        if prog <= 0.0:
            return

        ctx.save()
        x1, y1 = self.p1
        x2, y2 = self.p2
        curr_x = x1 + (x2 - x1) * prog
        curr_y = y1 + (y2 - y1) * prog

        ctx.set_source_rgba(*self.color.to_cairo())
        ctx.set_line_width(1.5)
        ctx.set_dash([6.0, 4.0], time * 20.0)
        ctx.move_to(x1, y1)
        ctx.line_to(curr_x, curr_y)
        ctx.stroke()
        ctx.set_dash([])

        # Badge at midpoint
        if prog > 0.5:
            mx = (x1 + x2) * 0.5
            my = (y1 + y2) * 0.5
            ctx.select_font_face("Inter", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
            ctx.set_font_size(10.0)
            text = f"cos(θ) = {self.similarity:.2f}"
            ext = ctx.text_extents(text)

            bw = ext.width + 12.0
            bh = ext.height + 8.0
            ctx.set_source_rgba(0.06, 0.1, 0.16, 0.9)
            ctx.rectangle(mx - bw * 0.5, my - bh * 0.5, bw, bh)
            ctx.fill()

            ctx.set_source_rgba(*self.color.to_cairo())
            ctx.set_line_width(1.0)
            ctx.rectangle(mx - bw * 0.5, my - bh * 0.5, bw, bh)
            ctx.stroke()

            ctx.move_to(mx - ext.width * 0.5, my + ext.height * 0.35)
            ctx.show_text(text)

        ctx.restore()


class VectorDimensionBar(Node):
    """Horizontal bar breakdown of embedding dimension values."""

    def __init__(
        self,
        dimensions: Optional[List[float]] = None,
        width: float = 240.0,
        height: float = 24.0,
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)
        self.dimensions = dimensions or [0.4, -0.8, 0.9, 0.1, -0.5, 0.7, -0.3, 0.6, -0.9, 0.3, 0.8, -0.2]
        self.width_val = float(width)
        self.height_val = float(height)

    def draw(self, ctx: Any, time: float = 0.0) -> None:
        w, h = self.width_val, self.height_val
        n = len(self.dimensions)
        if n == 0:
            return

        ctx.save()
        bar_w = w / n
        for i, val in enumerate(self.dimensions):
            x = i * bar_w
            bar_h = abs(val) * (h * 0.5)
            if val >= 0:
                ctx.set_source_rgba(0.1, 0.85, 0.5, 0.9)
                ctx.rectangle(x + 1.0, h * 0.5 - bar_h, bar_w - 2.0, bar_h)
            else:
                ctx.set_source_rgba(0.9, 0.25, 0.35, 0.9)
                ctx.rectangle(x + 1.0, h * 0.5, bar_w - 2.0, bar_h)
            ctx.fill()
        ctx.restore()


class SearchQueryProbe(Node):
    """Pulsing search query node that ripples into the cluster to highlight closest neighbors."""

    def __init__(self, radius: float = 6.0, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.radius = radius
        self.pulse = Signal(1.0, f"{self.name}.pulse")

    def draw(self, ctx: Any, time: float = 0.0) -> None:
        ctx.save()
        # Ripple rings
        for i in range(2):
            wave = (time * 1.5 + i * 0.5) % 1.0
            r = self.radius + wave * 30.0
            alpha = max(0.0, 1.0 - wave)
            ctx.set_source_rgba(0.2, 0.8, 1.0, alpha * 0.5)
            ctx.set_line_width(1.5)
            ctx.arc(0, 0, r, 0, 2 * math.pi)
            ctx.stroke()

        # Core probe
        ctx.set_source_rgba(1.0, 1.0, 1.0, 0.95)
        ctx.arc(0, 0, self.radius, 0, 2 * math.pi)
        ctx.fill()
        ctx.restore()


class VectorEmbeddingsVisualizer(Node):
    """
    Vector Embeddings & Semantic Space Suite.
    Visualizes high-dimensional vector clusters in 3D projection, cosine distance links,
    dimension bar charts, and semantic query probes.
    """

    def __init__(
        self,
        dimension: int = 3,
        num_points: int = 90,
        num_clusters: int = 3,
        radius: float = 160.0,
        width: float = 680.0,
        height: float = 500.0,
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)
        self.dimension = dimension
        self.width_val = float(width)
        self.height_val = float(height)
        self.radius = float(radius)
        self.shadow = DropShadow(color=Color(0.0, 0.0, 0.0, 0.5), blur=32.0, offset=(0.0, 16.0))

        # 3D Rotation signals
        self.rot_y = Signal(0.0, f"{self.name}.rot_y")
        self.rot_x = Signal(0.3, f"{self.name}.rot_x")

        # Cluster points
        rng = random.Random(42)
        self.points: List[ClusterPoint] = []
        cluster_colors = [colors.CYAN, colors.ROSE_500, colors.EMERALD, colors.AMBER]
        centers = [(-70.0, -30.0, 20.0), (60.0, 50.0, -30.0), (10.0, -80.0, -10.0)]

        for i in range(num_points):
            c_idx = i % num_clusters
            cx, cy, cz = centers[c_idx]
            col = cluster_colors[c_idx % len(cluster_colors)]
            px = cx + rng.gauss(0, radius * 0.2)
            py = cy + rng.gauss(0, radius * 0.2)
            pz = cz + rng.gauss(0, radius * 0.2)
            self.points.append(ClusterPoint(px, py, pz, cluster_id=c_idx, color=col, radius=3.5))

        # Similarity link
        self.sim_link = CosineSimilarityLink(p1=(-70.0, -30.0), p2=(60.0, 50.0), similarity=0.94)

        # Dimension Bar Breakdown
        self.dim_bar = VectorDimensionBar(width=200.0, height=22.0)
        self.dim_bar.position.set(Vector2D(self.width_val - 230.0, self.height_val - 45.0))
        self.add(self.dim_bar)

        # Search Query Probe
        self.probe = SearchQueryProbe()
        self.probe.position.set(Vector2D(self.width_val * 0.5 - 20.0, self.height_val * 0.5 - 10.0))
        self.add(self.probe)

    def rotate_cluster(
        self,
        angle: float = 360.0,
        duration: float = 3.0,
        ease: EasingFunc = Ease.in_out_cubic,
    ) -> AnimationAction:
        """
        Fluent generator animation verb to smoothly rotate the 3D embedding cluster.
        """
        rad = math.radians(angle)
        return self.rot_y.to(self.rot_y.get(0.0) + rad, duration=duration, ease=ease)

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
        ctx.set_source_rgba(0.18, 0.25, 0.38, 0.8)
        ctx.set_line_width(1.5)
        ctx.stroke()

        # Header Title & Metadata
        ctx.select_font_face("Inter", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
        ctx.set_font_size(14.0)
        ctx.set_source_rgba(0.9, 0.95, 1.0, 0.9)
        ctx.move_to(24.0, 36.0)
        ctx.show_text("Vector Embeddings Space (PCA / t-SNE 3D)")

        # Center cluster projection
        cx = w * 0.5
        cy = h * 0.5 + 10.0
        ry = self.rot_y.get(time)
        rx = self.rot_x.get(time)
        cos_y, sin_y = math.cos(ry), math.sin(ry)
        cos_x, sin_x = math.cos(rx), math.sin(rx)

        # Draw grid sphere / axis rings
        ctx.save()
        ctx.translate(cx, cy)
        ctx.set_source_rgba(0.15, 0.22, 0.35, 0.3)
        ctx.set_line_width(1.0)
        ctx.arc(0, 0, self.radius * 0.9, 0, 2 * math.pi)
        ctx.stroke()
        ctx.restore()

        # Project 3D points
        projected = []
        for pt in self.points:
            # Y-axis rotation
            x1 = pt.x * cos_y + pt.z * sin_y
            z1 = -pt.x * sin_y + pt.z * cos_y
            # X-axis rotation
            y2 = pt.y * cos_x - z1 * sin_x
            z2 = pt.y * sin_x + z1 * cos_x

            # Perspective scale
            scale = 300.0 / (300.0 + z2)
            screen_x = cx + x1 * scale
            screen_y = cy + y2 * scale
            projected.append((z2, screen_x, screen_y, pt.color, pt.radius * scale))

        # Sort back to front (Painter's algorithm)
        projected.sort(key=lambda item: item[0], reverse=True)

        for z, px, py, col, pr in projected:
            ctx.set_source_rgba(*col.to_cairo())
            ctx.arc(px, py, pr, 0, 2 * math.pi)
            ctx.fill()

        # Draw subcomponents (dimension bar, probe, etc.)
        super().draw(ctx, time)
        ctx.restore()
