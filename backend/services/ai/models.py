"""AI model configuration and response types."""

from enum import StrEnum
from typing import Any, Generic, TypeVar

from pydantic import BaseModel, Field

from app.config import settings

T = TypeVar("T", bound=BaseModel)


class AIProvider(StrEnum):
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    GEMINI = "gemini"


class AITask(StrEnum):
    WEBSITE_ANALYSIS = "website_analysis"
    COMPETITOR_RESEARCH = "competitor_research"
    AUDIENCE_RESEARCH = "audience_research"
    SEO_STRATEGY = "seo_strategy"
    CONTENT_PLANNING = "content_planning"
    CAPTION_WRITING = "caption_writing"
    SCRIPT_WRITING = "script_writing"


# Model routing: task → (provider, model, temperature).
# Model names come from settings so a provider retirement is an env change, not a code change.
MODEL_ROUTING: dict[AITask, tuple[AIProvider, str, float]] = {
    AITask.WEBSITE_ANALYSIS: (AIProvider.ANTHROPIC, settings.anthropic_model, 0.5),
    AITask.COMPETITOR_RESEARCH: (AIProvider.OPENAI, settings.openai_model, 0.6),
    AITask.AUDIENCE_RESEARCH: (AIProvider.ANTHROPIC, settings.anthropic_model, 0.6),
    AITask.SEO_STRATEGY: (AIProvider.OPENAI, settings.openai_model, 0.5),
    AITask.CONTENT_PLANNING: (AIProvider.ANTHROPIC, settings.anthropic_model, 0.7),
    AITask.CAPTION_WRITING: (AIProvider.OPENAI, settings.openai_model_mini, 0.8),
    AITask.SCRIPT_WRITING: (AIProvider.ANTHROPIC, settings.anthropic_model, 0.7),
}


class AICompletionResult(BaseModel):
    content: str
    provider: AIProvider
    model: str
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0


class AIStructuredResult(BaseModel, Generic[T]):
    data: Any  # typed at runtime via generic
    provider: AIProvider
    model: str
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0


class AIHealthStatus(BaseModel):
    openai_configured: bool
    anthropic_configured: bool
    gemini_configured: bool = False
    ready: bool
    models: dict[str, str] = Field(default_factory=dict)
