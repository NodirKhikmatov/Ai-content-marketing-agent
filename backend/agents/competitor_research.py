from typing import Any

from agents.base import AgentResult, BaseAgent
from services.ai.models import AITask
from services.ai.schemas import CompetitorResearchSchema
from services.ai.service import get_ai_service


class CompetitorResearchAgent(BaseAgent):
    name = "competitor_research"
    description = "Identifies and analyzes competitors in the market"

    async def run(self, context: dict[str, Any]) -> AgentResult:
        analysis = context.get("website_analysis")
        if not analysis:
            return AgentResult(success=False, error="Website analysis required")

        competitor_count = context.get("competitor_count", 8)

        try:
            ai = get_ai_service()
            user_prompt = f"""Based on this business profile, identify {competitor_count} competitors.

{self._build_prompt_context({"website_analysis": analysis}, ["website_analysis"])}

Return JSON with:
- "competitors": array of objects, each with name, url, strengths (array of short strings),
  weaknesses (array of short strings), content_gaps (array of short strings), positioning_summary
- "market_insights": string

Keep each strengths/weaknesses item under 15 words. Use JSON arrays, not prose paragraphs."""

            research, result = await ai.complete_structured(
                AITask.COMPETITOR_RESEARCH, user_prompt, CompetitorResearchSchema
            )

            return AgentResult(
                success=True,
                data=research.model_dump(),
                tokens_used=result.total_tokens,
            )

        except Exception as e:
            return AgentResult(success=False, error=self._agent_error(e))
