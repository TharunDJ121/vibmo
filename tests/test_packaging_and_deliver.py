import os
import shutil
import tempfile
from pathlib import Path
import pytest

from vibmo.packaging import ProjectArchive
from vibmo.studio.pages.deliver import get_render_queue, EXPORT_PRESETS, RenderQueueManager


def test_project_packaging_and_restoration():
    temp_dir = tempfile.mkdtemp()
    try:
        # Create a sample project script and dummy assets
        script_file = os.path.join(temp_dir, "my_scene.py")
        with open(script_file, "w", encoding="utf-8") as f:
            f.write("from vibmo.agent_api import *\nscene = Scene()\n")

        assets_dir = os.path.join(temp_dir, "assets")
        os.makedirs(assets_dir, exist_ok=True)
        sample_asset = os.path.join(assets_dir, "test_logo.png")
        with open(sample_asset, "w", encoding="utf-8") as f:
            f.write("fake_png_data")

        # 1. Package into .vibmo archive
        archive_path = os.path.join(temp_dir, "my_scene.vibmo")
        packaged_path = ProjectArchive.package(script_file, output_path=archive_path)
        assert os.path.exists(packaged_path)
        assert packaged_path.endswith(".vibmo")

        # 2. Inspect archive
        info = ProjectArchive.inspect(packaged_path)
        assert info["entry_script"] == "my_scene.py"
        assert len(info["assets"]) >= 1
        assert info["total_files"] >= 2

        # 3. Unpackage / Restore
        extract_dir = os.path.join(temp_dir, "restored_project")
        dest = ProjectArchive.unpackage(packaged_path, target_dir=extract_dir)
        assert os.path.exists(dest)
        assert os.path.exists(os.path.join(dest, "my_scene.py"))
        assert os.path.exists(os.path.join(dest, "assets", "test_logo.png"))
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)


def test_deliver_render_queue():
    q = RenderQueueManager()
    assert len(EXPORT_PRESETS) >= 5

    # Add job to queue
    job1 = q.add_job("mp4_1080p", name="Master Video Export")
    assert job1.job_id.startswith("job_")
    assert job1.status == "queued"
    assert job1.width == 1920
    assert job1.height == 1080

    job2 = q.add_job("reel_9_16", name="Instagram Reel Export")
    assert job2.width == 1080
    assert job2.height == 1920

    jobs = q.get_all_jobs()
    assert len(jobs) == 2

    # Remove job
    removed = q.remove_job(job1.job_id)
    assert removed is True
    assert len(q.get_all_jobs()) == 1

    # Clear completed
    job2.status = "completed"
    q.clear_completed()
    assert len(q.get_all_jobs()) == 0
