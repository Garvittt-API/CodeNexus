"""Provider-agnostic LLM interface."""

from __future__ import annotations

import json
import logging
from abc import ABC, abstractmethod
from typing import AsyncGenerator

import httpx

from ..core.config import get_settings, LLMProvider

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """You are CodeNexus, an expert code analysis assistant. You help developers understand code repositories by answering questions about code, explaining functions and classes, and finding relevant code snippets. Always be concise, accurate, and helpful. When explaining code, reference the file path and line numbers."""


class BaseLLMProvider(ABC):
    @abstractmethod
    async def generate(self, prompt: str, system: str = SYSTEM_PROMPT) -> str:
        pass

    @abstractmethod
    async def generate_stream(
        self, prompt: str, system: str = SYSTEM_PROMPT
    ) -> AsyncGenerator[str, None]:
        if False:
            yield ""


class OllamaProvider(BaseLLMProvider):
    def __init__(self, base_url: str = "http://localhost:11434", model: str = "llama3"):
        self.base_url = base_url
        self.model = model

    async def generate(self, prompt: str, system: str = SYSTEM_PROMPT) -> str:
        async with httpx.AsyncClient(timeout=120.0) as client:
            response = await client.post(
                f"{self.base_url}/api/generate",
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "system": system,
                    "stream": False,
                },
            )
            response.raise_for_status()
            return response.json().get("response", "")

    async def generate_stream(
        self, prompt: str, system: str = SYSTEM_PROMPT
    ) -> AsyncGenerator[str, None]:
        async with httpx.AsyncClient(timeout=120.0) as client:
            async with client.stream(
                "POST",
                f"{self.base_url}/api/generate",
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "system": system,
                    "stream": True,
                },
            ) as response:
                response.raise_for_status()
                async for line in response.aiter_lines():
                    if line:
                        try:
                            data = json.loads(line)
                            if "response" in data:
                                yield data["response"]
                        except json.JSONDecodeError:
                            continue


class OpenAIProvider(BaseLLMProvider):
    def __init__(self, api_key: str, model: str = "gpt-4"):
        self.api_key = api_key
        self.model = model

    async def generate(self, prompt: str, system: str = SYSTEM_PROMPT) -> str:
        async with httpx.AsyncClient(timeout=120.0) as client:
            response = await client.post(
                "https://api.openai.com/v1/chat/completions",
                headers={"Authorization": f"Bearer {self.api_key}"},
                json={
                    "model": self.model,
                    "messages": [
                        {"role": "system", "content": system},
                        {"role": "user", "content": prompt},
                    ],
                    "temperature": 0.3,
                },
            )
            response.raise_for_status()
            return response.json()["choices"][0]["message"]["content"]

    async def generate_stream(
        self, prompt: str, system: str = SYSTEM_PROMPT
    ) -> AsyncGenerator[str, None]:
        async with httpx.AsyncClient(timeout=120.0) as client:
            async with client.stream(
                "POST",
                "https://api.openai.com/v1/chat/completions",
                headers={"Authorization": f"Bearer {self.api_key}"},
                json={
                    "model": self.model,
                    "messages": [
                        {"role": "system", "content": system},
                        {"role": "user", "content": prompt},
                    ],
                    "temperature": 0.3,
                    "stream": True,
                },
            ) as response:
                response.raise_for_status()
                async for line in response.aiter_lines():
                    if line.startswith("data: ") and line != "data: [DONE]":
                        try:
                            data = json.loads(line[6:])
                            delta = data["choices"][0].get("delta", {})
                            if "content" in delta:
                                yield delta["content"]
                        except (json.JSONDecodeError, KeyError, IndexError):
                            continue


class AnthropicProvider(BaseLLMProvider):
    def __init__(self, api_key: str, model: str = "claude-3-sonnet-20240229"):
        self.api_key = api_key
        self.model = model

    async def generate(self, prompt: str, system: str = SYSTEM_PROMPT) -> str:
        async with httpx.AsyncClient(timeout=120.0) as client:
            response = await client.post(
                "https://api.anthropic.com/v1/messages",
                headers={
                    "x-api-key": self.api_key,
                    "anthropic-version": "2023-06-01",
                },
                json={
                    "model": self.model,
                    "max_tokens": 2048,
                    "system": system,
                    "messages": [{"role": "user", "content": prompt}],
                },
            )
            response.raise_for_status()
            return response.json()["content"][0]["text"]

    async def generate_stream(
        self, prompt: str, system: str = SYSTEM_PROMPT
    ) -> AsyncGenerator[str, None]:
        async with httpx.AsyncClient(timeout=120.0) as client:
            async with client.stream(
                "POST",
                "https://api.anthropic.com/v1/messages",
                headers={
                    "x-api-key": self.api_key,
                    "anthropic-version": "2023-06-01",
                },
                json={
                    "model": self.model,
                    "max_tokens": 2048,
                    "system": system,
                    "messages": [{"role": "user", "content": prompt}],
                    "stream": True,
                },
            ) as response:
                response.raise_for_status()
                async for line in response.aiter_lines():
                    if line.startswith("data: "):
                        try:
                            data = json.loads(line[6:])
                            if data.get("type") == "content_block_delta":
                                yield data.get("delta", {}).get("text", "")
                        except json.JSONDecodeError:
                            continue


class GeminiProvider(BaseLLMProvider):
    def __init__(self, api_key: str, model: str = "gemini-pro"):
        self.api_key = api_key
        self.model = model

    async def generate(self, prompt: str, system: str = SYSTEM_PROMPT) -> str:
        async with httpx.AsyncClient(timeout=120.0) as client:
            response = await client.post(
                f"https://generativelanguage.googleapis.com/v1beta/models/{self.model}:generateContent?key={self.api_key}",
                json={
                    "contents": [{"parts": [{"text": f"{system}\n\n{prompt}"}]}],
                    "generationConfig": {"temperature": 0.3},
                },
            )
            response.raise_for_status()
            return response.json()["candidates"][0]["content"]["parts"][0]["text"]

    async def generate_stream(
        self, prompt: str, system: str = SYSTEM_PROMPT
    ) -> AsyncGenerator[str, None]:
        async with httpx.AsyncClient(timeout=120.0) as client:
            async with client.stream(
                "POST",
                f"https://generativelanguage.googleapis.com/v1beta/models/{self.model}:streamGenerateContent?key={self.api_key}",
                json={
                    "contents": [{"parts": [{"text": f"{system}\n\n{prompt}"}]}],
                    "generationConfig": {"temperature": 0.3},
                },
            ) as response:
                response.raise_for_status()
                async for line in response.aiter_lines():
                    try:
                        data = json.loads(line)
                        text = data["candidates"][0]["content"]["parts"][0]["text"]
                        yield text
                    except (json.JSONDecodeError, KeyError, IndexError):
                        continue


class DeepSeekProvider(BaseLLMProvider):
    def __init__(self, api_key: str, model: str = "deepseek-chat"):
        self.api_key = api_key
        self.model = model

    async def generate(self, prompt: str, system: str = SYSTEM_PROMPT) -> str:
        async with httpx.AsyncClient(timeout=120.0) as client:
            response = await client.post(
                "https://api.deepseek.com/chat/completions",
                headers={"Authorization": f"Bearer {self.api_key}"},
                json={
                    "model": self.model,
                    "messages": [
                        {"role": "system", "content": system},
                        {"role": "user", "content": prompt},
                    ],
                },
            )
            response.raise_for_status()
            return response.json()["choices"][0]["message"]["content"]

    async def generate_stream(
        self, prompt: str, system: str = SYSTEM_PROMPT
    ) -> AsyncGenerator[str, None]:
        async with httpx.AsyncClient(timeout=120.0) as client:
            async with client.stream(
                "POST",
                "https://api.deepseek.com/chat/completions",
                headers={"Authorization": f"Bearer {self.api_key}"},
                json={
                    "model": self.model,
                    "messages": [
                        {"role": "system", "content": system},
                        {"role": "user", "content": prompt},
                    ],
                    "stream": True,
                },
            ) as response:
                response.raise_for_status()
                async for line in response.aiter_lines():
                    if line.startswith("data: ") and line != "data: [DONE]":
                        try:
                            data = json.loads(line[6:])
                            delta = data["choices"][0].get("delta", {})
                            if "content" in delta:
                                yield delta["content"]
                        except (json.JSONDecodeError, KeyError, IndexError):
                            continue


class MistralProvider(BaseLLMProvider):
    def __init__(self, api_key: str, model: str = "mistral-large-latest"):
        self.api_key = api_key
        self.model = model

    async def generate(self, prompt: str, system: str = SYSTEM_PROMPT) -> str:
        async with httpx.AsyncClient(timeout=120.0) as client:
            response = await client.post(
                "https://api.mistral.ai/v1/chat/completions",
                headers={"Authorization": f"Bearer {self.api_key}"},
                json={
                    "model": self.model,
                    "messages": [
                        {"role": "system", "content": system},
                        {"role": "user", "content": prompt},
                    ],
                },
            )
            response.raise_for_status()
            return response.json()["choices"][0]["message"]["content"]

    async def generate_stream(
        self, prompt: str, system: str = SYSTEM_PROMPT
    ) -> AsyncGenerator[str, None]:
        async with httpx.AsyncClient(timeout=120.0) as client:
            async with client.stream(
                "POST",
                "https://api.mistral.ai/v1/chat/completions",
                headers={"Authorization": f"Bearer {self.api_key}"},
                json={
                    "model": self.model,
                    "messages": [
                        {"role": "system", "content": system},
                        {"role": "user", "content": prompt},
                    ],
                    "stream": True,
                },
            ) as response:
                response.raise_for_status()
                async for line in response.aiter_lines():
                    if line.startswith("data: ") and line != "data: [DONE]":
                        try:
                            data = json.loads(line[6:])
                            delta = data["choices"][0].get("delta", {})
                            if "content" in delta:
                                yield delta["content"]
                        except (json.JSONDecodeError, KeyError, IndexError):
                            continue


class FakeLLMProvider(BaseLLMProvider):
    """Fallback provider that returns a mock response when no real provider is available."""

    async def generate(self, prompt: str, system: str = SYSTEM_PROMPT) -> str:
        return "LLM provider not configured. Please set up Ollama or provide an API key for your preferred provider."

    async def generate_stream(
        self, prompt: str, system: str = SYSTEM_PROMPT
    ) -> AsyncGenerator[str, None]:
        msg = "LLM provider not configured. Please set up Ollama or provide an API key for your preferred provider."
        for word in msg.split(" "):
            yield word + " "


def get_llm_provider() -> BaseLLMProvider:
    settings = get_settings()
    provider = settings.LLM_PROVIDER

    if provider == LLMProvider.OLLAMA:
        return OllamaProvider(
            base_url=settings.OLLAMA_BASE_URL, model=settings.LLM_MODEL
        )
    elif provider == LLMProvider.OPENAI and settings.OPENAI_API_KEY:
        return OpenAIProvider(api_key=settings.OPENAI_API_KEY, model=settings.LLM_MODEL)
    elif provider == LLMProvider.ANTHROPIC and settings.ANTHROPIC_API_KEY:
        return AnthropicProvider(
            api_key=settings.ANTHROPIC_API_KEY, model=settings.LLM_MODEL
        )
    elif provider == LLMProvider.GEMINI and settings.GEMINI_API_KEY:
        return GeminiProvider(api_key=settings.GEMINI_API_KEY, model=settings.LLM_MODEL)
    elif provider == LLMProvider.DEEPSEEK and settings.DEEPSEEK_API_KEY:
        return DeepSeekProvider(
            api_key=settings.DEEPSEEK_API_KEY, model=settings.LLM_MODEL
        )
    elif provider == LLMProvider.MISTRAL and settings.MISTRAL_API_KEY:
        return MistralProvider(
            api_key=settings.MISTRAL_API_KEY, model=settings.LLM_MODEL
        )

    logger.warning("No LLM provider configured, using FakeLLMProvider")
    return FakeLLMProvider()
