"""AI service unit tests (mocked — no live API calls)."""

from unittest.mock import AsyncMock, patch

import pytest

from services.ai.models import AICompletionResult, AIProvider, AITask
from services.ai.schemas import WebsiteAnalysisSchema
from services.ai.service import AIService


@pytest.fixture
def ai_service():
    return AIService()


def test_health_no_keys(ai_service):
    ai_service._openai._client = None
    ai_service._anthropic._client = None
    ai_service._gemini._api_key = ""
    health = ai_service.health()
    assert health.ready is False
    assert health.openai_configured is False
    assert health.gemini_configured is False


def test_model_routing_has_all_tasks():
    from services.ai.models import MODEL_ROUTING

    for task in AITask:
        assert task in MODEL_ROUTING
        provider, model, temp = MODEL_ROUTING[task]
        assert provider in (AIProvider.OPENAI, AIProvider.ANTHROPIC)
        assert model
        assert 0 <= temp <= 1


@pytest.mark.asyncio
async def test_complete_structured_openai(ai_service):
    mock_completion = AICompletionResult(
        content="{}",
        provider=AIProvider.OPENAI,
        model="gpt-4o",
        prompt_tokens=50,
        completion_tokens=50,
        total_tokens=100,
    )
    mock_data = {
        "business_type": "B2B SaaS",
        "products_services": ["CRM"],
        "target_audience": "SMBs",
        "unique_value_proposition": "Best CRM for small teams",
        "brand_tone": "professional",
        "key_messages": ["Easy to use"],
        "industry": "Software",
    }

    with (
        patch("services.ai.service.settings.ai_prefer_gemini", False),
        patch.object(
            ai_service._openai,
            "complete_json",
            AsyncMock(return_value=(mock_data, mock_completion)),
        ),
    ):
        data, result = await ai_service.complete_structured(
            AITask.COMPETITOR_RESEARCH,
            "Analyze competitors",
            WebsiteAnalysisSchema,
        )
        assert data.business_type == "B2B SaaS"
        assert result.total_tokens == 100


@pytest.mark.asyncio
async def test_complete_structured_defaults_max_tokens_to_none(ai_service):
    mock_completion = AICompletionResult(
        content="{}",
        provider=AIProvider.OPENAI,
        model="gpt-4o",
        prompt_tokens=50,
        completion_tokens=50,
        total_tokens=100,
    )
    complete_json = AsyncMock(return_value=({"keywords": []}, mock_completion))

    with patch.object(ai_service, "complete_json", complete_json):
        from services.ai.schemas import SEOStrategySchema

        await ai_service.complete_structured(
            AITask.SEO_STRATEGY,
            "Build SEO strategy",
            SEOStrategySchema,
        )
        assert complete_json.await_args.args[3] is None


def test_max_tokens_for_seo_strategy(ai_service):
    assert ai_service._max_tokens_for(AITask.SEO_STRATEGY) == 8192


@pytest.mark.asyncio
async def test_complete_json_falls_back_when_gemini_quota_exhausted(ai_service):
    from services.ai.gemini_client import GeminiAPIError

    mock_completion = AICompletionResult(
        content="{}",
        provider=AIProvider.OPENAI,
        model="gpt-4o",
        prompt_tokens=10,
        completion_tokens=10,
        total_tokens=20,
    )
    gemini_fail = AsyncMock(side_effect=GeminiAPIError(429, "Resource exhausted"))
    openai_ok = AsyncMock(return_value=({"ok": True}, mock_completion))

    with (
        patch("services.ai.service.settings.ai_prefer_gemini", True),
        patch.object(ai_service._gemini, "_api_key", "gemini-key"),
        patch.object(ai_service._openai, "_client", object()),
        patch.object(ai_service._gemini, "complete_json", gemini_fail),
        patch.object(ai_service._openai, "complete_json", openai_ok),
    ):
        data, result = await ai_service.complete_json(AITask.WEBSITE_ANALYSIS, "Analyze site")
        assert data == {"ok": True}
        assert result.provider == AIProvider.OPENAI
        gemini_fail.assert_awaited_once()
        openai_ok.assert_awaited_once()
