"""Persistent, shot-organised compositions for continuous motion graphics.

``Scene`` remains the small, single-canvas building block.  ``Composition``
adds named shot ranges while retaining one scene graph and one global timeline.
This means a layer created in one shot can keep moving in the next shot without
being rasterised, cut, or cross-faded at the boundary.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, Generator, List, Optional, Union

from vibmo.core.color import Color, colors
from vibmo.scene.scene import Scene
from vibmo.timeline.scheduler import Choreographer


@dataclass
class Shot:
    """A named range on a :class:`Composition` global timeline."""

    composition: "Composition"
    name: str
    start: float
    duration: Optional[float] = None
    animation_end: float = 0.0

    @property
    def end(self) -> float:
        """The declared end of this shot, or the end of its choreography."""
        return self.start + (self.duration if self.duration is not None else self.animation_end)

    def animate(self, fn: Union[Callable[[], Generator], Generator]) -> Union[Callable[[], Generator], Generator]:
        """Schedules choreography at this shot's global start time.

        The returned actions are applied to the composition's shared nodes, so
        their signals remain continuous across all later shots.
        """
        end = self.composition._animate_at(self.start, fn)
        self.animation_end = max(self.animation_end, end - self.start)
        if self.duration is None:
            self.composition.duration = max(self.composition.duration, end)
        return fn

    def add(self, *nodes: Any) -> Any:
        """Adds layers to the shared composition graph."""
        return self.composition.add(*nodes)

    def __enter__(self) -> "Shot":
        if self.composition._active_shot is not None:
            raise RuntimeError("Shots cannot be nested. Close the active shot first.")
        self.composition._active_shot = self
        return self

    def __exit__(self, exc_type: Any, exc: Any, traceback: Any) -> bool:
        self.composition._active_shot = None
        self.composition._finalize_shot(self)
        return False


class Composition(Scene):
    """A production timeline made of continuous, named shots.

    Unlike ``Sequence``, a Composition never composites rendered scene frames
    at a shot boundary.  It evaluates one persistent graph at global time.
    Use shots to organise a long animation while keeping node, camera, and
    property state continuous.
    """

    def __init__(
        self,
        width: int = 1920,
        height: int = 1080,
        fps: float = 60.0,
        duration: float = 0.1,
        background: Optional[Union[Color, str]] = colors.SLATE_950,
        theme: Optional[Any] = None,
        props: Optional[dict[str, Any]] = None,
    ) -> None:
        super().__init__(width, height, fps, max(0.1, duration), background, theme, props)
        self.shots: List[Shot] = []
        self._active_shot: Optional[Shot] = None

    def shot(self, name: str, duration: Optional[float] = None, at: Optional[float] = None) -> Shot:
        """Creates a named range; later shots start after the preceding one.

        If ``duration`` is omitted, the range grows to fit its choreography.
        An explicit ``at`` allows deliberate overlaps while still rendering a
        single global scene graph.
        """
        if not name.strip():
            raise ValueError("A shot requires a non-empty name.")
        if duration is not None and duration <= 0:
            raise ValueError("Shot duration must be greater than zero.")

        start = float(at) if at is not None else max((s.end for s in self.shots), default=0.0)
        if start < 0:
            raise ValueError("Shot start cannot be negative.")
        shot = Shot(self, name=name, start=start, duration=float(duration) if duration is not None else None)
        self.shots.append(shot)
        return shot

    def _animate_at(self, start: float, fn: Union[Callable[[], Generator], Generator]) -> float:
        choreographer = Choreographer()
        choreographer.current_time = start
        end = choreographer.run(fn)
        self.duration = max(self.duration, end)
        return end

    def animate(self, fn: Union[Callable[[], Generator], Generator]) -> Union[Callable[[], Generator], Generator]:
        """Schedules at the active shot start, or at zero outside a shot."""
        if self._active_shot is not None:
            return self._active_shot.animate(fn)
        self._animate_at(0.0, fn)
        return fn

    def _finalize_shot(self, shot: Shot) -> None:
        if shot.duration is None:
            shot.duration = max(0.1, shot.animation_end)
        self.duration = max(self.duration, shot.end)

    def validate(self) -> List[str]:
        """Extends scene validation with timeline-boundary continuity checks."""
        issues = super().validate()
        ordered = sorted(self.shots, key=lambda shot: shot.start)
        for index, shot in enumerate(ordered):
            if shot.animation_end > (shot.duration or 0.0) + 0.05:
                issues.append(
                    f"Shot '{shot.name}' choreography ends at {shot.animation_end:.2f}s, "
                    f"past its declared duration ({shot.duration:.2f}s)."
                )
            if index and shot.start > ordered[index - 1].end + 1e-6:
                issues.append(
                    f"Gap of {shot.start - ordered[index - 1].end:.2f}s before shot '{shot.name}'."
                )
        return issues

    def describe(self) -> str:
        base = super().describe()
        shot_lines = ["  Shots:"]
        for shot in sorted(self.shots, key=lambda item: item.start):
            shot_lines.append(f"    └─ {shot.name}: {shot.start:.2f}s – {shot.end:.2f}s")
        return base.replace("  Layer Tree:", "\n".join(shot_lines) + "\n  Layer Tree:")
