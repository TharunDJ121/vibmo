"""
Automated Pull Request Creator for Completed Jules Sessions.
Fetches completed Jules sessions, creates isolated feature branches, applies patches,
runs unit tests, and creates GitHub Pull Requests automatically via `gh` CLI.

Usage:
    # List completed sessions ready for PR:
    python scripts/jules_pull_and_pr.py --list

    # Process and create PR for a specific session:
    python scripts/jules_pull_and_pr.py --session 3757416439838088854

    # Process all completed sessions and create PRs:
    python scripts/jules_pull_and_pr.py --all
"""

import argparse
import subprocess
import sys
import os
import re
from pathlib import Path
from typing import Dict, List

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")


def get_jules_bin() -> str:
    jules_bin = Path(os.environ.get("LOCALAPPDATA", "")) / "Temp" / "jules_tmp" / "jules.exe"
    if jules_bin.exists():
        return str(jules_bin)
    npm_bin = Path(os.environ.get("APPDATA", "")) / "npm" / "node_modules" / "@google" / "jules" / "jules.exe"
    if npm_bin.exists():
        return str(npm_bin)
    return "jules"


def get_completed_sessions() -> List[Dict[str, str]]:
    """Parse completed sessions from `jules remote list --session`."""
    bin_cmd = get_jules_bin()
    res = subprocess.run([bin_cmd, "remote", "list", "--session"], stdin=subprocess.DEVNULL, capture_output=True, text=True)
    lines = res.stdout.strip().split("\n")
    sessions = []
    for line in lines[1:]:
        parts = line.strip().split()
        if len(parts) >= 5 and "TharunDJ121/vibmo" in line and parts[-1] == "Completed":
            session_id = parts[0]
            desc = " ".join(parts[1:-4])
            sessions.append({
                "id": session_id,
                "description": desc,
                "status": "Completed"
            })
    return sessions



def process_session(session: Dict[str, str], repo: str = "TharunDJ121/vibmo"):
    session_id = session["id"]
    desc = session["description"]
    branch_name = f"jules/session-{session_id}"

    print(f"\n=======================================================")
    print(f"📦 Processing Completed Session: {session_id}")
    print(f"Description: {desc}")
    print(f"Branch: {branch_name}")
    print(f"=======================================================\n")

    # 1. Ensure clean working directory
    subprocess.run(["git", "checkout", "main"], capture_output=True)
    subprocess.run(["git", "pull", "origin", "main"], capture_output=True)

    # 2. Create and checkout feature branch
    subprocess.run(["git", "checkout", "-B", branch_name], capture_output=True)

    # 3. Pull and apply patch from Jules
    print(f"Pulling patch for session {session_id}...")
    bin_cmd = get_jules_bin()
    pull_res = subprocess.run([bin_cmd, "remote", "pull", "--session", session_id, "--apply"], stdin=subprocess.DEVNULL, capture_output=True, text=True)
    print(pull_res.stdout)

    if pull_res.stderr:
        print(pull_res.stderr)

    # 4. Check git status for changed files
    status_res = subprocess.run(["git", "status", "--porcelain"], capture_output=True, text=True)
    if not status_res.stdout.strip():
        print(f"⚠️ No changes detected for session {session_id}. Switching back to main.")
        subprocess.run(["git", "checkout", "main"], capture_output=True)
        return

    print("Changed files:")
    print(status_res.stdout)

    # 5. Run pytest on any test files changed
    test_files = [line[3:].strip() for line in status_res.stdout.split("\n") if "tests/" in line and line.strip().endswith(".py")]
    if test_files:
        for tf in test_files:
            print(f"Running pytest on {tf}...")
            test_res = subprocess.run(["pytest", tf, "-q"], capture_output=True, text=True)
            print(test_res.stdout)
            if test_res.returncode != 0:
                print(f"⚠️ Test failure on {tf}:\n{test_res.stderr}")

    # 6. Commit changes
    title = f"feat(assets): {desc[:60]} (Jules #{session_id})"
    subprocess.run(["git", "add", "."], capture_output=True)
    commit_res = subprocess.run(["git", "commit", "-m", title], capture_output=True, text=True)
    print(commit_res.stdout)

    # 7. Push branch to GitHub
    print(f"Pushing branch {branch_name} to origin...")
    push_res = subprocess.run(["git", "push", "-u", "origin", branch_name, "--force"], capture_output=True, text=True)
    print(push_res.stdout)

    # 8. Create GitHub Pull Request via gh CLI
    print("Creating Pull Request on GitHub...")
    body_text = f"""## ✦ Automated Jules Asset PR

### Session Details
- **Session ID**: `{session_id}`
- **Description**: {desc}
- **Author**: Jules AI Agent

### Changes
Automated asset expansion module and isolated unit tests.
"""
    pr_res = subprocess.run([
        "gh", "pr", "create",
        "--title", title,
        "--body", body_text,
        "--head", branch_name,
        "--base", "main"
    ], capture_output=True, text=True)
    print(pr_res.stdout)
    if pr_res.stderr:
        print(pr_res.stderr)

    # 9. Return to main branch
    subprocess.run(["git", "checkout", "main"], capture_output=True)
    print(f"✅ Successfully processed session {session_id} and created PR.")


def main():
    parser = argparse.ArgumentParser(description="Auto pull & PR creator for Jules sessions.")
    parser.add_argument("--list", action="store_true", help="List completed sessions ready for PR")
    parser.add_argument("--session", type=str, help="Specific session ID to process")
    parser.add_argument("--all", action="store_true", help="Process all completed sessions")
    args = parser.parse_args()

    completed = get_completed_sessions()

    if args.list:
        print(f"\nFound {len(completed)} completed session(s) ready for PR:\n")
        for s in completed:
            print(f"   [{s['id']}] {s['description']}")
        print()
        return

    if args.session:
        target = [s for s in completed if s["id"] == args.session]
        if not target:
            target = [{"id": args.session, "description": "Automated Jules Task", "status": "Completed"}]
        process_session(target[0])
    elif args.all:
        print(f"\nProcessing all {len(completed)} completed session(s)...")
        for s in completed:
            process_session(s)
    else:
        print("Please specify --list, --session <id>, or --all")


if __name__ == "__main__":
    main()
