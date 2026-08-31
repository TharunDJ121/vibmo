"""
Deep empirical audit for PROJECT_CATALOG.md.
Tests every class, method, argument, code block, and recipe.
"""

import ast
import inspect
import pathlib
import re
import sys
import textwrap

# Ensure UTF-8 output
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

import vibmo
import vibmo.agent_api as agent_api

CATALOG_PATH = pathlib.Path(__file__).parent.parent / "PROJECT_CATALOG.md"

def test_code_blocks():
    print("\n" + "="*80)
    print("TESTING ALL PYTHON CODE BLOCKS IN PROJECT_CATALOG.MD")
    print("="*80)
    
    content = CATALOG_PATH.read_text(encoding="utf-8")
    lines = content.splitlines()
    
    in_block = False
    lang = ""
    block_lines = []
    start_line = 0
    blocks = []
    
    for i, line in enumerate(lines, 1):
        if line.strip().startswith("```"):
            if not in_block:
                in_block = True
                lang = line.strip()[3:].strip()
                start_line = i
                block_lines = []
            else:
                in_block = False
                blocks.append({
                    "start": start_line,
                    "end": i,
                    "lang": lang,
                    "code": "\n".join(block_lines)
                })
        elif in_block:
            block_lines.append(line)
            
    py_blocks = [b for b in blocks if b["lang"] in ("python", "py")]
    print(f"Total Python Blocks Found: {len(py_blocks)}\n")
    
    issues = []
    for idx, b in enumerate(py_blocks, 1):
        raw_code = b["code"]
        dedented = textwrap.dedent(raw_code).strip()
        print(f"--- Block {idx} (Lines {b['start']}-{b['end']}) ---")
        print(f"Code Preview:\n{textwrap.indent(dedented[:120], '  ')}...\n")
        
        # Syntax Check
        try:
            tree = ast.parse(dedented)
            print("  AST Syntax: OK")
        except SyntaxError as e:
            print(f"  AST Syntax: FAILED -> {e}")
            issues.append((idx, b["start"], "SyntaxError", str(e)))
            continue
            
        # Execution Check
        sandbox = {}
        exec("from vibmo.agent_api import *", sandbox)
        sandbox["__name__"] = "__main_test__" # avoid full render in if __name__ == '__main__':
        
        # Test imports and execution up to main execution
        try:
            exec(dedented, sandbox)
            print("  Execution: OK")
        except Exception as e:
            print(f"  Execution: FAILED -> {type(e).__name__}: {e}")
            issues.append((idx, b["start"], type(e).__name__, str(e)))
            
        print()
        
    return issues

def test_all_classes_and_methods():
    print("\n" + "="*80)
    print("TESTING ALL CATALOG CLASSES AND API EXPORTS")
    print("="*80)
    
    content = CATALOG_PATH.read_text(encoding="utf-8")
    
    # Find all backtick identifiers that look like Class names (PascalCase)
    class_candidates = set(re.findall(r"`([A-Z][a-zA-Z0-9]+)`", content))
    print(f"Found {len(class_candidates)} PascalCase symbols in backticks.")
    
    # Known exceptions that are not classes (e.g., Markdown headers, acronyms, or types)
    ignored = {"Scene", "Color", "Ease", "Node", "MP4", "GIF", "XML", "JSON", "VIBMO", "BPM", "HUD", "OTIO", "FCP", "DRTMode", "VRAM", "VBOs", "VAOs", "FBOs"}
    
    tested = 0
    missing_in_vibmo = []
    missing_in_agent_api = []
    
    for cls_name in sorted(class_candidates):
        if cls_name in ignored:
            continue
        tested += 1
        has_vibmo = hasattr(vibmo, cls_name)
        has_agent = hasattr(agent_api, cls_name)
        
        if not has_agent:
            if has_vibmo:
                missing_in_agent_api.append((cls_name, "Exported in vibmo, but MISSING from vibmo.agent_api"))
            else:
                # Check if it's anywhere in vibmo submodules
                found_in_sub = None
                for attr, mod in sys.modules.items():
                    if attr.startswith("vibmo.") and hasattr(mod, cls_name):
                        found_in_sub = attr
                        break
                if found_in_sub:
                    missing_in_agent_api.append((cls_name, f"Found in {found_in_sub}, but NOT in agent_api/vibmo root"))
                else:
                    missing_in_vibmo.append((cls_name, "Not found anywhere in vibmo"))
                    
    print(f"Tested {tested} class symbols.")
    print(f"Missing from agent_api: {len(missing_in_agent_api)}")
    for name, reason in missing_in_agent_api:
        print(f"  [AGENT_API MISSING] {name}: {reason}")
        
    print(f"Completely Missing: {len(missing_in_vibmo)}")
    for name, reason in missing_in_vibmo:
        print(f"  [TOTAL MISSING] {name}: {reason}")
        
    return missing_in_agent_api, missing_in_vibmo

def test_hardware_mockup_apis():
    print("\n" + "="*80)
    print("TESTING HARDWARE MOCKUP APIs (add_screen vs add_screen_content)")
    print("="*80)
    
    hardware_classes = [
        "FoldableDeviceFrame", "RuggedSmartwatchFrame", "SuperUltrawideMonitorFrame",
        "PosTerminalFrame", "CameraViewfinderOverlay", "MinimalistEInkTabletFrame",
        "SmartHomeHubFrame", "RetroArcadeCrtCabinet", "CctvQuadViewOverlay",
        "SpatialVisorFrame", "OledCinemaTvFrame", "AutomotiveCockpitDash",
        "HandheldGamingConsoleFrame", "CyberdeckChassisFrame", "MultiMonitorDeveloperRig",
        "LaptopFrame", "PhoneFrame", "BrowserWindow"
    ]
    
    results = []
    for h in hardware_classes:
        if hasattr(agent_api, h):
            cls = getattr(agent_api, h)
            has_add_screen = hasattr(cls, "add_screen")
            has_add_screen_content = hasattr(cls, "add_screen_content")
            has_add_content = hasattr(cls, "add_content")
            results.append({
                "class": h,
                "add_screen": has_add_screen,
                "add_screen_content": has_add_screen_content,
                "add_content": has_add_content
            })
            print(f"{h:30} -> add_screen: {has_add_screen!s:5} | add_screen_content: {has_add_screen_content!s:5} | add_content: {has_add_content!s:5}")
        else:
            print(f"{h:30} -> NOT FOUND IN AGENT_API")
    return results

def test_scene_audio_apis():
    print("\n" + "="*80)
    print("TESTING SCENE AUDIO APIs")
    print("="*80)
    
    scene = agent_api.Scene()
    scene_audio_methods = [m for m in dir(scene) if "audio" in m or "sfx" in m or "track" in m or "marker" in m]
    print(f"Scene audio/track methods: {scene_audio_methods}")
    
    print(f"has add_audio_clip: {hasattr(scene, 'add_audio_clip')}")
    print(f"has add_audio_track: {hasattr(scene, 'add_audio_track')}")
    print(f"has add_audio: {hasattr(scene, 'add_audio')}")
    print(f"has sfx attribute: {hasattr(scene, 'sfx')}")

def test_quality_gate_apis():
    print("\n" + "="*80)
    print("TESTING QUALITY GATES APIs")
    print("="*80)
    
    from vibmo.quality.slideshow_risk import SlideshowRiskScorer
    print(f"SlideshowRiskScorer methods: {[m for m in dir(SlideshowRiskScorer) if not m.startswith('_')]}")
    
    # Test SlideshowRiskScorer.evaluate vs evaluate_scene
    scene = agent_api.Scene()
    try:
        r1 = SlideshowRiskScorer.evaluate_scene(scene)
        print(f"SlideshowRiskScorer.evaluate_scene(scene) -> Success: verdict={r1.verdict}")
    except Exception as e:
        print(f"SlideshowRiskScorer.evaluate_scene(scene) -> FAILED: {e}")
        
    try:
        r2 = SlideshowRiskScorer.evaluate([{"name": "MasterScene", "nodes": len(scene.nodes)}])
        print(f"SlideshowRiskScorer.evaluate([...]) -> Success: verdict={r2.verdict}")
    except Exception as e:
        print(f"SlideshowRiskScorer.evaluate([...]) -> FAILED: {e}")

if __name__ == "__main__":
    test_code_blocks()
    test_all_classes_and_methods()
    test_hardware_mockup_apis()
    test_scene_audio_apis()
    test_quality_gate_apis()
