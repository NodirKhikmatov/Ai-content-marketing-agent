"""Unified AI service with model routing and structured outputs."""

import logging
from functools import lru_cache
from typing import Any, TypeVar

from pydantic import BaseModel

from app.config import settings
from services.ai.anthropic_client import AnthropicClient
from services.ai.errors import (
    format_all_providers_failed,
    is_recoverable_provider_error,
    should_skip_gemini_fallback,
)
from services.ai.gemini_client import GeminiClient
from services.ai.json_utils import parse_json_content
from services.ai.mock_responses import get_mock_response, get_mock_text
from services.ai.models import (
    AICompletionResult,
    AIHealthStatus,
    AIProvider,
    AITask,
    MODEL_ROUTING,
)
from services.ai.openai_client import OpenAIClient
from services.ai.prompts import get_system_prompt

logger = logging.getLogger(__name__)

T = TypeVar("T", bound=BaseModel)


class AIService:
    """Routes AI tasks to the appropriate provider and model."""

    def __init__(self) -> None:
        self._openai = OpenAIClient()
        self._anthropic = AnthropicClient()
        self._gemini = GeminiClient()

    @staticmethod
    def _mock_result() -> AICompletionResult:
        return AICompletionResult(
            content="",
            provider=AIProvider.GEMINI,
            model="mock",
            prompt_tokens=0,
            completion_tokens=0,
            total_tokens=0,
        )

    def health(self) -> AIHealthStatus:
        openai_ok = self._openai.is_configured
        anthropic_ok = self._anthropic.is_configured
        gemini_ok = self._gemini.is_configured
        return AIHealthStatus(
            openai_configured=openai_ok,
            anthropic_configured=anthropic_ok,
            gemini_configured=gemini_ok,
            ready=settings.ai_mock_mode or openai_ok or anthropic_ok or gemini_ok,
            models={
                task.value: f"{provider.value}/{model}"
                for task, (provider, model, _) in (
                    (t, self._resolve_routing(t)) for t in MODEL_ROUTING
                )
            },
        )

    def _resolve_routing(self, task: AITask) -> tuple[AIProvider, str, float]:
        provider, model, temperature = MODEL_ROUTING[task]

        if settings.ai_prefer_gemini and self._gemini.is_configured:
            return AIProvider.GEMINI, settings.gemini_model, temperature

        if provider == AIProvider.OPENAI and self._openai.is_configured:
            return provider, model, temperature
        if provider == AIProvider.ANTHROPIC and self._anthropic.is_configured:
            return provider, model, temperature
        if self._gemini.is_configured:
            return AIProvider.GEMINI, settings.gemini_model, temperature

        return provider, model, temperature

    def _max_tokens_for(self, task: AITask) -> int:
        if task in (
            AITask.COMPETITOR_RESEARCH,
            AITask.AUDIENCE_RESEARCH,
            AITask.CONTENT_PLANNING,
            AITask.SEO_STRATEGY,
        ):
            return 8192
        return 4096

    def _provider_chain(self, task: AITask) -> list[tuple[AIProvider, str, float]]:
        """Ordered providers to try; falls back when quota/rate limits hit."""
        _, _, temperature = MODEL_ROUTING[task]
        primary = self._resolve_routing(task)
        chain = [primary]
        seen = {primary[0]}

        candidates = [
            (AIProvider.OPENAI, settings.openai_model, self._openai.is_configured),
            (AIProvider.ANTHROPIC, settings.anthropic_model, self._anthropic.is_configured),
            (AIProvider.GEMINI, settings.gemini_model, self._gemini.is_configured),
        ]
        for provider, model, configured in candidates:
            if provider in seen or not configured:
                continue
            chain.append((provider, model, temperature))
            seen.add(provider)
        return chain

    async def _complete_json_with_provider(
        self,
        provider: AIProvider,
        model: str,
        temperature: float,
        system: str,
        user_prompt: str,
        tokens: int,
    ) -> tuple[dict[str, Any], AICompletionResult]:
        if provider == AIProvider.OPENAI:
            return await self._openai.complete_json(system, user_prompt, model, temperature)
        if provider == AIProvider.GEMINI:
            return await self._gemini.complete_json(
                system, user_prompt, model, temperature, max_tokens=tokens
            )
        return await self._anthropic.complete_json(
            system, user_prompt, model, max_tokens=tokens, temperature=temperature
        )

    async def complete_json(
        self,
        task: AITask,
        user_prompt: str,
        system_prompt: str | None = None,
        max_tokens: int | None = None,
    ) -> tuple[dict[str, Any], AICompletionResult]:
        if settings.ai_mock_mode:
            return get_mock_response(task), self._mock_result()

        system = system_prompt or get_system_prompt(task)
        tokens = max_tokens or self._max_tokens_for(task)
        errors: list[Exception] = []

        for provider, model, temperature in self._provider_chain(task):
            if provider == AIProvider.GEMINI and should_skip_gemini_fallback(errors):
                logger.warning(
                    "Skipping Gemini fallback for %s — Anthropic and OpenAI quotas exhausted",
                    task.value,
                )
                continue
            try:
                return await self._complete_json_with_provider(
                    provider, model, temperature, system, user_prompt, tokens
                )
            except Exception as exc:
                if not is_recoverable_provider_error(exc):
                    raise
                errors.append(exc)
                logger.warning(
                    "AI provider %s unavailable for %s (%s); trying fallback",
                    provider.value,
                    task.value,
                    exc,
                )

        if errors:
            raise RuntimeError(format_all_providers_failed(errors))
        raise RuntimeError("No AI provider configured")

    async def complete_structured(
        self,
        task: AITask,
        user_prompt: str,
        response_model: type[T],
        system_prompt: str | None = None,
        max_tokens: int | None = None,
    ) -> tuple[T, AICompletionResult]:
        data, result = await self.complete_json(task, user_prompt, system_prompt, max_tokens)
        return response_model.model_validate(data), result

    async def complete_text(
        self,
        task: AITask,
        user_prompt: str,
        system_prompt: str | None = None,
    ) -> AICompletionResult:
        if settings.ai_mock_mode:
            result = self._mock_result()
            result.content = get_mock_text(task)
            return result

        system = system_prompt or get_system_prompt(task)
        errors: list[Exception] = []

        for provider, model, temperature in self._provider_chain(task):
            if provider == AIProvider.GEMINI and should_skip_gemini_fallback(errors):
                logger.warning(
                    "Skipping Gemini fallback for %s — Anthropic and OpenAI quotas exhausted",
                    task.value,
                )
                continue
            try:
                if provider == AIProvider.OPENAI:
                    return await self._openai.complete(
                        system, user_prompt, model=model, temperature=temperature, json_mode=False
                    )
                if provider == AIProvider.GEMINI:
                    return await self._gemini.complete(
                        system, user_prompt, model=model, temperature=temperature, json_mode=False
                    )
                return await self._anthropic.complete(
                    system, user_prompt, model=model, temperature=temperature
                )
            except Exception as exc:
                if not is_recoverable_provider_error(exc):
                    raise
                errors.append(exc)
                logger.warning(
                    "AI provider %s unavailable for %s (%s); trying fallback",
                    provider.value,
                    task.value,
                    exc,
                )

        if errors:
            raise RuntimeError(format_all_providers_failed(errors))
        raise RuntimeError("No AI provider configured")


@lru_cache
def get_ai_service() -> AIService:
    if not settings.is_ai_configured:
        logger.warning("No AI API keys configured")
    return AIService()
