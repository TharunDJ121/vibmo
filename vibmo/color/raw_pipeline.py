import numpy as np

class CameraRawPipeline:
    """32-Bit Floating Point Sensor Debayering & Cinematic Image Controls."""
    
    @staticmethod
    def evaluate(
        rgb_tensor: np.ndarray,
        color_temp_kelvin: float = 6500.0,
        tint: float = 0.0,
        exposure_stops: float = 0.0,
        highlight_recovery: bool = True,
        gamut_compression: bool = True,
        contrast_s_curve: float = 1.0,
        midtone_detail: float = 0.0,
        color_boost_vibrance: float = 0.0,
    ) -> np.ndarray:
        # 1. Linear Exposure scaling in 32-bit float
        img = rgb_tensor.astype(np.float32) * (2.0 ** exposure_stops)
        
        # 2. Kelvin Color Temperature & Tint Adjustment
        temp_ratio = 6500.0 / max(2000.0, color_temp_kelvin)
        img[..., 0] *= temp_ratio               # Red channel warmth
        img[..., 2] *= (1.0 / temp_ratio)       # Blue channel coolness
        img[..., 1] *= (1.0 + (tint / 150.0))   # Green/Magenta tint
        
        # 3. Highlight Recovery (reconstruct saturated highlights)
        if highlight_recovery:
            luma = 0.2126 * img[..., 0] + 0.7152 * img[..., 1] + 0.0722 * img[..., 2]
            blown_mask = luma > 1.0
            if np.any(blown_mask):
                # Smoothly compress specular overshoots into shoulder
                img[blown_mask] = 1.0 + np.tanh(img[blown_mask] - 1.0) * 0.5

        # 4. Gamut Compression (protect against neon LED clipping)
        if gamut_compression:
            max_c = np.maximum.reduce([img[..., 0], img[..., 1], img[..., 2]])
            compression_mask = max_c > 0.95
            img[compression_mask] = 0.95 + 0.05 * np.tanh((img[compression_mask] - 0.95) / 0.05)

        # 5. Smart Color Boost (Vibrance targeting low-saturation areas)
        if color_boost_vibrance != 0.0:
            max_val = np.max(img, axis=-1, keepdims=True)
            min_val = np.min(img, axis=-1, keepdims=True)
            sat = np.clip((max_val - min_val) / (max_val + 1e-6), 0.0, 1.0)
            boost_factor = 1.0 + (color_boost_vibrance * (1.0 - sat))
            mean_c = np.mean(img, axis=-1, keepdims=True)
            img = mean_c + (img - mean_c) * boost_factor

        return np.clip(img, 0.0, 1.0)
