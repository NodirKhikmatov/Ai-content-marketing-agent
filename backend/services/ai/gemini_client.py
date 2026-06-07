import asyncio
import json
import logging
import re
from typing import Any, TypeVar

import httpx
from pydantic import BaseModel
from tenacity import retry, retry_if_not_exception_type, stop_after_attempt, wait_exponential

from app.config import settings
from services.ai.json_utils import parse_json_content
from services.ai.models import AICompletionResult, AIProvider

logger = logging.getLogger(__name__)

T = TypeVar("T", bound=BaseModel)

GEMINI_API_BASE = "https://generativelanguage.googleapis.com/v1beta"


class GeminiAPIError(Exception):
    """Non-retryable Gemini API error."""

    def __init__(self, status_code: int, message: str) -> None:
        self.status_code = status_code
        super().__init__(message)


def _strip_json_fences(content: str) -> str:
    content = content.strip()
    if content.startswith("```"):
        content = re.sub(r"^```(?:json)?\n?", "", content)
        content = re.sub(r"\n?```$", "", content)
    return content.strip()


class GeminiClient:
    """Async Google Gemini client via REST (free tier friendly)."""

    def __init__(self) -> None:
        self._api_key = settings.gemini_api_key

    @property
    def is_configured(self) -> bool:
        return bool(self._api_key)

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_not_exception_type((GeminiAPIError,)),
        reraise=True,
    )
    async def complete(
        self,
        system_prompt: str,
        user_prompt: str,
        model: str = settings.gemini_model,
        temperature: float = 0.7,
        json_mode: bool = True,
        max_tokens: int = 4096,
        _rate_limit_attempt: int = 0,
    ) -> AICompletionResult:
        if not self._api_key:
            raise RuntimeError("GEMINI_API_KEY not configured")

        url = f"{GEMINI_API_BASE}/models/{model}:generateContent"
        generation_config: dict[str, Any] = {
            "temperature": temperature,
            "maxOutputTokens": max_tokens,
        }
        if json_mode:
            generation_config["responseMimeType"] = "application/json"

        payload: dict[str, Any] = {
            "contents": [{"parts": [{"text": user_prompt}]}],
            "systemInstruction": {
                "parts": [
                    {
                        "text": (
                            f"{system_prompt}\n\n"
                            "Respond with valid JSON only. No markdown fences."
                        )
                    }
                ]
            },
            "generationConfig": generation_config,
        }

        logger.info("Gemini request model=%s", model)

        async with httpx.AsyncClient(timeout=120.0) as client:
            response = await client.post(url, params={"key": self._api_key}, json=payload)

        if response.status_code >= 400:
            detail = response.text[:500]
            try:
                detail = response.json().get("error", {}).get("message", detail)
            except Exception:
                pass
            detail_text = str(detail)
            if response.status_code == 429 and _rate_limit_attempt < 3:
                retry_match = re.search(r"please retry in ([0-9.]+)s", detail_text.lower())
                if retry_match:
                    # Always wait at least 65s so Gemini's 60s RPM window fully resets
                    wait_s = max(float(retry_match.group(1)) + 5.0, 65.0)
                    logger.warning("Gemini rate limited; retrying in %.1fs", wait_s)
                    await asyncio.sleep(wait_s)
                    return await self.complete(
                        system_prompt,
                        user_prompt,
                        model=model,
                        temperature=temperature,
                        json_mode=json_mode,
                        max_tokens=max_tokens,
                        _rate_limit_attempt=_rate_limit_attempt + 1,
                    )
            raise GeminiAPIError(response.status_code, detail_text)

        data = response.json()
        candidates = data.get("candidates") or []
        if not candidates:
            raise RuntimeError("Gemini returned no candidates")

        parts = candidates[0].get("content", {}).get("parts") or []
        content = parts[0].get("text", "") if parts else ""

        usage_meta = data.get("usageMetadata") or {}
        prompt_tokens = usage_meta.get("promptTokenCount", 0)
        completion_tokens = usage_meta.get("candidatesTokenCount", 0)

        return AICompletionResult(
            content=content,
            provider=AIProvider.GEMINI,
            model=model,
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            total_tokens=prompt_tokens + completion_tokens,
        )

    async def complete_json(
        self,
        system_prompt: str,
        user_prompt: str,
        model: str = settings.gemini_model,
        temperature: float = 0.7,
        max_tokens: int = 4096,
    ) -> tuple[dict[str, Any], AICompletionResult]:
        result = await self.complete(
            system_prompt,
            user_prompt,
            model=model,
            temperature=temperature,
            json_mode=True,
            max_tokens=max_tokens,
        )
        data = parse_json_content(result.content)
        return data, result

    async def complete_structured(
        self,
        system_prompt: str,
        user_prompt: str,
        response_model: type[T],
        model: str = settings.gemini_model,
        temperature: float = 0.7,
        max_tokens: int = 4096,
    ) -> tuple[T, AICompletionResult]:
        data, result = await self.complete_json(
            system_prompt, user_prompt, model, temperature, max_tokens
        )
        return response_model.model_validate(data), result
