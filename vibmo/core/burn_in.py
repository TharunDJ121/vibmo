import datetime
from dataclasses import dataclass
from typing import Dict, Any

@dataclass
class BurnInConfig:
    text: str
    font: str = "monospace"
    size: int = 24
    color: str = "#FFFFFF"
    opacity: float = 1.0
    bg_color: str = "#000000"
    bg_opacity: float = 0.5
    x: float = 10.0
    y: float = 10.0

class Variables:
    """Dynamic string interpolation engine for metadata replacement."""
    
    @staticmethod
    def evaluate(text: str, context: Dict[str, Any]) -> str:
        now = datetime.datetime.now()
        replacements = {
            "%date": now.strftime("%Y-%m-%d"),
            "%time": now.strftime("%H:%M:%S"),
            "%clipName": context.get("clip_name", "Unknown"),
            "%timecode": context.get("timecode", "00:00:00:00"),
            "%resolution": context.get("resolution", "1920x1080"),
        }
        for key, val in replacements.items():
            text = text.replace(key, str(val))
        return text

class DataBurnIn:
    """Post-processing node that renders text/logo overlays."""
    
    def __init__(self, config: BurnInConfig):
        self.config = config

    def apply(self, frame_buffer: Any, context: Dict[str, Any]) -> Any:
        evaluated_text = Variables.evaluate(self.config.text, context)
        # Placeholder for actual rasterization logic (e.g., Cairo/Pillow)
        # to draw the evaluated_text over the frame_buffer
        return frame_buffer
