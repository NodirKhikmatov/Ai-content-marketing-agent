import json
import logging
import re
from typing import Any, TypeVar

from anthropic import AsyncAnthropic
from openai import APIStatusError, AsyncOpenAI
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


class OpenAIClient:
    """Async OpenAI client with retry and token tracking."""

    def __init__(self) -> None:
        self._client = (
            AsyncOpenAI(api_key=settings.openai_api_key) if settings.openai_api_key else None
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
        model: str = settings.openai_model,
        temperature: float = 0.7,
        json_mode: bool = True,
    ) -> AICompletionResult:
        if not self._client:
            raise RuntimeError("OpenAI API key not configured")

        kwargs: dict[str, Any] = {
            "model": model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            "temperature": temperature,
        }
        if json_mode:
            kwargs["response_format"] = {"type": "json_object"}

        logger.info("OpenAI request model=%s tokens_est=%d", model, len(user_prompt) // 4)

        response = await self._client.chat.completions.create(**kwargs)
        usage = response.usage

        return AICompletionResult(
            content=response.choices[0].message.content or "",
            provider=AIProvider.OPENAI,
            model=model,
            prompt_tokens=usage.prompt_tokens if usage else 0,
            completion_tokens=usage.completion_tokens if usage else 0,
            total_tokens=usage.total_tokens if usage else 0,
        )

    async def complete_json(
        self,
        system_prompt: str,
        user_prompt: str,
        model: str = settings.openai_model,
        temperature: float = 0.7,
    ) -> tuple[dict[str, Any], AICompletionResult]:
        result = await self.complete(
            system_prompt, user_prompt, model=model, temperature=temperature, json_mode=True
        )
        data = parse_json_content(result.content)
        return data, result

    async def complete_structured(
        self,
        system_prompt: str,
        user_prompt: str,
        response_model: type[T],
        model: str = settings.openai_model,
        temperature: float = 0.7,
    ) -> tuple[T, AICompletionResult]:
        data, result = await self.complete_json(system_prompt, user_prompt, model, temperature)
        return response_model.model_validate(data), result
