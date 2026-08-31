"""
Audio Track analysis, FFT frequency extraction, beat detection, visualizers, procedural SFX, and ducking.
"""

from vibmo.audio.track import AudioTrack, TimelineAudioClip
from vibmo.audio.analyzer import AudioAnalyzer
from vibmo.audio.sfx import ProceduralSFX, SFXTrack
from vibmo.audio.library import CURATED_AUDIO_PRESETS, fetch_online_audio
from vibmo.audio.visualizers import (
    SpectrumBars,
    CircularSpectrum,
    WaveformRibbon,
    VinylRecord,
    AudioProgressBar,
)
from vibmo.audio.visualization import (
    SpectrumVisualizer,
    CircularEqualizer,
    AudioReactivePulse,
)
from vibmo.audio.sfx_library import (
    ProceduralSFXGenerator,
    AudioDucker,
)
from vibmo.audio.energy import (
    AudioEnergyAnalyzer,
    AudioEnergyProfile,
    EnergyFrame,
)
from vibmo.audio.ducker import (
    VoiceoverDucker,
    VoiceoverSegment,
)
from vibmo.audio.beat_sync import (
    BeatSyncGrid,
    TimelineSFXTable,
    SFXCue,
)

__all__ = [
    "AudioTrack",
    "TimelineAudioClip",
    "AudioAnalyzer",
    "ProceduralSFX",
    "SFXTrack",
    "CURATED_AUDIO_PRESETS",
    "fetch_online_audio",
    "SpectrumBars",
    "CircularSpectrum",
    "WaveformRibbon",
    "VinylRecord",
    "AudioProgressBar",
    # Advanced Visualizers
    "SpectrumVisualizer",
    "CircularEqualizer",
    "AudioReactivePulse",
    # Procedural SFX & Ducking
    "ProceduralSFXGenerator",
    "AudioDucker",
    "AudioEnergyAnalyzer",
    "AudioEnergyProfile",
    "EnergyFrame",
    "VoiceoverDucker",
    "VoiceoverSegment",
    "BeatSyncGrid",
    "TimelineSFXTable",
    "SFXCue",
]

