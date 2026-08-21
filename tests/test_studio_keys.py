"""
Tests for API Key Persistence, Masking, and Studio Settings Endpoints.
"""

import os
import pytest
from fastapi.testclient import TestClient
from vibmo.ai.keys import (
    mask_key,
    get_all_keys,
    save_key,
    verify_key_connection,
)
from vibmo.studio.router import create_studio_app


def test_masking():
    assert mask_key("sk-ant-api03-abcdef123456789") == "sk-ant...6789"
    assert mask_key("sk-short") == "••••••••"
    assert mask_key("") == ""


def test_save_and_retrieve_keys():
    save_key("openai", "sk-test-mock-key-12345678")
    keys = get_all_keys()
    assert "openai" in keys
    assert keys["openai"]["is_configured"] is True
    assert "sk-tes...5678" in keys["openai"]["masked_key"]


def test_studio_keys_endpoints():
    app = create_studio_app()
    client = TestClient(app)

    # 1. Get Keys
    resp = client.get("/api/settings/keys")
    assert resp.status_code == 200
    data = resp.json()
    assert "providers" in data
    assert "anthropic" in data["providers"]

    # 2. Update Key
    resp = client.post(
        "/api/settings/keys",
        json={"provider": "groq", "key": "gsk_test_mock_12345678"},
    )
    assert resp.status_code == 200


def test_studio_ai_edit_endpoint():
    app = create_studio_app()
    client = TestClient(app)

    resp = client.post(
        "/api/ai/edit",
        json={
            "prompt": "change background to aurora",
            "code": "from motio.agent_api import *\ns1 = Scene()\ns1.add(GradientBackdrop.sunset())",
        },
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "ok"
    assert "GradientBackdrop.aurora()" in data["code"]
