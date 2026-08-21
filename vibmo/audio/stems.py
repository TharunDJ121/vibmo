"""
Multi-Track Audio Mixing, Stem Separation, and Foley Automation.
"""

from __future__ import annotations
import os
import subprocess
from typing import Any, Dict, List, Optional
from vibmo.audio.track import TimelineAudioClip


class AudioStemMixer:
    """
    Groups timeline audio tracks by stem category (Music, VO, SFX, Foley)
    and mixes them into isolated multi-track broadcast stems.
    """

    @classmethod
    def mix_stems(
        cls,
        audio_clips: List[TimelineAudioClip],
        duration: float,
        output_dir: str,
    ) -> Dict[str, str]:
        """Mixes and exports categorized stems as WAV files."""
        os.makedirs(output_dir, exist_ok=True)
        stems_map: Dict[str, List[TimelineAudioClip]] = {
            "music": [],
            "vo": [],
            "sfx": [],
            "master": list(audio_clips),
        }

        for clip in audio_clips:
            name_lower = (clip.name or clip.file_path).lower()
            if any(k in name_lower for k in ("music", "song", "bgm", "beat", "track")):
                stems_map["music"].append(clip)
            elif any(k in name_lower for k in ("vo", "voice", "speech", "narration", "dialogue")):
                stems_map["vo"].append(clip)
            else:
                stems_map["sfx"].append(clip)

        generated_files: Dict[str, str] = {}
        for stem_name, clips in stems_map.items():
            if not clips and stem_name != "master":
                continue
            out_file = os.path.join(output_dir, f"stem_{stem_name}.wav")
            cls._render_stem_ffmpeg(clips, duration, out_file)
            if os.path.exists(out_file):
                generated_files[stem_name] = os.path.abspath(out_file)

        return generated_files

    @classmethod
    def _render_stem_ffmpeg(
        cls,
        clips: List[TimelineAudioClip],
        duration: float,
        out_path: str,
    ) -> None:
        if not clips:
            # Generate silent WAV
            cmd = [
                "ffmpeg", "-y", "-f", "lavfi", "-i", f"anullsrc=r=44100:cl=stereo",
                "-t", f"{duration:.3f}", "-c:a", "pcm_s16le", out_path
            ]
            try:
                subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
            except Exception:
                pass
            return

        cmd = ["ffmpeg", "-y"]
        filter_parts = []
        for i, clip in enumerate(clips):
            cmd.extend(["-i", clip.file_path])
            label = f"a{i}"
            filter_parts.append(clip.ffmpeg_filter(i, label))

        if len(clips) > 1:
            inputs_str = "".join(f"[a{i}]" for i in range(len(clips)))
            filter_parts.append(f"{inputs_str}amix=inputs={len(clips)}:duration=longest:dropout_transition=0[out]")
            final_label = "[out]"
        else:
            final_label = "[a0]"

        cmd.extend([
            "-filter_complex", ";".join(filter_parts),
            "-map", final_label,
            "-t", f"{duration:.3f}",
            "-c:a", "pcm_s16le",
            out_path,
        ])

        try:
            subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
        except Exception:
            pass
