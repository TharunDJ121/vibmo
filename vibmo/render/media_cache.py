"""
Media decoding and caching layer.
Avoids spinning up FFmpeg for every frame fetch during preview/playback.
"""

import os
import subprocess
import numpy as np
from pathlib import Path
from typing import Optional, Dict


CACHE_DIR = Path.home() / ".cache" / "vibmo" / "media_proxies"


class MediaProxyCache:
    """
    Decodes video assets into persistent low-res image sequences or RAM proxies
    to enable instant scrubbing and visual evaluation.
    """
    
    _frame_cache: Dict[str, Dict[int, np.ndarray]] = {}
    
    @classmethod
    def get_frame(cls, video_path: str, time: float, fps: float = 30.0) -> Optional[np.ndarray]:
        """Fetches a specific frame, caching the decoded stream in memory."""
        if not os.path.exists(video_path):
            return None
            
        frame_idx = int(time * fps)
        cache_key = f"{video_path}_{fps}"
        
        if cache_key not in cls._frame_cache:
            cls._frame_cache[cache_key] = {}
            
        if frame_idx in cls._frame_cache[cache_key]:
            return cls._frame_cache[cache_key][frame_idx]
            
        # Fallback to slow FFmpeg extraction if not cached
        # In a full implementation, this would trigger a background thread to decode
        # a chunk of frames around the requested time using a persistent pipe or cv2.VideoCapture.
        try:
            import cv2
            cap = cv2.VideoCapture(video_path)
            cap.set(cv2.CAP_PROP_POS_MSEC, int(time * 1000))
            ret, frame = cap.read()
            cap.release()
            
            if ret:
                # Convert BGR to RGB
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                # Ensure it's RGBA for Cairo compositing
                frame_rgba = cv2.cvtColor(frame_rgb, cv2.COLOR_RGB2RGBA)
                cls._frame_cache[cache_key][frame_idx] = frame_rgba
                return frame_rgba
        except ImportError:
            pass
            
        return None
        
    @classmethod
    def clear_cache(cls):
        cls._frame_cache.clear()
