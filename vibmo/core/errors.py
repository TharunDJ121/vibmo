"""
Agent-Native Self-Healing Exceptions for Vibmo.
Provides structured, actionable error tracebacks with embedded prompt instructions for AI agents and developers.
"""

from __future__ import annotations
from typing import Optional


class VibmoError(Exception):
    """Base class for all Vibmo runtime errors with self-healing advice."""

    def __init__(self, message: str, tip: Optional[str] = None) -> None:
        self.message = message
        self.tip = tip
        formatted = f"\n\n[*] [Vibmo Engine Error]: {message}"
        if tip:
            formatted += f"\n  --> How to fix (AI Agent Instruction): {tip}\n"
        super().__init__(formatted)


class VibmoLayoutError(VibmoError):
    """Raised when coordinates, bounds, or layout constraints are invalid."""
    pass


class VibmoAssetError(VibmoError):
    """Raised when an image, audio, video, or font file cannot be located."""
    pass


class VibmoAnimationError(VibmoError):
    """Raised when an animation sequence or yielded action is malformed."""
    pass


class VibmoParameterError(VibmoError):
    """Raised when an unrecognized property name, easing string, or enum value is passed."""
    pass


def validate_kwargs(target_name: str, passed_kwargs: dict, allowed_keys: set) -> None:
    """Validates that all passed kwargs are recognized, raising VibmoParameterError with fuzzy suggestions if not."""
    import difflib
    for k in passed_kwargs:
        if k not in allowed_keys:
            suggestions = difflib.get_close_matches(k, list(allowed_keys), n=2, cutoff=0.5)
            tip = f"Use one of: {sorted(list(allowed_keys))}"
            if suggestions:
                tip = f"Did you mean '{suggestions[0]}'? Supported parameters: {sorted(list(allowed_keys))}"
            raise VibmoParameterError(
                f"Unknown parameter '{k}' passed to '{target_name}'.",
                tip=tip,
            )

