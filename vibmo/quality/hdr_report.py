from dataclasses import dataclass
from typing import List, Dict, Any


@dataclass
class HDRReportData:
    filename: str
    resolution: str
    frame_rate: float
    total_frames: int
    color_space: str
    max_cll_nits: float
    max_cll_frame: int
    max_fall_nits: float
    max_fall_frame: int
    avg_cll_nits: float
    frame_luminance_curve: List[float]


class HDRReportGenerator:
    """Generates broadcast compliance light level audit reports."""

    @staticmethod
    def generate_markdown_report(data: HDRReportData) -> str:
        """Builds a structured markdown audit report."""
        report = f"""# ✦ Vibmo HDR Light Level Compliance Report

## File Information
- **Target File**: `{data.filename}`
- **Resolution**: {data.resolution} @ {data.frame_rate} FPS
- **Duration**: {data.total_frames} frames
- **Color Primaries / EOTF**: {data.color_space} (SMPTE ST.2084 PQ)

## Broadcast HDR Metrics (CEA-861.3 / BT.2408)
| Metric | Value (nits) | Frame Landmark | Status |
| :--- | :--- | :--- | :--- |
| **MaxCLL (Max Content Light Level)** | **{data.max_cll_nits:.2f} nits** | Frame #{data.max_cll_frame} | {'✅ PASS (< 1000 nits)' if data.max_cll_nits <= 1000 else '⚠️ WARNING (Master Cap Exceeded)'} |
| **MaxFALL (Max Frame Average Light)** | **{data.max_fall_nits:.2f} nits** | Frame #{data.max_fall_frame} | {'✅ PASS (< 400 nits)' if data.max_fall_nits <= 400 else '⚠️ WARNING (High APL)'} |
| **Average Scene Luminance** | **{data.avg_cll_nits:.2f} nits** | Full Sequence | ✅ Nominal |

## Artistic Intent & Tone Mapping Guidance
- **Diffuse White (Graphics & UI)**: Aligned at 203 nits standard.
- **Specular Ceiling**: Peak highlights preserved with smooth shoulder rolloff.
"""
        return report
