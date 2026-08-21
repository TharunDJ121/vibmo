"""
✦ Launch Vibmo Studio Pro with AI Director & In-Studio API Key Management.
Run:
    python launch_studio.py
"""

from vibmo.studio.router import launch_studio

if __name__ == "__main__":
    print("[✦ Vibmo Studio] Launching Live Web Studio with AI Director (LangGraph) & API Keys...")
    launch_studio(script_path="replicate_gpt5_demo.py", host="127.0.0.1", port=8000)
