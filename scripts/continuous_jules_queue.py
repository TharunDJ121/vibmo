"""
Continuous Jules Cloud Session Queue & Auto-Merge Engine.
Monitors remote sessions, merges PRs into main cleanly, and dispatches remaining tasks (92-100) as concurrency slots open.
"""

import json
import os
import re
import subprocess
import sys
import time
from pathlib import Path

# Ensure UTF-8 output
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

ROOT_DIR = Path(__file__).resolve().parent.parent
REPO = "TharunDJ121/vibmo"

jules_bin = Path(os.environ.get("LOCALAPPDATA", "")) / "Temp" / "jules_tmp" / "jules.exe"
npm_bin = Path(os.environ.get("APPDATA", "")) / "npm" / "node_modules" / "@google" / "jules" / "jules.exe"

use_shell = False
if jules_bin.exists():
    bin_cmd = str(jules_bin)
elif npm_bin.exists():
    bin_cmd = str(npm_bin)
else:
    bin_cmd = "jules.cmd" if sys.platform == "win32" else "jules"
    use_shell = sys.platform == "win32"


def get_remaining_tasks_to_dispatch():
    catalog_path = ROOT_DIR / "docs" / "JULES_100_TASKS.md"
    content = catalog_path.read_text(encoding="utf-8", errors="ignore")
    task_blocks = re.findall(
        r"### Task (\d+): (.*?)\n- \*\*Implementation File\*\*: `(.*?)`\n- \*\*Test File\*\*: `(.*?)`\n- \*\*Prompt\*\*:\n```text\n(.*?)\n```",
        content,
        re.DOTALL
    )
    # Check if files already exist on disk
    pending = []
    for num_str, title, impl, test, prompt in task_blocks:
        num = int(num_str)
        if num >= 92:
            impl_file = ROOT_DIR / impl
            test_file = ROOT_DIR / test
            if not (impl_file.exists() and test_file.exists()):
                pending.append((num, title, impl, test, prompt))
    return pending


def try_dispatch_pending():
    pending = get_remaining_tasks_to_dispatch()
    if not pending:
        return
    
    print(f"\n[Queue] Checking if slots are available for {len(pending)} pending tasks (92-100)...", flush=True)
    for num, title, impl, test, prompt in pending:
        res = subprocess.run(
            [bin_cmd, "new", "--repo", REPO, prompt.strip()],
            stdin=subprocess.DEVNULL,
            capture_output=True,
            text=True,
            shell=use_shell,
            timeout=30,
        )
        if "Session is created" in res.stdout or res.returncode == 0:
            print(f"✓ Dispatched Task #{num:02d}: {title}", flush=True)
            for line in res.stdout.splitlines():
                if "ID:" in line or "URL:" in line:
                    print(f"   {line.strip()}", flush=True)
        else:
            if "FAILED_PRECONDITION" in res.stdout or "FAILED_PRECONDITION" in res.stderr:
                print(f"ℹ Quota full. Task #{num:02d} queued for next slot.", flush=True)
                break
            else:
                print(f"Output for Task #{num:02d}: {res.stdout.strip()[:80]}", flush=True)
        time.sleep(1)


def merge_all_prs():
    # Run conflict resolver
    resolver = ROOT_DIR / "scripts" / "resolve_all_github_conflicts.py"
    if resolver.exists():
        subprocess.run([sys.executable, "-u", str(resolver)], stdin=subprocess.DEVNULL)


if __name__ == "__main__":
    print("🚀 Jules Autonomous Queue & Auto-Merge Engine Active.", flush=True)
    try_dispatch_pending()
    merge_all_prs()
