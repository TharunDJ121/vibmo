"""
High-Performance Multi-Tier In-Memory Frame Server & Background Pre-Renderer.
Thread-safe, crash-proof, and optimized for real-time 60 FPS in-browser playback.
"""

from __future__ import annotations
import io
import base64
import time as pytime
import threading
from typing import Any, Dict, Optional, Tuple
import numpy as np
from PIL import Image


class FrameServer:
    """Renders, compresses, caches, and streams scene frames at 60 FPS."""

    def __init__(self, scene: Any) -> None:
        self.scene = scene
        self._cache: Dict[Tuple[int, int], str] = {}  # (scale_percent, frame_index) -> base64_jpeg
        self._lock = threading.Lock()
        self._render_lock = threading.Lock()
        self._prewarmer_thread: Optional[threading.Thread] = None
        self._stop_prewarm = threading.Event()
        self._last_valid_b64: Optional[str] = None

    def clear_cache(self) -> None:
        with self._lock:
            self._cache.clear()

    def update_scene(self, new_scene: Any) -> None:
        self.scene = new_scene
        self.clear_cache()
        self.prewarm_timeline(scale=0.5, max_frames=240)

    def get_frame_base64(self, time: float, scale: float = 0.5, quality: int = 70) -> str:
        """Returns base64 JPEG string for frame at time, checking cache first."""
        fps = getattr(self.scene, "fps", 60.0) or 60.0
        scale_key = int(round(scale * 100))
        frame_idx = int(round(time * fps))
        cache_key = (scale_key, frame_idx)

        with self._lock:
            if cache_key in self._cache:
                return self._cache[cache_key]

        try:
            with self._render_lock:
                # Render frame on sequence or rasterizer
                if hasattr(self.scene, "render_frame"):
                    rgba = self.scene.render_frame(time=time, scale=1.0)
                elif hasattr(self.scene, "_rasterizer"):
                    rgba = self.scene._rasterizer.render_frame(
                        root_nodes=self.scene.nodes,
                        time=time,
                        background=self.scene.background,
                        camera=self.scene.camera,
                        post_fx=self.scene.post_fx,
                    )
                else:
                    rgba = np.zeros((720, 1280, 4), dtype=np.uint8)
                img = Image.fromarray(rgba, "RGBA")

                if scale < 0.99:
                    w = max(1, int(self.scene.width * scale))
                    h = max(1, int(self.scene.height * scale))
                    img = img.resize((w, h), Image.Resampling.BILINEAR)

                buf = io.BytesIO()
                rgb_img = img.convert("RGB")
                rgb_img.save(buf, format="JPEG", quality=quality, optimize=False)
                b64_str = base64.b64encode(buf.getvalue()).decode("utf-8")
                self._last_valid_b64 = b64_str

            with self._lock:
                self._cache[cache_key] = b64_str

            return b64_str

        except Exception as e:
            if self._last_valid_b64:
                return self._last_valid_b64
            # Emergency blank fallback
            fallback_img = Image.new("RGB", (640, 360), color=(11, 17, 32))
            buf = io.BytesIO()
            fallback_img.save(buf, format="JPEG", quality=50)
            return base64.b64encode(buf.getvalue()).decode("utf-8")

    def prewarm_timeline(self, scale: float = 0.5, max_frames: int = 300) -> None:
        """Launches a background worker to pre-render the full timeline gently without blocking playback."""
        if self._prewarmer_thread and self._prewarmer_thread.is_alive():
            self._stop_prewarm.set()

        self._stop_prewarm.clear()

        def _worker():
            total_frames = min(max_frames, int(self.scene.duration * self.scene.fps))
            dt = 1.0 / self.scene.fps
            for i in range(total_frames):
                if self._stop_prewarm.is_set():
                    break
                t = i * dt
                self.get_frame_base64(t, scale=scale)
                pytime.sleep(0.01)  # Yield CPU to interactive requests

        self._prewarmer_thread = threading.Thread(target=_worker, daemon=True)
        self._prewarmer_thread.start()
