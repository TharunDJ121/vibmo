"""
Unit tests for AutoReframe and SilenceCutter.
"""

import pytest
from vibmo.video_post.auto_reframe import AutoReframe, ReframePlan
from vibmo.video_post.silence_cutter import SilenceCutter, SilenceInterval


def test_auto_reframe_crop_calculation():
    # 1920x1080 (16:9) to portrait (9:16)
    plan = AutoReframe.calculate_crop(1920, 1080, target_aspect="portrait", center_x_ratio=0.5)
    assert isinstance(plan, ReframePlan)
    assert plan.crop_height == 1080
    assert plan.crop_width == 606 or plan.crop_width == 608 or abs(plan.crop_width - 607) <= 2
    assert "crop=" in plan.ffmpeg_filter

    # 1920x1080 to square (1:1)
    plan_sq = AutoReframe.calculate_crop(1920, 1080, target_aspect="square")
    assert plan_sq.crop_height == 1080
    assert plan_sq.crop_width == 1080


def test_silence_cutter_speech_intervals():
    intervals = [
        SilenceInterval(start_time=2.0, end_time=3.5, duration=1.5),
        SilenceInterval(start_time=7.0, end_time=8.2, duration=1.2),
    ]
    speech = SilenceCutter.calculate_active_speech_intervals(total_duration=10.0, silence_intervals=intervals)
    assert len(speech) >= 2
