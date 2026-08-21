"""
LangGraph-powered Motion Graphics Architecture.
StateGraph pipeline for Natural Language Story Generation, Surgical Scene & Frame Editing,
Visual Storyboard Pre-flight Inspection, and Auto-Repair.
"""

from __future__ import annotations
import os
import re
from typing import Any, Dict, List, Optional
from langgraph.graph import StateGraph, END

from vibmo.ai.state import MotionGraphState
from vibmo.ai.surgical_editor import SurgicalSceneEditor
from vibmo.ai.keys import get_active_provider_key


def classify_intent_node(state: MotionGraphState) -> MotionGraphState:
    """Classifies user instruction as surgical edit vs new full story generation."""
    prompt = state.get("prompt", "").strip()
    current_code = state.get("current_code", "").strip()
    p_low = prompt.lower()

    log = state.get("execution_log", [])
    log.append(f"Classifying intent for prompt: '{prompt[:60]}...'")

    # If existing code is present and instruction asks to change/update/fix/tweak/make
    is_edit_intent = bool(current_code) and any(
        kw in p_low for kw in ["change", "update", "make", "replace", "set", "speed", "color", "zoom", "faster", "slower", "add", "remove", "in scene", "scene 1", "scene 2", "scene 3", "scene 4", "scene 5", "scene 6"]
    )

    intent = "surgical_scene_edit" if is_edit_intent else "new_story_generation"
    log.append(f"Intent classified as: {intent}")

    return {
        **state,
        "intent": intent,
        "iteration": state.get("iteration", 0) + 1,
        "execution_log": log,
    }


def surgical_edit_node(state: MotionGraphState) -> MotionGraphState:
    """Performs precision surgical modifications on targeted scenes and nodes."""
    prompt = state.get("prompt", "")
    current_code = state.get("current_code", "")
    log = state.get("execution_log", [])

    log.append("Executing surgical scene & frame modifications...")
    updated_code, changes = SurgicalSceneEditor.apply_edit(current_code, prompt)

    for ch in changes:
        log.append(f"  • {ch}")

    return {
        **state,
        "updated_code": updated_code,
        "response_message": "\n".join(changes),
        "execution_log": log,
    }


def generate_full_story_node(state: MotionGraphState) -> MotionGraphState:
    """Synthesizes a brand new multi-scene Motio sequence from natural language."""
    prompt = state.get("prompt", "")
    log = state.get("execution_log", [])
    log.append("Synthesizing multi-scene declarative Motio script...")

    # Template-based zero-boilerplate synthesizer
    code_template = f'''"""
✦ Generated Motion Graphics Sequence: {prompt[:40]}
Generated via Motio LangGraph Motion Engine.
"""

from motio.agent_api import *

# 1. Scene 1: High-Impact Entrance
s1 = Scene(width=720, height=1280, fps=60, duration=1.8, background=Color.WHITE)
card = ModelCard(title="Launch 2.0", subtitle="Next-Gen AI", preview_text="L a u n", position=(80, 560), shimmer=True)
s1.add(GradientBackdrop.sunset(), card)
s1.action(card.pop_in(delay=0.04, duration=0.45), card.bounce(amplitude=1.06, count=1, delay=0.95, duration=0.35))

# 2. Scene 2: Interactive Prompt Pill with Live Typing Stream
s2 = Scene(width=720, height=1280, fps=60, duration=2.0, background=Color.WHITE)
pill = ChatInputBar(text="{prompt[:36]}", variant="smooth", typing_start=0.20, typing_speed=28.0, position=(40, 596), shimmer=True)
s2.add(pill)
s2.action(pill.pop_in(duration=0.35))

# 3. Scene 3: Kinetic Typography Punch
s3 = Scene(width=720, height=1280, fps=60, duration=1.8, background=Color.WHITE)
kt = KineticSnapText(base_word="Think", word_a="faster", word_b="smarter", color_a="#8b5cf6", color_b="#f97316", switch_time=0.85)
s3.add(kt)
s3.action(kt.pop_in(duration=0.35), kt.bounce(amplitude=1.14, count=1, delay=0.85, duration=0.35))

# 4. Scene 4: Call to Action Pill Button with Specular Shimmer
s4 = Scene(width=720, height=1280, fps=60, duration=1.6, background=Color.WHITE)
cta = PillLaunchButton("Get Started", position=(130, 592), shimmer=True)
s4.add(GradientBackdrop.aurora(), cta)
s4.action(cta.pop_in(delay=0.04, duration=0.5), cta.bounce(amplitude=1.08, count=1, delay=0.55, duration=0.35))

# Assemble Master Sequence with Sound Design
seq = Sequence(s1, s2, s3, s4, transition=CrossFade(0.08))
seq.add_bg_music("tech_ambient_pulse", volume=0.20)
seq.add_sfx("whoosh_cinematic", time=0.04, volume=0.35)
seq.add_sfx("ui_click_mechanical", time=0.60, volume=0.50)
seq.add_sfx("freesound_community-keyboard-typing-5997.mp3", time=1.85, volume=0.70, duration=1.6)
seq.add_sfx("success_bell_chime", time=4.80, volume=0.75)

if __name__ == "__main__":
    seq.storyboard("storyboard.png")
    seq.render("output.mp4", quality="high")
'''
    return {
        **state,
        "updated_code": code_template,
        "response_message": "Generated 4-scene motion graphics sequence.",
        "execution_log": log,
    }


def validate_storyboard_node(state: MotionGraphState) -> MotionGraphState:
    """Pre-flight checks the updated code and renders visual feedback storyboard."""
    code = state.get("updated_code", "")
    log = state.get("execution_log", [])
    log.append("Validating script syntax and executing pre-flight checks...")

    is_valid, errors = SurgicalSceneEditor.execute_and_test(code)

    if is_valid:
        log.append("✅ Code verified: Syntax valid, zero runtime errors.")
    else:
        log.append(f"⚠️ Validation encountered {len(errors)} error(s): {errors[0] if errors else ''}")

    return {
        **state,
        "is_valid": is_valid,
        "validation_errors": errors,
        "execution_log": log,
    }


def auto_repair_node(state: MotionGraphState) -> MotionGraphState:
    """Self-healing node: attempts automated fixes for syntax or timing errors."""
    code = state.get("updated_code", "")
    errors = state.get("validation_errors", [])
    log = state.get("execution_log", [])
    log.append("Attempting self-healing repair...")

    repaired_code = code
    # Common fix: missing imports
    if "NameError" in str(errors) and "motio.agent_api" not in repaired_code:
        repaired_code = "from motio.agent_api import *\n" + repaired_code
        log.append("  • Injected missing 'from motio.agent_api import *'")

    return {
        **state,
        "updated_code": repaired_code,
        "iteration": state.get("iteration", 0) + 1,
        "execution_log": log,
    }


def route_intent(state: MotionGraphState) -> str:
    """Routes based on intent classification."""
    if state.get("intent") == "surgical_scene_edit":
        return "surgical_edit"
    return "generate_full_story"


def route_validation(state: MotionGraphState) -> str:
    """Routes based on validation success or loop limit."""
    if state.get("is_valid", False) or state.get("iteration", 0) >= 3:
        return END
    return "auto_repair"


def build_motion_graph() -> Any:
    """Builds and compiles the full LangGraph Motion StateGraph."""
    graph = StateGraph(MotionGraphState)

    # Register Nodes
    graph.add_node("classify_intent", classify_intent_node)
    graph.add_node("surgical_edit", surgical_edit_node)
    graph.add_node("generate_full_story", generate_full_story_node)
    graph.add_node("validate_storyboard", validate_storyboard_node)
    graph.add_node("auto_repair", auto_repair_node)

    # Set Entry Point
    graph.set_entry_point("classify_intent")

    # Conditional Branching
    graph.add_conditional_edges(
        "classify_intent",
        route_intent,
        {
            "surgical_edit": "surgical_edit",
            "generate_full_story": "generate_full_story",
        },
    )

    graph.add_edge("surgical_edit", "validate_storyboard")
    graph.add_edge("generate_full_story", "validate_storyboard")

    graph.add_conditional_edges(
        "validate_storyboard",
        route_validation,
        {
            END: END,
            "auto_repair": "auto_repair",
        },
    )

    graph.add_edge("auto_repair", "validate_storyboard")

    return graph.compile()


# Singleton compiled graph
motion_langgraph = build_motion_graph()


def run_motion_edit(prompt: str, current_code: str = "") -> Dict[str, Any]:
    """Top-level invocation wrapper for running surgical edits through LangGraph."""
    initial_state: MotionGraphState = {
        "prompt": prompt,
        "current_code": current_code,
        "iteration": 0,
        "execution_log": [],
    }
    result = motion_langgraph.invoke(initial_state)
    return result
