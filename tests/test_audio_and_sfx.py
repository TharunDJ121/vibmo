"""
Unit tests for audio analysis, procedural sound synthesis, and audio visualizers.
"""

import os
import tempfile
import numpy as np
import pytest
from vibmo.audio.track import AudioTrack
from vibmo.audio.track import TimelineAudioClip
from vibmo.render.ffmpeg import FFmpegPipeWriter
from vibmo.audio.analyzer import AudioAnalyzer
from vibmo.audio.sfx import ProceduralSFX, SFXTrack
from vibmo.audio.library import generate_procedural_backing_track
from vibmo.audio.visualizers import (
    SpectrumBars,
    CircularSpectrum,
    WaveformRibbon,
    VinylRecord,
    AudioProgressBar,
)


def test_procedural_sfx_all_sounds():
    sounds = ["pop", "click", "whoosh", "riser", "bass_drop", "sparkle"]
    for snd in sounds:
        arr = ProceduralSFX.generate(snd)
        assert isinstance(arr, np.ndarray)
        assert arr.ndim == 1
        assert len(arr) > 100
        assert np.max(np.abs(arr)) <= 2.5




def test_sfx_track_mixing():
    track = SFXTrack(sample_rate=48000)
    track.add("pop", time=0.1, volume=0.8)
    track.add("whoosh", time=0.5, volume=0.9)

    temp_wav = os.path.join(tempfile.gettempdir(), "test_sfx_mix.wav")
    try:
        out_path = track.render_to_wav(duration=1.0, output_path=temp_wav)
        assert os.path.exists(out_path)
        assert os.path.getsize(out_path) > 1000
    finally:
        if os.path.exists(temp_wav):
            os.remove(temp_wav)


def test_procedural_backing_track_synth():
    track_arr = generate_procedural_backing_track(genre="tech_ambient", duration=2.0)
    assert isinstance(track_arr, np.ndarray)
    assert len(track_arr) == int(2.0 * 44100)


def test_audio_analyzer_and_visualizers():
    # Synthetic test track
    track = AudioTrack("dummy_synth.wav")
    analyzer = AudioAnalyzer(track)

    spec = analyzer.get_spectrum(time=0.5)
    assert len(spec) > 0
    assert analyzer.bass(0.5) >= 0.0

    # Visualizers
    bars = SpectrumBars(audio=track, bar_count=16)
    circ = CircularSpectrum(audio=track, radius=120)
    wave = WaveformRibbon(audio=track)
    vinyl = VinylRecord(radius=100)
    prog = AudioProgressBar(duration=5.0)

    assert bars is not None
    assert circ is not None
    assert wave is not None
    assert vinyl is not None
    assert prog is not None


def test_timeline_audio_clip_builds_a_timed_mix_filter(tmp_path):
    audio_path = tmp_path / "voiceover.wav"
    audio_path.touch()
    clip = TimelineAudioClip(
        str(audio_path), start=1.25, duration=3.0, volume=0.8, fade_in=0.2, fade_out=0.5
    )
    chain = clip.ffmpeg_filter(1, "a1")
    assert "atrim=duration=3.000000" in chain
    assert "adelay=1250:all=1" in chain
    assert chain.endswith("[a1]")

    # Build without spawning FFmpeg; command generation is the unit under test.
    writer = object.__new__(FFmpegPipeWriter)
    writer.output_path = str(tmp_path / "mix.mp4")
    writer.width = 1920
    writer.height = 1080
    writer.fps = 60.0
    writer.preset = "mp4"
    writer.audio_path = None
    writer.audio_tracks = [clip]
    writer.crf = 18
    command = writer._build_command()
    assert any("amix=inputs=1:duration=longest:normalize=0[aout]" in item for item in command)
    assert command.count("-map") == 2

    writer.audio_path = str(audio_path)
    writer.audio_tracks = [clip]
    command = writer._build_command()
    assert any("amix=inputs=1" in item for item in command)
