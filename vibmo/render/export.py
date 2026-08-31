"""
High-Level Multi-Format Video Exporter with quality presets, batch rendering, and format converters.
"""

from __future__ import annotations
import os
from typing import Any, Callable, Dict, List, Optional, Sequence, Union, TYPE_CHECKING
from enum import Enum
from dataclasses import dataclass

if TYPE_CHECKING:
    from vibmo.scene.scene import Scene


class ExportQuality(Enum):
    DRAFT = "draft"
    PREVIEW = "preview"
    HIGH = "high"
    FOUR_K = "4k60"
    TRANSPARENT_WEBM = "transparent_webm"
    GIF = "gif"


@dataclass
class QualityPreset:
    width: int
    height: int
    fps: int
    crf: int
    codec: str
    preset: str


QUALITY_PRESETS: Dict[str, QualityPreset] = {
    "draft": QualityPreset(width=854, height=480, fps=30, crf=28, codec="libx264", preset="ultrafast"),
    "preview": QualityPreset(width=1280, height=720, fps=30, crf=23, codec="libx264", preset="veryfast"),
    "high": QualityPreset(width=1920, height=1080, fps=60, crf=18, codec="libx264", preset="medium"),
    "4k60": QualityPreset(width=3840, height=2160, fps=60, crf=16, codec="libx264", preset="slow"),
    "transparent_webm": QualityPreset(width=1920, height=1080, fps=60, crf=20, codec="libvpx-vp9", preset="good"),
    "gif": QualityPreset(width=800, height=450, fps=24, crf=0, codec="gif", preset="medium"),
}


class Exporter:
    """
    Unified multi-format exporter for single scenes and batch queues.
    """

    @classmethod
    def export(
        cls,
        scene: Scene,
        output_path: str = "output.mp4",
        quality: Union[str, ExportQuality] = ExportQuality.HIGH,
        engine: str = "local",
        on_progress: Optional[Callable[[float], None]] = None,
    ) -> str:
        """Export a Scene to video file using the specified quality preset."""
        q_key = quality.value if isinstance(quality, ExportQuality) else str(quality).lower()
        preset = QUALITY_PRESETS.get(q_key, QUALITY_PRESETS["high"])

        # Override scene dimensions/fps if preset differs
        original_w, original_h, original_fps = scene.width, scene.height, scene.fps
        scene.width = preset.width
        scene.height = preset.height
        scene.fps = preset.fps

        try:
            if engine == "lambda":
                from vibmo.render.cloud.lambda_orchestrator import CloudRenderOrchestrator
                CloudRenderOrchestrator.run(scene, output_path)
                return output_path
            else:
                res = scene.render(output_path=output_path, on_progress=on_progress)
                return output_path
        finally:
            scene.width = original_w
            scene.height = original_h
            scene.fps = original_fps

    @classmethod
    def batch_render(
        cls,
        scenes: Sequence[Tuple[Scene, str]],  # (scene, output_filename)
        output_dir: str = "output",
        quality: Union[str, ExportQuality] = ExportQuality.HIGH,
        on_scene_complete: Optional[Callable[[int, int, str], None]] = None,
    ) -> List[str]:
        """Batch render multiple scenes sequentially."""
        os.makedirs(output_dir, exist_ok=True)
        rendered = []
        total = len(scenes)

        for i, (sc, fname) in enumerate(scenes):
            out_file = os.path.join(output_dir, fname)
            cls.export(sc, output_path=out_file, quality=quality)
            rendered.append(out_file)
            if on_scene_complete:
                on_scene_complete(i + 1, total, out_file)

        return rendered
