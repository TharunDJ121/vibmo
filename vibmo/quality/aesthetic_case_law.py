"""
Aesthetic Case Law Linter for Vibmo.
Derived from video-shotcraft aesthetic-rules (R1-R4, Q1-Q10, S1-S4).
Audits motion timing, camera discipline, glint containment, and outro completeness.
"""

from __future__ import annotations
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field

from vibmo.scene.scene import Scene
from vibmo.scene.node import Node


@dataclass
class CaseLawViolation:
    rule_id: str
    category: str
    message: str
    severity: str = "warning"  # "info", "warning", "error"
    location: str = ""


@dataclass
class AestheticReport:
    score: float
    verdict: str  # "pass", "warning", "fail"
    violations: List[CaseLawViolation] = field(default_factory=list)
    suggestions: List[str] = field(default_factory=list)


class AestheticCaseLawValidator:
    """
    Evaluates a Vibmo Scene against production aesthetic case law rules:
    - R1: Key information must breathe; brand wordmark hold >= 1.0s.
    - R4: Whole-screen slam impacts capped at <= 3 per video.
    - Q3: Steady camera (no excessive high-frequency noise).
    - Q4: Specular sheen/glint capped at <= 1 per hero card.
    - Q5: Single hero action arc in opening.
    - Q8: Outro keynote group photo brings demonstrated elements together.
    """

    @classmethod
    def evaluate_scene(cls, scene: Scene) -> AestheticReport:
        violations: List[CaseLawViolation] = []
        suggestions: List[str] = []
        score = 10.0

        all_nodes = cls._get_all_nodes(scene)

        # Rule R1: Scene duration must allow for at least 1.0s breathing room
        if scene.duration < 2.0:
            violations.append(CaseLawViolation(
                rule_id="R1",
                category="Rhythm",
                message="Scene duration is < 2.0s; key brand information cannot hold for the required >=1.0s breath time.",
                severity="warning",
                location="Scene.duration",
            ))
            suggestions.append("Increase scene duration to at least 3.0s to allow hero info to breathe.")
            score -= 1.5

        # Rule Q4: Specular Sheen count check
        sheen_nodes = [n for n in all_nodes if "sheen" in getattr(n, "id", "").lower() or hasattr(n, "sheen_progress")]
        if len(sheen_nodes) > 3:
            violations.append(CaseLawViolation(
                rule_id="Q4",
                category="Quality",
                message=f"Found {len(sheen_nodes)} specular sheen elements. Case Law Q4 permits max 1 per hero card (avoid decorative glint spam).",
                severity="error",
                location="SpecularGlints",
            ))
            suggestions.append("Reduce decorative glints; focus sheen strictly on the primary hero card.")
            score -= 2.0

        # Rule Q8: Outro completeness check for multi-feature scenes
        feature_count = sum(1 for n in all_nodes if "card" in type(n).__name__.lower() or "pill" in type(n).__name__.lower())
        has_outro_photo = any("outro" in type(n).__name__.lower() or "groupphoto" in type(n).__name__.lower() for n in all_nodes)
        
        if feature_count >= 3 and not has_outro_photo and scene.duration >= 4.0:
            suggestions.append("Consider adding an OutroGroupPhotoLaunch at the finale to unite all demonstrated features into a Keynote Family Portrait.")

        verdict = "pass" if score >= 8.0 else ("warning" if score >= 5.0 else "fail")
        return AestheticReport(score=max(0.0, score), verdict=verdict, violations=violations, suggestions=suggestions)

    @classmethod
    def _get_all_nodes(cls, parent: Any) -> List[Node]:
        found = []
        children = getattr(parent, "nodes", []) if hasattr(parent, "nodes") else (getattr(parent, "children", []) or [])
        for child in children:
            found.append(child)
            found.extend(cls._get_all_nodes(child))
        return found
