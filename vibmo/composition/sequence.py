"""
Multi-Scene Sequence composition and transition engine for modular motion graphics.
"""

from __future__ import annotations
import math
import numpy as np
from typing import Any, List, Optional, Sequence as PySequence, Tuple, Union
from PIL import Image

from vibmo.core.easing import Ease, EasingFunc
from vibmo.scene.scene import Scene
from vibmo.render.pipeline import Pipeline


class Transition:
    """Base class for visual transitions between sequential scenes."""

    def __init__(self, duration: float = 0.5) -> None:
        self.duration = float(duration)

    def blend(self, img_a: np.ndarray, img_b: np.ndarray, progress: float) -> np.ndarray:
        raise NotImplementedError


class CrossFade(Transition):
    """Smooth cross-dissolve opacity blend between two scenes."""

    def blend(self, img_a: np.ndarray, img_b: np.ndarray, progress: float) -> np.ndarray:
        p = max(0.0, min(1.0, float(progress)))
        out = (img_a.astype(np.float32) * (1.0 - p) + img_b.astype(np.float32) * p).astype(np.uint8)
        return out


class Slide(Transition):
    """Directional slide transition pushing scene A off screen with scene B."""

    def __init__(self, direction: str = "left", duration: float = 0.6, ease: EasingFunc = Ease.out_expo) -> None:
        super().__init__(duration=duration)
        self.direction = direction.lower()
        self.ease = ease

    def blend(self, img_a: np.ndarray, img_b: np.ndarray, progress: float) -> np.ndarray:
        p = self.ease(max(0.0, min(1.0, float(progress))))
        h, w, _ = img_a.shape
        out = np.zeros_like(img_a)

        if self.direction == "left":
            shift = int(w * p)
            if shift < w:
                out[:, : w - shift] = img_a[:, shift:]
            if shift > 0:
                out[:, w - shift :] = img_b[:, :shift]
        elif self.direction == "right":
            shift = int(w * p)
            if shift < w:
                out[:, shift:] = img_a[:, : w - shift]
            if shift > 0:
                out[:, :shift] = img_b[:, w - shift :]
        elif self.direction == "up":
            shift = int(h * p)
            if shift < h:
                out[: h - shift, :] = img_a[shift:, :]
            if shift > 0:
                out[h - shift :, :] = img_b[:shift, :]
        else:  # down
            shift = int(h * p)
            if shift < h:
                out[shift:, :] = img_a[: h - shift, :]
            if shift > 0:
                out[:shift, :] = img_b[h - shift :, :]

        return out


class Sequence:
    """
    Chains independently rendered scenes into a video with explicit transitions.

    For animation that must preserve layer and camera state across a shot
    boundary, use :class:`vibmo.composition.composition.Composition` instead.
    """

    def __init__(
        self,
        *scenes: Scene,
        transition: Optional[Transition] = None,
        audio_path: Optional[str] = None,
    ) -> None:
        if not scenes:
            raise ValueError("Sequence requires at least one Scene.")
        
        self.scenes: List[Scene] = list(scenes)
        self.default_transition = transition or CrossFade(duration=0.5)
        self.width = self.scenes[0].width
        self.height = self.scenes[0].height
        self.fps = self.scenes[0].fps
        self.audio_path = audio_path or getattr(self.scenes[0], "audio_path", None)
        self.sfx_cues: List[Tuple[str, float, float, Optional[float]]] = []
        self.bg_tracks: List[Tuple[str, float, float]] = []

        # Compute total duration accounting for transitions
        self.scene_starts: List[float] = []
        cur_t = 0.0
        for i, s in enumerate(self.scenes):
            self.scene_starts.append(cur_t)
            trans_dur = self.default_transition.duration if i < len(self.scenes) - 1 else 0.0
            cur_t += max(0.1, s.duration - trans_dur)

        self.duration = cur_t
        self.total_duration = cur_t

    def add_sfx(
        self,
        audio: str,
        time: float = 0.0,
        volume: float = 1.0,
        duration: Optional[float] = None,
    ) -> Sequence:
        """Schedules a sound effect cue at timeline timestamp."""
        self.sfx_cues.append((audio, float(time), float(volume), duration))
        return self

    def add_bg_music(
        self,
        audio: str,
        start_time: float = 0.0,
        volume: float = 0.25,
    ) -> Sequence:
        """Adds a background soundtrack layer at timeline timestamp."""
        self.bg_tracks.append((audio, float(start_time), float(volume)))
        return self

    def mix_soundtrack(self, sample_rate: int = 48000) -> Optional[str]:
        """Automatically mixes all background music and SFX cues into a broadcast WAV."""
        if not self.sfx_cues and not self.bg_tracks:
            return self.audio_path

        import os
        import subprocess
        from scipy.io import wavfile
        from vibmo.audio.library import fetch_online_audio

        n_samples = int(self.duration * sample_rate)
        master = np.zeros(n_samples, dtype=np.float32)

        def mix_file(file_or_preset: str, start_time: float, volume: float, max_dur: Optional[float] = None):
            resolved = fetch_online_audio(file_or_preset)
            if not resolved or not os.path.exists(resolved):
                return

            # If MP3/OGG, convert to temporary WAV for fast linear mixing
            ext = os.path.splitext(resolved)[1].lower()
            wav_path = resolved
            if ext in (".mp3", ".ogg", ".m4a", ".aac"):
                wav_path = os.path.splitext(resolved)[0] + "_converted.wav"
                if not os.path.exists(wav_path):
                    try:
                        subprocess.run(["ffmpeg", "-y", "-i", resolved, "-ar", str(sample_rate), "-ac", "1", wav_path], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                    except Exception:
                        wav_path = resolved

            try:
                sr, data = wavfile.read(wav_path)
                if data.dtype == np.int16:
                    arr = data.astype(np.float32) / 32767.0
                else:
                    arr = data.astype(np.float32)
                if arr.ndim > 1:
                    arr = np.mean(arr, axis=1)

                if max_dur:
                    arr = arr[:int(max_dur * sr)]

                s_idx = int(start_time * sample_rate)
                e_idx = min(s_idx + len(arr), n_samples)
                clip_len = e_idx - s_idx
                if clip_len > 0 and s_idx < n_samples:
                    master[s_idx:e_idx] += arr[:clip_len] * volume
            except Exception:
                pass

        # Mix background music
        for track, st, vol in self.bg_tracks:
            mix_file(track, st, vol)

        # Mix SFX cues
        for sfx, st, vol, dur in self.sfx_cues:
            mix_file(sfx, st, vol, dur)

        # Normalize
        peak = np.max(np.abs(master))
        if peak > 1e-4:
            master = master / peak * 0.94
        pcm16 = (master * 32767.0).astype(np.int16)

        cache_dir = os.path.join(os.getcwd(), ".vibmo_cache")
        os.makedirs(cache_dir, exist_ok=True)
        out_soundtrack = os.path.join(cache_dir, "sequence_soundtrack.wav")
        wavfile.write(out_soundtrack, sample_rate, pcm16)
        self.audio_path = out_soundtrack
        return out_soundtrack


    def render_frame(self, time: float, scale: float = 1.0) -> np.ndarray:
        """Evaluates and renders the composite frame at timestamp t."""
        t = max(0.0, min(self.duration, float(time)))

        def render_scene(scene: Scene, local_time: float) -> np.ndarray:
            return scene._rasterizer.render_frame(
                root_nodes=scene.nodes,
                time=max(0.0, min(scene.duration, local_time)),
                background=scene.background,
                camera=scene.camera,
                post_fx=scene.post_fx,
                scale=scale,
            )

        # Locate active scene. A transition begins at the next scene's start
        for i, scene_i in enumerate(self.scenes):
            start_i = self.scene_starts[i]
            local_t = t - start_i
            is_last = i == len(self.scenes) - 1

            if is_last:
                return render_scene(scene_i, local_t)

            next_start = self.scene_starts[i + 1]
            if t < next_start:
                return render_scene(scene_i, local_t)

            transition_end = start_i + scene_i.duration
            if t < transition_end:
                next_scene = self.scenes[i + 1]
                progress = (t - next_start) / self.default_transition.duration
                frame_a = render_scene(scene_i, local_t)
                frame_b = render_scene(next_scene, t - next_start)
                return self.default_transition.blend(frame_a, frame_b, progress)

        # Fallback to last scene end frame
        last_s = self.scenes[-1]
        return last_s._rasterizer.render_frame(
            root_nodes=last_s.nodes,
            time=last_s.duration,
            background=last_s.background,
            camera=last_s.camera,
            post_fx=last_s.post_fx,
            scale=scale,
        )

    def validate(self) -> List[str]:
        """Checks compatibility before rendering a raster-frame sequence."""
        issues: List[str] = []
        for index, scene in enumerate(self.scenes[1:], start=1):
            if scene.width != self.width or scene.height != self.height:
                issues.append(
                    f"Scene {index + 1} is {scene.width}x{scene.height}; expected {self.width}x{self.height}."
                )
            if scene.fps != self.fps:
                issues.append(f"Scene {index + 1} uses {scene.fps} FPS; expected {self.fps} FPS.")

        for index, scene in enumerate(self.scenes[:-1]):
            if self.default_transition.duration >= scene.duration:
                issues.append(
                    f"Transition after scene {index + 1} ({self.default_transition.duration:.2f}s) "
                    f"must be shorter than that scene ({scene.duration:.2f}s)."
                )
        if any(getattr(scene, "audio_path", None) for scene in self.scenes[1:]):
            issues.append("Sequence only muxes one audio file; use Composition for a continuous multi-track soundtrack.")
        return issues

    def storyboard(self, path: Optional[str] = "storyboard.png", rows: int = 2, cols: int = 3) -> Image.Image:
        """Generates a contact sheet covering the full multi-scene sequence progression."""
        from PIL import ImageDraw
        
        n_frames = rows * cols
        thumb_w, thumb_h = 480, 270
        header_h = 24
        pad = 20
        sheet_w = pad + cols * (thumb_w + pad)
        sheet_h = pad + rows * (thumb_h + header_h + pad)
        sheet = Image.new("RGBA", (sheet_w, sheet_h), (9, 13, 22, 255))
        draw = ImageDraw.Draw(sheet)

        times = np.linspace(0.0, max(0.1, self.duration - 0.01), n_frames)

        for i, t in enumerate(times):
            r = i // cols
            c = i % cols
            x = pad + c * (thumb_w + pad)
            y = pad + r * (thumb_h + header_h + pad)

            rgba = self.render_frame(float(t))
            frame_img = Image.fromarray(rgba, "RGBA").resize((thumb_w, thumb_h), Image.Resampling.BILINEAR)
            sheet.paste(frame_img, (x, y + header_h))

            time_label = f"t = {t:.2f}s ({int(t * self.fps)}f / {int(self.duration * self.fps)}f)"
            draw.text((x + 4, y + 6), time_label, fill=(241, 245, 249, 255))
            draw.rectangle([x, y + header_h, x + thumb_w, y + header_h + thumb_h], outline=(99, 102, 241, 200), width=2)

        if path:
            import os
            dir_name = os.path.dirname(path)
            if dir_name:
                os.makedirs(dir_name, exist_ok=True)
            sheet.save(path)
        return sheet

    def render(
        self,
        output_path: str = "output.mp4",
        preset: str = "mp4",
        quality: str = "high",
        show_progress: bool = True,
        max_workers: Optional[int] = None,
    ) -> None:
        """Renders the multi-scene sequence to video."""
        from vibmo.render.ffmpeg import FFmpegPipeWriter
        from rich.progress import Progress, BarColumn, TextColumn, TimeRemainingColumn
        import os

        # Mix sound cues and bg music if configured
        self.mix_soundtrack()

        render_w = self.width
        render_h = self.height
        render_fps = self.fps

        if quality == "draft":
            render_w = max(320, int(self.width * 0.5))
            render_h = max(180, int(self.height * 0.5))
            render_fps = min(30.0, self.fps * 0.5)
        elif quality == "fast":
            render_w = max(640, int(self.width * 0.667))
            render_h = max(360, int(self.height * 0.667))
            render_fps = min(30.0, self.fps)

        total_frames = max(1, int(math.ceil(self.duration * render_fps)))
        dt = 1.0 / render_fps

        writer = FFmpegPipeWriter(
            output_path=output_path,
            width=render_w,
            height=render_h,
            fps=render_fps,
            preset=preset,
            audio_path=self.audio_path,
        )

        with Progress(
            TextColumn("[bold cyan]Rendering Sequence {task.fields[filename]}[/bold cyan]"),
            BarColumn(complete_style="green", finished_style="bold green"),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            TextColumn("•"),
            TextColumn("{task.completed}/{task.total} frames"),
            TimeRemainingColumn(),
            disable=not show_progress,
        ) as progress:
            task = progress.add_task("render", total=total_frames, filename=output_path)
            for i in range(total_frames):
                rgba = self.render_frame(i * dt)
                if quality != "high":
                    img = Image.fromarray(rgba, "RGBA").resize((render_w, render_h), Image.Resampling.BILINEAR)
                    rgba = np.array(img)
                writer.write_frame(rgba)
                progress.advance(task)

        writer.close()

    def preview(self, host: str = "127.0.0.1", port: int = 8000) -> None:
        """Launches the interactive Web Studio in browser for this sequence."""
        from vibmo.studio.router import launch_studio
        launch_studio(self, host=host, port=port)
