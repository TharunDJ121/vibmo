"""
Unit tests for AI Agent scene generation, LLM tool calling schema export, plugin registry, and script watcher.
"""

import json
import time
import pytest
from vibmo.scene.scene import Scene
from vibmo.ai.agent_scene import AgentSceneGenerator
from vibmo.ai.schema import generate_component_schemas, export_llm_tool_definitions
from vibmo.plugins.registry import PluginRegistry, register_component, register_filter
from vibmo.studio.watcher import ScriptWatcher
from vibmo.scene.node import Node
from vibmo.fx.filters import FilmGrain



def test_scene_from_prompt_synthesis():
    prompt = "Create a high converting launch video for Vortex DB with $148K MRR"
    scene = Scene.from_prompt(prompt, duration=3.5)

    assert isinstance(scene, Scene)
    assert scene.duration == 3.5
    assert len(scene.nodes) >= 2
    # Check that pre-flight validation succeeds
    assert scene.validate() == []


def test_llm_schema_exporter_formats():
    # 1. Component schemas
    schemas = generate_component_schemas()
    assert len(schemas) >= 15

    # 2. OpenAI Tool Call Schema
    openai_json = export_llm_tool_definitions(format_type="openai")
    openai_tools = json.loads(openai_json)
    assert len(openai_tools) >= 15
    assert openai_tools[0]["type"] == "function"

    # 3. Anthropic Tool Schema
    anthropic_json = export_llm_tool_definitions(format_type="anthropic")
    anthropic_tools = json.loads(anthropic_json)
    assert len(anthropic_tools) >= 15
    assert "input_schema" in anthropic_tools[0]

    # 4. Gemini Function Declarations
    gemini_json = export_llm_tool_definitions(format_type="gemini")
    gemini_data = json.loads(gemini_json)
    assert "function_declarations" in gemini_data


def test_plugin_registry_and_decorator():
    @register_component(name="MyCustomWidget")
    class CustomWidget(Node):
        def draw(self, ctx, time=0.0):
            pass

    @register_filter(name="MyCyberpunkShader")
    class CyberpunkShader:
        def apply(self, surface, time=0.0):
            return surface


    assert PluginRegistry.get_component("MyCustomWidget") == CustomWidget
    assert "MyCustomWidget" in PluginRegistry.list_components()
    assert "MyCyberpunkShader" in PluginRegistry.list_filters()


def test_script_watcher_change_detection(tmp_path):
    script_file = tmp_path / "test_scene.py"
    script_file.write_text("scene = None", encoding="utf-8")

    change_count = [0]
    def on_reload():
        change_count[0] += 1

    watcher = ScriptWatcher(str(script_file), on_change=on_reload, poll_interval=0.05)
    watcher.start()

    time.sleep(0.1)
    script_file.write_text("scene = 123", encoding="utf-8")
    time.sleep(0.15)

    watcher.stop()
    assert change_count[0] >= 1
