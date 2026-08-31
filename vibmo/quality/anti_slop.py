"""
✦ Vibmo Quality: Anti-Slop & Craft Restraint Validator
Inspired by Remocn craft rules (no ALL-CAPS reflexes, no decorative tracking, no glow halos, single-accent discipline).
"""

from __future__ import annotations

from dataclasses import dataclass, field, asdict
from typing import Any, List, Optional, Sequence, Union
import re

from vibmo.scene.scene import Scene
from vibmo.scene.node import Node
from vibmo.typography.text import Text
from vibmo.core.color import Color


@dataclass
class SlopViolation:
    rule: str
    severity: str  # "error", "warning"
    element: str
    message: str
    suggestion: str


@dataclass
class AntiSlopReport:
    verdict: str  # "pass", "warning", "fail"
    violations: List[SlopViolation] = field(default_factory=list)
    score: float = 10.0  # 0 to 10 scale (10 is pristine)

    def to_dict(self) -> dict[str, Any]:
        return {
            "verdict": self.verdict,
            "score": self.score,
            "violations": [asdict(v) for v in self.violations],
        }


class AntiSlopValidator:
    """
    Automated pre-flight inspection engine detecting AI-generated motion graphics slop.
    """
    @classmethod
    def evaluate_scene(cls, scene: Scene) -> AntiSlopReport:
        violations: List[SlopViolation] = []

        # Recursively collect all nodes
        nodes = cls._get_all_nodes(scene)
        text_nodes = [n for n in nodes if isinstance(n, Text) or hasattr(n, "raw_text") or hasattr(n, "text")]

        # 1. Check for ALL-CAPS Overuse
        for t in text_nodes:
            txt = getattr(t, "raw_text", None) or getattr(t, "text", "")
            if isinstance(txt, str) and len(txt.strip()) > 15:
                # If mostly uppercase without markdown tags
                clean_txt = re.sub(r"<[^>]+>", "", txt).strip()
                if clean_txt.isupper() and not any(tag in txt for tag in ["<#", "http", "JSON"]):
                    violations.append(
                        SlopViolation(
                            rule="No ALL-CAPS Sentences",
                            severity="warning",
                            element=str(getattr(t, "name", "Text")),
                            message=f"Long text rendered in ALL-CAPS: '{clean_txt[:30]}...'",
                            suggestion="Prefer sentence case for titles and body text; reserve uppercase for badges & acronyms.",
                        )
                    )

        # 2. Check for Decorative Letter-Spacing
        for t in text_nodes:
            ls = getattr(t, "letter_spacing", 0.0)
            if isinstance(ls, (int, float)) and ls > 4.0:
                violations.append(
                    SlopViolation(
                        rule="No Decorative Wide Tracking",
                        severity="warning",
                        element=str(getattr(t, "name", "Text")),
                        message=f"Letter spacing is {ls}px (> 4px).",
                        suggestion="Use default font tracking unless the entire component is specifically designed for letter tracking animation.",
                    )
                )

        # 3. Check for Giant Glow Halos / Blurs behind headings
        for n in nodes:
            shadow = getattr(n, "shadow", None)
            if shadow is not None:
                blur = getattr(shadow, "blur", 0.0)
                if blur > 32.0:
                    violations.append(
                        SlopViolation(
                            rule="No Oversized Glow Halos",
                            severity="warning",
                            element=str(getattr(n, "name", "Node")),
                            message=f"Drop shadow blur radius is {blur}px (> 32px).",
                            suggestion="Use subtle 1px elevation and crisp 1px borders instead of large decorative glow blobs.",
                        )
                    )

        # Compute Score
        error_count = sum(1 for v in violations if v.severity == "error")
        warn_count = sum(1 for v in violations if v.severity == "warning")

        score = max(0.0, 10.0 - (error_count * 3.0 + warn_count * 1.0))
        if error_count > 0 or score < 6.0:
            verdict = "fail"
        elif warn_count > 0 or score < 8.5:
            verdict = "warning"
        else:
            verdict = "pass"

        return AntiSlopReport(verdict=verdict, violations=violations, score=score)

    @classmethod
    def _get_all_nodes(cls, parent: Any) -> List[Node]:
        found = []
        children = getattr(parent, "nodes", []) if hasattr(parent, "nodes") else (getattr(parent, "children", []) or [])
        for child in children:
            found.append(child)
            found.extend(cls._get_all_nodes(child))
        return found
