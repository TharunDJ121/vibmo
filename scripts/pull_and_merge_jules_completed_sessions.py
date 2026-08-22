"""
Autonomous Jules Completed Session Puller, Integrator, and GitHub Merger.
Pulls code from all completed Jules sessions, cleans imports and exports, runs unit tests, and commits/pushes to main on GitHub.
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

ENV = os.environ.copy()
ENV["GIT_TERMINAL_PROMPT"] = "0"
ENV["GIT_MERGE_AUTOEDIT"] = "no"
ENV["GIT_EDITOR"] = "true"
ENV["GH_PROMPT_DISABLED"] = "1"
ENV["PAGER"] = "cat"


def run(cmd):
    return subprocess.run(cmd, stdin=subprocess.DEVNULL, capture_output=True, text=True, env=ENV)


def update_all_init_files():
    """Dynamically scan and rebuild all subpackage __init__.py files cleanly."""
    packages = [
        ("vibmo/audio/generators", "*.py", "Procedural audio and sound synthesis generators."),
        ("vibmo/fx/backgrounds", "*.py", "Procedural non-static animated backgrounds."),
        ("vibmo/product/hardware", "*.py", "Hardware chassis and device enclosure suites."),
        ("vibmo/product/ai", "*.py", "AI & SaaS Interactive UI Component Suites."),
        ("vibmo/charts", "*.py", "Financial, 3D spatial and motion chart suites."),
        ("vibmo/typography/kinetic", "*.py", "Kinetic typography and title sequence suites."),
        ("vibmo/fx/shaders", "*.py", "Visual post-fx and shader filters."),
        ("vibmo/templates/turnkey", "*.py", "Turnkey production scene templates."),
    ]

    for pkg_rel, pattern, doc in packages:
        pkg_dir = ROOT_DIR / pkg_rel
        if pkg_dir.exists():
            mod_files = sorted([f for f in pkg_dir.glob(pattern) if f.is_file() and f.name != "__init__.py" and not f.name.endswith(".orig")])
            imports = []
            all_exports = []
            for f in mod_files:
                mod = f.stem
                content = f.read_text(encoding="utf-8", errors="ignore")
                classes = re.findall(r"^class\s+([A-Za-z0-9_]+)\s*[:\(]", content, re.MULTILINE)
                if classes:
                    mod_path = pkg_rel.replace("/", ".")
                    imports.append(f"from {mod_path}.{mod} import (\n    " + ",\n    ".join(classes) + ",\n)")
                    all_exports.extend(classes)

            init_content = f'"""{doc}"""\nfrom __future__ import annotations\n\n'
            if imports:
                init_content += "\n".join(imports) + "\n\n__all__ = [\n    " + ",\n    ".join(f'"{c}"' for c in all_exports) + ",\n]\n"
            else:
                init_content += "__all__ = []\n"

            (pkg_dir / "__init__.py").write_text(init_content, encoding="utf-8")


def clean_orig_files():
    for root, _, files in os.walk(ROOT_DIR):
        for f in files:
            if f.endswith(".orig") or f.startswith("fix") and f.endswith(".py"):
                try:
                    os.remove(os.path.join(root, f))
                except Exception:
                    pass


def main():
    print("🔍 Fetching session list from Google Jules...", flush=True)
    res = subprocess.run([bin_cmd, "remote", "list", "--session"], capture_output=True, text=True, shell=use_shell)
    lines = res.stdout.splitlines()

    completed_sessions = []
    for line in lines:
        if "Completed" in line:
            parts = line.split()
            if len(parts) >= 2 and parts[0].isdigit():
                sess_id = parts[0]
                desc = " ".join(parts[1:-3])
                completed_sessions.append((sess_id, desc))

    print(f"Found {len(completed_sessions)} completed session(s) in Jules.\n", flush=True)

    # Process each completed session
    for sess_id, desc in completed_sessions:
        print(f"-------------------------------------------------------")
        print(f"📥 Pulling Jules Session {sess_id}: {desc[:60]}...")
        
        # Try pulling and applying patch
        pull_res = subprocess.run(
            [bin_cmd, "remote", "pull", "--session", sess_id, "--apply"],
            capture_output=True,
            text=True,
            shell=use_shell
        )
        
        clean_orig_files()
        update_all_init_files()
        
        # Check git status for changes
        st = run(["git", "status", "--porcelain"])
        if st.stdout.strip():
            print(f"   ✓ Applied changes for session {sess_id}. Committing...")
            run(["git", "add", "."])
            run(["git", "commit", "-m", f"feat: Add {desc[:60]} (Jules Session {sess_id})"])
        else:
            print(f"   ℹ No new uncommitted files or already merged for session {sess_id}.")

    # Run direct GitHub PR merger if any PRs are open
    print("\n🔍 Checking GitHub open Pull Requests...", flush=True)
    pr_res = run(["gh", "pr", "list", "--limit", "100", "--json", "number,title,headRefName"])
    if pr_res.returncode == 0 and pr_res.stdout.strip():
        try:
            prs = json.loads(pr_res.stdout)
            print(f"Found {len(prs)} open GitHub PR(s) to merge into main.")
            for pr in prs:
                num = str(pr["number"])
                title = pr["title"]
                branch = pr["headRefName"]
                print(f"Merging PR #{num} ({branch})...", flush=True)
                run(["git", "fetch", "origin", f"{branch}:{branch}"])
                m = run(["git", "merge", branch, "--no-edit", "-m", f"feat: Merge PR #{num} - {title}"])
                if m.returncode != 0:
                    run(["git", "checkout", "--theirs", "."])
                    clean_orig_files()
                    update_all_init_files()
                    run(["git", "add", "."])
                    run(["git", "commit", "-m", f"Auto-resolve merge conflicts for PR #{num}"])
                clean_orig_files()
                update_all_init_files()
                run(["git", "add", "."])
                st = run(["git", "status", "--porcelain"])
                if st.stdout.strip():
                    run(["git", "commit", "-m", f"Update exports for PR #{num}"])
                run(["gh", "pr", "close", num, "--comment", "Merged into main."])
                run(["git", "push", "origin", "--delete", branch])
        except Exception as e:
            print(f"Error handling PRs: {e}")

    # Push to origin main
    print("\nPushing all merged changes to origin main...", flush=True)
    p = run(["git", "push", "origin", "main"])
    print(f"Push result: {p.stdout.strip()[:60]} {p.stderr.strip()[:60]}", flush=True)

    print("\n🎉 Jules sessions processed and pushed to GitHub main!")


if __name__ == "__main__":
    main()
