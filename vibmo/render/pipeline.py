"""
Render Pipeline coordinating frame generation, multi-processing, progress display, and FFmpeg output.
"""

from __future__ import annotations
import math
import numpy as np
from PIL import Image
from typing import Any, List, Optional
import os
import concurrent.futures
from rich.progress import Progress, BarColumn, TextColumn, TimeRemainingColumn, SpinnerColumn
from vibmo.render.rasterizer import Rasterizer
from vibmo.render.ffmpeg import FFmpegPipeWriter


_worker_scene: Any = None


def _init_worker(scene: Any) -> None:
    global _worker_scene
    _worker_scene = scene


def _render_frame_task(
    t: float,
    width: int,
    height: int,
    motion_blur: bool,
    shutter_angle: float,
) -> np.ndarray:
    """Worker function to render a single frame using process-local scene instance."""
    global _worker_scene
    scene = _worker_scene
    rasterizer = Rasterizer(width, height)
    if motion_blur:
        return rasterizer.render_frame_with_motion_blur(
            root_nodes=scene.nodes,
            time=t,
            fps=scene.fps,
            shutter_angle=shutter_angle,
            background=scene.background,
            camera=scene.camera,
            post_fx=scene.post_fx,
        )
    else:
        return rasterizer.render_frame(
            root_nodes=scene.nodes,
            time=t,
            background=scene.background,
            camera=scene.camera,
            post_fx=scene.post_fx,
        )


class Pipeline:
    """Orchestrates frame rendering and video encoding."""

    def __init__(self, scene: Any) -> None:
        self.scene = scene

    def render_to_file(
        self,
        output_path: str,
        preset: str = "mp4",
        quality: str = "high",
        motion_blur: bool = False,
        shutter_angle: float = 180.0,
        show_progress: bool = True,
        max_workers: Optional[int] = None,
        resume: bool = False,
    ) -> None:
        # Prevent OpenBLAS/OMP thread bombs inside workers
        os.environ["OPENBLAS_NUM_THREADS"] = "1"
        os.environ["OMP_NUM_THREADS"] = "1"
        os.environ["MKL_NUM_THREADS"] = "1"
        os.environ["NUMEXPR_NUM_THREADS"] = "1"

        render_w = self.scene.width
        render_h = self.scene.height
        render_fps = self.scene.fps

        if quality == "draft":
            render_w = max(320, int(self.scene.width * 0.5))
            render_h = max(180, int(self.scene.height * 0.5))
            render_fps = min(30.0, self.scene.fps * 0.5)
            motion_blur = False
        elif quality == "fast":
            render_w = max(640, int(self.scene.width * 0.667))
            render_h = max(360, int(self.scene.height * 0.667))
            render_fps = min(30.0, self.scene.fps)

        if max_workers is None:
            max_workers = min(max(1, (os.cpu_count() or 2) - 1), 16)

        total_frames = max(1, int(math.ceil(self.scene.duration * render_fps)))
        dt = 1.0 / render_fps

        cache_dir = None
        if resume:
            stem = os.path.splitext(os.path.basename(output_path))[0]
            cache_dir = os.path.join(".vibmo_cache", stem)
            os.makedirs(cache_dir, exist_ok=True)

        audio_path = getattr(self.scene, "audio_path", None)
        audio_tracks = getattr(self.scene, "audio_tracks", None)
        writer = FFmpegPipeWriter(
            output_path=output_path,
            width=render_w,
            height=render_h,
            fps=render_fps,
            preset=preset,
            audio_path=audio_path,
            audio_tracks=audio_tracks,
        )

        with Progress(
            TextColumn("[bold cyan]Rendering {task.fields[filename]}[/bold cyan]"),
            BarColumn(complete_style="green", finished_style="bold green"),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            TextColumn("•"),
            TextColumn("{task.completed}/{task.total} frames"),
            TextColumn("•"),
            TextColumn("[yellow]{task.fields[workers]} cores[/yellow]"),
            TextColumn("•"),
            TimeRemainingColumn(),
            disable=not show_progress,
        ) as progress:
            task = progress.add_task("render", total=total_frames, filename=output_path, workers=max_workers)

            if max_workers > 1:
                with concurrent.futures.ProcessPoolExecutor(
                    max_workers=max_workers,
                    initializer=_init_worker,
                    initargs=(self.scene,),
                ) as executor:
                    chunk_size = max_workers * 4
                    for chunk_start in range(0, total_frames, chunk_size):
                        chunk_end = min(total_frames, chunk_start + chunk_size)
                        
                        futures = []
                        cached_frames = {}
                        for i in range(chunk_start, chunk_end):
                            frame_cache_path = os.path.join(cache_dir, f"f_{i:06d}.raw") if cache_dir else None
                            if frame_cache_path and os.path.exists(frame_cache_path):
                                with open(frame_cache_path, "rb") as f:
                                    cached_frames[i] = np.frombuffer(f.read(), dtype=np.uint8).reshape((render_h, render_w, 4))
                                futures.append((i, None))
                            else:
                                fut = executor.submit(
                                    _render_frame_task,
                                    i * dt,
                                    render_w,
                                    render_h,
                                    motion_blur,
                                    shutter_angle,
                                )
                                futures.append((i, fut))
                        
                        # Process chunk strictly in order
                        for idx, future in futures:
                            if future is None:
                                rgba = cached_frames[idx]
                            else:
                                rgba = future.result()
                                if cache_dir:
                                    fpath = os.path.join(cache_dir, f"f_{idx:06d}.raw")
                                    with open(fpath, "wb") as f:
                                        f.write(rgba.tobytes())
                            writer.write_frame(rgba)
                            progress.advance(task)
            else:
                _init_worker(self.scene)
                for i in range(total_frames):
                    frame_cache_path = os.path.join(cache_dir, f"f_{i:06d}.raw") if cache_dir else None
                    if frame_cache_path and os.path.exists(frame_cache_path):
                        with open(frame_cache_path, "rb") as f:
                            rgba = np.frombuffer(f.read(), dtype=np.uint8).reshape((render_h, render_w, 4))
                    else:
                        rgba = _render_frame_task(
                            i * dt, render_w, render_h, motion_blur, shutter_angle
                        )
                        if cache_dir:
                            with open(frame_cache_path, "wb") as f:
                                f.write(rgba.tobytes())
                    writer.write_frame(rgba)
                    progress.advance(task)

        writer.close()
        
        # Cleanup cache upon successful complete render
        if cache_dir and os.path.exists(cache_dir):
            import shutil
            try:
                shutil.rmtree(cache_dir)
            except Exception:
                pass
