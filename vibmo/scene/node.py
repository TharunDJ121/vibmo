"""
Scene Graph Node Hierarchy, Transform propagation, Hit-testing, and Motion Verbs.
"""

from __future__ import annotations
import math
import uuid
from typing import Any, Callable, List, Literal, Optional, Sequence, Tuple, Union
from vibmo.core.vector import Vector2D
from vibmo.core.matrix import Matrix3x3
from vibmo.core.color import Color, colors
from vibmo.core.signal import Signal, AnimationAction
from vibmo.core.easing import Ease, EasingFunc


class _FloatBinding:
    def __init__(self, base_pos: Any, amplitude: float, speed: float):
        self.base_pos = Vector2D.from_any(base_pos)
        self.amplitude = amplitude
        self.speed = speed

    def __call__(self, t: float) -> Vector2D:
        offset_y = math.sin(t * math.pi * self.speed) * self.amplitude
        return Vector2D(self.base_pos.x, self.base_pos.y + offset_y)


class _BeatScaleBinding:
    def __init__(self, base_scale: Any, analyzer: Any, band: str, amplitude: float):
        self.base_scale = Vector2D.from_any(base_scale)
        self.analyzer = analyzer
        self.band = band
        self.amplitude = amplitude

    def __call__(self, t: float) -> Vector2D:
        if self.band == "bass":
            val = self.analyzer.bass(t)
        elif self.band == "mid":
            val = self.analyzer.mid(t)
        elif self.band == "treble":
            val = self.analyzer.treble(t)
        else:
            val = self.analyzer.rms(t)
            
        scale_fac = 1.0 + (val * (self.amplitude - 1.0))
        return Vector2D(self.base_scale.x * scale_fac, self.base_scale.y * scale_fac)


class Node:
    """Base class for all visual and structural elements in the Vibmo Scene Graph."""

    def __init__(
        self,
        name: str = "",
        position: Union[Vector2D, Sequence[float], float] = (0.0, 0.0),
        scale: Union[Vector2D, Sequence[float], float] = (1.0, 1.0),
        rotation: float = 0.0,
        rotate_x: float = 0.0,
        rotate_y: float = 0.0,
        z: float = 0.0,
        anchor: Union[Vector2D, Sequence[float], float] = (0.0, 0.0),
        opacity: float = 1.0,
        skew: Union[Vector2D, Sequence[float], float] = (0.0, 0.0),
        visible: bool = True,
        z_index: int = 0,
        **kwargs: Any,
    ) -> None:
        self.id = str(uuid.uuid4())[:8]
        self.name = name or f"{self.__class__.__name__}_{self.id}"
        self.parent: Optional[Node] = None
        self.children: List[Node] = []
        for k, v in kwargs.items():
            setattr(self, k, v)

        # Animatable Signals
        self.position = Signal(Vector2D.from_any(position), f"{self.name}.position")
        self.z = Signal(float(z), f"{self.name}.z")
        self.scale = Signal(Vector2D.from_any(scale), f"{self.name}.scale")
        self.rotation = Signal(float(rotation), f"{self.name}.rotation")  # in radians, Z-axis
        self.rotate_z = self.rotation
        self.rotate_x = Signal(float(rotate_x), f"{self.name}.rotate_x")
        self.rotate_y = Signal(float(rotate_y), f"{self.name}.rotate_y")

        self.anchor = Signal(Vector2D.from_any(anchor), f"{self.name}.anchor")
        self.opacity = Signal(float(opacity), f"{self.name}.opacity")
        self.skew = Signal(Vector2D.from_any(skew), f"{self.name}.skew")

        self.visible = visible
        self.z_index = z_index
        self.in_point = 0.0
        self.out_point: Optional[float] = None
        self.clip_path: Optional[Node] = None
        self.mask: Optional[Any] = None
        self.blend_mode: str = "normal"
        self.backdrop_filter: Optional[Any] = None
        self.filters: List[Any] = []
        self.constraints: List[Any] = []

    def add_constraint(self, constraint: Any) -> Node:
        """Attaches a transform constraint (LookAt, Follow, Path) to this node."""
        self.constraints.append(constraint)
        return self

    def apply_constraints(self, time: float) -> None:
        """Evaluates all attached rigging constraints at timestamp t."""
        for c in self.constraints:
            c.apply(self, time)

    def set_mask(
        self,
        shape: Any,
        mode: str = "add",
        invert: bool = False,
        feather: float = 0.0,
        opacity: float = 1.0,
    ) -> Node:

        """Applies a vector or layer mask with optional edge feathering and inversion."""
        from vibmo.compositing.mask import Mask
        self.mask = Mask(shape=shape, mode=mode, invert=invert, feather=feather, opacity=opacity)
        return self

    def set_blend_mode(self, mode: Union[str, Any]) -> Node:
        """Sets the compositing blend mode (e.g. 'multiply', 'screen', 'overlay', 'add')."""
        self.blend_mode = mode.value if hasattr(mode, "value") else str(mode).lower()
        return self

    def trim(self, in_point: float = 0.0, out_point: Optional[float] = None) -> Node:
        """Sets explicit NLE in-point and out-point timeline boundaries for this layer."""
        self.in_point = float(in_point)
        self.out_point = float(out_point) if out_point is not None else None
        return self


    def at(self, x: float, y: float) -> Node:
        """Fluent helper: Sets node position coordinates directly and returns self."""
        self.position.set(Vector2D(float(x), float(y)))
        return self

    def align(
        self,
        alignment: Literal["center", "top_left", "top_center", "top_right", "bottom_left", "bottom_center", "bottom_right"] = "center",
        canvas_size: Tuple[float, float] = (1920.0, 1080.0),
    ) -> Node:
        """Fluent helper: Centers or aligns the node relative to the canvas and returns self."""
        cw, ch = canvas_size
        bx, by, bw, bh = self.local_bounds(0.0)
        bw = max(10.0, bw)
        bh = max(10.0, bh)

        align_str = alignment.value if hasattr(alignment, "value") else str(alignment).lower()

        if align_str == "center":
            self.position.set(Vector2D((cw - bw) * 0.5, (ch - bh) * 0.5))
        elif align_str == "top_left":
            self.position.set(Vector2D(40.0, 40.0))
        elif align_str == "top_center":
            self.position.set(Vector2D((cw - bw) * 0.5, 40.0))
        elif align_str == "top_right":
            self.position.set(Vector2D(cw - bw - 40.0, 40.0))
        elif align_str == "bottom_left":
            self.position.set(Vector2D(40.0, ch - bh - 40.0))
        elif align_str == "bottom_center":
            self.position.set(Vector2D((cw - bw) * 0.5, ch - bh - 40.0))
        elif align_str == "bottom_right":
            self.position.set(Vector2D(cw - bw - 40.0, ch - bh - 40.0))
        return self


    def scale_to(self, s: float) -> Node:
        """Fluent helper: Sets uniform scale and returns self."""
        self.scale.set(Vector2D(float(s), float(s)))
        return self

    def opacity_to(self, op: float) -> Node:
        """Fluent helper: Sets opacity and returns self."""
        self.opacity.set(float(op))
        return self

    # Hierarchy Management
    def add(self, *nodes: Node) -> Node:
        for node in nodes:
            if node.parent is not None:
                node.parent.remove(node)
            node.parent = self
            self.children.append(node)
        return self

    def remove(self, node: Node) -> None:
        if node in self.children:
            self.children.remove(node)
            node.parent = None

    def clear(self) -> None:
        for child in self.children:
            child.parent = None
        self.children.clear()

    # Spatial Transform & Bounds
    def local_matrix(self, time: float = 0.0) -> Matrix3x3:
        return Matrix3x3.compose(
            position=self.position.get(time),
            scale=self.scale.get(time),
            rotation_rad=self.rotation.get(time),
            rotate_x_rad=self.rotate_x.get(time),
            rotate_y_rad=self.rotate_y.get(time),
            anchor=self.anchor.get(time),
            skew_rad=self.skew.get(time),
        )

    def world_matrix(self, time: float = 0.0) -> Matrix3x3:
        mat = self.local_matrix(time)
        curr = self.parent
        while curr is not None:
            mat = curr.local_matrix(time).multiply(mat)
            curr = curr.parent
        return mat

    def world_opacity(self, time: float = 0.0) -> float:
        if time < self.in_point or (self.out_point is not None and time > self.out_point):
            return 0.0
        op = max(0.0, min(1.0, self.opacity.get(time)))
        curr = self.parent
        while curr is not None:
            if time < curr.in_point or (curr.out_point is not None and time > curr.out_point):
                return 0.0
            op *= max(0.0, min(1.0, curr.opacity.get(time)))
            curr = curr.parent
        return op

    def local_bounds(self, time: float = 0.0) -> Tuple[float, float, float, float]:
        """Returns (x, y, width, height) in local coordinate space."""
        return (0.0, 0.0, 0.0, 0.0)

    def world_bounds(self, time: float = 0.0) -> Tuple[float, float, float, float]:
        """Calculates axis-aligned bounding box in world canvas space."""
        lx, ly, lw, lh = self.local_bounds(time)
        if lw <= 0 and lh <= 0 and self.children:
            # Aggregate children bounds
            min_x, min_y, max_x, max_y = float("inf"), float("inf"), float("-inf"), float("-inf")
            for c in self.children:
                cx, cy, cw, ch = c.world_bounds(time)
                min_x = min(min_x, cx)
                min_y = min(min_y, cy)
                max_x = max(max_x, cx + cw)
                max_y = max(max_y, cy + ch)
            if min_x != float("inf"):
                return (min_x, min_y, max_x - min_x, max_y - min_y)

        mat = self.world_matrix(time)
        corners = [
            mat.transform_point((lx, ly)),
            mat.transform_point((lx + lw, ly)),
            mat.transform_point((lx + lw, ly + lh)),
            mat.transform_point((lx, ly + lh)),
        ]
        xs = [p.x for p in corners]
        ys = [p.y for p in corners]
        min_x, max_x = min(xs), max(xs)
        min_y, max_y = min(ys), max(ys)
        return (min_x, min_y, max_x - min_x, max_y - min_y)

    def hit_test(self, world_x: float, world_y: float, time: float = 0.0) -> Optional[Node]:
        """Hit test against node and its children for interactive canvas selection."""
        if not self.visible or self.world_opacity(time) <= 0.01:
            return None

        # Check children in reverse z/rendering order (topmost first)
        for child in reversed(self.children):
            hit = child.hit_test(world_x, world_y, time)
            if hit is not None:
                return hit

        # Test self
        inv_mat = self.world_matrix(time).inverse()
        local_pt = inv_mat.transform_point((world_x, world_y))
        lx, ly, lw, lh = self.local_bounds(time)
        if lx <= local_pt.x <= lx + lw and ly <= local_pt.y <= ly + lh:
            return self
        return None

    # Custom Draw Hook
    def draw(self, ctx: Any, time: float = 0.0) -> None:
        """Override in subclasses to perform vector rasterization."""
        pass

    # ==========================================
    # VIBE MOTION VERBS
    # ==========================================

    def pop_in(
        self,
        delay: float = 0.0,
        duration: float = 0.7,
        scale_from: float = 0.6,
        ease: Optional[EasingFunc] = None,
    ) -> Any:
        """Pops the node in using natural spring physics and opacity fade."""
        spring_ease = ease or Ease.spring(stiffness=140, damping=13)
        self.scale.set(Vector2D(scale_from, scale_from))
        self.opacity.set(0.0)
        from vibmo.timeline.scheduler import ParallelGroup
        return ParallelGroup([
            self.scale.to(Vector2D(1.0, 1.0), duration=duration, ease=spring_ease, delay=delay),
            self.opacity.to(1.0, duration=duration * 0.5, ease=Ease.out_quad, delay=delay),
        ])

    def fade_up(
        self,
        offset: float = 30.0,
        duration: float = 0.6,
        delay: float = 0.0,
        ease: Optional[EasingFunc] = None,
    ) -> Any:
        """Slides the node up from an offset with smooth deceleration."""
        e = ease or Ease.out_cubic
        curr_pos = self.position.get()
        self.position.set(Vector2D(curr_pos.x, curr_pos.y + offset))
        self.opacity.set(0.0)
        from vibmo.timeline.scheduler import ParallelGroup
        return ParallelGroup([
            self.position.to(curr_pos, duration=duration, ease=e, delay=delay),
            self.opacity.to(1.0, duration=duration * 0.8, ease=Ease.out_quad, delay=delay),
        ])

    def fade_in(
        self,
        duration: float = 0.5,
        delay: float = 0.0,
        ease: Optional[EasingFunc] = None,
    ) -> AnimationAction:
        self.opacity.set(0.0)
        return self.opacity.to(1.0, duration=duration, ease=ease or Ease.out_quad, delay=delay)

    def fade_out(
        self,
        duration: float = 0.5,
        delay: float = 0.0,
        ease: Optional[EasingFunc] = None,
    ) -> AnimationAction:
        return self.opacity.to(0.0, duration=duration, ease=ease or Ease.in_quad, delay=delay)

    def bounce(
        self,
        amplitude: float = 1.2,
        count: int = 1,
        duration: float = 0.6,
        delay: float = 0.0,
    ) -> Any:
        """Elastic bounce pulse."""
        curr_scale = self.scale.get()
        peak_scale = Vector2D(curr_scale.x * amplitude, curr_scale.y * amplitude)
        from vibmo.timeline.scheduler import SequentialGroup
        return SequentialGroup([
            self.scale.to(peak_scale, duration=duration * 0.4, ease=Ease.out_quad, delay=delay),
            self.scale.to(curr_scale, duration=duration * 0.6, ease=Ease.spring(stiffness=180, damping=10)),
        ])


    def float_idle(
        self,
        amplitude: float = 8.0,
        duration: float = 2.0,
        speed: float = 1.0,
    ) -> None:
        """Sets up continuous organic floating oscillation."""
        base_pos = self.position.get()
        self.position.bind(_FloatBinding(base_pos, amplitude, speed))

    def tilt_3d(
        self,
        pitch: float = 0.25,
        yaw: float = -0.35,
        duration: float = 1.0,
        ease: Optional[EasingFunc] = None,
        delay: float = 0.0,
    ) -> Any:
        """Tilts the node in 3D perspective space (pitch around X axis, yaw around Y axis)."""
        e = ease or Ease.out_expo
        from vibmo.timeline.scheduler import ParallelGroup
        return ParallelGroup([
            self.rotate_x.to(float(pitch), duration=duration, ease=e, delay=delay),
            self.rotate_y.to(float(yaw), duration=duration, ease=e, delay=delay),
        ])

    def reset_tilt(
        self,
        duration: float = 0.8,
        ease: Optional[EasingFunc] = None,
        delay: float = 0.0,
    ) -> Any:
        """Pulls 3D tilt angles back to flat 2D alignment."""
        e = ease or Ease.out_expo
        from vibmo.timeline.scheduler import ParallelGroup
        return ParallelGroup([
            self.rotate_x.to(0.0, duration=duration, ease=e, delay=delay),
            self.rotate_y.to(0.0, duration=duration, ease=e, delay=delay),
        ])


    def follow_path(
        self,
        path: Any,
        duration: float = 2.0,
        auto_orient: bool = True,
        offset_angle: float = 0.0,
        ease: Optional[EasingFunc] = None,
        delay: float = 0.0,
    ) -> AnimationAction:
        """Animates this node along an SVG path curve with optional automatic tangential rotation."""
        from vibmo.spatial.motion_path import MotionPathAction
        return MotionPathAction(
            node=self,
            path_or_d=path,
            duration=duration,
            auto_orient=auto_orient,
            offset_angle=offset_angle,
            ease=ease or Ease.in_out_cubic,
            delay=delay,
        )

    def bounce_on_beat(
        self,
        analyzer: Any,
        band: str = "bass",
        amplitude: float = 1.3,
    ) -> None:
        """Dynamically pulses the node scale based on the audio frequency band."""
        base_scale = self.scale.get()
        self.scale.bind(_BeatScaleBinding(base_scale, analyzer, band, amplitude))

    def __repr__(self) -> str:
        return f"<{self.name} id={self.id}>"
