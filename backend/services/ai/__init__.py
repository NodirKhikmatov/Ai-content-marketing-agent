"""AI service package."""

from services.ai.models import AITask
from services.ai.service import AIService, get_ai_service

# Backward-compatible re-exports
from services.ai.anthropic_client import AnthropicClient
from services.ai.openai_client import OpenAIClient

__all__ = [
    "AIService",
    "AITask",
    "AnthropicClient",
    "OpenAIClient",
    "get_ai_service",
]
