from typing import Any

from agents.base import AgentResult, BaseAgent
from services.ai.models import AITask
from services.ai.schemas import CaptionSchema
from services.ai.service import get_ai_service


class CaptionWriterAgent(BaseAgent):
    name = "caption_writer"
    description = "Writes platform-specific social media captions"

    async def run(self, context: dict[str, Any]) -> AgentResult:
        content_item = context.get("content_item")
        if not content_item:
            return AgentResult(success=False, error="Content item required")

        brand_tone = context.get("brand_tone", "professional, engaging")
        channel = content_item.get("channel", "linkedin")

        try:
            ai = get_ai_service()
            user_prompt = f"""Write a {channel} caption for this content:

Title: {content_item.get('title')}
Description: {content_item.get('description', '')}
Brand tone: {brand_tone}
Keywords: {content_item.get('keyword_targets', [])}

Return JSON with caption, hashtags, hook, cta, character_count.
Platform: linkedin=professional, tiktok=casual, instagram=visual."""

            caption, result = await ai.complete_structured(
                AITask.CAPTION_WRITING, user_prompt, CaptionSchema
            )

            return AgentResult(
                success=True,
                data=caption.model_dump(),
                tokens_used=result.total_tokens,
            )

        except Exception as e:
            return AgentResult(success=False, error=self._agent_error(e))
