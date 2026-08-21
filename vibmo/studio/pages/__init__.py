"""
Modular Workspace Pages for Vibmo Studio Pro (Motion, Fusion, Color, Fairlight, Deliver).
"""

from vibmo.studio.pages.fusion import FusionGraph
from vibmo.studio.pages.color import ColorGradeState
from vibmo.studio.pages.fairlight import FAIRLIGHT_FOLEY_SOUNDBOARD
from vibmo.studio.pages.deliver import EXPORT_PRESETS

__all__ = [
    "FusionGraph",
    "ColorGradeState",
    "FAIRLIGHT_FOLEY_SOUNDBOARD",
    "EXPORT_PRESETS",
]
