"""
Rendering engine, Cairo vector rasterizer, GPU compositor, FFmpeg streaming pipelines, and multi-format exporter.
"""

from vibmo.render.rasterizer import Rasterizer
from vibmo.render.ffmpeg import FFmpegPipeWriter
from vibmo.render.pipeline import Pipeline
from vibmo.render.export import Exporter, ExportQuality, QUALITY_PRESETS
from vibmo.render.backend import RenderBackend, HybridRenderBackend, CPURenderBackend, get_optimal_backend
from vibmo.render.gpu.compositor import GPUCompositor
from vibmo.render.fcp_exporter import Fcp7Exporter
from vibmo.render.otio_exporter import OtioExporter

__all__ = [
    "Rasterizer",
    "FFmpegPipeWriter",
    "Pipeline",
    "Exporter",
    "ExportQuality",
    "QUALITY_PRESETS",
    "RenderBackend",
    "HybridRenderBackend",
    "CPURenderBackend",
    "get_optimal_backend",
    "GPUCompositor",
    "Fcp7Exporter",
    "OtioExporter",
]
