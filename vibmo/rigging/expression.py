"""
Reactive Expression Rigging System for procedural animations.
"""

from __future__ import annotations
import math
from typing import Any, Callable, Dict, Optional, Union
from vibmo.core.signal import Signal


class ExpressionSignal(Signal):
    """
    A reactive Signal whose value is dynamically calculated by an expression function f(t).
    Supports mathematical expressions, noise harmonics, and multi-node reactive dependencies.
    """

    def __init__(self, expr_fn: Callable[[float], Any], name: str = "") -> None:
        super().__init__(initial_value=expr_fn(0.0), name=name)
        self.expr_fn = expr_fn

    def get(self, time: float) -> Any:
        try:
            return self.expr_fn(time)
        except Exception:
            return self._initial_value


def expression(expr_fn: Callable[[float], Any], name: str = "") -> ExpressionSignal:
    """Helper to create an expression-driven reactive signal."""
    return ExpressionSignal(expr_fn, name=name)
