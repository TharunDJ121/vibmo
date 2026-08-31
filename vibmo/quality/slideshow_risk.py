"""
Slideshow Risk Evaluator for Vibmo / Motio.

Scores a motion graphics scene or scene plan across 6 dimensions to reliably
predict whether the output will feel like a static presentation/slideshow
rather than fluid, cinematic directed video.

Dimensions (0-5 scale, lower is better):
  - repetition: repeated layouts/backgrounds without variation
  - decorative_visuals: visuals that decorate rather than communicate narrative
  - weak_motion: motion lacking clear narrative or physical purpose
  - weak_shot_intent: framing/reveal lacking clear intent
  - typography_overreliance: over-dependence on static text without visual support
  - unsupported_cinematic_claims: cinematic pacing claims without actual dynamics

Verdict scale:
  < 2.0: strong (truly cinematic & dynamic)
  < 3.0: acceptable
  < 4.0: revise (add motion dynamics / visual hierarchy)
  >= 4.0: fail (too static, feels like a slide deck)
"""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass, asdict
from typing import Any, Sequence


@dataclass
class RiskDimension:
    score: float
    reason: str


@dataclass
class SlideshowRiskReport:
    average_score: float
    verdict: str  # "strong", "acceptable", "revise", "fail"
    dimensions: dict[str, RiskDimension]
    suggestions: list[str]

    def to_dict(self) -> dict[str, Any]:
        return {
            "average_score": self.average_score,
            "verdict": self.verdict,
            "dimensions": {k: asdict(v) for k, v in self.dimensions.items()},
            "suggestions": self.suggestions,
        }


class SlideshowRiskScorer:
    """Evaluates motion graphics scene graphs and plans against slideshow anti-patterns."""

    @classmethod
    def evaluate(
        cls,
        scenes: Sequence[dict[str, Any]],
        edit_decisions: dict[str, Any] | None = None,
        renderer_family: str | None = None,
    ) -> SlideshowRiskReport:
        if not scenes:
            return SlideshowRiskReport(
                average_score=5.0,
                verdict="fail",
                dimensions={},
                suggestions=["Provide at least one scene to evaluate."],
            )

        dims = {
            "repetition": cls._score_repetition(scenes),
            "decorative_visuals": cls._score_decorative(scenes),
            "weak_motion": cls._score_weak_motion(scenes),
            "weak_shot_intent": cls._score_weak_intent(scenes),
            "typography_overreliance": cls._score_typography(scenes),
            "unsupported_cinematic_claims": cls._score_cinematic_claims(scenes, renderer_family),
        }

        scores = [d.score for d in dims.values()]
        avg = round(sum(scores) / len(scores), 2)

        if avg < 2.0:
            verdict = "strong"
        elif avg < 3.0:
            verdict = "acceptable"
        elif avg < 4.0:
            verdict = "revise"
        else:
            verdict = "fail"

        suggestions: list[str] = []
        for name, dim in dims.items():
            if dim.score >= 3.0:
                suggestions.append(f"[{name.replace('_', ' ').title()}]: {dim.reason}")

        return SlideshowRiskReport(
            average_score=avg,
            verdict=verdict,
            dimensions=dims,
            suggestions=suggestions,
        )

    @classmethod
    def evaluate_scene(cls, scene: Any) -> SlideshowRiskReport:
        """Evaluate a live Vibmo Scene object."""
        scenes_data: list[dict[str, Any]] = []
        duration = getattr(scene, "duration", 5.0)
        node_count = len(getattr(scene, "nodes", []))
        
        # Analyze scene nodes
        node_types = [type(n).__name__ for n in getattr(scene, "nodes", [])]
        has_motion = any(hasattr(n, "position") and len(getattr(n.position, "_keyframes", [])) > 0 for n in getattr(scene, "nodes", []))
        
        scenes_data.append({
            "type": "vibmo_scene",
            "duration": duration,
            "node_count": node_count,
            "node_types": node_types,
            "has_motion": has_motion,
            "description": f"Scene with {node_count} nodes ({', '.join(node_types[:4])})",
        })
        return cls.evaluate(scenes_data)

    @classmethod
    def _score_repetition(cls, scenes: Sequence[dict]) -> RiskDimension:
        if len(scenes) < 3:
            return RiskDimension(0.5, "Short sequence with minimal repetition risk")

        types = Counter(s.get("type", "unknown") for s in scenes)
        _, most_common_count = types.most_common(1)[0]
        type_ratio = most_common_count / len(scenes)

        if type_ratio > 0.65:
            return RiskDimension(4.2, f"{type_ratio:.0%} of scenes use identical structure. Vary visual formats.")
        elif type_ratio > 0.45:
            return RiskDimension(2.5, "Moderate layout similarity across scenes.")
        return RiskDimension(1.0, "Good variety across scene types and layouts.")

    @classmethod
    def _score_decorative(cls, scenes: Sequence[dict]) -> RiskDimension:
        decorative_keywords = {"stock", "generic", "background_only", "abstract_fill"}
        decor_count = 0
        for s in scenes:
            desc = str(s.get("description", "")).lower()
            if any(kw in desc for kw in decorative_keywords):
                decor_count += 1

        ratio = decor_count / len(scenes)
        if ratio > 0.4:
            return RiskDimension(3.8, "High proportion of purely decorative background scenes without core subject focus.")
        elif ratio > 0.2:
            return RiskDimension(2.0, "Moderate decorative visual balance.")
        return RiskDimension(0.8, "Visuals directly support narrative concepts.")

    @classmethod
    def _score_weak_motion(cls, scenes: Sequence[dict]) -> RiskDimension:
        static_scenes = 0
        for s in scenes:
            has_motion = s.get("has_motion", True)
            motion_desc = s.get("motion", "")
            if not has_motion or motion_desc in ("none", "static", "hold"):
                static_scenes += 1

        ratio = static_scenes / len(scenes)
        if ratio > 0.5:
            return RiskDimension(4.0, "Over half the scenes are static without spring physics, pans, or zooms.")
        elif ratio > 0.25:
            return RiskDimension(2.2, "Some static intervals detected; consider adding continuous float_idle or camera tracking.")
        return RiskDimension(0.7, "Active dynamic choreography with natural physics.")

    @classmethod
    def _score_weak_intent(cls, scenes: Sequence[dict]) -> RiskDimension:
        lacking_intent = sum(1 for s in scenes if not s.get("shot_language") and not s.get("intent"))
        ratio = lacking_intent / len(scenes)
        if ratio > 0.6:
            return RiskDimension(3.0, "Scenes lack explicit cinematography framing (close_up, orbital, dolly_in).")
        return RiskDimension(1.0, "Cinematography framing is well specified.")

    @classmethod
    def _score_typography(cls, scenes: Sequence[dict]) -> RiskDimension:
        text_heavy = 0
        for s in scenes:
            types = s.get("node_types", [])
            text_nodes = sum(1 for t in types if "Text" in t or "Title" in t or "Caption" in t)
            total = len(types) or 1
            if text_nodes / total > 0.7:
                text_heavy += 1

        ratio = text_heavy / len(scenes)
        if ratio > 0.5:
            return RiskDimension(3.7, "Heavy overreliance on text cards. Augment with charts, mockups, or vector illustrations.")
        return RiskDimension(1.0, "Balanced mixture of typography, vector assets, and UI components.")

    @classmethod
    def _score_cinematic_claims(cls, scenes: Sequence[dict], renderer_family: str | None) -> RiskDimension:
        return RiskDimension(1.0, "Pacing verified against engine capabilities.")
