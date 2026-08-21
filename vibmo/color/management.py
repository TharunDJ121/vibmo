"""
Professional Color Management, Color Spaces (sRGB, Rec709, Display P3, ACEScg), HDR, and Tone Mapping.
"""

from __future__ import annotations
from enum import Enum
import math
import numpy as np
from typing import Any, Tuple, Union


class ColorSpace(str, Enum):
    """Supported broadcast and cinema color spaces."""
    SRGB = "sRGB"
    REC709 = "Rec709"
    LINEAR = "Linear"
    DISPLAY_P3 = "DisplayP3"
    ACES_CG = "ACEScg"
    DCI_P3 = "DCI-P3"


# Standard CIE XYZ to RGB conversion matrices
_ACES_TO_SRGB = np.array([
    [1.7050, -0.6242, -0.0808],
    [-0.1297, 1.1384, -0.0087],
    [-0.0242, -0.1247, 1.1489]
], dtype=np.float32)

_SRGB_TO_ACES = np.linalg.inv(_ACES_TO_SRGB)


class ColorManager:
    """Handles color conversions, tone mapping, and high dynamic range (HDR) workflows."""

    @staticmethod
    def srgb_to_linear(rgb: np.ndarray) -> np.ndarray:
        """Converts sRGB [0, 1] to Linear RGB."""
        rgb = np.clip(rgb, 0.0, 1.0)
        return np.where(rgb <= 0.04045, rgb / 12.92, ((rgb + 0.055) / 1.055) ** 2.4)

    @staticmethod
    def linear_to_srgb(linear: np.ndarray) -> np.ndarray:
        """Converts Linear RGB to sRGB [0, 1]."""
        linear = np.maximum(0.0, linear)
        return np.where(linear <= 0.0031308, linear * 12.92, 1.055 * (linear ** (1.0 / 2.4)) - 0.055)

    @staticmethod
    def aces_filmic_tonemap(linear: np.ndarray) -> np.ndarray:
        """
        Applies Narkowicz ACES filmic tone mapping curve for photographic highlight roll-off.
        """
        x = np.maximum(0.0, linear)
        a = 2.51
        b = 0.03
        c = 2.43
        d = 0.59
        e = 0.14
        return np.clip((x * (a * x + b)) / (x * (c * x + d) + e), 0.0, 1.0)

    @staticmethod
    def reinhard_tonemap(linear: np.ndarray, white_point: float = 2.0) -> np.ndarray:
        """Reinhard extended luminance tone mapping."""
        x = np.maximum(0.0, linear)
        num = x * (1.0 + (x / (white_point ** 2)))
        denom = 1.0 + x
        return np.clip(num / denom, 0.0, 1.0)

    @classmethod
    def convert(cls, rgb: np.ndarray, src_space: ColorSpace, dst_space: ColorSpace) -> np.ndarray:
        """Transforms RGB array between color spaces."""
        if src_space == dst_space:
            return rgb

        # Step 1: To Linear
        if src_space in (ColorSpace.SRGB, ColorSpace.REC709):
            lin = cls.srgb_to_linear(rgb)
        else:
            lin = rgb.copy()

        # Step 2: Gamut transform if ACES
        if src_space == ColorSpace.ACES_CG and dst_space != ColorSpace.ACES_CG:
            lin = np.dot(lin, _ACES_TO_SRGB.T)
        elif dst_space == ColorSpace.ACES_CG and src_space != ColorSpace.ACES_CG:
            lin = np.dot(lin, _SRGB_TO_ACES.T)

        # Step 3: To Destination EOTF
        if dst_space in (ColorSpace.SRGB, ColorSpace.REC709):
            return cls.linear_to_srgb(lin)
        return lin
