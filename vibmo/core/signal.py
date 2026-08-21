"""
Reactive Signal and Animatable Property system for procedural and timeline-based motion.
"""

from __future__ import annotations
from typing import Any, Callable, Generic, List, Optional, TypeVar, Union
from vibmo.core.easing import Ease, EasingFunc
from vibmo.core.vector import Vector2D
from vibmo.core.color import Color

T = TypeVar("T")


def _interpolate_any(v1: Any, v2: Any, progress: float) -> Any:
    """Polymorphic interpolator supporting float, Vector2D, Color, and lists."""
    if isinstance(v1, (int, float)) and isinstance(v2, (int, float)):
        return v1 + (v2 - v1) * progress
    if isinstance(v1, Vector2D) or isinstance(v2, Vector2D):
        p1 = Vector2D.from_any(v1)
        p2 = Vector2D.from_any(v2)
        return p1.lerp(p2, progress)
    if isinstance(v1, Color) or isinstance(v2, Color):
        c1 = Color.from_any(v1)
        c2 = Color.from_any(v2)
        return c1.lerp(c2, progress)
    if isinstance(v1, (list, tuple)) and isinstance(v2, (list, tuple)) and len(v1) == len(v2):
        values = [_interpolate_any(a, b, progress) for a, b in zip(v1, v2)]
        return tuple(values) if isinstance(v1, tuple) and isinstance(v2, tuple) else values
    # Discrete jump at 50%
    return v1 if progress < 0.5 else v2


class AnimationSegment:
    """A discrete interpolation segment on a timeline."""

    def __init__(
        self,
        start_time: float,
        duration: float,
        start_value: Any,
        end_value: Any,
        ease: EasingFunc = Ease.in_out_quad,
    ) -> None:
        self.start_time = float(start_time)
        self.duration = max(1e-5, float(duration))
        self.end_time = self.start_time + self.duration
        self.start_value = start_value
        self.end_value = end_value
        self.ease = ease

    def evaluate(self, time: float) -> Any:
        if time <= self.start_time:
            return self.start_value
        if time >= self.end_time:
            # Preserve the property type at the final frame.  For example,
            # a Vector2D signal animated to ``(x, y)`` must still evaluate as
            # Vector2D after its segment has completed.
            return _interpolate_any(self.start_value, self.end_value, 1.0)
        t_norm = (time - self.start_time) / self.duration
        progress = self.ease(t_norm)
        return _interpolate_any(self.start_value, self.end_value, progress)


class Signal(Generic[T]):
    """
    An animatable property with reactive evaluation and timeline interpolation.
    """

    def __init__(self, initial_value: T, name: str = "") -> None:
        self.name = name
        self._initial_value = initial_value
        self._current_value = initial_value
        self._segments: List[AnimationSegment] = []
        self._binding: Optional[Callable[[float], T]] = None

    def get(self, time: Optional[float] = None) -> T:
        if self._binding is not None:
            return self._binding(time if time is not None else 0.0)
        if time is None:
            return self._current_value
        return self.evaluate_at(time)

    def __call__(self, time: Optional[float] = None) -> T:
        return self.get(time)

    def set(self, value: T) -> Signal[T]:
        self._current_value = value
        self._initial_value = value
        self._binding = None
        return self

    def bind(self, func: Callable[[float], T]) -> None:
        """Binds this signal to a dynamic function of time t."""
        self._binding = func

    def link_to(self, other_signal: Signal, map_fn: Optional[Callable[[Any], Any]] = None) -> Signal[T]:
        """Dynamically links this signal's value to another signal's evaluation (Expression Engine)."""
        if map_fn is not None:
            self.bind(lambda t: map_fn(other_signal.get(t)))
        else:
            self.bind(lambda t: other_signal.get(t))
        return self

    def to(
        self,
        target_value: T,
        duration: float = 1.0,
        ease: EasingFunc = Ease.out_quad,
        delay: float = 0.0,
        start_time: Optional[float] = None,
    ) -> AnimationAction:
        """Returns an animation action that can be yielded in an @scene.animate coroutine."""
        return AnimationAction(
            signal=self,
            target_value=target_value,
            duration=duration,
            ease=ease,
            delay=delay,
            explicit_start_time=start_time,
        )

    def from_value(
        self,
        start_value: T,
        duration: float = 1.0,
        ease: EasingFunc = Ease.out_quad,
        delay: float = 0.0,
    ) -> AnimationAction:
        """Animates from start_value to the current value."""
        curr = self._current_value
        self._current_value = start_value
        return self.to(curr, duration=duration, ease=ease, delay=delay)

    def add_segment(self, segment: AnimationSegment) -> None:
        self._segments.append(segment)
        self._segments.sort(key=lambda s: s.start_time)
        self._current_value = segment.end_value

    def evaluate_at(self, time: float) -> T:
        if self._binding is not None:
            return self._binding(time)
        if not self._segments:
            return self._current_value

        # If before first segment
        if time < self._segments[0].start_time:
            return self._initial_value

        # Find corresponding segment or gap
        for seg in self._segments:
            if seg.start_time <= time <= seg.end_time:
                return seg.evaluate(time)

        # In gap between segments or after last segment
        val = self._initial_value
        for seg in self._segments:
            if time >= seg.end_time:
                val = seg.end_value
            elif time < seg.start_time:
                break
        return val

    def __repr__(self) -> str:
        return f"Signal({self.name or 'val'}={self._current_value})"


class AnimationAction:
    """Represents a scheduled animation on a signal."""

    def __init__(
        self,
        signal: Signal,
        target_value: Any,
        duration: float,
        ease: EasingFunc,
        delay: float = 0.0,
        explicit_start_time: Optional[float] = None,
    ) -> None:
        self.signal = signal
        self.target_value = target_value
        self.duration = duration
        self.ease = ease
        self.delay = delay
        self.explicit_start_time = explicit_start_time

    def apply_at(self, current_time: float) -> float:
        """Applies this animation starting at current_time and returns the end time."""
        start = self.explicit_start_time if self.explicit_start_time is not None else (current_time + self.delay)
        start_val = self.signal.get(start)
        segment = AnimationSegment(
            start_time=start,
            duration=self.duration,
            start_value=start_val,
            end_value=self.target_value,
            ease=self.ease,
        )
        self.signal.add_segment(segment)
        return start + self.duration
