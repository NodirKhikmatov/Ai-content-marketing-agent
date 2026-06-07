from typing import Any

from agents.base import AgentResult, BaseAgent
from services.ai.models import AITask
from services.ai.schemas import ScriptSchema
from services.ai.service import get_ai_service


class ScriptWriterAgent(BaseAgent):
    name = "script_writer"
    description = "Writes video scripts, blog outlines, and image prompts"

    async def run(self, context: dict[str, Any]) -> AgentResult:
        content_item = context.get("content_item")
        if not content_item:
            return AgentResult(success=False, error="Content item required")

        brand_tone = context.get("brand_tone", "professional, engaging")
        channel = content_item.get("channel", "youtube")
        content_format = content_item.get("format", "video")

        try:
            ai = get_ai_service()
            user_prompt = f"""Create content assets for:

Title: {content_item.get('title')}
Channel: {channel} | Format: {content_format}
Description: {content_item.get('description', '')}
Brand tone: {brand_tone}

Return JSON with script, blog_outline, image_prompt, b_roll_suggestions."""

            script, result = await ai.complete_structured(
                AITask.SCRIPT_WRITING, user_prompt, ScriptSchema
            )

            return AgentResult(
                success=True,
                data=script.model_dump(),
                tokens_used=result.total_tokens,
            )

        except Exception as e:
            return AgentResult(success=False, error=self._agent_error(e))
