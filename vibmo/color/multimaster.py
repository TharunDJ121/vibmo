from dataclasses import dataclass, field
from typing import Dict, List, Optional
import numpy as np


@dataclass
class TrimPass:
    name: str                           # e.g. "SDR_Rec709", "HDR_1000_P3"
    target_nits: float = 100.0          # Target peak luminance
    target_gamut: str = "Rec.709"       # Target color gamut
    lift_trim: float = 0.0              # -0.025 to +0.025
    gamma_trim: float = 0.0             # Midtone contrast trim
    gain_trim: float = 0.0              # Peak highlight trim
    sat_gain_trim: float = 0.0          # Saturation gain in highlights
    chroma_weight: float = 0.0          # Saturated area darkening
    tone_detail: float = 0.0            # Highlight texture recovery


class MultiMasterTrimManager:
    """Manages simultaneous multi-deliverable grade trims over a Hero Master grade."""

    def __init__(self, master_nits: float = 4000.0):
        self.master_nits = master_nits
        self.trims: Dict[str, TrimPass] = {}
        self._add_default_trims()

    def _add_default_trims(self):
        self.trims["SDR_Rec709"] = TrimPass(name="SDR_Rec709", target_nits=100.0, target_gamut="Rec.709")
        self.trims["HDR10_1000"] = TrimPass(name="HDR10_1000", target_nits=1000.0, target_gamut="Rec.2020")

    def add_trim_pass(self, trim: TrimPass):
        self.trims[trim.name] = trim

    def evaluate_trim(self, hero_rgb: np.ndarray, trim_name: str) -> np.ndarray:
        """Applies trim pass metadata on top of the hero grade buffer."""
        if trim_name not in self.trims:
            return hero_rgb
        trim = self.trims[trim_name]

        # 1. Luminance scaling to target display
        scale = trim.target_nits / self.master_nits
        trimmed = hero_rgb * (scale ** (1.0 - trim.gain_trim * 0.2))

        # 2. Lift/Gamma/Gain adjustments
        if trim.gamma_trim != 0.0:
            gamma_factor = 1.0 / max(0.1, 1.0 + trim.gamma_trim * 0.5)
            trimmed = np.power(np.maximum(0.0, trimmed), gamma_factor)

        # 3. Saturation Trim in Highlights
        if trim.sat_gain_trim != 0.0:
            luma = 0.2126 * trimmed[..., 0] + 0.7152 * trimmed[..., 1] + 0.0722 * trimmed[..., 2]
            mean_l = luma[..., np.newaxis]
            trimmed = mean_l + (trimmed - mean_l) * (1.0 + trim.sat_gain_trim)

        return np.clip(trimmed, 0.0, 1.0)
