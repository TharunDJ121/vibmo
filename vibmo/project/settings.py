from dataclasses import dataclass, field
from enum import Enum

class AspectRatioPreset(str, Enum):
    WIDESCREEN_16_9 = "16:9"
    PORTRAIT_9_16 = "9:16"
    SQUARE_1_1 = "1:1"
    ANAMORPHIC_2_39 = "2.39:1"
    SOCIAL_4_5 = "4:5"

class ScalingFilter(str, Enum):
    BILINEAR = "bilinear"
    BICUBIC = "bicubic"
    LANCZOS = "lanczos"
    CATMULL_ROM = "catmull_rom"
    MITCHELL = "mitchell"
    SINC = "sinc"

@dataclass
class ProjectMasterSettings:
    """DaVinci Resolve-grade Master Project & Timeline Configuration."""
    width: int = 1920
    height: int = 1080
    fps: float = 60.0
    aspect_ratio: AspectRatioPreset = AspectRatioPreset.WIDESCREEN_16_9
    pixel_aspect_ratio: float = 1.0
    
    # 32-Bit Float Color Science
    color_science: str = "DaVinci_YRGB_Color_Managed"
    working_color_space: str = "ACEScg"
    output_color_space: str = "Rec.709-A"  # Prevents QuickTime gamma shift
    use_s_curve_contrast: bool = True
    
    # Performance & Cache Defaults
    timeline_proxy_resolution: float = 1.0  # 1.0 (Full), 0.5 (Half), 0.25 (Quarter)
    render_cache_format: str = "ProRes_422_HQ"
    cache_auto_delete_days: int = 7
    background_caching_idle_seconds: float = 3.0
    
    # Delivery Safety Flags
    force_highest_quality_on_deliver: bool = True
    use_render_cache_on_deliver: bool = False
    
    def toggle_vertical(self):
        """1-Click Portrait swap for Shorts / Reels / TikTok."""
        self.width, self.height = self.height, self.width
        self.aspect_ratio = AspectRatioPreset.PORTRAIT_9_16 if self.width < self.height else AspectRatioPreset.WIDESCREEN_16_9
