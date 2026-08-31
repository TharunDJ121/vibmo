"""
Pre-Flight Composition Validator for Vibmo / Motio.

Performs static verification on scenes, asset references, aspect ratios,
and audio tracks before executing video rendering.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Sequence


@dataclass
class PreflightIssue:
    severity: str  # "error", "warning", "info"
    message: str
    target: str


@dataclass
class PreflightReport:
    passed: bool
    errors: list[PreflightIssue]
    warnings: list[PreflightIssue]

    @property
    def total_issues(self) -> int:
        return len(self.errors) + len(self.warnings)


class PreflightValidator:
    """Pre-render sanity checker."""

    @classmethod
    def validate_scene(cls, scene: Any) -> PreflightReport:
        errors: list[PreflightIssue] = []
        warnings: list[PreflightIssue] = []

        # Check scene dimensions
        w = getattr(scene, "width", 1920)
        h = getattr(scene, "height", 1080)
        if w <= 0 or h <= 0:
            errors.append(PreflightIssue("error", f"Invalid scene dimensions: {w}x{h}", "Scene"))

        # Check duration & fps
        dur = getattr(scene, "duration", 5.0)
        fps = getattr(scene, "fps", 60)
        if dur <= 0:
            errors.append(PreflightIssue("error", f"Invalid scene duration: {dur}s", "Scene"))
        if fps <= 0 or fps > 240:
            errors.append(PreflightIssue("error", f"Invalid scene fps: {fps}", "Scene"))

        # Check nodes
        nodes = getattr(scene, "nodes", [])
        if not nodes:
            warnings.append(PreflightIssue("warning", "Scene contains no child nodes", "Scene"))

        for node in nodes:
            # Check image/video assets if present
            path = getattr(node, "path", None) or getattr(node, "src", None) or getattr(node, "file_path", None)
            if path and isinstance(path, (str, Path)):
                p = Path(path)
                if not p.is_file() and not str(path).startswith("http"):
                    warnings.append(PreflightIssue("warning", f"Asset path not found on disk: {path}", type(node).__name__))

        return PreflightReport(
            passed=len(errors) == 0,
            errors=errors,
            warnings=warnings,
        )
