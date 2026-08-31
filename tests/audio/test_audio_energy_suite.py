"""
Unit tests for Vibmo Audio Energy & Voiceover Ducker.
"""

import pytest
from vibmo.audio.energy import AudioEnergyAnalyzer, AudioEnergyProfile
from vibmo.audio.ducker import VoiceoverDucker, VoiceoverSegment


def test_audio_energy_analyzer_synthetic():
    profile = AudioEnergyAnalyzer.analyze("non_existent.mp3", video_duration=6.0)
    assert isinstance(profile, AudioEnergyProfile)
    assert profile.duration == 6.0
    assert len(profile.frames) > 0
    loudness = profile.get_loudness_at(3.0)
    assert isinstance(loudness, float)


def test_voiceover_ducker():
    ducker = VoiceoverDucker(normal_volume=1.0, ducked_volume=0.2, fade_in_time=0.3, fade_out_time=0.2)
    segments = [(2.0, 4.0)]

    # At t=0.0 -> no voiceover, full volume
    vol_0 = ducker.compute_volume_at(0.0, segments)
    assert vol_0 == 1.0

    # At t=3.0 -> middle of voiceover, fully ducked
    vol_3 = ducker.compute_volume_at(3.0, segments)
    assert vol_3 == 0.2

    # At t=1.85 -> in the fade-in window, volume between 0.2 and 1.0
    vol_fade = ducker.compute_volume_at(1.85, segments)
    assert 0.2 < vol_fade < 1.0

    # At t=5.0 -> after release, full volume again
    vol_5 = ducker.compute_volume_at(5.0, segments)
    assert vol_5 == 1.0
