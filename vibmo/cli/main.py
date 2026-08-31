"""
Vibmo Production CLI:
  vibmo ai <prompt>       Generate or surgically edit motion graphics via AI
  vibmo render <script>   Render scene or sequence to MP4, WebM, ProRes, or GIF
  vibmo storyboard <script> Generate visual contact sheet
  vibmo studio <script>   Launch interactive browser Studio
  vibmo inspect <script>  Debug and inspect scene graph without rendering
  vibmo watch <script>    Watch file and live-reload storyboard on save
  vibmo init <name>       Scaffold a new motion design project
"""

import sys
import os
import time
import json
import argparse
import importlib.util
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from rich.console import Console
from rich.panel import Panel
from rich.tree import Tree
from rich.table import Table

# Ensure Windows terminal handles UTF-8 gracefully
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

console = Console()

BANNER = r"""[bold cyan]
  __  __  ___ _____ ___ ___  
 |  \/  |/ _ \_   _|_ _/ _ \ 
 | |\/| | | | || |  | | | | |
 | |  | | |_| || |  | | |_| |
 |_|  |_|\___/ |_| |___\___/ 
[/bold cyan] [bold white]Production Motion Design System (v2.0)[/bold white]
"""


def _load_runnable_from_file(file_path: str):
    abs_path = os.path.abspath(file_path)
    if not os.path.exists(abs_path):
        console.print(f"[bold red]Error:[/bold red] Script not found at '{file_path}'")
        sys.exit(1)

    spec = importlib.util.spec_from_file_location("user_vibmo_script", abs_path)
    if spec is None or spec.loader is None:
        console.print(f"[bold red]Error:[/bold red] Could not load module from '{file_path}'")
        sys.exit(1)

    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)

    import inspect
    from vibmo.scene.scene import Scene
    from vibmo.composition.sequence import Sequence

    # 1. First priority: Check for existing Scene/Sequence instances
    for attr_name in dir(mod):
        attr = getattr(mod, attr_name)
        if not isinstance(attr, type) and isinstance(attr, (Scene, Sequence)):
            if attr_name == "scene" or len(getattr(attr, "nodes", [])) > 0:
                return attr

    # 2. Second priority: Any other Scene/Sequence instance
    for attr_name in dir(mod):
        attr = getattr(mod, attr_name)
        if not isinstance(attr, type) and isinstance(attr, (Scene, Sequence)):
            return attr

    # 3. Third priority: Factory functions
    for attr_name in dir(mod):
        attr = getattr(mod, attr_name)
        if inspect.isfunction(attr) and any(kw in attr_name.lower() for kw in ("create", "build", "make", "get_scene", "demo")):
            try:
                res = attr()
                if isinstance(res, (Scene, Sequence)):
                    return res
            except Exception:
                pass

    console.print("[bold red]Error:[/bold red] No [cyan]Scene[/cyan] or [cyan]Sequence[/cyan] found in script.")
    sys.exit(1)


def init_project(project_name: str) -> None:
    root = Path(project_name)
    if root.exists():
        console.print(f"[bold red]Error:[/bold red] Directory '{project_name}' already exists.")
        sys.exit(1)

    (root / "assets").mkdir(parents=True, exist_ok=True)
    (root / "fonts").mkdir(parents=True, exist_ok=True)
    (root / "scenes").mkdir(parents=True, exist_ok=True)
    (root / "renders").mkdir(parents=True, exist_ok=True)
    (root / "storyboard").mkdir(parents=True, exist_ok=True)

    project_py_code = '''"""
Vibmo Motion Design Project
"""

from motio.agent_api import *

# 1. Initialize Scene (1080p @ 60 FPS)
scene = Scene(
    width=1920,
    height=1080,
    fps=60,
    duration=5.0,
    background=colors.DARK_NAVY,
)

# 2. Add Shaders
scene.add_post_fx(Vignette(intensity=0.25), FilmGrain(amount=0.015))

# 3. Assemble UI Mockup
browser = BrowserWindow(
    url="https://vibmo.design",
    title="Vibmo — Next-Gen Motion Graphics",
    width=1280,
    height=720,
    position=(320, 180),
)

card = GlassCard(direction="column", gap=12, padding=24, corner_radius=16)
icon = Icon("lucide:sparkles", size=32, color=colors.INDIGO)
title = KineticText("Welcome to Vibmo", font_size=28, bold=True)
counter = MetricCounter(start_val=0, end_val=100000, prefix="$", font_size=42, bold=True, color=colors.EMERALD)

card.add(icon, title, counter)
browser.add_content(card)
scene.add(browser)

# 4. Choreograph Motion Verbs
@scene.animate
def main():
    browser.position.set((320, 300))
    browser.opacity.set(0.0)
    
    yield scene.all(
        browser.position.to((320, 180), duration=0.9, ease=Ease.spring(stiffness=130, damping=12)),
        browser.opacity.to(1.0, duration=0.7),
        title.reveal_characters(stagger=0.03),
        counter.count_to(duration=1.8, ease=Ease.out_expo),
    )
    
    browser.float_idle(amplitude=6, speed=1.2)
    yield scene.wait(1.5)

if __name__ == "__main__":
    scene.storyboard("storyboard/preview.png")
    scene.render("renders/output.mp4", quality="high")
'''
    with open(root / "project.py", "w", encoding="utf-8") as f:
        f.write(project_py_code)

    vibmo_toml = f'''[project]
name = "{project_name}"
version = "0.2.0"
fps = 60
resolution = [1920, 1080]
output_dir = "renders"
'''
    with open(root / "vibmo.toml", "w", encoding="utf-8") as f:
        f.write(vibmo_toml)

    console.print(Panel(
        f"[bold green]Created new Vibmo project in [bold white]{project_name}[/bold white]![/bold green]\n\n"
        f"Next steps:\n"
        f"  [cyan]cd {project_name}[/cyan]\n"
        f"  [cyan]vibmo studio project.py[/cyan]   (Open live Web Studio)\n"
        f"  [cyan]vibmo render project.py[/cyan]   (Render master video)",
        title="Vibmo Project Ready",
        border_style="cyan"
    ))


def cmd_inspect(script_path: str) -> None:
    """Inspects scene structure, nodes, shaders, and validation health."""
    console.print(f"[bold cyan]Inspecting:[/bold cyan] {script_path}\n")
    runnable = _load_runnable_from_file(script_path)

    # Summary Panel
    w = getattr(runnable, "width", 1920)
    h = getattr(runnable, "height", 1080)
    fps = getattr(runnable, "fps", 60.0)
    dur = getattr(runnable, "duration", 0.0)
    bg = getattr(runnable, "background", None)
    bg_hex = bg.to_hex() if hasattr(bg, "to_hex") else str(bg)

    t = Table(title="Scene Configuration", border_style="cyan")
    t.add_column("Property", style="bold white")
    t.add_column("Value", style="green")
    t.add_row("Resolution", f"{w} x {h}")
    t.add_row("Frame Rate", f"{fps} FPS")
    t.add_row("Duration", f"{dur:.2f}s ({int(dur * fps)} frames)")
    t.add_row("Background", f"{bg_hex}")
    console.print(t)
    console.print()

    # Node Tree
    tree = Tree("[bold cyan]✦ Scene Root Hierarchy[/bold cyan]")
    nodes = getattr(runnable, "nodes", [])

    def _add_nodes(parent_tree, node_list):
        for n in node_list:
            pos = n.position.get(0.0) if hasattr(n, "position") else (0, 0)
            px = pos.x if hasattr(pos, "x") else pos[0]
            py = pos.y if hasattr(pos, "y") else pos[1]
            op = n.opacity.get(0.0) if hasattr(n, "opacity") else 1.0
            label = f"[bold green]{n.__class__.__name__}[/bold green] [white]'{n.name}'[/white] at ({px:.0f}, {py:.0f}) opacity={op:.2f}"
            branch = parent_tree.add(label)
            if hasattr(n, "children") and n.children:
                _add_nodes(branch, n.children)

    _add_nodes(tree, nodes)
    console.print(tree)
    console.print()

    # Post-FX
    post_fx = getattr(runnable, "post_fx", [])
    if post_fx:
        fx_names = [fx.__class__.__name__ for fx in post_fx]
        console.print(f"[bold magenta]Post-FX Shaders:[/bold magenta] {', '.join(fx_names)}")

    # Validation
    if hasattr(runnable, "validate"):
        issues = runnable.validate()
        if issues:
            console.print(f"\n[bold yellow]⚠️ Validation Warnings ({len(issues)}):[/bold yellow]")
            for iss in issues:
                console.print(f"  • {iss}")
        else:
            console.print("\n[bold green]✅ Scene Validation: 0 warnings, ready for broadcast render.[/bold green]")


def cmd_watch(script_path: str, open_studio: bool = False, port: int = 8000) -> None:
    """Watches a script for changes and automatically re-validates and regenerates storyboards."""
    abs_path = os.path.abspath(script_path)
    if not os.path.exists(abs_path):
        console.print(f"[bold red]Error:[/bold red] File not found: {script_path}")
        return

    if open_studio:
        from vibmo.studio.router import launch_studio
        console.print(f"[bold cyan]Launching Studio with hot-reload watcher on {script_path}...[/bold cyan]")
        launch_studio(scene=None, script_path=script_path, port=port)
        return

    console.print(f"[bold cyan]Watching for changes in:[/bold cyan] {script_path}")
    console.print("[dim]Press Ctrl+C to stop.[/dim]\n")

    last_mtime = os.path.getmtime(abs_path)
    try:
        while True:
            time.sleep(0.5)
            curr_mtime = os.path.getmtime(abs_path)
            if curr_mtime != last_mtime:
                last_mtime = curr_mtime
                console.print(f"\n[bold yellow]✦ Change detected at {time.strftime('%H:%M:%S')}[/bold yellow]")
                try:
                    runnable = _load_runnable_from_file(script_path)
                    out_sb = "storyboard_live.png"
                    if hasattr(runnable, "storyboard"):
                        runnable.storyboard(out_sb)
                        console.print(f"  [bold green]✓[/bold green] Storyboard updated: [cyan]{out_sb}[/cyan]")
                    if hasattr(runnable, "validate"):
                        issues = runnable.validate()
                        if issues:
                            console.print(f"  [bold yellow]⚠️ {len(issues)} validation warning(s):[/bold yellow] {issues[0]}")
                        else:
                            console.print("  [bold green]✓[/bold green] Validation: All systems nominal")
                except Exception as e:
                    console.print(f"  [bold red]✗ Error loading script:[/bold red] {e}")
    except KeyboardInterrupt:
        console.print("\n[bold cyan]Watcher stopped.[/bold cyan]")


def cmd_ai(
    prompt: Optional[str] = None,
    edit_script: Optional[str] = None,
    output_video: Optional[str] = None,
    chat_mode: bool = False,
    provider: Optional[str] = None,
) -> None:
    """Executes AI natural language generation, surgical edits, or interactive chat."""
    from vibmo.ai.autonomous import AutonomousPipeline
    from vibmo.ai.graph import run_motion_edit
    from vibmo.ai.memory import get_global_memory

    if chat_mode:
        console.print("[bold cyan]✦ Entering Vibmo AI Director Interactive Chat Mode[/bold cyan]")
        console.print("[dim]Type your instructions below. Type 'exit' or 'quit' to finish.[/dim]\n")
        memory = get_global_memory()
        current_code = ""

        if edit_script and os.path.exists(edit_script):
            with open(edit_script, "r", encoding="utf-8") as f:
                current_code = f.read()
            console.print(f"[green]Loaded base script from {edit_script}[/green]\n")

        while True:
            try:
                user_input = console.input("[bold magenta]AI Director > [/bold magenta]").strip()
                if not user_input or user_input.lower() in ("exit", "quit", "q"):
                    break

                res = run_motion_edit(prompt=user_input, current_code=current_code, provider=provider)
                current_code = res.get("updated_code", current_code)
                msg = res.get("response_message", "Edit applied.")
                console.print(f"[bold green]AI:[/bold green] {msg}")

                if edit_script:
                    with open(edit_script, "w", encoding="utf-8") as f:
                        f.write(current_code)
                    console.print(f"[dim]Saved updates to {edit_script}[/dim]\n")

            except KeyboardInterrupt:
                break
        console.print("\n[bold cyan]Exited AI chat mode.[/bold cyan]")
        return

    if not prompt:
        console.print("[bold red]Error:[/bold red] Please provide a prompt or use --chat.")
        return

    # Surgical edit mode
    if edit_script and os.path.exists(edit_script):
        with open(edit_script, "r", encoding="utf-8") as f:
            code = f.read()

        console.print(f"[bold cyan]Applying surgical AI edit to:[/bold cyan] {edit_script}")
        console.print(f"[dim]Instruction: '{prompt}'[/dim]\n")

        res = run_motion_edit(prompt=prompt, current_code=code, provider=provider)
        updated_code = res.get("updated_code", code)

        with open(edit_script, "w", encoding="utf-8") as f:
            f.write(updated_code)

        console.print(Panel(
            f"[bold green]✓ Script successfully updated![/bold green]\n\n"
            f"[white]{res.get('response_message', 'Modifications applied.')}[/white]",
            title="Surgical Edit Applied",
            border_style="green"
        ))
        return

    # Autonomous prompt-to-video generation
    out_vid = output_video or "ai_output.mp4"
    console.print(f"[bold cyan]Generating Motion Graphics from Prompt:[/bold cyan] '{prompt}'")
    console.print("[dim]Synthesizing code, validating timeline, and rendering master video...[/dim]\n")

    res = AutonomousPipeline.generate_and_render(
        prompt=prompt,
        output_video_path=out_vid,
        provider=provider,
        quality="high",
    )

    if res.get("success"):
        console.print(Panel(
            f"[bold green]✓ Video rendered successfully![/bold green]\n\n"
            f"Output Video: [bold cyan]{res.get('video_path')}[/bold cyan]\n"
            f"Storyboard:   [bold cyan]{res.get('storyboard_path')}[/bold cyan]\n"
            f"Duration:     [white]{res.get('duration', 0.0):.2f}s[/white]",
            title="AI Motion Generation Complete",
            border_style="green"
        ))
    else:
        errs = "\n".join(res.get("errors", ["Unknown error"]))
        console.print(Panel(
            f"[bold red]Generation encountered issues:[/bold red]\n\n{errs}",
            title="Generation Error",
            border_style="red"
        ))


def cli():
    if len(sys.argv) > 1 and sys.argv[1] not in ("mcp", "schema"):
        console.print(BANNER)
    parser = argparse.ArgumentParser(prog="vibmo", description="Vibmo Production Motion Design CLI")

    subparsers = parser.add_subparsers(dest="command", required=True)

    # vibmo ai
    ai_parser = subparsers.add_parser("ai", help="Generate or edit motion graphics using AI natural language")
    ai_parser.add_argument("prompt", nargs="?", default=None, help="Prompt description or edit instruction")
    ai_parser.add_argument("--edit", default=None, help="Path to Python script to surgically modify")
    ai_parser.add_argument("-o", "--output", default="ai_output.mp4", help="Output MP4 file path")
    ai_parser.add_argument("--chat", action="store_true", help="Launch interactive terminal chat session with AI Director")
    ai_parser.add_argument("--provider", default=None, choices=["openai", "anthropic", "gemini", "groq", "openrouter"], help="AI provider override")

    # vibmo inspect
    inspect_parser = subparsers.add_parser("inspect", help="Inspect and debug scene graph, hierarchy, and validation")
    inspect_parser.add_argument("script", help="Python scene or sequence script file")

    # vibmo watch
    watch_parser = subparsers.add_parser("watch", help="Watch script and live-reload storyboards or Studio")
    watch_parser.add_argument("script", help="Python scene or sequence script file")
    watch_parser.add_argument("--studio", action="store_true", help="Auto-launch interactive Studio in browser")
    watch_parser.add_argument("--port", type=int, default=8000, help="Web Studio port")

    # vibmo create / template
    create_parser = subparsers.add_parser("create", help="Create project from a production template")
    create_parser.add_argument("template", choices=["saas_launch", "app_demo", "tech_intro"], help="Template type")
    create_parser.add_argument("name", nargs="?", default=None, help="Directory name for the new project")

    # vibmo templates
    subparsers.add_parser("templates", help="List available production templates")

    # vibmo init
    init_parser = subparsers.add_parser("init", help="Scaffold a new motion graphics project")
    init_parser.add_argument("name", help="Name of project directory to create")

    # vibmo render
    render_parser = subparsers.add_parser("render", help="Render scene/sequence to video or GIF")
    render_parser.add_argument("script", help="Python scene or sequence script file")
    render_parser.add_argument("-o", "--output", default="output.mp4", help="Output filepath (.mp4, .webm, .gif, .mov)")
    render_parser.add_argument("-q", "--quality", default="high", choices=["draft", "fast", "high", "4k"], help="Render quality preset")
    render_parser.add_argument(
        "-p", "--preset", default="mp4",
        help="Codec/Social preset: 'mp4', 'webm', 'prores', 'gif', 'instagram-reel', 'tiktok', 'youtube-short', 'twitter', 'linkedin'"
    )
    render_parser.add_argument("--props", default=None, help="JSON string or path to .json file with runtime props")
    render_parser.add_argument("--resume", action="store_true", help="Resume interrupted render from cache")
    render_parser.add_argument("--motion-blur", action="store_true", help="Enable sub-frame motion blur")

    # vibmo storyboard
    sb_parser = subparsers.add_parser("storyboard", help="Generate visual storyboard contact sheet")
    sb_parser.add_argument("script", help="Python scene or sequence script file")
    sb_parser.add_argument("-o", "--output", default="storyboard.png", help="Output contact sheet image")
    sb_parser.add_argument("--props", default=None, help="JSON string or path to .json file with runtime props")
    sb_parser.add_argument("--rows", type=int, default=2, help="Storyboard rows")
    sb_parser.add_argument("--cols", type=int, default=3, help="Storyboard columns")

    # vibmo studio / preview
    studio_parser = subparsers.add_parser("studio", help="Launch interactive in-browser Web Studio")
    studio_parser.add_argument("script", nargs="?", default=None, help="Optional Python scene script file")
    studio_parser.add_argument("--port", type=int, default=8000, help="Web Studio port")

    preview_parser = subparsers.add_parser("preview", help="Alias for 'vibmo studio'")
    preview_parser.add_argument("script", nargs="?", default=None, help="Optional Python scene script file")
    preview_parser.add_argument("--port", type=int, default=8000, help="Web Studio port")

    # vibmo schema
    schema_parser = subparsers.add_parser("schema", help="Export LLM tool calling schema (OpenAI, Anthropic, Gemini)")
    schema_parser.add_argument("--format", default="openai", choices=["openai", "anthropic", "gemini", "json"], help="Schema output format")

    # vibmo mcp
    subparsers.add_parser("mcp", help="Start Model Context Protocol (MCP) JSON-RPC stdio server for AI agents")

    # vibmo desktop (PySide6 Native Workstation)
    desktop_parser = subparsers.add_parser("desktop", help="Launch native PySide6 Desktop Workstation")
    desktop_parser.add_argument("project", nargs="?", default=None, help="Optional .vibmo project file or script")

    # vibmo package (DaVinci .dra Project Bundle)
    package_parser = subparsers.add_parser("package", help="Bundle script, assets, fonts, and LUTs into a self-contained .vibmo archive")
    package_parser.add_argument("script", help="Python scene or sequence script file")
    package_parser.add_argument("-o", "--output", default=None, help="Output .vibmo archive file path")
    package_parser.add_argument("--no-assets", action="store_true", help="Exclude local assets/ folder")
    package_parser.add_argument("--no-preview", action="store_true", help="Exclude storyboard preview image")

    # vibmo unpackage (Restore .vibmo Archive)
    unpackage_parser = subparsers.add_parser("unpackage", help="Extract and restore a .vibmo project archive")
    unpackage_parser.add_argument("archive", help="Path to .vibmo archive file")
    unpackage_parser.add_argument("-d", "--dest", default=None, help="Target destination directory to extract to")

    # vibmo doctor
    subparsers.add_parser("doctor", help="Run environment and dependency diagnostic checks")

    args = parser.parse_args()

    if args.command == "package":
        from vibmo.packaging import ProjectArchive
        out_path = ProjectArchive.package(
            script_path=args.script,
            output_path=args.output,
            include_assets=not args.no_assets,
            include_preview=not args.no_preview,
        )
        info = ProjectArchive.inspect(out_path)
        console.print(Panel(
            f"[bold green]Successfully bundled project archive into [bold white]{out_path}[/bold white]![/bold green]\n\n"
            f"  * Entry Script: [cyan]{info.get('entry_script')}[/cyan]\n"
            f"  * Bundled Assets: [cyan]{len(info.get('assets', []))}[/cyan]\n"
            f"  * Total Archive Size: [cyan]{info.get('archive_size_bytes', 0):,} bytes[/cyan]\n"
            f"  * Contains Preview Storyboard: [cyan]{info.get('has_preview')}[/cyan]",
            title="✦ Vibmo Project Package Created",
            border_style="green"
        ))
        return

    if args.command == "unpackage":
        from vibmo.packaging import ProjectArchive
        dest_dir = ProjectArchive.unpackage(
            archive_path=args.archive,
            target_dir=args.dest,
        )
        console.print(Panel(
            f"[bold green]Successfully unpacked project archive to [bold white]{dest_dir}[/bold white]![/bold green]\n\n"
            f"Next steps:\n"
            f"  [cyan]cd {dest_dir}[/cyan]\n"
            f"  [cyan]vibmo studio scene.py[/cyan]",
            title="✦ Vibmo Project Restored",
            border_style="green"
        ))
        return

    if args.command == "ai":
        cmd_ai(
            prompt=args.prompt,
            edit_script=args.edit,
            output_video=args.output,
            chat_mode=args.chat,
            provider=args.provider,
        )
        return

    if args.command == "inspect":
        cmd_inspect(args.script)
        return

    if args.command == "watch":
        cmd_watch(args.script, open_studio=args.studio, port=args.port)
        return

    if args.command == "desktop":
        from vibmo.desktop.app import launch_desktop_studio
        console.print("[bold cyan]Launching Vibmo Studio Pro Desktop Workstation...[/bold cyan]")
        sys.exit(launch_desktop_studio(project_path=args.project))

    if args.command == "mcp":
        from vibmo.mcp.server import run_mcp_server
        run_mcp_server()
        return

    if args.command == "schema":
        from vibmo.ai.schema import export_llm_tool_definitions
        schema_json = export_llm_tool_definitions(args.format)
        console.print(schema_json)
        return

    if args.command == "doctor":
        import shutil
        import subprocess

        console.print("[bold cyan][*] Running Vibmo System Diagnostics...[/bold cyan]\n")
        all_passed = True

        # 1. Python
        py_ver = sys.version.split()[0]
        console.print(f"  [bold green][OK][/bold green] Python Runtime: [bold white]{py_ver}[/bold white]")

        # 2. PyCairo
        try:
            import cairo
            c_ver = getattr(cairo, "version", getattr(cairo, "cairo_version_string", lambda: "installed")())
            console.print(f"  [bold green][OK][/bold green] PyCairo Vector Backend: [bold white]{c_ver}[/bold white]")
        except Exception as e:
            console.print(f"  [bold red][FAIL][/bold red] PyCairo: Failed ({e})")
            all_passed = False

        # 3. NumPy & SciPy
        try:
            import numpy as np
            import scipy
            console.print(f"  [bold green][OK][/bold green] Math & Signal Processing: NumPy {np.__version__}, SciPy {scipy.__version__}")
        except Exception as e:
            console.print(f"  [bold red][FAIL][/bold red] NumPy/SciPy: Failed ({e})")
            all_passed = False

        # 4. FFmpeg
        ffmpeg_bin = shutil.which("ffmpeg")
        if ffmpeg_bin:
            try:
                out = subprocess.run(["ffmpeg", "-version"], capture_output=True, text=True).stdout
                first_line = out.splitlines()[0] if out else "Unknown"
                console.print(f"  [bold green][OK][/bold green] FFmpeg Video Encoder: [bold white]{first_line}[/bold white] at {ffmpeg_bin}")
            except Exception:
                console.print(f"  [bold green][OK][/bold green] FFmpeg Video Encoder: Located at {ffmpeg_bin}")
        else:
            console.print("  [bold yellow][WARN][/bold yellow] FFmpeg: [bold yellow]Not found in PATH[/bold yellow]. (Required for video rendering)")
            all_passed = False

        # 5. Headless Browser
        from vibmo.importers.web import find_system_browser
        browser_path = find_system_browser()
        if browser_path:
            console.print(f"  [bold green][OK][/bold green] Web Ingestion Engine: Browser found at [bold white]{browser_path}[/bold white]")
        else:
            console.print("  [bold yellow][WARN][/bold yellow] Web Ingestion: No Chrome/Edge browser found (optional for Asset.web/Asset.html)")

        # 6. ModernGL GPU Shaders
        try:
            import moderngl
            console.print(f"  [bold green][OK][/bold green] Hardware GPU Shaders: ModernGL {moderngl.__version__}")
        except ImportError:
            console.print("  [bold white][INFO][/bold white] Hardware GPU Shaders: ModernGL not installed (using high-speed CPU fallback)")

        # 7. AI Providers
        from vibmo.ai.keys import get_all_keys
        keys = get_all_keys()
        configured = [v["name"] for v in keys.values() if v["is_configured"]]
        if configured:
            console.print(f"  [bold green][OK][/bold green] Configured AI Providers: [bold white]{', '.join(configured)}[/bold white]")
        else:
            console.print("  [bold yellow][INFO][/bold yellow] AI Providers: No API keys configured in .env (falling back to deterministic synthesis)")

        console.print()
        if all_passed:
            console.print(Panel("[bold green]All core systems operational! Ready to render production graphics.[/bold green]", border_style="green"))
        else:
            console.print(Panel("[bold yellow]Some optional dependencies or FFmpeg are missing. Check above.[/bold yellow]", border_style="yellow"))
        return

    if args.command == "templates":
        from vibmo.templates.catalog import TEMPLATES
        console.print("[bold cyan]Available Production Templates:[/bold cyan]")
        for k, v in TEMPLATES.items():
            console.print(f"  * [bold green]{k}[/bold green]: {v['description']}")
        return

    if args.command == "create":
        from vibmo.templates.catalog import TEMPLATES
        proj_name = args.name or f"my_{args.template}"
        tmpl = TEMPLATES.get(args.template)
        if not tmpl:
            console.print(f"[bold red]Error:[/bold red] Unknown template '{args.template}'")
            return

        root = Path(proj_name)
        if root.exists():
            console.print(f"[bold red]Error:[/bold red] Directory '{proj_name}' already exists.")
            return

        (root / "assets").mkdir(parents=True, exist_ok=True)
        (root / "fonts").mkdir(parents=True, exist_ok=True)
        (root / "renders").mkdir(parents=True, exist_ok=True)
        (root / "storyboard").mkdir(parents=True, exist_ok=True)

        with open(root / "project.py", "w", encoding="utf-8") as f:
            f.write(tmpl["code"])

        with open(root / "vibmo.toml", "w", encoding="utf-8") as f:
            f.write(f'[project]\nname = "{proj_name}"\ntemplate = "{args.template}"\nfps = 60\n')

        console.print(Panel(
            f"[bold green]Created project from [bold white]{args.template}[/bold white] template in [bold white]{proj_name}[/bold white]![/bold green]\n\n"
            f"Next steps:\n"
            f"  [cyan]cd {proj_name}[/cyan]\n"
            f"  [cyan]vibmo studio project.py[/cyan]   (Open live Web Studio)\n"
            f"  [cyan]vibmo render project.py[/cyan]   (Render master video)",
            title="Template Initialized",
            border_style="green"
        ))
        return

    if args.command == "init":
        init_project(args.name)
        return

    if args.command in ("studio", "preview"):
        from vibmo.studio.router import launch_studio
        console.print(f"[bold cyan]Starting Vibmo Studio Pro[/bold cyan] on [green]http://127.0.0.1:{args.port}[/green]...")
        launch_studio(scene=None, script_path=args.script, port=args.port)
        return

    if not getattr(args, "script", None):
        console.print("[bold red]Error:[/bold red] Script argument is required for this command.")
        return

    runnable = _load_runnable_from_file(args.script)

    # Handle Runtime Data Props
    props_arg = getattr(args, "props", None)
    if props_arg and hasattr(runnable, "props"):
        if os.path.exists(props_arg):
            with open(props_arg, "r", encoding="utf-8") as f:
                runnable.props.update(json.load(f))
        else:
            try:
                runnable.props.update(json.loads(props_arg))
            except Exception:
                pass

    if args.command == "render":
        # Handle Social Media Presets with aspect ratio adjustments
        preset_name = args.preset.lower()
        if preset_name in ("instagram-reel", "tiktok", "youtube-short"):
            if hasattr(runnable, "width") and hasattr(runnable, "height"):
                runnable.width = 1080
                runnable.height = 1920
        elif preset_name == "twitter":
            if hasattr(runnable, "width") and hasattr(runnable, "height"):
                runnable.width = 1280
                runnable.height = 720

        console.print(f"[bold cyan]Rendering[/bold cyan] [white]{args.script}[/white] -> [green]{args.output}[/green] (quality={args.quality}, preset={args.preset})...")
        if hasattr(runnable, "render"):
            try:
                runnable.render(
                    output_path=args.output,
                    preset=args.preset if args.preset in ("mp4", "webm", "prores", "gif") else "mp4",
                    quality=args.quality,
                    resume=getattr(args, "resume", False),
                    motion_blur=getattr(args, "motion_blur", False),
                )
            except TypeError:
                runnable.render(
                    output_path=args.output,
                    preset="mp4",
                    quality=args.quality,
                )
        console.print(f"[bold green][OK] Done![/bold green] Video saved to [cyan]{args.output}[/cyan]")

    elif args.command == "storyboard":
        console.print(f"[bold cyan]Generating Storyboard[/bold cyan] [white]{args.script}[/white] -> [green]{args.output}[/green]...")
        runnable.storyboard(path=args.output, rows=args.rows, cols=args.cols)
        console.print(f"[bold green][OK] Done![/bold green] Storyboard saved to [cyan]{args.output}[/cyan]")


if __name__ == "__main__":
    cli()
