"""
Anti-PPT Meta-Director & Continuous Beat Graph Planner for Vibmo.
Inspired by video-production-skills ai-motion-director.
Formulates motion theses, plans continuous physical beat graphs, and validates against the Anti-PPT Gate.
"""

from __future__ import annotations
from typing import List, Dict, Any, Optional, Union
from dataclasses import dataclass, field

from vibmo.scene.scene import Scene
from vibmo.scene.node import Node


@dataclass
class MotionThesis:
    """The single-sentence movement thesis of the video."""
    visual_metaphor: str
    start_state: str
    end_state: str
    core_claim: str

    def to_statement(self) -> str:
        return f"This video moves by showing {self.visual_metaphor} transforming from {self.start_state} to {self.end_state}, proving {self.core_claim}."


@dataclass
class BeatNode:
    """An individual beat on the continuous motion timeline."""
    time_start: float
    time_end: float
    narrative_job: str  # "hook", "reveal", "contrast", "mechanism", "consequence", "proof", "close", "cta"
    main_moving_object: str
    start_state: str
    end_state: str
    motion_verb: str  # e.g., "stream", "orbit", "cluster", "split", "morph", "dissolve", "expand"
    camera_motion: str = "push"  # "push", "pan", "parallax", "orbit", "stable"
    text_role: str = "title"  # "title", "label", "caption", "counter", "none"
    has_state_change: bool = True
    ppt_risk: str = ""


class BeatGraph:
    """
    Continuous Timeline Beat Graph.
    Ensures the video functions as a continuous visual system rather than disconnected slides.
    """

    def __init__(self, thesis: MotionThesis) -> None:
        self.thesis = thesis
        self.beats: List[BeatNode] = []

    def add_beat(
        self,
        time_start: float,
        time_end: float,
        narrative_job: str,
        main_moving_object: str,
        start_state: str,
        end_state: str,
        motion_verb: str,
        camera_motion: str = "push",
        text_role: str = "title",
        has_state_change: bool = True,
        ppt_risk: str = "",
    ) -> BeatNode:
        beat = BeatNode(
            time_start=time_start,
            time_end=time_end,
            narrative_job=narrative_job,
            main_moving_object=main_moving_object,
            start_state=start_state,
            end_state=end_state,
            motion_verb=motion_verb,
            camera_motion=camera_motion,
            text_role=text_role,
            has_state_change=has_state_change,
            ppt_risk=ppt_risk,
        )
        self.beats.append(beat)
        return beat

    def total_duration(self) -> float:
        return self.beats[-1].time_end if self.beats else 0.0

    def state_change_ratio(self) -> float:
        if not self.beats:
            return 0.0
        return sum(1 for b in self.beats if b.has_state_change) / len(self.beats)


@dataclass
class AntiPptReport:
    score: float
    verdict: str  # "pass", "warning", "fail"
    violations: List[str] = field(default_factory=list)
    suggestions: List[str] = field(default_factory=list)


class AntiPptGate:
    """
    Anti-PPT Gate Quality Validator.
    Rejects static slide-like compositions and validates continuous visual metaphors.
    """

    @classmethod
    def evaluate_beat_graph(cls, graph: BeatGraph) -> AntiPptReport:
        violations = []
        suggestions = []
        score = 10.0

        # Rule 1: At least 80% of beats must have physical state changes
        ratio = graph.state_change_ratio()
        if ratio < 0.8:
            violations.append(f"Only {ratio*100:.0f}% of beats show state changes. Rule requires >=80% visible physical transformations.")
            suggestions.append("Replace static fade-ins with physical motion verbs (stream, orbit, cluster, morph, expand).")
            score -= 3.0

        # Rule 2: Check for forbidden slide-like motion verbs (only fade/pop everywhere)
        static_verbs = {"fade", "slide_in", "pop", "appear"}
        all_static = all(b.motion_verb.lower() in static_verbs for b in graph.beats)
        if all_static and len(graph.beats) > 2:
            violations.append("All beats use static entrance verbs (fade/pop). Video lacks physical kinetic metaphors.")
            suggestions.append("Introduce dynamic spatial verbs: orbit, cluster, split, swarm, dial, expand.")
            score -= 2.5

        # Rule 3: Timeline continuity check
        for i in range(len(graph.beats) - 1):
            gap = graph.beats[i+1].time_start - graph.beats[i].time_end
            if gap > 0.1:
                violations.append(f"Discontinuous gap of {gap:.2f}s detected between beat {i+1} and {i+2}.")
                score -= 1.0

        verdict = "pass" if score >= 8.0 else ("warning" if score >= 5.0 else "fail")
        return AntiPptReport(score=max(0.0, score), verdict=verdict, violations=violations, suggestions=suggestions)
