"""LLM service wrapper."""

from __future__ import annotations

import logging
from typing import AsyncGenerator

from ..core.exceptions import LLMError
from ..infrastructure.llm_provider import get_llm_provider

logger = logging.getLogger(__name__)


async def generate_explanation(prompt: str) -> str:
    """Generate an explanation using the configured LLM provider."""
    provider = get_llm_provider()
    try:
        return await provider.generate(prompt)
    except Exception as e:
        logger.error("LLM generation failed: %s", e)
        raise LLMError(f"Failed to generate explanation: {e}")


async def generate_explanation_stream(prompt: str) -> AsyncGenerator[str, None]:
    """Stream an explanation from the LLM provider."""
    provider = get_llm_provider()
    try:
        async for chunk in provider.generate_stream(prompt):
            yield chunk
    except Exception as e:
        logger.error("LLM stream failed: %s", e)
        yield f"\n\n[LLM Error: {e}]"
