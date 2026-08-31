import numpy as np
from dataclasses import dataclass
from typing import Tuple, Optional
from enum import Enum


class FitMode(str, Enum):
    CONTAIN = "contain"  # Scale entire image to fit (letterbox/pillarbox)
    COVER = "cover"      # Scale full frame with crop
    FILL = "fill"        # Stretch to all corners
    CENTER = "center"    # Center crop with no resizing


@dataclass
class Transform2D:
    x: float = 0.0
    y: float = 0.0
    zoom_x: float = 1.0
    zoom_y: float = 1.0
    rotation_deg: float = 0.0
    anchor_x: float = 0.5
    anchor_y: float = 0.5


class SizingPipeline:
    """10-Stage Concatenated Resolution-Independent Sizing Engine."""

    @staticmethod
    def compute_fit_scale(src_w: int, src_h: int, dst_w: int, dst_h: int, mode: FitMode) -> Tuple[float, float, float, float]:
        """Calculates scale and translation offsets for mismatched resolution files."""
        if mode == FitMode.CENTER:
            return 1.0, 1.0, (dst_w - src_w) / 2.0, (dst_h - src_h) / 2.0
        elif mode == FitMode.FILL:
            return dst_w / src_w, dst_h / src_h, 0.0, 0.0

        scale_w = dst_w / src_w
        scale_h = dst_h / src_h

        if mode == FitMode.CONTAIN:
            scale = min(scale_w, scale_h)
        else:  # COVER
            scale = max(scale_w, scale_h)

        new_w = src_w * scale
        new_h = src_h * scale
        offset_x = (dst_w - new_w) / 2.0
        offset_y = (dst_h - new_h) / 2.0
        return scale, scale, offset_x, offset_y

    @classmethod
    def concatenate_affine_matrix(
        cls,
        fit_scale: Tuple[float, float, float, float],
        edit_sizing: Transform2D,
        input_sizing: Transform2D,
        dynamic_zoom_progress: float = 0.0,
        dynamic_zoom_end: Optional[Transform2D] = None,
    ) -> np.ndarray:
        """
        Combines Fit, Edit Sizing, Input Sizing, and Dynamic Zoom into a single 3x3 matrix.
        Applied directly on source pixels to eliminate multi-pass interpolation blur.
        """
        # Interpolate dynamic zoom
        dz_zoom = 1.0
        dz_x, dz_y = 0.0, 0.0
        if dynamic_zoom_end is not None:
            t = dynamic_zoom_progress
            dz_zoom = 1.0 + (dynamic_zoom_end.zoom_x - 1.0) * t
            dz_x = dynamic_zoom_end.x * t
            dz_y = dynamic_zoom_end.y * t

        total_scale_x = fit_scale[0] * edit_sizing.zoom_x * input_sizing.zoom_x * dz_zoom
        total_scale_y = fit_scale[1] * edit_sizing.zoom_y * input_sizing.zoom_y * dz_zoom
        total_tx = fit_scale[2] + edit_sizing.x + input_sizing.x + dz_x
        total_ty = fit_scale[3] + edit_sizing.y + input_sizing.y + dz_y

        rad = np.radians(edit_sizing.rotation_deg + input_sizing.rotation_deg)
        cos_r = np.cos(rad)
        sin_r = np.sin(rad)

        matrix = np.array([
            [total_scale_x * cos_r, -total_scale_y * sin_r, total_tx],
            [total_scale_x * sin_r,  total_scale_y * cos_r, total_ty],
            [0.0,                   0.0,                    1.0]
        ], dtype=np.float32)

        return matrix
