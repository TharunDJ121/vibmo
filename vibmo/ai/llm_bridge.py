"""
Universal LLM Bridge for Vibmo.
Provides zero-dependency (httpx-based) synchronous and streaming LLM calls
across Anthropic, OpenAI, Google Gemini, Groq, and OpenRouter.
"""

from __future__ import annotations
import os
import json
import base64
from typing import Any, Dict, Generator, List, Optional, Tuple, Union
import httpx

from vibmo.ai.keys import get_active_provider_key, PROVIDERS


# Default model selections per provider
DEFAULT_MODELS = {
    "anthropic": "claude-3-7-sonnet-latest",
    "openai": "gpt-4o",
    "gemini": "gemini-2.0-flash",
    "groq": "llama-3.3-70b-versatile",
    "openrouter": "anthropic/claude-3.7-sonnet",
}


class LLMBridge:
    """
    Direct HTTP/REST client for invoking AI reasoning models without heavy external SDKs.
    """

    @classmethod
    def call(
        cls,
        prompt: str,
        system_prompt: Optional[str] = None,
        provider: Optional[str] = None,
        model: Optional[str] = None,
        images_base64: Optional[List[str]] = None,
        temperature: float = 0.2,
        max_tokens: int = 4096,
        timeout: float = 45.0,
    ) -> Tuple[bool, str, Dict[str, Any]]:
        """
        Executes a single-turn completion.
        Returns: (success: bool, response_text: str, metadata: dict)
        """
        active_provider, api_key = get_active_provider_key(provider)
        if not active_provider or not api_key:
            return (
                False,
                "No configured AI API key found. Please configure OPENAI_API_KEY, ANTHROPIC_API_KEY, or GEMINI_API_KEY.",
                {"provider": None, "model": None},
            )

        chosen_model = model or DEFAULT_MODELS.get(active_provider, "gpt-4o")

        try:
            if active_provider == "anthropic":
                return cls._call_anthropic(
                    api_key=api_key,
                    model=chosen_model,
                    prompt=prompt,
                    system_prompt=system_prompt,
                    images_base64=images_base64,
                    temperature=temperature,
                    max_tokens=max_tokens,
                    timeout=timeout,
                )
            elif active_provider == "gemini":
                return cls._call_gemini(
                    api_key=api_key,
                    model=chosen_model,
                    prompt=prompt,
                    system_prompt=system_prompt,
                    images_base64=images_base64,
                    temperature=temperature,
                    max_tokens=max_tokens,
                    timeout=timeout,
                )
            else:
                # OpenAI / Groq / OpenRouter OpenAI-compatible format
                base_url = "https://api.openai.com/v1"
                if active_provider == "groq":
                    base_url = "https://api.groq.com/openai/v1"
                elif active_provider == "openrouter":
                    base_url = "https://openrouter.ai/api/v1"

                return cls._call_openai_compatible(
                    api_key=api_key,
                    base_url=base_url,
                    provider_name=active_provider,
                    model=chosen_model,
                    prompt=prompt,
                    system_prompt=system_prompt,
                    images_base64=images_base64,
                    temperature=temperature,
                    max_tokens=max_tokens,
                    timeout=timeout,
                )
        except Exception as e:
            return False, f"LLM API Call Error ({active_provider}): {str(e)}", {"error": str(e), "provider": active_provider}

    @classmethod
    def stream(
        cls,
        prompt: str,
        system_prompt: Optional[str] = None,
        provider: Optional[str] = None,
        model: Optional[str] = None,
        temperature: float = 0.2,
        max_tokens: int = 4096,
        timeout: float = 45.0,
    ) -> Generator[str, None, None]:
        """
        Streams response tokens in real-time.
        """
        active_provider, api_key = get_active_provider_key(provider)
        if not active_provider or not api_key:
            yield "Error: No active AI API key configured. Please set an API key in Settings."
            return

        chosen_model = model or DEFAULT_MODELS.get(active_provider, "gpt-4o")

        try:
            if active_provider == "anthropic":
                headers = {
                    "x-api-key": api_key,
                    "anthropic-version": "2023-06-01",
                    "content-type": "application/json",
                }
                body: Dict[str, Any] = {
                    "model": chosen_model,
                    "max_tokens": max_tokens,
                    "temperature": temperature,
                    "stream": True,
                    "messages": [{"role": "user", "content": prompt}],
                }
                if system_prompt:
                    body["system"] = system_prompt

                with httpx.Client(timeout=timeout) as client:
                    with client.stream("POST", "https://api.anthropic.com/v1/messages", headers=headers, json=body) as response:
                        for line in response.iter_lines():
                            if line.startswith("data: "):
                                data_str = line[6:].strip()
                                if data_str == "[DONE]":
                                    break
                                try:
                                    evt = json.loads(data_str)
                                    if evt.get("type") == "content_block_delta":
                                        delta = evt.get("delta", {})
                                        if delta.get("type") == "text_delta":
                                            yield delta.get("text", "")
                                except Exception:
                                    continue

            elif active_provider == "gemini":
                # Use standard call for Gemini streaming or fallback
                success, text, _ = cls.call(prompt, system_prompt=system_prompt, provider="gemini", model=model)
                yield text

            else:
                # OpenAI / Groq / OpenRouter
                base_url = "https://api.openai.com/v1"
                if active_provider == "groq":
                    base_url = "https://api.groq.com/openai/v1"
                elif active_provider == "openrouter":
                    base_url = "https://openrouter.ai/api/v1"

                headers = {
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json",
                }
                messages = []
                if system_prompt:
                    messages.append({"role": "system", "content": system_prompt})
                messages.append({"role": "user", "content": prompt})

                body = {
                    "model": chosen_model,
                    "messages": messages,
                    "temperature": temperature,
                    "max_tokens": max_tokens,
                    "stream": True,
                }

                with httpx.Client(timeout=timeout) as client:
                    with client.stream("POST", f"{base_url}/chat/completions", headers=headers, json=body) as response:
                        for line in response.iter_lines():
                            if line.startswith("data: "):
                                data_str = line[6:].strip()
                                if data_str == "[DONE]":
                                    break
                                try:
                                    evt = json.loads(data_str)
                                    choices = evt.get("choices", [])
                                    if choices:
                                        content = choices[0].get("delta", {}).get("content", "")
                                        if content:
                                            yield content
                                except Exception:
                                    continue
        except Exception as e:
            yield f"\n[Streaming Error: {str(e)}]"

    # -------------------------------------------------------------------------
    # Provider Implementations
    # -------------------------------------------------------------------------

    @classmethod
    def _call_anthropic(
        cls,
        api_key: str,
        model: str,
        prompt: str,
        system_prompt: Optional[str],
        images_base64: Optional[List[str]],
        temperature: float,
        max_tokens: int,
        timeout: float,
    ) -> Tuple[bool, str, Dict[str, Any]]:
        headers = {
            "x-api-key": api_key,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json",
        }

        user_content: List[Dict[str, Any]] = []
        if images_base64:
            for img in images_base64:
                media_type = "image/png"
                clean_b64 = img
                if img.startswith("data:"):
                    parts = img.split(",", 1)
                    if len(parts) == 2:
                        clean_b64 = parts[1]
                        if "image/jpeg" in parts[0]:
                            media_type = "image/jpeg"
                user_content.append({
                    "type": "image",
                    "source": {
                        "type": "base64",
                        "media_type": media_type,
                        "data": clean_b64,
                    }
                })
        user_content.append({"type": "text", "text": prompt})

        body: Dict[str, Any] = {
            "model": model,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "messages": [{"role": "user", "content": user_content}],
        }
        if system_prompt:
            body["system"] = system_prompt

        with httpx.Client(timeout=timeout) as client:
            resp = client.post("https://api.anthropic.com/v1/messages", headers=headers, json=body)
            if resp.status_code != 200:
                return False, f"Anthropic API Error ({resp.status_code}): {resp.text}", {"status_code": resp.status_code}
            
            data = resp.json()
            blocks = data.get("content", [])
            text_out = "".join(b.get("text", "") for b in blocks if b.get("type") == "text")
            return True, text_out.strip(), {"provider": "anthropic", "model": model, "usage": data.get("usage")}

    @classmethod
    def _call_openai_compatible(
        cls,
        api_key: str,
        base_url: str,
        provider_name: str,
        model: str,
        prompt: str,
        system_prompt: Optional[str],
        images_base64: Optional[List[str]],
        temperature: float,
        max_tokens: int,
        timeout: float,
    ) -> Tuple[bool, str, Dict[str, Any]]:
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }

        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})

        user_content: Union[str, List[Dict[str, Any]]] = prompt
        if images_base64:
            user_content = [{"type": "text", "text": prompt}]
            for img in images_base64:
                url_val = img if img.startswith("data:") else f"data:image/png;base64,{img}"
                user_content.append({
                    "type": "image_url",
                    "image_url": {"url": url_val}
                })

        messages.append({"role": "user", "content": user_content})

        body = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }

        with httpx.Client(timeout=timeout) as client:
            resp = client.post(f"{base_url}/chat/completions", headers=headers, json=body)
            if resp.status_code != 200:
                return False, f"{provider_name.capitalize()} API Error ({resp.status_code}): {resp.text}", {"status_code": resp.status_code}

            data = resp.json()
            choices = data.get("choices", [])
            if not choices:
                return False, f"No choices returned from {provider_name}", {}
            text_out = choices[0].get("message", {}).get("content", "")
            return True, text_out.strip(), {"provider": provider_name, "model": model, "usage": data.get("usage")}

    @classmethod
    def _call_gemini(
        cls,
        api_key: str,
        model: str,
        prompt: str,
        system_prompt: Optional[str],
        images_base64: Optional[List[str]],
        temperature: float,
        max_tokens: int,
        timeout: float,
    ) -> Tuple[bool, str, Dict[str, Any]]:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"
        
        parts: List[Dict[str, Any]] = []
        if images_base64:
            for img in images_base64:
                mime_type = "image/png"
                clean_b64 = img
                if img.startswith("data:"):
                    p = img.split(",", 1)
                    if len(p) == 2:
                        clean_b64 = p[1]
                        if "image/jpeg" in p[0]:
                            mime_type = "image/jpeg"
                parts.append({
                    "inline_data": {
                        "mime_type": mime_type,
                        "data": clean_b64,
                    }
                })
        parts.append({"text": prompt})

        body: Dict[str, Any] = {
            "contents": [{"parts": parts}],
            "generationConfig": {
                "temperature": temperature,
                "maxOutputTokens": max_tokens,
            }
        }
        if system_prompt:
            body["systemInstruction"] = {
                "parts": [{"text": system_prompt}]
            }

        with httpx.Client(timeout=timeout) as client:
            resp = client.post(url, json=body)
            if resp.status_code != 200:
                return False, f"Gemini API Error ({resp.status_code}): {resp.text}", {"status_code": resp.status_code}

            data = resp.json()
            candidates = data.get("candidates", [])
            if not candidates:
                return False, "No candidates returned from Gemini", {}
            candidate_parts = candidates[0].get("content", {}).get("parts", [])
            text_out = "".join(p.get("text", "") for p in candidate_parts)
            return True, text_out.strip(), {"provider": "gemini", "model": model}
