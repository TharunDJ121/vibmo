"""
Interactive Jules Batch Runner for Massive Asset Expansion.
Dispatches 100 isolated Jules coding tasks across 7 sections to Google Jules CLI.

Usage:
    # List all 7 sections and 100 tasks:
    python scripts/launch_jules_batch.py --list

    # Dry-run Section 1 (displays exact commands without calling jules):
    python scripts/launch_jules_batch.py --section 1 --dry-run

    # Dispatch all 15 tasks of Section 2 to Jules:
    python scripts/launch_jules_batch.py --section 2

    # Dispatch a specific task (e.g. Task 46):
    python scripts/launch_jules_batch.py --task 46
"""

import argparse
import subprocess
import sys
import os
import re
from pathlib import Path
from typing import Dict, List

# Ensure UTF-8 output on Windows consoles
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")



def parse_prompts_from_markdown(md_path: Path) -> List[Dict[str, str]]:
    """Parse the 100 task prompts from the master markdown catalog."""
    if not md_path.exists():
        print(f"Error: Prompt catalog not found at {md_path}")
        sys.exit(1)

    content = md_path.read_text(encoding="utf-8")
    task_blocks = re.findall(r"### Task (\d+): (.*?)\n- \*\*Implementation File\*\*: `(.*?)`\n- \*\*Test File\*\*: `(.*?)`\n- \*\*Prompt\*\*:\n```text\n(.*?)\n```", content, re.DOTALL)

    tasks = []
    for num_str, title, impl_file, test_file, prompt_text in task_blocks:
        task_num = int(num_str)
        if task_num <= 15:
            sec = 1
        elif task_num <= 30:
            sec = 2
        elif task_num <= 45:
            sec = 3
        elif task_num <= 60:
            sec = 4
        elif task_num <= 75:
            sec = 5
        elif task_num <= 90:
            sec = 6
        else:
            sec = 7

        tasks.append({
            "task_num": task_num,
            "section": sec,
            "title": title.strip(),
            "impl_file": impl_file.strip(),
            "test_file": test_file.strip(),
            "prompt": prompt_text.strip(),
        })

    return tasks


def main():
    parser = argparse.ArgumentParser(description="Launch Jules tasks for asset expansion.")
    parser.add_argument("--section", type=int, choices=[1, 2, 3, 4, 5, 6, 7], help="Section number to execute (1-7)")
    parser.add_argument("--task", type=int, help="Single task number to execute (1-100)")
    parser.add_argument("--repo", type=str, default="TharunDJ121/vibmo", help="GitHub repo for Jules")
    parser.add_argument("--dry-run", action="store_true", help="Print commands without executing")
    parser.add_argument("--list", action="store_true", help="List all sections and tasks")

    args = parser.parse_args()

    catalog_path = Path(r"C:\Users\djtha\.gemini\antigravity\brain\dc0cbd97-18b5-4852-8e94-21a134202321\jules_100_tasks_prompts.md")
    tasks = parse_prompts_from_markdown(catalog_path)

    if args.list:
        print(f"\n=======================================================")
        print(f"  ✦ MOTIO / VIBMO — 100 JULES ASSET EXPANSION TASKS")
        print(f"=======================================================\n")
        sections_info = {
            1: ("Procedural Audio & Foley Suites", "50-65 SFX"),
            2: ("Non-Static Animated Backgrounds & Backdrops", "50-60 Backdrops"),
            3: ("Hardware Chassis & Device Enclosures", "45-60 Mockups"),
            4: ("AI & SaaS Interactive UI Component Suites", "50-65 Components"),
            5: ("Financial, 3D Spatial & Motion Chart Suites", "50-60 Charts"),
            6: ("Kinetic Typography & Title Sequence Suites", "50-60 Typography"),
            7: ("Visual Post-FX Shaders & Turnkey Templates", "35-45 Templates"),
        }
        for s_num, (s_name, s_count) in sections_info.items():
            s_tasks = [t for t in tasks if t["section"] == s_num]
            print(f"Section {s_num}: {s_name} ({len(s_tasks)} tasks | ~{s_count})")
            for t in s_tasks:
                print(f"   [{t['task_num']:02d}] {t['title']} -> {t['impl_file']}")
            print()
        return

    selected_tasks = []
    if args.task:
        selected_tasks = [t for t in tasks if t["task_num"] == args.task]
        if not selected_tasks:
            print(f"Error: Task {args.task} not found in catalog.")
            sys.exit(1)
    elif args.section:
        selected_tasks = [t for t in tasks if t["section"] == args.section]
    else:
        print("Please specify --section [1-7], --task [1-100], or --list")
        sys.exit(1)

    jules_bin = Path(os.environ.get("LOCALAPPDATA", "")) / "Temp" / "jules_tmp" / "jules.exe"
    bin_cmd = str(jules_bin) if jules_bin.exists() else "jules"

    print(f"\n🚀 Ready to launch {len(selected_tasks)} task(s) for repo '{args.repo}'...\n")

    for t in selected_tasks:
        print(f"-------------------------------------------------------")
        print(f"Task #{t['task_num']:02d}: {t['title']}")
        print(f"Target: {t['impl_file']}")
        print(f"Test:   {t['test_file']}")
        if args.dry_run:
            print(f"Command:\n  jules new --repo {args.repo} \"{t['prompt'][:80]}...\"\n")
        else:
            print(f"Dispatching to Jules...")
            try:
                res = subprocess.run(
                    [bin_cmd, "new", "--repo", args.repo, t["prompt"]],
                    stdin=subprocess.DEVNULL,
                    capture_output=True,
                    text=True,
                    timeout=30,
                )
                print(res.stdout)
                if res.stderr:
                    print(res.stderr)
            except Exception as e:
                print(f"Execution failed: {e}")

    print("Batch processing complete.")



if __name__ == "__main__":
    main()
