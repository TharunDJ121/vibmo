"""
Audio Streaming and Waveform Peak Extraction Server for Web Studio.
"""

from __future__ import annotations
import os
import tempfile
import uuid
from typing import Any, List, Optional
import numpy as np


class AudioServer:
    """Manages audio file streaming and waveform visualization peak data."""

    def __init__(self, scene: Any) -> None:
        self.scene = scene
        self._rendered_sfx_path: Optional[str] = None

    def update_scene(self, new_scene: Any) -> None:
        self.scene = new_scene
        self._rendered_sfx_path = None


    def get_audio_filepath(self) -> Optional[str]:
        """Returns the active audio file path, rendering SFX cues if no background track is set."""
        if self.scene.audio_path and os.path.exists(self.scene.audio_path):
            return self.scene.audio_path

        # If scene has SFX cues, synthesize master WAV
        if hasattr(self.scene, "sfx") and len(self.scene.sfx.cues) > 0:
            if not self._rendered_sfx_path or not os.path.exists(self._rendered_sfx_path):
                temp_wav = os.path.join(tempfile.gettempdir(), f"studio_sfx_{uuid.uuid4().hex[:8]}.wav")
                self.scene.sfx.render_to_wav(self.scene.duration, temp_wav)
                self._rendered_sfx_path = temp_wav
            return self._rendered_sfx_path

        return None

    def extract_waveform_peaks(self, num_points: int = 400) -> List[float]:
        """Extracts normalized waveform peaks [0.0 - 1.0] across timeline duration."""
        path = self.get_audio_filepath()
        if not path or not os.path.exists(path):
            # Return gentle synthetic dummy waveform
            t = np.linspace(0, 1, num_points)
            return list(np.clip(np.abs(np.sin(t * 12.0) * 0.4 + np.random.rand(num_points) * 0.2), 0.05, 1.0))

        try:
            from scipy.io import wavfile
            if path.endswith(".wav"):
                sr, data = wavfile.read(path)
                if data.ndim > 1:
                    data = data.mean(axis=1)
                data = np.abs(data.astype(np.float32))
                max_val = np.max(data)
                if max_val > 0:
                    data = data / max_val

                # Downsample into num_points buckets
                bucket_size = max(1, len(data) // num_points)
                peaks = []
                for i in range(num_points):
                    start = i * bucket_size
                    end = min(len(data), start + bucket_size)
                    if start < len(data):
                        peaks.append(float(np.max(data[start:end])))
                    else:
                        peaks.append(0.0)
                return peaks
        except Exception:
            pass

        # Fallback
        return [0.1] * num_points
