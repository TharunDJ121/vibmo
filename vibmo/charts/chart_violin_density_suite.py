import math
import numpy as np
from scipy.stats import gaussian_kde
from typing import Any, List, Optional, Tuple, Sequence
from vibmo.scene.node import Node
from vibmo.core.vector import Vector2D
from vibmo.core.color import Color, colors
from vibmo.core.signal import Signal


class ProbabilityDensityKernel(Node):
    """
    Smooth outline curve representing continuous probability distribution.
    It calculates a KDE for the given data and renders a symmetrical polygon.
    """
    def __init__(
        self,
        data: List[float],
        width: float = 100.0,
        height: float = 300.0,
        fill_color: Color = colors.BLUE.with_alpha(0.3),
        line_color: Color = colors.BLUE,
        line_width: float = 2.0,
        **kwargs: Any
    ):
        super().__init__(**kwargs)
        self.data = np.array(data)
        self.width = Signal(width)
        self.height = Signal(height)
        self.fill_color = Signal(fill_color)
        self.line_color = Signal(line_color)
        self.line_width = Signal(line_width)

        # Precompute KDE and normalized coordinates
        if len(self.data) < 2:
            self.min_val = np.min(self.data) if len(self.data) > 0 else 0.0
            self.max_val = np.max(self.data) if len(self.data) > 0 else 0.0
            self.y_samples = np.array([self.min_val, self.max_val])
            self.densities = np.zeros(2)
            self.normalized_densities = np.zeros(2)
            self.kde = None
        else:
            self.min_val = np.min(self.data)
            self.max_val = np.max(self.data)

            # Handle zero variance case
            if self.min_val == self.max_val:
                self.y_samples = np.array([self.min_val - 1.0, self.min_val, self.max_val + 1.0])
                self.densities = np.array([0.0, 1.0, 0.0])
                self.normalized_densities = np.array([0.0, 1.0, 0.0])
                self.kde = None
            else:
                self.kde = gaussian_kde(self.data)

                # Sample points along the y-axis (representing values)
                self.y_samples = np.linspace(self.min_val, self.max_val, 100)
                self.densities = self.kde(self.y_samples)

                # Normalize densities
                self.max_density = np.max(self.densities)
                if self.max_density > 0:
                    self.normalized_densities = self.densities / self.max_density
                else:
                    self.normalized_densities = np.zeros_like(self.densities)

        self.scale_min = self.min_val
        self.scale_max = self.max_val

    def draw(self, ctx: Any, time: float = 0.0) -> None:
        w = self.width.get()
        h = self.height.get()
        fc = self.fill_color.get()
        lc = self.line_color.get()
        lw = self.line_width.get()

        if len(self.data) == 0:
            return

        val_range = self.scale_max - self.scale_min
        if val_range == 0:
            val_range = 1.0

        half_w = w / 2

        ctx.save()

        # Draw path
        ctx.new_path()

        # Right side
        for y_val, density in zip(self.y_samples, self.normalized_densities):
            x = density * half_w
            # Map y_val to height, min is at bottom, max is at top
            y = h - ((y_val - self.scale_min) / val_range) * h
            ctx.line_to(x, y)

        # Left side (symmetric)
        for y_val, density in reversed(list(zip(self.y_samples, self.normalized_densities))):
            x = -density * half_w
            y = h - ((y_val - self.scale_min) / val_range) * h
            ctx.line_to(x, y)

        ctx.close_path()

        if fc.a > 0:
            ctx.set_source_rgba(*fc.to_cairo())
            ctx.fill_preserve()

        if lw > 0:
            ctx.set_line_width(lw)
            ctx.set_source_rgba(*lc.to_cairo())
            ctx.stroke()
        else:
            ctx.new_path()

        ctx.restore()

        super().draw(ctx, time)


class MedianQuartileMarker(Node):
    """
    Inner box plot core showing median white dot, interquartile thick bar, and min/max whiskers.
    """
    def __init__(
        self,
        data: List[float],
        width: float = 10.0,
        height: float = 300.0,
        whisker_width: float = 2.0,
        marker_color: Color = colors.WHITE,
        line_color: Color = colors.SLATE_900.with_alpha(0.8),
        **kwargs: Any
    ):
        super().__init__(**kwargs)
        self.data = np.array(data)
        self.width = Signal(width)
        self.height = Signal(height)
        self.whisker_width = Signal(whisker_width)
        self.marker_color = Signal(marker_color)
        self.line_color = Signal(line_color)

        self.min_val = np.min(self.data) if len(self.data) > 0 else 0.0
        self.max_val = np.max(self.data) if len(self.data) > 0 else 0.0
        self.q1 = np.percentile(self.data, 25) if len(self.data) > 0 else 0.0
        self.median = np.median(self.data) if len(self.data) > 0 else 0.0
        self.q3 = np.percentile(self.data, 75) if len(self.data) > 0 else 0.0
        self.scale_min = self.min_val
        self.scale_max = self.max_val

    def draw(self, ctx: Any, time: float = 0.0) -> None:
        w = self.width.get()
        h = self.height.get()
        ww = self.whisker_width.get()
        mc = self.marker_color.get()
        lc = self.line_color.get()

        if len(self.data) == 0:
            return

        val_range = self.scale_max - self.scale_min
        if val_range == 0:
            val_range = 1.0

        def get_y(val: float) -> float:
            return h - ((val - self.scale_min) / val_range) * h

        y_min = get_y(self.min_val)
        y_max = get_y(self.max_val)
        y_q1 = get_y(self.q1)
        y_median = get_y(self.median)
        y_q3 = get_y(self.q3)

        ctx.save()

        ctx.set_line_width(ww)
        ctx.set_source_rgba(*lc.to_cairo())

        # Draw whiskers
        ctx.new_path()
        ctx.move_to(0, y_min)
        ctx.line_to(0, y_q1)
        ctx.stroke()

        ctx.new_path()
        ctx.move_to(0, y_q3)
        ctx.line_to(0, y_max)
        ctx.stroke()

        # Draw IQR bar
        ctx.set_line_width(w)
        ctx.new_path()
        ctx.move_to(0, y_q1)
        ctx.line_to(0, y_q3)
        ctx.stroke()

        # Draw median dot
        ctx.set_source_rgba(*mc.to_cairo())
        ctx.new_path()
        ctx.arc(0, y_median, w / 2, 0, 2 * math.pi)
        ctx.fill()

        ctx.restore()

        super().draw(ctx, time)


class OutlierJitterDots(Node):
    """
    Individual jittered data points plotted alongside the density curve.
    """
    def __init__(
        self,
        data: List[float],
        width: float = 60.0,
        height: float = 300.0,
        dot_radius: float = 2.0,
        dot_color: Color = colors.SLATE_900.with_alpha(0.5),
        jitter_seed: int = 42,
        **kwargs: Any
    ):
        super().__init__(**kwargs)
        self.data = np.array(data)
        self.width = Signal(width)
        self.height = Signal(height)
        self.dot_radius = Signal(dot_radius)
        self.dot_color = Signal(dot_color)

        self.min_val = np.min(self.data) if len(self.data) > 0 else 0.0
        self.max_val = np.max(self.data) if len(self.data) > 0 else 0.0
        self.scale_min = self.min_val
        self.scale_max = self.max_val

        # Deterministic jittering
        rng = np.random.default_rng(jitter_seed)
        self.jitters = rng.uniform(-0.5, 0.5, size=len(self.data))

    def draw(self, ctx: Any, time: float = 0.0) -> None:
        w = self.width.get()
        h = self.height.get()
        r = self.dot_radius.get()
        dc = self.dot_color.get()

        if len(self.data) == 0:
            return

        val_range = self.scale_max - self.scale_min
        if val_range == 0:
            val_range = 1.0

        ctx.save()
        ctx.set_source_rgba(*dc.to_cairo())

        for val, jitter in zip(self.data, self.jitters):
            x = jitter * w
            y = h - ((val - self.scale_min) / val_range) * h

            ctx.new_path()
            ctx.arc(x, y, r, 0, 2 * math.pi)
            ctx.fill()

        ctx.restore()

        super().draw(ctx, time)


class ViolinDistributionPlot(Node):
    """
    Symmetrical vertical kernel density estimation (KDE) curve visualizer across multiple categories.
    Composes ProbabilityDensityKernel, MedianQuartileMarker, and OutlierJitterDots.
    """
    def __init__(
        self,
        datasets: List[List[float]],
        labels: Optional[List[str]] = None,
        category_spacing: float = 150.0,
        violin_width: float = 100.0,
        height: float = 300.0,
        show_jitter: bool = True,
        fill_colors: Optional[List[Color]] = None,
        **kwargs: Any
    ):
        super().__init__(**kwargs)
        self.datasets = datasets
        self.labels = labels or [f"Cat {i}" for i in range(len(datasets))]
        self.category_spacing = Signal(category_spacing)
        self.violin_width = Signal(violin_width)
        self.height = Signal(height)

        if fill_colors is None:
            self.fill_colors = [colors.BLUE.with_alpha(0.3)] * len(datasets)
        else:
            self.fill_colors = fill_colors

        # Global min and max for consistent y-scale across all violins
        all_data = np.concatenate(self.datasets) if any(len(d) > 0 for d in self.datasets) else np.array([])
        if len(all_data) > 0:
            self.global_min = np.min(all_data)
            self.global_max = np.max(all_data)
        else:
            self.global_min = 0.0
            self.global_max = 1.0

        self._build_violins(show_jitter)

    def _build_violins(self, show_jitter: bool) -> None:
        spacing = self.category_spacing.get()
        vw = self.violin_width.get()
        h = self.height.get()

        total_width = (len(self.datasets) - 1) * spacing
        start_x = -total_width / 2

        for i, data in enumerate(self.datasets):
            if len(data) == 0:
                continue

            x = start_x + i * spacing
            color = self.fill_colors[i % len(self.fill_colors)]
            line_color = color.with_alpha(1.0)

            # Create a group node for this violin to center it at x
            violin_group = Node(name=f"Violin_{i}", position=(x, 0))

            # The children need to be initialized with data and they scale to their own data's min/max.
            # To have consistent scaling across all violins, we should ideally adjust their calculation,
            # or just let them scale their own min/max but pass global bounds?
            # A simple trick is to inject min/max after initialization.

            kde_node = ProbabilityDensityKernel(
                data=data, width=vw, height=h, fill_color=color, line_color=line_color
            )
            kde_node.scale_min = self.global_min
            kde_node.scale_max = self.global_max
            # Recompute y_samples with global bounds for consistency if needed,
            # though KDE is built on its own data, which is fine, we just want y mapped to global scale.
            if kde_node.kde is not None:
                kde_node.y_samples = np.linspace(self.global_min, self.global_max, 100)
                kde_node.densities = kde_node.kde(kde_node.y_samples)
                if np.max(kde_node.densities) > 0:
                    kde_node.normalized_densities = kde_node.densities / np.max(kde_node.densities)
                else:
                    kde_node.normalized_densities = np.zeros_like(kde_node.densities)
            elif len(data) >= 1 and kde_node.min_val == kde_node.max_val:
                # Retain the spike for zero-variance data, mapped to new global space
                kde_node.y_samples = np.array([kde_node.min_val - 1.0, kde_node.min_val, kde_node.max_val + 1.0])
                kde_node.densities = np.array([0.0, 1.0, 0.0])
                kde_node.normalized_densities = np.array([0.0, 1.0, 0.0])

            box_node = MedianQuartileMarker(data=data, height=h)
            box_node.scale_min = self.global_min
            box_node.scale_max = self.global_max

            violin_group.add(kde_node)

            if show_jitter:
                jitter_node = OutlierJitterDots(data=data, width=vw * 0.6, height=h)
                jitter_node.scale_min = self.global_min
                jitter_node.scale_max = self.global_max
                violin_group.add(jitter_node)

            violin_group.add(box_node)

            self.add(violin_group)

    def draw(self, ctx: Any, time: float = 0.0) -> None:
        # Note: We let children draw themselves via super().draw()
        super().draw(ctx, time)
