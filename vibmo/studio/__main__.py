"""
CLI Entrypoint for launching Vibmo Studio Pro.
Usage:
    python -m vibmo.studio [script_path.py] [--port 8000] [--host 127.0.0.1]
"""

import sys
import argparse
from vibmo.studio.router import launch_studio


def main():
    parser = argparse.ArgumentParser(description="✦ Vibmo Studio Pro — Live Motion Graphics Workstation")
    parser.add_argument("script", nargs="?", default=None, help="Path to Python script to load (optional)")
    parser.add_argument("--port", type=int, default=8000, help="Server port (default: 8000)")
    parser.add_argument("--host", type=str, default="127.0.0.1", help="Server host (default: 127.0.0.1)")

    args = parser.parse_args()
    print(f"[Vibmo Studio] Launching Live Web Studio on http://{args.host}:{args.port}...")
    launch_studio(script_path=args.script, host=args.host, port=args.port)


if __name__ == "__main__":
    main()
