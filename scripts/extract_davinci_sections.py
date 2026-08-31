"""
Deep content extraction from DaVinci Resolve Reference Manual.
Reads actual page text from critical architectural sections.
"""
import sys, os, json
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

import pypdf

reader = pypdf.PdfReader("DaVinci Resolve.pdf")
total = len(reader.pages)
print(f"Loaded: {total} pages\n")

def extract_pages(start, end, label):
    """Extract text from a range of pages."""
    text = []
    for i in range(start - 1, min(end, total)):
        try:
            t = reader.pages[i].extract_text()
            if t:
                text.append(t)
        except:
            pass
    combined = "\n".join(text)
    return combined

sections = {
    # Interface & Architecture overview
    "01_interface_overview": (12, 73),
    # Project Settings & Color Management
    "02_project_settings_color_mgmt": (139, 169),
    # Color Management (ACES, RCM)
    "03_color_management_aces": (225, 290),
    # Cut Page - fast editing paradigm
    "04_cut_page": (653, 700),
    # Edit Page - NLE timeline
    "05_edit_page_timeline": (814, 870),
    # Edit - Trimming tools
    "06_edit_trimming": (962, 1010),
    # Transitions & Compositing
    "07_transitions_compositing": (1176, 1260),
    # Speed Effects & Retime
    "08_speed_effects": (1253, 1280),
    # Fusion Introduction
    "09_fusion_intro": (1317, 1372),
    # Fusion Node Editor
    "10_fusion_node_editor": (1423, 1475),
    # Fusion Splines & Keyframes
    "11_fusion_splines_keyframes": (1547, 1610),
    # Fusion 3D Workspace
    "12_fusion_3d_workspace": (1710, 1760),
    # Fusion Particle System
    "13_fusion_particles": (1880, 1920),
    # Fusion Mask tools
    "14_fusion_masks": (1770, 1810),
    # Fusion Text+
    "15_fusion_text_plus": (1950, 1968),
    # Color Page Introduction
    "16_color_intro": (3084, 3115),
    # Color Page Scopes
    "17_color_scopes": (3115, 3160),
    # Color Primary Wheels
    "18_color_primary_grading": (3189, 3240),
    # Color Curves
    "19_color_curves": (3240, 3280),
    # Color Qualifiers & Windows
    "20_color_qualifiers_windows": (3280, 3360),
    # Color Node Graph
    "21_color_node_graph": (3360, 3420),
    # Fairlight Page
    "22_fairlight_page": (3814, 3870),
    # Fairlight Tracks & Busses
    "23_fairlight_tracks_busses": (3870, 3915),
    # Fairlight EQ & Dynamics
    "24_fairlight_eq_dynamics": (3940, 3990),
    # Fairlight Mixing
    "25_fairlight_mixing": (4020, 4060),
    # Deliver Page
    "26_deliver_page": (4170, 4220),
    # Scripting & Workflow API
    "27_scripting_api": (4409, 4444),
    # Resolve FX Overview
    "28_resolve_fx": (3594, 3640),
}

os.makedirs("docs/davinci_sections", exist_ok=True)

for name, (start, end) in sections.items():
    print(f"Extracting: {name} (pages {start}-{end})...")
    text = extract_pages(start, end, name)
    filepath = f"docs/davinci_sections/{name}.txt"
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(text)
    # Print summary stats
    lines = text.split("\n")
    words = len(text.split())
    print(f"  -> {len(lines)} lines, {words} words, saved to {filepath}")

print("\nDone! All sections extracted.")
