import os
import re
import subprocess
import sys
from pathlib import Path

# Ensure UTF-8 console output
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

REPO = "TharunDJ121/vibmo"
catalog_path = Path("docs") / "JULES_100_TASKS.md"
content = catalog_path.read_text(encoding="utf-8", errors="ignore")
task_blocks = re.findall(r"### Task (\d+): (.*?)\n- \*\*Implementation File\*\*: `(.*?)`\n- \*\*Test File\*\*: `(.*?)`\n- \*\*Prompt\*\*:\n```text\n(.*?)\n```", content, re.DOTALL)

print(f"Total parsed tasks in catalog: {len(task_blocks)}")

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

# Dispatch Section 5, 6, and 7 tasks (Tasks 61 to 100)
remaining_tasks = [(int(num), title, prompt) for num, title, impl, test, prompt in task_blocks if int(num) >= 61]
print(f"Dispatching {len(remaining_tasks)} tasks (Tasks 61 to 100) directly to Google Jules Cloud...")

for task_num, title, prompt in remaining_tasks:
    print(f"\n[Task #{task_num:02d}] {title[:50]}...")
    try:
        res = subprocess.run(
            [bin_cmd, "new", "--repo", REPO, prompt.strip()],
            stdin=subprocess.DEVNULL,
            capture_output=True,
            text=True,
            shell=use_shell,
            timeout=35,
        )
        if "Session is created" in res.stdout:
            print("  ✓ Created:", res.stdout.strip().splitlines()[-1])
        else:
            print("  Output:", res.stdout.strip()[:80] if res.stdout else res.stderr.strip()[:80])
    except Exception as e:
        print("  Error:", e)

print("\n🚀 All remaining tasks uploaded and queued directly in Google Jules Cloud!")
