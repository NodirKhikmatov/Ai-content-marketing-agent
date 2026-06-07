from typing import Any

from agents.base import AgentResult, BaseAgent
from services.ai.models import AITask
from services.ai.schemas import AudienceResearchSchema
from services.ai.service import get_ai_service


class AudienceResearchAgent(BaseAgent):
    name = "audience_research"
    description = "Builds detailed audience personas and content preferences"

    async def run(self, context: dict[str, Any]) -> AgentResult:
        if not context.get("website_analysis"):
            return AgentResult(success=False, error="Website analysis required")

        try:
            ai = get_ai_service()
            user_prompt = f"""Create audience research based on:

{self._build_prompt_context(context, ["website_analysis", "competitors", "market_insights"])}

Return JSON with:
- "personas": array of 3 objects, each with name (string), role (string), demographics (string),
  pain_points (array of strings), goals (array of strings), content_preferences (array of strings),
  platforms (array of strings)
- "audience_summary": string (not an object)
- "content_preferences": object (optional)

Use short string fields and JSON arrays — not nested objects for demographics or summary."""

            research, result = await ai.complete_structured(
                AITask.AUDIENCE_RESEARCH, user_prompt, AudienceResearchSchema
            )

            return AgentResult(
                success=True,
                data=research.model_dump(),
                tokens_used=result.total_tokens,
            )

        except Exception as e:
            return AgentResult(success=False, error=self._agent_error(e))
