"""
Tests for LLMBridge and Provider Routing in Vibmo.
"""

import pytest
from unittest.mock import patch, MagicMock
from vibmo.ai.llm_bridge import LLMBridge, DEFAULT_MODELS


def test_llm_bridge_no_key():
    with patch("vibmo.ai.llm_bridge.get_active_provider_key", return_value=(None, None)):
        success, text, meta = LLMBridge.call(prompt="Hello")
        assert not success
        assert "No configured AI API key found" in text


def test_llm_bridge_openai_mock():
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = {
        "choices": [{"message": {"content": "```python\nscene = Scene()\n```"}}],
        "usage": {"total_tokens": 42},
    }

    with patch("vibmo.ai.llm_bridge.get_active_provider_key", return_value=("openai", "sk-mock-key")), \
         patch("httpx.Client.post", return_value=mock_resp):
        success, text, meta = LLMBridge.call(
            prompt="Create a scene",
            system_prompt="You are a motion designer",
            provider="openai",
        )
        assert success
        assert "scene = Scene()" in text
        assert meta["provider"] == "openai"


def test_llm_bridge_anthropic_mock():
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = {
        "content": [{"type": "text", "text": "```python\nscene = Scene(duration=4.0)\n```"}],
        "usage": {"input_tokens": 10, "output_tokens": 20},
    }

    with patch("vibmo.ai.llm_bridge.get_active_provider_key", return_value=("anthropic", "sk-ant-mock")), \
         patch("httpx.Client.post", return_value=mock_resp):
        success, text, meta = LLMBridge.call(
            prompt="Make a card",
            provider="anthropic",
        )
        assert success
        assert "duration=4.0" in text
        assert meta["provider"] == "anthropic"


def test_llm_bridge_gemini_mock():
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = {
        "candidates": [{
            "content": {"parts": [{"text": "```python\ncard = GlassCard()\n```"}]}
        }]
    }

    with patch("vibmo.ai.llm_bridge.get_active_provider_key", return_value=("gemini", "gemini-mock-key")), \
         patch("httpx.Client.post", return_value=mock_resp):
        success, text, meta = LLMBridge.call(
            prompt="Make a glass card",
            provider="gemini",
        )
        assert success
        assert "GlassCard" in text
        assert meta["provider"] == "gemini"
