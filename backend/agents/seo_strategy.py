from typing import Any

from agents.base import AgentResult, BaseAgent
from services.ai.models import AITask
from services.ai.schemas import SEOStrategySchema
from services.ai.service import get_ai_service


class SEOStrategyAgent(BaseAgent):
    name = "seo_strategy"
    description = "Generates comprehensive SEO keyword strategy"

    async def run(self, context: dict[str, Any]) -> AgentResult:
        if not context.get("website_analysis"):
            return AgentResult(success=False, error="Website analysis required")

        try:
            ai = get_ai_service()
            keyword_count = int(context.get("keyword_count", 10))
            user_prompt = f"""Create an SEO keyword strategy with exactly {keyword_count} keywords:

{self._build_prompt_context(context, ["website_analysis", "competitors", "personas", "audience_summary"])}

Return JSON with:
- "keywords": array of {keyword_count} objects, each with keyword (string), search_volume (number),
  difficulty (number 0-100), intent (one of: informational, commercial, transactional, navigational),
  cluster (string), priority (one of: low, medium, high),
  content_suggestions (array of strings)
- "clusters": array of cluster name strings
- "strategy_summary": string (not an object)

Use valid JSON only. No trailing commas. Keep content_suggestions to 1-2 short strings per keyword."""

            strategy, result = await ai.complete_structured(
                AITask.SEO_STRATEGY, user_prompt, SEOStrategySchema
            )

            return AgentResult(
                success=True,
                data=strategy.model_dump(),
                tokens_used=result.total_tokens,
            )

        except Exception as e:
            return AgentResult(success=False, error=self._agent_error(e))
