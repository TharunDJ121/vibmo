"""
Fairlight Audio Page: Soundboard triggers, Foley presets, and Multi-Track Audio Mixer.
"""

from __future__ import annotations
from typing import Any, Dict, List


FAIRLIGHT_FOLEY_SOUNDBOARD: List[Dict[str, Any]] = [
    {"name": "pop", "label": "Bubbly Pop", "icon": "🫧", "category": "UI Feedback", "default_vol": 0.8},
    {"name": "click", "label": "Mechanical Click", "icon": "🖱️", "category": "UI Feedback", "default_vol": 0.9},
    {"name": "whoosh", "label": "Airy Whoosh", "icon": "💨", "category": "Transitions", "default_vol": 0.75},
    {"name": "riser", "label": "Tension Riser", "icon": "📈", "category": "Cinematic", "default_vol": 0.7},
    {"name": "bass_drop", "label": "808 Sub Thud", "icon": "💥", "category": "Impact", "default_vol": 0.85},
    {"name": "sparkle", "label": "Chime Sparkle", "icon": "✨", "category": "Magic", "default_vol": 0.7},
]
