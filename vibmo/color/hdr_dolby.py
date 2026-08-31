import json
import numpy as np
from dataclasses import dataclass, field
from typing import List, Dict, Any, Tuple


@dataclass
class DolbyVisionL1Data:
    min_pq: float       # Minimum scene luminance in 12-bit PQ code (0.0 to 1.0)
    max_pq: float       # Peak highlight luminance in 12-bit PQ code
    avg_pq: float       # Average picture level (APL) in 12-bit PQ code


@dataclass
class HDR10StaticMetadata:
    max_cll: float      # Maximum Content Light Level in nits (cd/m2)
    max_fall: float     # Maximum Frame Average Light Level in nits (cd/m2)


class DolbyVisionAnalyzer:
    """Computes frame-accurate Dolby Vision L1 and HDR10 MaxCLL/MaxFALL statistics."""

    @staticmethod
    def linear_to_pq(linear_nits: np.ndarray) -> np.ndarray:
        """SMPTE ST.2084 Perceptual Quantizer (PQ) transfer function."""
        y = np.clip(linear_nits / 10000.0, 0.0, 1.0)
        m1 = 2610.0 / 16384.0
        m2 = 2523.0 / 4096.0 * 128.0
        c1 = 3424.0 / 4096.0
        c2 = 2413.0 / 4096.0 * 32.0
        c3 = 2392.0 / 4096.0 * 32.0

        y_m1 = y ** m1
        num = c1 + c2 * y_m1
        den = 1.0 + c3 * y_m1
        return (num / den) ** m2

    @classmethod
    def analyze_frame(cls, rgb_linear_nits: np.ndarray) -> Tuple[DolbyVisionL1Data, float]:
        """Analyzes a single frame buffer, returning L1 metrics and frame average nits."""
        luma_nits = 0.2126 * rgb_linear_nits[..., 0] + 0.7152 * rgb_linear_nits[..., 1] + 0.0722 * rgb_linear_nits[..., 2]
        pq_values = cls.linear_to_pq(luma_nits)

        min_pq = float(np.min(pq_values))
        max_pq = float(np.max(pq_values))
        avg_pq = float(np.mean(pq_values))
        frame_fall = float(np.mean(luma_nits))

        return DolbyVisionL1Data(min_pq=min_pq, max_pq=max_pq, avg_pq=avg_pq), frame_fall

    @classmethod
    def compute_shot_hdr10_metadata(cls, frame_falls: List[float], max_nits_per_frame: List[float]) -> HDR10StaticMetadata:
        """Computes MaxCLL and MaxFALL across all frames in a scene."""
        max_cll = float(np.max(max_nits_per_frame)) if max_nits_per_frame else 0.0
        max_fall = float(np.max(frame_falls)) if frame_falls else 0.0
        return HDR10StaticMetadata(max_cll=max_cll, max_fall=max_fall)

    @classmethod
    def export_hdr10plus_json(cls, shot_analyses: List[Dict[str, Any]], output_json_path: str):
        """Exports SMPTE ST 2094-40 Profile B JSON metadata sidecar."""
        payload = {
            "version": "1.0",
            "ColorDescription": {
                "ColorPrimaries": "BT.2020",
                "TransferCharacteristics": "SMPTE ST 2084",
                "MatrixCoefficients": "BT.2020 non-constant",
            },
            "SceneList": shot_analyses,
        }
        with open(output_json_path, "w", encoding="utf-8") as f:
            json.dump(payload, f, indent=2)
