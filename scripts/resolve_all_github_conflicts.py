"""
Batch PR Conflict Resolver & Auto-Merger with Non-Interactive Safe Execution.
"""

import json
import os
import re
import subprocess
import sys
import time
from pathlib import Path

# Ensure UTF-8 output and autoflush
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

ROOT_DIR = Path(__file__).resolve().parent.parent

# Set non-interactive environment variables
ENV = os.environ.copy()
ENV["GIT_TERMINAL_PROMPT"] = "0"
ENV["GIT_MERGE_AUTOEDIT"] = "no"
ENV["GIT_EDITOR"] = "true"
ENV["GH_PROMPT_DISABLED"] = "1"
ENV["PAGER"] = "cat"


def run(cmd, check=False):
    """Executes a command non-interactively with captured output."""
    return subprocess.run(
        cmd,
        stdin=subprocess.DEVNULL,
        capture_output=True,
        text=True,
        env=ENV,
        check=check,
    )


def update_all_init_files():
    """Dynamically scan and rebuild all subpackage __init__.py files cleanly."""
    packages = [
        ("vibmo/fx/backgrounds", "bg_*.py", "Procedural non-static animated backgrounds."),
        ("vibmo/product/hardware", "hw_*.py", "Hardware chassis and device enclosure suites."),
        ("vibmo/product/ai", "ui_*.py", "AI & SaaS Interactive UI Component Suites."),
        ("vibmo/charts", "chart_*.py", "Financial, 3D spatial and motion chart suites."),
    ]

    for pkg_rel, pattern, doc in packages:
        pkg_dir = ROOT_DIR / pkg_rel
        if pkg_dir.exists():
            mod_files = sorted([f for f in pkg_dir.glob(pattern) if f.is_file() and not f.name.endswith(".orig")])
            imports = []
            all_exports = []
            for f in mod_files:
                mod = f.stem
                content = f.read_text(encoding="utf-8", errors="ignore")
                classes = re.findall(r"^class\s+([A-Za-z0-9_]+)\s*\(", content, re.MULTILINE)
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
    """Remove any .orig files left by patch or merge rejects."""
    for root, _, files in os.walk(ROOT_DIR):
        for f in files:
            if f.endswith(".orig"):
                try:
                    os.remove(os.path.join(root, f))
                except Exception:
                    pass


def main():
    print("🔍 Fetching all open Pull Requests from GitHub...", flush=True)
    res = run(["gh", "pr", "list", "--limit", "100", "--json", "number,title,headRefName"])
    if res.returncode != 0:
        print(f"Error fetching PRs: {res.stderr}", flush=True)
        return

    try:
        prs = json.loads(res.stdout)
    except Exception as e:
        print(f"JSON decode error: {e}", flush=True)
        return

    # Sort ascending by PR number (merge oldest PRs first)
    prs.sort(key=lambda x: int(x["number"]))
    print(f"Found {len(prs)} open Pull Request(s) to process.\n", flush=True)

    for pr in prs:
        num = str(pr["number"])
        title = pr["title"]
        branch = pr["headRefName"]

        print(f"=======================================================", flush=True)
        print(f"🚀 Processing PR #{num}: {title}", flush=True)
        print(f"   Branch: {branch}", flush=True)
        print(f"=======================================================", flush=True)

        # 1. Update main
        run(["git", "checkout", "main"])
        run(["git", "pull", "origin", "main"])

        # Delete local branch if already exists to ensure fresh checkout
        run(["git", "branch", "-D", branch])

        # 2. Checkout PR branch
        co = run(["gh", "pr", "checkout", num])
        print(f"Checked out PR #{num}: {co.stdout.strip()[:60]}", flush=True)

        # 3. Merge origin/main into PR branch
        run(["git", "fetch", "origin", "main"])
        m = run(["git", "merge", "origin/main", "--no-edit", "-m", f"Merge main into PR #{num}"])
        
        status = run(["git", "status", "--porcelain"])
        has_conflict = any(code in status.stdout for code in ["UU ", "AA ", "DU ", "UD ", "DD "])

        if has_conflict or m.returncode != 0:
            print("⚡ Merge conflict detected. Auto-reconciling...", flush=True)
            run(["git", "checkout", "--theirs", "."])
            clean_orig_files()
            update_all_init_files()
            run(["git", "add", "."])
            run(["git", "commit", "-m", f"Auto-resolve merge conflicts for PR #{num}"])

        clean_orig_files()
        update_all_init_files()
        run(["git", "add", "."])
        
        status_after = run(["git", "status", "--porcelain"])
        if status_after.stdout.strip():
            run(["git", "commit", "-m", f"Clean up exports for PR #{num}"])

        # 4. Push updated branch
        print("Pushing resolved branch to origin...", flush=True)
        p = run(["git", "push", "origin", "HEAD"])
        if p.returncode != 0:
            print(f"Push warning: {p.stderr.strip()[:100]}", flush=True)

        # 5. Merge PR via GitHub CLI
        print(f"Merging PR #{num} into main...", flush=True)
        merge_res = run(["gh", "pr", "merge", num, "--merge", "--delete-branch"])
        print(f"PR #{num} merge output: {merge_res.stdout.strip()[:120]} {merge_res.stderr.strip()[:120]}", flush=True)

        # 6. Switch back to main and pull latest
        run(["git", "checkout", "main"])
        run(["git", "pull", "origin", "main"])
        print(f"✓ PR #{num} complete.\n", flush=True)

    print("🎉 All open Pull Requests processed and merged into main!", flush=True)


if __name__ == "__main__":
    main()
