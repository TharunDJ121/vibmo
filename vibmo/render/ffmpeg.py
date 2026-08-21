"""
High-speed video and animated GIF export pipeline via direct FFmpeg streaming pipe.
"""

from __future__ import annotations
import subprocess
import os
import shutil
import numpy as np
from typing import Any, Optional, Sequence


class FFmpegPipeWriter:
    """Streams raw RGBA frame buffers directly into FFmpeg encoder subprocess."""

    def __init__(
        self,
        output_path: str,
        width: int,
        height: int,
        fps: float = 60.0,
        preset: str = "mp4",
        audio_path: Optional[str] = None,
        audio_tracks: Optional[Sequence[Any]] = None,
        crf: int = 18,
    ) -> None:
        self.output_path = output_path
        self.width = width
        self.height = height
        self.fps = fps
        self.preset = preset.lower()
        self.audio_path = audio_path
        self.audio_tracks = list(audio_tracks or [])
        self.crf = crf
        self.process: Optional[subprocess.Popen] = None
        self._start_ffmpeg()

    def _start_ffmpeg(self) -> None:
        cmd = self._build_command()
        self.process = subprocess.Popen(
            cmd,
            stdin=subprocess.PIPE,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.PIPE,
        )

    def _build_command(self) -> list[str]:
        """Constructs the encoder command, keeping timeline audio declarative."""
        ffmpeg_bin = shutil.which("ffmpeg") or "ffmpeg"

        # Base input from stdin (raw RGBA video stream)
        cmd = [
            ffmpeg_bin,
            "-y",
            "-loglevel", "error",
            "-f", "rawvideo",
            "-vcodec", "rawvideo",
            "-s", f"{self.width}x{self.height}",
            "-pix_fmt", "rgba",
            "-r", str(self.fps),
            "-i", "-",  # stdin
        ]

        audio_tracks = [track for track in self.audio_tracks if os.path.exists(track.file_path)]
        if self.audio_path and os.path.exists(self.audio_path) and not any(
            os.path.abspath(track.file_path) == os.path.abspath(self.audio_path) for track in audio_tracks
        ):
            from vibmo.audio.track import TimelineAudioClip
            # Preserve backwards-compatible ``add_audio`` as the bed track
            # when it is combined with new timeline clips.
            audio_tracks.insert(0, TimelineAudioClip(self.audio_path, name="Main audio"))

        for track in audio_tracks:
            cmd.extend(["-i", track.file_path])

        ext = os.path.splitext(self.output_path)[1].lower()
        has_audio = bool(audio_tracks) and not (ext == ".gif" or self.preset == "gif")
        if has_audio:
            filters = [track.ffmpeg_filter(index, f"a{index}") for index, track in enumerate(audio_tracks, start=1)]
            input_labels = "".join(f"[a{index}]" for index in range(1, len(audio_tracks) + 1))
            filters.append(f"{input_labels}amix=inputs={len(audio_tracks)}:duration=longest:normalize=0[aout]")
            cmd.extend(["-filter_complex", ";".join(filters), "-map", "0:v", "-map", "[aout]"])

        # Output encoding settings based on preset / extension
        if ext == ".gif" or self.preset == "gif":
            # High-quality 2-pass palette GIF filter
            cmd.extend([
                "-filter_complex", "[0:v] split [a][b];[a] palettegen=reserve_transparent=on:transparency_color=ffffff [p];[b][p] paletteuse=dither=bayer:bayer_scale=3",
                self.output_path,
            ])
        elif ext == ".webm" or self.preset == "webm":
            # VP9 with Alpha channel transparency
            cmd.extend([
                "-c:v", "libvpx-vp9",
                "-pix_fmt", "yuva420p",
                "-crf", str(self.crf),
                "-b:v", "0",
            ])
            if has_audio:
                cmd.extend(["-c:a", "libopus", "-b:a", "128k", "-shortest"])
            cmd.append(self.output_path)
        elif self.preset == "prores" or ext == ".mov":
            # Apple ProRes 4444 with Alpha
            cmd.extend([
                "-c:v", "prores_ks",
                "-profile:v", "4",  # 4444
                "-pix_fmt", "yuva444p10le",
            ])
            if has_audio:
                cmd.extend(["-c:a", "pcm_s16le", "-shortest"])
            cmd.append(self.output_path)
        else:
            # Standard H.264 MP4 (fast, compatible everywhere, instant web streaming)
            cmd.extend([
                "-c:v", "libx264",
                "-pix_fmt", "yuv420p",
                "-preset", "fast",
                "-crf", str(self.crf),
                "-movflags", "+faststart",
            ])
            if has_audio:
                cmd.extend(["-c:a", "aac", "-b:a", "192k", "-shortest"])
            cmd.append(self.output_path)


        return cmd

    def write_frame(self, rgba_frame: np.ndarray) -> None:
        """Writes a single (H, W, 4) uint8 numpy array to ffmpeg stdin."""
        if self.process and self.process.stdin:
            self.process.stdin.write(rgba_frame.tobytes())

    def close(self) -> None:
        """Closes stdin and waits for FFmpeg to finish encoding."""
        if self.process:
            if self.process.stdin:
                self.process.stdin.close()
                # ``communicate()`` flushes stdin when it is still attached.
                # It raises ValueError when that stream has already been closed.
                self.process.stdin = None
            _, stderr = self.process.communicate()
            if self.process.returncode != 0:
                err_msg = stderr.decode("utf-8", errors="replace")
                raise RuntimeError(f"FFmpeg error (code {self.process.returncode}): {err_msg}")
            self.process = None
