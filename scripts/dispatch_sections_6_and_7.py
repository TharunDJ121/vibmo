"""
Dispatch script for remaining tasks in Section 6 (Tasks 77-90) and Section 7 (Tasks 91-100).
"""

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

REPO = "TharunDJ121/vibmo"
catalog_path = Path("docs") / "JULES_100_TASKS.md"
content = catalog_path.read_text(encoding="utf-8", errors="ignore")

task_blocks = re.findall(
    r"### Task (\d+): (.*?)\n- \*\*Implementation File\*\*: `(.*?)`\n- \*\*Test File\*\*: `(.*?)`\n- \*\*Prompt\*\*:\n```text\n(.*?)\n```",
    content,
    re.DOTALL
)

print(f"Total catalog tasks found: {len(task_blocks)}")

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

# Filter tasks 77 to 100
tasks_to_run = [(int(num), title, impl, test, prompt) for num, title, impl, test, prompt in task_blocks if int(num) >= 77]
print(f"Found {len(tasks_to_run)} tasks to dispatch to Jules (Tasks 77 to 100):\n")

dispatched = 0
for task_num, title, impl, test, prompt in tasks_to_run:
    print(f"-------------------------------------------------------")
    print(f"🚀 Dispatching Task #{task_num:02d}: {title}")
    print(f"   Target: {impl}")
    print(f"   Test:   {test}")
    
    try:
        res = subprocess.run(
            [bin_cmd, "new", "--repo", REPO, prompt.strip()],
            stdin=subprocess.DEVNULL,
            capture_output=True,
            text=True,
            shell=use_shell,
            timeout=35,
        )
        if "Session is created" in res.stdout or res.returncode == 0:
            lines = [l for l in res.stdout.strip().splitlines() if l.strip()]
            for l in lines:
                print(f"   ✓ {l}")
            dispatched += 1
        else:
            print(f"   Output: {res.stdout.strip()[:100]}")
            if res.stderr:
                print(f"   Stderr: {res.stderr.strip()[:100]}")
    except Exception as e:
        print(f"   Error: {e}")
    
    time.sleep(1)

print(f"\n🎉 Successfully dispatched {dispatched}/{len(tasks_to_run)} tasks to Google Jules!")
