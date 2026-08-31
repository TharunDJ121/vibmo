"""
Deep Analyzer for DaVinci Resolve Reference Manual (4,444 pages).
Extracts detailed chapter structures and topic mappings for Vibmo architecture.
"""

import os
import sys
import json
import pypdf

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

PDF_PATH = "DaVinci Resolve.pdf"

def analyze_details():
    if not os.path.exists("docs/davinci_outline_full.json"):
        return

    with open("docs/davinci_outline_full.json", "r", encoding="utf-8") as f:
        outline = json.load(f)

    def find_items(query_keywords):
        matches = []
        for item in outline:
            t = item["title"].lower()
            if any(k.lower() in t for k in query_keywords):
                matches.append(item)
        return matches

    print("=================================================================")
    print("✦ DAVINCI RESOLVE ARCHITECTURE ANALYSIS FOR VIBMO ROADMAP")
    print("=================================================================\n")

    domains = [
        ("1. Fusion Node Compositing & Visual DAG", ["fusion", "node editor", "spline", "macro", "merge", "3d nodes", "particles"]),
        ("2. Color Page, Scopes & Grade Nodes", ["color page", "grading", "primary", "lift, gamma", "curves", "scopes", "qualifier", "power windows"]),
        ("3. Fairlight Audio Engine, DSP & Foley", ["fairlight", "equalizer", "dynamics", "channel strip", "busses", "foley", "audio tracks", "meters"]),
        ("4. Edit Page NLE, Trimming & Timeline", ["edit page", "timeline", "trimming", "transitions", "transforms", "speed effects", "retime"]),
        ("5. Media Management & Media Pool", ["media page", "media pool", "metadata", "smart bins", "conforming"]),
        ("6. Deliver Engine & Render Pipeline", ["deliver page", "rendering media", "presets", "render queue", "dcp", "codecs"]),
        ("7. Automation, Python Scripting & DCTL", ["scripting", "python", "dctl", "workflow integrations", "tcp protocol", "api"]),
    ]

    domain_summary = {}

    for title, kws in domains:
        matched = find_items(kws)
        domain_summary[title] = matched
        print(f"📌 {title} ({len(matched)} matching sections):")
        for m in matched[:8]:
            print(f"   • [p. {m['page']}] {m['title']}")
        if len(matched) > 8:
            print(f"   • ... +{len(matched) - 8} more sections")
        print()

    # Save domain summary
    with open("docs/davinci_domain_mappings.json", "w", encoding="utf-8") as f:
        json.dump(domain_summary, f, indent=2, ensure_ascii=False)

    print("Saved domain mappings to docs/davinci_domain_mappings.json")

if __name__ == "__main__":
    analyze_details()
