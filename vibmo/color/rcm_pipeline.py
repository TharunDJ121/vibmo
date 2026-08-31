from __future__ import annotations
import numpy as np
from enum import Enum
from typing import Tuple, Optional


class ColorSpace(str, Enum):
    SRGB = "sRGB"
    REC709 = "Rec.709"
    REC2020 = "Rec.2020"
    DCI_P3 = "DCI-P3"
    DAVINCI_WIDE_GAMUT = "DaVinci_Wide_Gamut"
    ACES_CG = "ACEScg"


class DRTMode(str, Enum):
    NONE = "none"
    DAVINCI = "davinci"
    SATURATION_PRESERVING = "saturation_preserving"
    SIMPLE = "simple"


class RCMPipeline:
    """Scene-Referred 32-Bit Float Color Pipeline with Highlight Preservation."""

    # 3x3 Primary Conversion Matrices to DaVinci Wide Gamut (DWG)
    MATRICES_TO_DWG = {
        ColorSpace.REC709: np.array([
            [0.6068, 0.2878, 0.1054],
            [0.0818, 0.8872, 0.0310],
            [0.0264, 0.1070, 0.8666]
        ], dtype=np.float32),
        ColorSpace.SRGB: np.array([
            [0.6068, 0.2878, 0.1054],
            [0.0818, 0.8872, 0.0310],
            [0.0264, 0.1070, 0.8666]
        ], dtype=np.float32),
        ColorSpace.REC2020: np.array([
            [0.8262, 0.1444, 0.0294],
            [0.0526, 0.9324, 0.0150],
            [0.0125, 0.0483, 0.9392]
        ], dtype=np.float32),
        ColorSpace.DCI_P3: np.array([
            [0.7228, 0.2116, 0.0656],
            [0.0620, 0.9168, 0.0212],
            [0.0182, 0.0768, 0.9050]
        ], dtype=np.float32),
        ColorSpace.DAVINCI_WIDE_GAMUT: np.eye(3, dtype=np.float32),
    }

    @classmethod
    def sdr_to_hdr_diffuse_white(cls, rgb: np.ndarray, target_nits: float = 203.0) -> np.ndarray:
        """
        Remaps SDR 100-nit graphics/titles to 203-nit diffuse white in HDR (BT.2408 standard).
        Prevents motion graphics text from looking dull gray on HDR screens.
        """
        scale_factor = target_nits / 100.0
        return rgb * scale_factor

    @classmethod
    def apply_drt_tone_mapping(
        cls,
        rgb_linear: np.ndarray,
        mode: DRTMode = DRTMode.DAVINCI,
        peak_nits: float = 1000.0,
        sat_rolloff_start_nits: float = 400.0,
    ) -> np.ndarray:
        """
        Output Display Rendering Transform (DRT) mapping wide dynamic range to target display.
        Compresses extreme highlight overshoots while preserving chromaticity.
        """
        if mode == DRTMode.NONE:
            return rgb_linear

        img = np.maximum(0.0, rgb_linear)
        luma = 0.2126 * img[..., 0] + 0.7152 * img[..., 1] + 0.0722 * img[..., 2]

        if mode == DRTMode.DAVINCI:
            # Smooth luminance roll-off with controlled highlight desaturation
            scale = peak_nits / 100.0
            norm_luma = luma / scale
            mapped_luma = norm_luma / (1.0 + norm_luma)
            # Avoid division by zero
            safe_luma = luma / scale + 1e-6
            ratio = np.where(luma > 1e-6, mapped_luma / safe_luma, 1.0)
            img = img * ratio[..., np.newaxis]

            # High-luminance desaturation
            desat_mask = luma > (sat_rolloff_start_nits / 100.0)
            if np.any(desat_mask):
                t = np.clip((luma[desat_mask] - sat_rolloff_start_nits / 100.0) / (scale + 1e-6), 0.0, 1.0)
                mean_l = luma[desat_mask][..., np.newaxis]
                img[desat_mask] = img[desat_mask] * (1.0 - t[..., np.newaxis] * 0.7) + mean_l * (t[..., np.newaxis] * 0.7)

        return img
