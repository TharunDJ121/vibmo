"""
Animated Metric and Number Counter with formatting and exponential deceleration.
"""

from __future__ import annotations
from typing import Any, Optional, Union
from vibmo.core.color import Color, colors
from vibmo.core.signal import Signal, AnimationAction
from vibmo.core.easing import Ease, EasingFunc
from vibmo.typography.text import Text


class MetricCounter(Text):
    """Animates numbers smoothly with prefixes (e.g. '$') and separators (e.g. '1,450,000')."""

    def __init__(
        self,
        start_val: float = 0.0,
        end_val: float = 100.0,
        prefix: str = "",
        suffix: str = "",
        decimals: int = 0,
        font_size: float = 48.0,
        bold: bool = True,
        color: Optional[Union[Color, str]] = colors.WHITE,
        **kwargs: Any,
    ) -> None:
        self.prefix = prefix

        self.suffix = suffix
        self.decimals = decimals
        self.target_end = end_val
        self.numeric_val = Signal(float(start_val), f"{kwargs.get('name', 'counter')}.val")

        initial_text = self._format_number(start_val)
        super().__init__(
            text=initial_text,
            font_size=font_size,
            bold=bold,
            color=color,
            **kwargs,
        )

    @property
    def end_val(self) -> float:
        return self.target_end

    @property
    def start_val(self) -> float:
        return self.numeric_val.get(0.0)


    def _format_number(self, val: float) -> str:
        if self.decimals == 0:
            formatted = f"{int(round(val)):,}"
        else:
            formatted = f"{val:,.{self.decimals}f}"
        return f"{self.prefix}{formatted}{self.suffix}"

    def count_to(
        self,
        target: Optional[float] = None,
        duration: float = 1.8,
        ease: Optional[EasingFunc] = None,
        delay: float = 0.0,
    ) -> AnimationAction:
        """Counts smoothly from current value to target with easing."""
        tgt = target if target is not None else self.target_end
        e = ease or Ease.out_expo
        return self.numeric_val.to(tgt, duration=duration, ease=e, delay=delay)

    def draw(self, ctx: Any, time: float = 0.0) -> None:
        curr_num = self.numeric_val.get(time)
        self.text.set(self._format_number(curr_num))
        super().draw(ctx, time)

    def local_bounds(self, time: float = 0.0) -> Tuple[float, float, float, float]:
        curr_num = self.numeric_val.get(time)
        self.text.set(self._format_number(curr_num))
        return super().local_bounds(time)
