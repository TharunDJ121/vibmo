"""
Vibmo Production CLI:
  vibmo init <name>       Scaffold a new motion design project
  vibmo render <script>   Render scene or sequence to MP4, WebM, ProRes, or GIF
  vibmo storyboard <script> Generate visual contact sheet
  vibmo studio <script>   Launch interactive browser Studio
"""

import sys
import os
import json
import argparse
import importlib.util
from pathlib import Path

from rich.console import Console
from rich.panel import Panel

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
[/bold cyan] [bold white]Production Motion Design System[/bold white]
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
            # If named 'scene' or has nodes, return immediately
            if attr_name == "scene" or len(getattr(attr, "nodes", [])) > 0:
                return attr

    # 2. Second priority: Any other Scene/Sequence instance
    for attr_name in dir(mod):
        attr = getattr(mod, attr_name)
        if not isinstance(attr, type) and isinstance(attr, (Scene, Sequence)):
            return attr

    # 3. Third priority: Factory functions (NOT classes)
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

    # Create directory tree
    (root / "assets").mkdir(parents=True, exist_ok=True)
    (root / "fonts").mkdir(parents=True, exist_ok=True)
    (root / "scenes").mkdir(parents=True, exist_ok=True)
    (root / "renders").mkdir(parents=True, exist_ok=True)
    (root / "storyboard").mkdir(parents=True, exist_ok=True)

    # Scaffolding project.py
    project_py_code = '''"""
Vibmo Motion Design Project
"""

from vibmo import (
    Scene,
    GlassCard,
    KineticText,
    MetricCounter,
    BrowserWindow,
    Cursor,
    Icon,
    Ease,
    FilmGrain,
    Vignette,
    colors,
    Color,
)

# 1. Initialize Scene (1080p @ 60 FPS)
scene = Scene(
    width=1920,
    height=1080,
    fps=60,
    duration=5.0,
    background=Color.hex("#090d16"),
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

    # Scaffolding vibmo.toml
    vibmo_toml = f'''[project]
name = "{project_name}"
version = "0.1.0"
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


def cli():
    if len(sys.argv) > 1 and sys.argv[1] not in ("mcp", "schema"):
        console.print(BANNER)
    parser = argparse.ArgumentParser(prog="vibmo", description="Vibmo Production Motion Design CLI")

    subparsers = parser.add_subparsers(dest="command", required=True)

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
    render_parser.add_argument("-p", "--preset", default="mp4", help="Codec preset (mp4, webm, prores, gif)")
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
    studio_parser = subparsers.add_parser("studio", help="Launch interactive in-browser Web Studio (script optional)")
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
    desktop_parser = subparsers.add_parser("desktop", help="Launch native PySide6 Desktop Workstation (DaVinci/AE style)")
    desktop_parser.add_argument("project", nargs="?", default=None, help="Optional .vibmo project file or script")

    # vibmo doctor
    subparsers.add_parser("doctor", help="Run environment and dependency diagnostic checks")

    args = parser.parse_args()

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
        console.print(f"[bold cyan]Rendering[/bold cyan] [white]{args.script}[/white] -> [green]{args.output}[/green] (quality={args.quality})...")
        if hasattr(runnable, "render"):
            try:
                runnable.render(
                    output_path=args.output,
                    preset=args.preset,
                    quality=args.quality,
                    resume=getattr(args, "resume", False),
                    motion_blur=getattr(args, "motion_blur", False),
                )
            except TypeError:
                # Fallback for Sequence
                runnable.render(
                    output_path=args.output,
                    preset=args.preset,
                    quality=args.quality,
                )
        console.print(f"[bold green][OK] Done![/bold green] Video saved to [cyan]{args.output}[/cyan]")
    elif args.command == "storyboard":
        console.print(f"[bold cyan]Generating Storyboard[/bold cyan] [white]{args.script}[/white] -> [green]{args.output}[/green]...")
        runnable.storyboard(path=args.output, rows=args.rows, cols=args.cols)
        console.print(f"[bold green][OK] Done![/bold green] Storyboard saved to [cyan]{args.output}[/cyan]")



if __name__ == "__main__":
    cli()
