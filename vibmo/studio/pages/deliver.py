"""
Deliver / Render Page: Export Presets, Codec Settings, and Render Queue Manager.
"""

from __future__ import annotations
from typing import Any, Dict, List


EXPORT_PRESETS: List[Dict[str, Any]] = [
    {
        "id": "mp4_high",
        "name": "Master Video (1080p60 H.264)",
        "format": "mp4",
        "quality": "high",
        "description": "Crisp 1080p @ 60 FPS master for YouTube, X, and launch sites.",
    },
    {
        "id": "mp4_draft",
        "name": "Ultra-Fast Draft (540p30)",
        "format": "mp4",
        "quality": "draft",
        "description": "Lightning-fast preview export in under 2 seconds.",
    },
    {
        "id": "webm_alpha",
        "name": "Transparent Alpha (WebM VP9)",
        "format": "webm",
        "quality": "high",
        "description": "Transparent background for embedding directly on web pages.",
    },
    {
        "id": "prores_4k",
        "name": "ProRes 422 HQ (4K UHD)",
        "format": "mov",
        "quality": "high",
        "description": "Broadcast-ready uncompressed video master.",
    },
    {
        "id": "gif_loop",
        "name": "Animated GIF (Looping)",
        "format": "gif",
        "quality": "fast",
        "description": "Optimized animated GIF for GitHub README and documentation.",
    },
]
