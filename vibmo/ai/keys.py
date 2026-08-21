"""
API Key Management & Connectivity Verification for AI Providers.
Supports OpenAI, Anthropic, Gemini, Groq, and OpenRouter with secure local persistence and masking.
"""

from __future__ import annotations
import os
import re
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
import httpx


ENV_FILE = Path(".env")

PROVIDERS = {
    "openai": {
        "env_var": "OPENAI_API_KEY",
        "name": "OpenAI",
        "url": "https://api.openai.com/v1/models",
        "header_type": "bearer",
    },
    "anthropic": {
        "env_var": "ANTHROPIC_API_KEY",
        "name": "Anthropic",
        "url": "https://api.anthropic.com/v1/messages",
        "header_type": "x-api-key",
    },
    "gemini": {
        "env_var": "GEMINI_API_KEY",
        "name": "Google Gemini",
        "url": "https://generativelanguage.googleapis.com/v1beta/models",
        "header_type": "query_or_header",
    },
    "groq": {
        "env_var": "GROQ_API_KEY",
        "name": "Groq",
        "url": "https://api.groq.com/openai/v1/models",
        "header_type": "bearer",
    },
    "openrouter": {
        "env_var": "OPENROUTER_API_KEY",
        "name": "OpenRouter",
        "url": "https://openrouter.ai/api/v1/models",
        "header_type": "bearer",
    },
}


def mask_key(key: str) -> str:
    """Masks an API key for safe UI presentation (e.g. sk-ant...948f)."""
    if not key or len(key) <= 10:
        return "••••••••" if key else ""
    return f"{key[:6]}...{key[-4:]}"


def get_all_keys() -> Dict[str, Dict[str, Any]]:
    """Returns current status of all supported LLM providers."""
    results = {}
    for provider_id, meta in PROVIDERS.items():
        env_var = meta["env_var"]
        raw_key = os.environ.get(env_var, "")
        if not raw_key and ENV_FILE.exists():
            # Read from .env if present
            raw_key = _read_key_from_env(env_var)

        results[provider_id] = {
            "name": meta["name"],
            "env_var": env_var,
            "is_configured": bool(raw_key),
            "masked_key": mask_key(raw_key),
        }
    return results


def get_active_provider_key(preferred_provider: Optional[str] = None) -> Tuple[Optional[str], Optional[str]]:
    """Returns the first configured (provider_id, raw_key) tuple."""
    if preferred_provider and preferred_provider in PROVIDERS:
        meta = PROVIDERS[preferred_provider]
        key = os.environ.get(meta["env_var"]) or _read_key_from_env(meta["env_var"])
        if key:
            return preferred_provider, key

    # Check fallback order: anthropic -> openai -> gemini -> groq -> openrouter
    for p_id in ["anthropic", "openai", "gemini", "groq", "openrouter"]:
        meta = PROVIDERS[p_id]
        key = os.environ.get(meta["env_var"]) or _read_key_from_env(meta["env_var"])
        if key:
            return p_id, key
    return None, None


def save_key(provider_id: str, key_value: str) -> bool:
    """Saves API key to current process environment and persists in .env."""
    if provider_id not in PROVIDERS:
        raise ValueError(f"Unsupported provider '{provider_id}'")

    env_var = PROVIDERS[provider_id]["env_var"]
    clean_key = key_value.strip()

    # Set in memory
    if clean_key:
        os.environ[env_var] = clean_key
    elif env_var in os.environ:
        del os.environ[env_var]

    # Persist in .env
    _write_key_to_env(env_var, clean_key)
    return True


def verify_key_connection(provider_id: str, key_value: Optional[str] = None) -> Tuple[bool, str]:
    """Performs a lightweight connectivity test with the provider."""
    if provider_id not in PROVIDERS:
        return False, f"Unknown provider: {provider_id}"

    meta = PROVIDERS[provider_id]
    key = key_value or os.environ.get(meta["env_var"]) or _read_key_from_env(meta["env_var"])
    if not key:
        return False, f"No key configured for {meta['name']}"

    try:
        headers = {}
        params = {}
        if meta["header_type"] == "bearer":
            headers["Authorization"] = f"Bearer {key}"
        elif meta["header_type"] == "x-api-key":
            headers["x-api-key"] = key
            headers["anthropic-version"] = "2023-06-01"
        elif meta["header_type"] == "query_or_header":
            headers["x-goog-api-key"] = key

        with httpx.Client(timeout=6.0) as client:
            resp = client.get(meta["url"], headers=headers, params=params)
            # Most endpoints return 200 on valid key or 400 with valid schema
            if resp.status_code in (200, 201, 400):
                return True, f"Successfully connected to {meta['name']}!"
            elif resp.status_code in (401, 403):
                return False, f"Authentication failed: Invalid API key ({resp.status_code})"
            else:
                return True, f"Provider reached (Status {resp.status_code})"
    except Exception as e:
        return False, f"Connection error: {str(e)}"


# Alias for backward compatibility
test_key_connection = verify_key_connection


def _read_key_from_env(var_name: str) -> str:
    if not ENV_FILE.exists():
        return ""
    try:
        content = ENV_FILE.read_text(encoding="utf-8")
        match = re.search(rf"^{var_name}\s*=\s*['\"]?(.*?)['\"]?\s*$", content, re.MULTILINE)
        if match:
            return match.group(1).strip()
    except Exception:
        pass
    return ""


def _write_key_to_env(var_name: str, value: str) -> None:
    content = ""
    if ENV_FILE.exists():
        try:
            content = ENV_FILE.read_text(encoding="utf-8")
        except Exception:
            content = ""

    pattern = rf"^{var_name}\s*=.*$"
    if re.search(pattern, content, re.MULTILINE):
        if value:
            new_content = re.sub(pattern, f"{var_name}={value}", content, flags=re.MULTILINE)
        else:
            new_content = re.sub(pattern, "", content, flags=re.MULTILINE)
    else:
        new_content = content.rstrip() + f"\n{var_name}={value}\n" if value else content

    ENV_FILE.write_text(new_content.strip() + "\n", encoding="utf-8")
