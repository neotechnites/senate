"""Unified Multi-Model Gateway for The Senate.

Provides provider-agnostic LLM routing across Anthropic, Google, OpenAI, and local providers.
Enables cross-model adversarial auditing and specialized task routing.
"""

import json
import os
import subprocess
from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List, Optional


class ModelProvider(str, Enum):
    ANTHROPIC = "anthropic"
    GOOGLE = "google"
    OPENAI = "openai"
    LOCAL = "local"
    CLI = "cli"


@dataclass
class ModelResponse:
    content: str
    provider: str
    model_name: str
    duration_s: float
    usage_tokens: Dict[str, int]
    is_error: bool = False
    error_message: Optional[str] = None


class ModelGateway:
    """Provider-agnostic router and multi-model executor."""

    def __init__(self, default_provider: ModelProvider = ModelProvider.CLI):
        self.default_provider = default_provider

    def query(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        model: Optional[str] = None,
        provider: Optional[ModelProvider] = None,
        json_mode: bool = False,
    ) -> ModelResponse:
        """Query a model using the appropriate provider backend."""
        selected_provider = provider or self.default_provider

        if selected_provider == ModelProvider.CLI:
            return self._query_cli(prompt, system_prompt, model or "claude")
        elif selected_provider == ModelProvider.ANTHROPIC:
            return self._query_anthropic(prompt, system_prompt, model or "claude-3-5-sonnet-20241022", json_mode)
        elif selected_provider == ModelProvider.GOOGLE:
            return self._query_google(prompt, system_prompt, model or "gemini-1.5-pro", json_mode)
        elif selected_provider == ModelProvider.OPENAI:
            return self._query_openai(prompt, system_prompt, model or "gpt-4o", json_mode)
        else:
            return ModelResponse(
                content="",
                provider=str(selected_provider),
                model_name=model or "unknown",
                duration_s=0.0,
                usage_tokens={},
                is_error=True,
                error_message=f"Unsupported model provider: {selected_provider}",
            )

    def _query_cli(self, prompt: str, system_prompt: Optional[str], model_name: str) -> ModelResponse:
        """Fallback to local CLI model runner if API keys are not directly exported."""
        import time
        start = time.time()
        
        # Check if claude or other CLI is available
        cli_bin = os.path.expanduser(f"~/.local/bin/{model_name}")
        if not os.path.exists(cli_bin):
            cli_bin = model_name

        cmd = [cli_bin, "-p", prompt]
        if system_prompt:
            cmd.extend(["--system-prompt", system_prompt])

        try:
            res = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
            duration = time.time() - start
            if res.returncode == 0:
                return ModelResponse(
                    content=res.stdout.strip(),
                    provider="cli",
                    model_name=model_name,
                    duration_s=round(duration, 2),
                    usage_tokens={"input": len(prompt) // 4, "output": len(res.stdout) // 4},
                )
            else:
                return ModelResponse(
                    content="",
                    provider="cli",
                    model_name=model_name,
                    duration_s=round(duration, 2),
                    usage_tokens={},
                    is_error=True,
                    error_message=res.stderr.strip() or f"CLI returned code {res.returncode}",
                )
        except Exception as e:
            return ModelResponse(
                content="",
                provider="cli",
                model_name=model_name,
                duration_s=time.time() - start,
                usage_tokens={},
                is_error=True,
                error_message=str(e),
            )

    def _query_anthropic(self, prompt: str, system_prompt: Optional[str], model: str, json_mode: bool) -> ModelResponse:
        api_key = os.environ.get("ANTHROPIC_API_KEY")
        if not api_key:
            return self._query_cli(prompt, system_prompt, "claude")
        
        import time
        import urllib.request
        start = time.time()

        url = "https://api.anthropic.com/v1/messages"
        headers = {
            "x-api-key": api_key,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json",
        }
        body: Dict[str, Any] = {
            "model": model,
            "max_tokens": 4096,
            "messages": [{"role": "user", "content": prompt}],
        }
        if system_prompt:
            body["system"] = system_prompt

        try:
            req = urllib.request.Request(url, data=json.dumps(body).encode("utf-8"), headers=headers)
            with urllib.request.urlopen(req, timeout=60) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                duration = time.time() - start
                content = "".join(b.get("text", "") for b in data.get("content", []))
                return ModelResponse(
                    content=content,
                    provider="anthropic",
                    model_name=model,
                    duration_s=round(duration, 2),
                    usage_tokens={
                        "input": data.get("usage", {}).get("input_tokens", 0),
                        "output": data.get("usage", {}).get("output_tokens", 0),
                    },
                )
        except Exception as e:
            return ModelResponse(content="", provider="anthropic", model_name=model, duration_s=time.time() - start, usage_tokens={}, is_error=True, error_message=str(e))

    def _query_google(self, prompt: str, system_prompt: Optional[str], model: str, json_mode: bool) -> ModelResponse:
        api_key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
        if not api_key:
            return ModelResponse(content="", provider="google", model_name=model, duration_s=0.0, usage_tokens={}, is_error=True, error_message="GEMINI_API_KEY not configured in environment.")

        import time
        import urllib.request
        start = time.time()

        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"
        headers = {"content-type": "application/json"}
        
        contents = []
        if system_prompt:
            contents.append({"role": "user", "parts": [{"text": f"SYSTEM INSTRUCTION: {system_prompt}"}]})
            contents.append({"role": "model", "parts": [{"text": "Understood."}]})
        contents.append({"role": "user", "parts": [{"text": prompt}]})

        body = {"contents": contents}
        if json_mode:
            body["generationConfig"] = {"responseMimeType": "application/json"}

        try:
            req = urllib.request.Request(url, data=json.dumps(body).encode("utf-8"), headers=headers)
            with urllib.request.urlopen(req, timeout=60) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                duration = time.time() - start
                candidates = data.get("candidates", [])
                content = ""
                if candidates:
                    parts = candidates[0].get("content", {}).get("parts", [])
                    content = "".join(p.get("text", "") for p in parts)
                return ModelResponse(
                    content=content,
                    provider="google",
                    model_name=model,
                    duration_s=round(duration, 2),
                    usage_tokens={
                        "input": data.get("usageMetadata", {}).get("promptTokenCount", 0),
                        "output": data.get("usageMetadata", {}).get("candidatesTokenCount", 0),
                    },
                )
        except Exception as e:
            return ModelResponse(content="", provider="google", model_name=model, duration_s=time.time() - start, usage_tokens={}, is_error=True, error_message=str(e))

    def _query_openai(self, prompt: str, system_prompt: Optional[str], model: str, json_mode: bool) -> ModelResponse:
        api_key = os.environ.get("OPENAI_API_KEY")
        if not api_key:
            return ModelResponse(content="", provider="openai", model_name=model, duration_s=0.0, usage_tokens={}, is_error=True, error_message="OPENAI_API_KEY not configured in environment.")

        import time
        import urllib.request
        start = time.time()

        url = "https://api.openai.com/v1/chat/completions"
        headers = {
            "authorization": f"Bearer {api_key}",
            "content-type": "application/json",
        }
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        body: Dict[str, Any] = {
            "model": model,
            "messages": messages,
        }
        if json_mode:
            body["response_format"] = {"type": "json_object"}

        try:
            req = urllib.request.Request(url, data=json.dumps(body).encode("utf-8"), headers=headers)
            with urllib.request.urlopen(req, timeout=60) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                duration = time.time() - start
                choices = data.get("choices", [])
                content = choices[0].get("message", {}).get("content", "") if choices else ""
                return ModelResponse(
                    content=content,
                    provider="openai",
                    model_name=model,
                    duration_s=round(duration, 2),
                    usage_tokens={
                        "input": data.get("usage", {}).get("prompt_tokens", 0),
                        "output": data.get("usage", {}).get("completion_tokens", 0),
                    },
                )
        except Exception as e:
            return ModelResponse(content="", provider="openai", model_name=model, duration_s=time.time() - start, usage_tokens={}, is_error=True, error_message=str(e))
