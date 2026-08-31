"""
Deliver / Render Page: Export Presets, Codec Settings, and Render Queue Manager.
Inspired by DaVinci Resolve Chapter 1 (Deliver Page Batch Queue & Presets).
"""

from __future__ import annotations
import os
import time
import uuid
import threading
from typing import Any, Dict, List, Optional


EXPORT_PRESETS: List[Dict[str, Any]] = [
    {
        "id": "mp4_1080p",
        "name": "Master 1080p (H.264 60FPS)",
        "format": "mp4",
        "quality": "high",
        "aspect_ratio": "16:9",
        "width": 1920,
        "height": 1080,
        "description": "Crisp 1080p @ 60 FPS master for YouTube, X, and web launch.",
    },
    {
        "id": "reel_9_16",
        "name": "Social Reel / TikTok (9:16 Vertical)",
        "format": "mp4",
        "quality": "high",
        "aspect_ratio": "9:16",
        "width": 1080,
        "height": 1920,
        "description": "Vertical format optimized for Instagram Reels, TikTok, and YouTube Shorts.",
    },
    {
        "id": "square_1_1",
        "name": "Square Feed (1:1)",
        "format": "mp4",
        "quality": "high",
        "aspect_ratio": "1:1",
        "width": 1080,
        "height": 1080,
        "description": "1080x1080 square format for LinkedIn, Instagram carousel, and feeds.",
    },
    {
        "id": "webm_alpha",
        "name": "Transparent Alpha (WebM VP9)",
        "format": "webm",
        "quality": "high",
        "aspect_ratio": "16:9",
        "width": 1920,
        "height": 1080,
        "description": "Transparent background for overlaying on websites and web apps.",
    },
    {
        "id": "prores_4k",
        "name": "ProRes 422 HQ (4K Master)",
        "format": "mov",
        "quality": "high",
        "aspect_ratio": "16:9",
        "width": 3840,
        "height": 2160,
        "description": "Broadcast-grade uncompressed master for archive and cinema.",
    },
    {
        "id": "gif_loop",
        "name": "Animated GIF (Looping)",
        "format": "gif",
        "quality": "fast",
        "aspect_ratio": "16:9",
        "width": 960,
        "height": 540,
        "description": "Lightweight animated GIF for GitHub README and documentation.",
    },
]


class RenderJob:
    """Represents a single rendering task in the batch queue."""
    def __init__(
        self,
        job_id: str,
        name: str,
        preset_id: str,
        output_filename: str,
        width: int = 1920,
        height: int = 1080,
        quality: str = "high",
        format_type: str = "mp4",
    ):
        self.job_id = job_id
        self.name = name
        self.preset_id = preset_id
        self.output_filename = output_filename
        self.width = width
        self.height = height
        self.quality = quality
        self.format_type = format_type
        self.status = "queued"  # queued, rendering, completed, failed, cancelled
        self.progress = 0.0
        self.error_message: Optional[str] = None
        self.created_at = time.time()
        self.completed_at: Optional[float] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "job_id": self.job_id,
            "name": self.name,
            "preset_id": self.preset_id,
            "output_filename": self.output_filename,
            "width": self.width,
            "height": self.height,
            "quality": self.quality,
            "format_type": self.format_type,
            "status": self.status,
            "progress": round(self.progress, 1),
            "error_message": self.error_message,
            "created_at": self.created_at,
            "completed_at": self.completed_at,
        }


class RenderQueueManager:
    """Manages the queue of render jobs and sequential/parallel execution."""
    def __init__(self):
        self.jobs: List[RenderJob] = []
        self._lock = threading.Lock()
        self._is_processing = False

    def add_job(
        self,
        preset_id: str,
        name: Optional[str] = None,
        custom_output: Optional[str] = None,
    ) -> RenderJob:
        with self._lock:
            preset = next((p for p in EXPORT_PRESETS if p["id"] == preset_id), EXPORT_PRESETS[0])
            job_id = f"job_{uuid.uuid4().hex[:8]}"
            job_name = name or preset["name"]
            out_fn = custom_output or f"export_{preset_id}_{int(time.time())}.{preset['format']}"

            job = RenderJob(
                job_id=job_id,
                name=job_name,
                preset_id=preset_id,
                output_filename=out_fn,
                width=preset.get("width", 1920),
                height=preset.get("height", 1080),
                quality=preset.get("quality", "high"),
                format_type=preset.get("format", "mp4"),
            )
            self.jobs.append(job)
            return job

    def remove_job(self, job_id: str) -> bool:
        with self._lock:
            for i, j in enumerate(self.jobs):
                if j.job_id == job_id:
                    if j.status == "queued":
                        self.jobs.pop(i)
                        return True
                    elif j.status == "rendering":
                        j.status = "cancelled"
                        return True
                    else:
                        self.jobs.pop(i)
                        return True
            return False

    def clear_completed(self) -> None:
        with self._lock:
            self.jobs = [j for j in self.jobs if j.status in ("queued", "rendering")]

    def get_all_jobs(self) -> List[Dict[str, Any]]:
        with self._lock:
            return [j.to_dict() for j in self.jobs]

    def get_job(self, job_id: str) -> Optional[RenderJob]:
        with self._lock:
            return next((j for j in self.jobs if j.job_id == job_id), None)


_GLOBAL_RENDER_QUEUE = RenderQueueManager()

def get_render_queue() -> RenderQueueManager:
    return _GLOBAL_RENDER_QUEUE
