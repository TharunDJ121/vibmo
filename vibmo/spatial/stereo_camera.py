from __future__ import annotations
from dataclasses import dataclass
import numpy as np

class ViewMode:
    LEFT_EYE = "left"
    RIGHT_EYE = "right"
    ANAGLYPH_RC = "anaglyph_red_cyan"
    SIDE_BY_SIDE = "side_by_side"

@dataclass
class StereoConfig:
    convergence_plane_z: float = 0.0   # Z-depth where parallax is zero (screen level)
    interocular_distance: float = 65.0 # Distance between eyes (mm)
    floating_window_left_crop: float = 0.0
    floating_window_right_crop: float = 0.0

class StereoCamera:
    """Calculates sub-pixel shifts for left and right eyes based on layer depth."""
    
    def __init__(self, config: StereoConfig):
        self.config = config

    def calculate_parallax_shift(self, layer_z: float, eye: str) -> float:
        """
        Positive parallax: Layer is behind screen (shifts outward).
        Negative parallax: Layer pops out of screen (shifts inward).
        """
        depth_delta = layer_z - self.config.convergence_plane_z
        shift = (self.config.interocular_distance / 2.0) * (depth_delta * 0.01)
        
        if eye == ViewMode.LEFT_EYE:
            return shift
        elif eye == ViewMode.RIGHT_EYE:
            return -shift
        return 0.0

    def apply_floating_window(self, left_frame: np.ndarray, right_frame: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
        """Fixes edge occlusions / window violations to preserve stereo illusion."""
        if self.config.floating_window_left_crop > 0:
            crop_px = int(self.config.floating_window_left_crop)
            left_frame[:, :crop_px] = 0  # Black out left edge
            
        if self.config.floating_window_right_crop > 0:
            crop_px = int(self.config.floating_window_right_crop)
            right_frame[:, -crop_px:] = 0 # Black out right edge
            
        return left_frame, right_frame
