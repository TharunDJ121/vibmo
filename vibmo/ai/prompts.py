"""
Comprehensive Prompt Engineering & System Instructions for Vibmo AI Engine.
Teaches LLMs how to construct production-quality motion design code with zero boilerplate.
"""

from __future__ import annotations
from typing import Optional
from vibmo.ai.schema import generate_component_schemas


def build_system_prompt(custom_context: Optional[str] = None) -> str:
    """
    Constructs the master Vibmo system prompt with dynamic component catalog introspection.
    """
    schemas = generate_component_schemas()
    component_lines = []
    for s in schemas[:35]:  # include primary semantic components
        name = s.get("name")
        desc = s.get("description", "")
        component_lines.append(f"- `{name}`: {desc}")

    components_doc = "\n".join(component_lines)

    base_prompt = f"""You are the Master AI Motion Graphics Engineer & Director for Vibmo (and Motio).
Your task is to write pristine, broadcast-ready Python motion graphics scripts with zero boilerplate.

## ✦ Core Principles & Rules:
1. **The God Import**: ALWAYS start scripts with `from motio.agent_api import *` (or `from vibmo.agent_api import *`).
2. **Declarative Scene Graph**:
   ```python
   scene = Scene(
       width=1920,
       height=1080,
       fps=60,
       duration=5.0,
       background=colors.DARK_NAVY,
   )
   ```
3. **Semantic Primitives & Cards**:
   - `GlassCard(direction="column", gap=16, padding=32, corner_radius=24, position=(240, 200))`
   - `KineticText("Headline Text", font_size=36, bold=True, color=colors.CYAN)`
   - `MetricCounter(start_val=0, end_val=150000, prefix="$", suffix=" MRR", font_size=52, bold=True, color=colors.EMERALD)`
   - `BrowserWindow(url="https://app.io", title="App Demo", width=1280, height=720, position=(320, 180))`
   - `AreaChart(data=[...], width=600, height=280, color=colors.INDIGO)`
   - `BarChart(data=[...], labels=[...], width=600, height=280, color=colors.CYAN)`
   - `Icon("lucide:sparkles", size=36, color=colors.CYAN)`
   - `Cursor()`, `Spotlight()`, `StatCard()`, `CodeWindow()`, `DataTable()`
4. **Cinematic Post-FX**:
   - `scene.add_post_fx(Vignette(intensity=0.25), FilmGrain(amount=0.015))`
5. **Choreography Generators (`@scene.animate`)**:
   ```python
   @scene.animate
   def main():
       # Parallel entrance
       yield scene.all(
           card.pop_in(delay=0.1, duration=0.8),
           chart.fade_up(offset=30, duration=0.8),
       )
       # Synchronized wave reveal & numeric ticker
       yield scene.all(
           title.reveal_characters(stagger=0.025),
           counter.count_to(duration=1.8, ease=Ease.out_expo),
       )
       card.float_idle(amplitude=6, speed=1.2)
       yield scene.wait(1.5)
   ```
6. **Multi-Scene Sequences**:
   If multi-scene, define `s1 = Scene(...)`, `s2 = Scene(...)` and assemble with `seq = Sequence(s1, s2, transition=CrossFade(0.5))` and sound effects: `seq.add_sfx("whoosh_cinematic", time=0.05)`.
7. **Timing Constraints**: Ensure sum of delays and action durations does NOT exceed `scene.duration`.

## 📦 Key Component Inventory:
{components_doc}

## 🎨 Color Tokens Available:
- `colors.DARK_NAVY`, `colors.SLATE_950`, `colors.CYAN`, `colors.INDIGO`, `colors.EMERALD`, `colors.VIOLET`, `colors.ROSE`, `colors.AMBER`, `colors.WHITE`, `colors.BLUE`

## Output Format Requirement:
Output ONLY executable Python code inside a single ```python ... ``` block. No markdown conversation or explanations outside the code block unless explicitly asked.
"""
    if custom_context:
        base_prompt += f"\n\n## Additional User Context & Instructions:\n{custom_context}"

    return base_prompt.strip()


def build_surgical_edit_prompt(current_code: str, instruction: str) -> str:
    """
    Constructs prompt specifically for surgical modifications of an existing script.
    """
    return f"""You are modifying an existing Vibmo motion graphics Python script.

## Instruction:
{instruction}

## Current Script Code:
```python
{current_code}
```

## Guidelines for Surgical Edits (Schema Mode):
1. You must translate the user's intent into a JSON object representing a Schema Operation.
2. The engine no longer accepts raw Python code replacements for surgical edits.
3. Supported operation types: "change_shot_duration", "set_font_asset".
4. Output EXACTLY ONE JSON block representing the edit, wrapped in ```json ... ```.

Example Output:
```json
{{
  "op_type": "change_shot_duration",
  "payload": {{
    "shot_id": "main_shot",
    "duration": 5.5
  }}
}}
```
"""


def build_auto_repair_prompt(code: str, errors: list[str]) -> str:
    """
    Constructs prompt for self-healing error repair.
    """
    err_str = "\n".join(errors)
    return f"""The following Vibmo motion graphics script produced runtime or validation errors.
Fix the errors and return the corrected, fully working Python code.

## Errors Encountered:
{err_str}

## Broken Code:
```python
{code}
```

## Instructions:
1. Diagnose the root cause of the syntax or runtime error.
2. Ensure imports are complete (`from motio.agent_api import *` or `from vibmo.agent_api import *`).
3. Ensure all variable names, component arguments, and animation verbs match the Vibmo API.
4. Output the fixed, complete code in a single ```python ... ``` block.
"""
