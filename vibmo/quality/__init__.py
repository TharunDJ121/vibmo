"""
Quality, Validation and Pacing Framework for Vibmo.
"""

from vibmo.quality.slideshow_risk import (
    SlideshowRiskScorer,
    SlideshowRiskReport,
    RiskDimension,
)
from vibmo.quality.pacing import (
    ScenePacingVerifier,
    TimelineLandmark,
    PacingReport,
)
from vibmo.quality.preflight import (
    PreflightValidator,
    PreflightReport,
    PreflightIssue,
)
from vibmo.quality.anti_slop import (
    AntiSlopValidator,
    AntiSlopReport,
    SlopViolation,
)
from vibmo.quality.aesthetic_case_law import (
    AestheticCaseLawValidator,
    AestheticReport,
    CaseLawViolation,
)
from vibmo.quality.replica_verifier import (
    VideoReplicaVerifier,
    FidelityLevel,
    FrameComparisonResult,
    GateVerdict,
)

__all__ = [
    "SlideshowRiskScorer",
    "SlideshowRiskReport",
    "RiskDimension",
    "ScenePacingVerifier",
    "TimelineLandmark",
    "PacingReport",
    "PreflightValidator",
    "PreflightReport",
    "PreflightIssue",
    "AntiSlopValidator",
    "AntiSlopReport",
    "SlopViolation",
    "AestheticCaseLawValidator",
    "AestheticReport",
    "CaseLawViolation",
    "VideoReplicaVerifier",
    "FidelityLevel",
    "FrameComparisonResult",
    "GateVerdict",
]
