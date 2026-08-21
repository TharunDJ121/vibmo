"""
Coroutine and Generator-based choreography scheduler for Vibmo animations.
"""

from __future__ import annotations
import inspect
from typing import Any, Callable, Generator, Iterable, List, Optional, Union
from vibmo.core.signal import AnimationAction


class WaitAction:
    """Delays execution by duration seconds."""
    def __init__(self, duration: float) -> None:
        self.duration = max(0.0, float(duration))


class ParallelGroup:
    """Executes multiple animation actions or generator coroutines in parallel."""
    def __init__(self, actions: Sequence[Any]) -> None:
        self.actions = list(actions)

    def __iter__(self):
        return iter(self.actions)

    def apply_at(self, start_time: float) -> float:
        max_end = start_time
        for sub in self.actions:
            if hasattr(sub, "apply_at"):
                end = sub.apply_at(start_time)
            elif isinstance(sub, (list, tuple)):
                end = ParallelGroup(sub).apply_at(start_time)
            else:
                end = start_time
            max_end = max(max_end, end)
        return max_end


class SequentialGroup:
    """Executes actions sequentially."""
    def __init__(self, actions: Sequence[Any]) -> None:
        self.actions = list(actions)

    def __iter__(self):
        return iter(self.actions)

    def apply_at(self, start_time: float) -> float:
        curr = start_time
        for sub in self.actions:
            if hasattr(sub, "apply_at"):
                curr = sub.apply_at(curr)
            elif isinstance(sub, (list, tuple)):
                curr = ParallelGroup(sub).apply_at(curr)
        return curr




def _flatten_actions(items: Iterable[Any]) -> List[Any]:
    result = []
    for item in items:
        if isinstance(item, (list, tuple)):
            result.extend(_flatten_actions(item))
        elif isinstance(item, ParallelGroup):
            result.extend(_flatten_actions(item.actions))
        elif item is not None:
            result.append(item)
    return result


def all(*actions: Any) -> ParallelGroup:
    """Choreograph animations in parallel, yielding when all complete."""
    return ParallelGroup(_flatten_actions(actions))


def sequence(*actions: Any) -> SequentialGroup:
    """Choreograph animations sequentially."""
    return SequentialGroup(_flatten_actions(actions))



def wait(duration: float) -> WaitAction:
    """Pauses the timeline by duration seconds."""
    return WaitAction(duration)


class Choreographer:
    """Executes generator functions to schedule animation segments onto signals."""

    def __init__(self) -> None:
        self.current_time = 0.0

    def run(self, gen_func: Union[Callable[[], Generator], Generator]) -> float:
        """Runs the generator and returns the final scene duration."""
        gen = gen_func() if callable(gen_func) else gen_func
        if not inspect.isgenerator(gen):
            return self.current_time

        self._process_generator(gen)
        return self.current_time

    def _process_generator(self, gen: Generator) -> None:
        try:
            val = next(gen)
            while True:
                max_end = self._apply_action(val, self.current_time)
                self.current_time = max(self.current_time, max_end)
                val = next(gen)
        except StopIteration:
            pass

    def _apply_action(self, action: Any, start_time: float) -> float:
        if action is None:
            return start_time

        if isinstance(action, WaitAction):
            return start_time + action.duration

        if isinstance(action, AnimationAction):
            return action.apply_at(start_time)

        if isinstance(action, list):
            # Treat list as parallel by default
            return self._apply_action(ParallelGroup(action), start_time)

        if isinstance(action, ParallelGroup):
            max_end = start_time
            for sub in action.actions:
                end = self._apply_action(sub, start_time)
                max_end = max(max_end, end)
            return max_end

        if isinstance(action, SequentialGroup):
            curr = start_time
            for sub in action.actions:
                curr = self._apply_action(sub, curr)
            return curr

        if inspect.isgenerator(action):
            # Nested coroutine
            sub_choreographer = Choreographer()
            sub_choreographer.current_time = start_time
            sub_choreographer._process_generator(action)
            return sub_choreographer.current_time

        return start_time
