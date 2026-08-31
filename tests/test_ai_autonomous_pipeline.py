"""
Tests for AutonomousPipeline in Vibmo.
"""

import pytest
import os
import tempfile
from vibmo.ai.autonomous import AutonomousPipeline
from vibmo.ai.graph import run_motion_edit


def test_run_motion_edit_deterministic():
    res = run_motion_edit("Make a high tech launch video with $100K MRR")
    assert res.get("is_valid")
    assert "updated_code" in res
    assert "Scene" in res["updated_code"]


def test_autonomous_pipeline_execution():
    with tempfile.TemporaryDirectory() as tmpdir:
        out_mp4 = os.path.join(tmpdir, "test_render.mp4")
        out_sb = os.path.join(tmpdir, "test_sb.png")

        res = AutonomousPipeline.generate_and_render(
            prompt="Simple card pop in",
            output_video_path=out_mp4,
            output_storyboard_path=out_sb,
            quality="draft",
        )

        assert res.get("success")
        assert res.get("code")
        assert os.path.exists(out_sb)
        assert res.get("storyboard_base64") is not None
