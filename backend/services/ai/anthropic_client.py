import json
import logging
import re
from typing import Any, TypeVar

from anthropic import APIStatusError, AsyncAnthropic
from pydantic import BaseModel
from tenacity import retry, retry_if_not_exception_type, stop_after_attempt, wait_exponential

from app.config import settings
from services.ai.json_utils import parse_json_content
from services.ai.models import AICompletionResult, AIProvider

logger = logging.getLogger(__name__)

T = TypeVar("T", bound=BaseModel)


def _strip_json_fences(content: str) -> str:
    content = content.strip()
    if content.startswith("```"):
        content = re.sub(r"^```(?:json)?\n?", "", content)
        content = re.sub(r"\n?```$", "", content)
    return content.strip()


class AnthropicClient:
    """Async Anthropic client with retry and token tracking."""

    def __init__(self) -> None:
        self._client = (
            AsyncAnthropic(api_key=settings.anthropic_api_key)
            if settings.anthropic_api_key
            else None
        )

    @property
    def is_configured(self) -> bool:
        return self._client is not None

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_not_exception_type((APIStatusError,)),
        reraise=True,
    )
    async def complete(
        self,
        system_prompt: str,
        user_prompt: str,
        model: str = settings.anthropic_model,
        max_tokens: int = 4096,
        temperature: float = 0.7,
    ) -> AICompletionResult:
        if not self._client:
            raise RuntimeError("Anthropic API key not configured")

        logger.info("Anthropic request model=%s", model)

        response = await self._client.messages.create(
            model=model,
            max_tokens=max_tokens,
            temperature=temperature,
            system=f"{system_prompt}\n\nRespond with valid JSON only. No markdown fences.",
            messages=[{"role": "user", "content": user_prompt}],
        )

        content = response.content[0].text
        usage = response.usage

        return AICompletionResult(
            content=content,
            provider=AIProvider.ANTHROPIC,
            model=model,
            prompt_tokens=usage.input_tokens if usage else 0,
            completion_tokens=usage.output_tokens if usage else 0,
            total_tokens=(usage.input_tokens + usage.output_tokens) if usage else 0,
        )

    async def complete_json(
        self,
        system_prompt: str,
        user_prompt: str,
        model: str = settings.anthropic_model,
        max_tokens: int = 4096,
        temperature: float = 0.7,
    ) -> tuple[dict[str, Any], AICompletionResult]:
        result = await self.complete(
            system_prompt, user_prompt, model=model, max_tokens=max_tokens, temperature=temperature
        )
        data = parse_json_content(result.content)
        return data, result

    async def complete_structured(
        self,
        system_prompt: str,
        user_prompt: str,
        response_model: type[T],
        model: str = settings.anthropic_model,
        max_tokens: int = 4096,
        temperature: float = 0.7,
    ) -> tuple[T, AICompletionResult]:
        data, result = await self.complete_json(
            system_prompt, user_prompt, model, max_tokens, temperature
        )
        return response_model.model_validate(data), result
