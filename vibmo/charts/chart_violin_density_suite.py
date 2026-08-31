import math
import numpy as np
from scipy.stats import gaussian_kde
from typing import Any, List, Optional, Tuple, Sequence, Union
from vibmo.scene.node import Node
from vibmo.core.vector import Vector2D
from vibmo.core.color import Color, colors
from vibmo.core.signal import Signal, AnimationAction
from vibmo.core.easing import Ease, EasingFunc
from vibmo.timeline.scheduler import ParallelGroup


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
        fill_color: Union[Color, str] = colors.BLUE.with_alpha(0.3),
        line_color: Union[Color, str] = colors.BLUE,
        line_width: float = 2.0,
        **kwargs: Any
    ):
        super().__init__(**kwargs)
        self.data = np.array(data)
        self.width = Signal(float(width), f"{self.name}.width")
        self.height = Signal(float(height), f"{self.name}.height")
        self.fill_color = Signal(Color.from_any(fill_color), f"{self.name}.fill_color")
        self.line_color = Signal(Color.from_any(line_color), f"{self.name}.line_color")
        self.line_width = Signal(float(line_width), f"{self.name}.line_width")
        self.expand_progress = Signal(1.0, f"{self.name}.expand_progress")

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
        w = self.width.get(time)
        h = self.height.get(time)
        fc = self.fill_color.get(time)
        lc = self.line_color.get(time)
        lw = self.line_width.get(time)
        prog = max(0.0, min(1.0, float(self.expand_progress.get(time))))

        if len(self.data) == 0 or prog <= 0.001:
            super().draw(ctx, time)
            return

        val_range = self.scale_max - self.scale_min
        if val_range == 0:
            val_range = 1.0

        half_w = (w / 2) * prog

        ctx.save()

        # Draw path
        ctx.new_path()

        # Right side
        for y_val, density in zip(self.y_samples, self.normalized_densities):
            x = density * half_w
            y = h - ((y_val - self.scale_min) / val_range) * h
            ctx.line_to(x, y)

        # Left side (symmetric)
        for y_val, density in reversed(list(zip(self.y_samples, self.normalized_densities))):
            x = -density * half_w
            y = h - ((y_val - self.scale_min) / val_range) * h
            ctx.line_to(x, y)

        ctx.close_path()

        # Fill
        ctx.set_source_rgba(*fc.to_cairo())
        ctx.fill_preserve()

        # Stroke outline
        ctx.set_line_width(lw)
        ctx.set_source_rgba(*lc.to_cairo())
        ctx.stroke()

        ctx.restore()
        super().draw(ctx, time)


class MedianQuartileMarker(Node):
    """
    Mini box-and-whisker plot superimposed directly inside the violin center.
    """
    def __init__(
        self,
        data: List[float],
        width: float = 12.0,
        height: float = 300.0,
        whisker_width: float = 2.0,
        marker_color: Union[Color, str] = colors.WHITE,
        line_color: Union[Color, str] = colors.SLATE_900,
        **kwargs: Any
    ):
        super().__init__(**kwargs)
        self.data = np.array(data)
        self.width = Signal(float(width))
        self.height = Signal(float(height))
        self.whisker_width = Signal(float(whisker_width))
        self.marker_color = Signal(Color.from_any(marker_color))
        self.line_color = Signal(Color.from_any(line_color))

        self.min_val = np.min(self.data) if len(self.data) > 0 else 0.0
        self.max_val = np.max(self.data) if len(self.data) > 0 else 0.0
        self.q1 = np.percentile(self.data, 25) if len(self.data) > 0 else 0.0
        self.median = np.median(self.data) if len(self.data) > 0 else 0.0
        self.q3 = np.percentile(self.data, 75) if len(self.data) > 0 else 0.0
        self.scale_min = self.min_val
        self.scale_max = self.max_val

    def draw(self, ctx: Any, time: float = 0.0) -> None:
        w = self.width.get(time)
        h = self.height.get(time)
        ww = self.whisker_width.get(time)
        mc = self.marker_color.get(time)
        lc = self.line_color.get(time)

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
        dot_color: Union[Color, str] = colors.SLATE_900.with_alpha(0.5),
        jitter_seed: int = 42,
        **kwargs: Any
    ):
        super().__init__(**kwargs)
        self.data = np.array(data)
        self.width = Signal(float(width))
        self.height = Signal(float(height))
        self.dot_radius = Signal(float(dot_radius))
        self.dot_color = Signal(Color.from_any(dot_color))

        self.min_val = np.min(self.data) if len(self.data) > 0 else 0.0
        self.max_val = np.max(self.data) if len(self.data) > 0 else 0.0
        self.scale_min = self.min_val
        self.scale_max = self.max_val

        rng = np.random.default_rng(jitter_seed)
        self.jitters = rng.uniform(-0.5, 0.5, size=len(self.data))

    def draw(self, ctx: Any, time: float = 0.0) -> None:
        w = self.width.get(time)
        h = self.height.get(time)
        r = self.dot_radius.get(time)
        dc = self.dot_color.get(time)

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
        datasets: Optional[List[List[float]]] = None,
        distributions: Optional[List[List[float]]] = None,
        labels: Optional[List[str]] = None,
        category_spacing: float = 150.0,
        violin_width: float = 100.0,
        height: float = 300.0,
        show_jitter: bool = True,
        fill_colors: Optional[List[Color]] = None,
        **kwargs: Any
    ):
        super().__init__(**kwargs)
        self.datasets = distributions if distributions is not None else (datasets or [])
        self.labels = labels or [f"Cat {i}" for i in range(len(self.datasets))]
        self.category_spacing = Signal(float(category_spacing))
        self.violin_width = Signal(float(violin_width))
        self.height = Signal(float(height))
        self.kde_nodes: List[ProbabilityDensityKernel] = []

        if fill_colors is None:
            self.fill_colors = [colors.BLUE.with_alpha(0.3)] * len(self.datasets)
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
        self.clear()
        self.kde_nodes = []

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
            line_color = color.with_alpha(1.0) if hasattr(color, "with_alpha") else color

            violin_group = Node(name=f"Violin_{i}", position=(x, 0))

            kde_node = ProbabilityDensityKernel(
                data=data, width=vw, height=h, fill_color=color, line_color=line_color
            )
            kde_node.scale_min = self.global_min
            kde_node.scale_max = self.global_max

            if kde_node.kde is not None:
                kde_node.y_samples = np.linspace(self.global_min, self.global_max, 100)
                kde_node.densities = kde_node.kde(kde_node.y_samples)
                if np.max(kde_node.densities) > 0:
                    kde_node.normalized_densities = kde_node.densities / np.max(kde_node.densities)
                else:
                    kde_node.normalized_densities = np.zeros_like(kde_node.densities)
            elif len(data) >= 1 and kde_node.min_val == kde_node.max_val:
                kde_node.y_samples = np.array([kde_node.min_val - 1.0, kde_node.min_val, kde_node.max_val + 1.0])
                kde_node.densities = np.array([0.0, 1.0, 0.0])
                kde_node.normalized_densities = np.array([0.0, 1.0, 0.0])

            box_node = MedianQuartileMarker(data=data, height=h)
            box_node.scale_min = self.global_min
            box_node.scale_max = self.global_max

            violin_group.add(kde_node)
            self.kde_nodes.append(kde_node)

            if show_jitter:
                jitter_node = OutlierJitterDots(data=data, width=vw * 0.6, height=h)
                jitter_node.scale_min = self.global_min
                jitter_node.scale_max = self.global_max
                violin_group.add(jitter_node)

            violin_group.add(box_node)
            self.add(violin_group)

    def expand_kde(
        self,
        duration: float = 1.2,
        delay: float = 0.0,
        stagger: float = 0.05,
        ease: Optional[EasingFunc] = None
    ) -> ParallelGroup:
        """Animates KDE density curves blooming outwards with spring physics."""
        e = ease or Ease.out_back
        actions = []
        for i, kde_node in enumerate(self.kde_nodes):
            kde_node.expand_progress.set(0.0)
            actions.append(kde_node.expand_progress.to(1.0, duration=duration, delay=delay + i * stagger, ease=e))
        return ParallelGroup(actions)

    def draw(self, ctx: Any, time: float = 0.0) -> None:
        super().draw(ctx, time)


ViolinDensityPlot = ViolinDistributionPlot
KdeEnvelopeCurve = ProbabilityDensityKernel
