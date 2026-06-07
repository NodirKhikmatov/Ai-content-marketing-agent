from typing import Any

from agents.base import AgentResult, BaseAgent
from services.ai.models import AITask
from services.ai.schemas import ContentPlanSchema
from services.ai.service import get_ai_service


class ContentPlannerAgent(BaseAgent):
    name = "content_planner"
    description = "Creates a 30-day multi-channel content calendar"

    async def run(self, context: dict[str, Any]) -> AgentResult:
        calendar_days = context.get("calendar_days", 30)

        try:
            ai = get_ai_service()
            user_prompt = f"""Create a {calendar_days}-day content calendar.

{self._build_prompt_context(context, [
    "website_analysis", "competitors", "personas",
    "keywords", "clusters", "strategy_summary", "content_preferences"
])}

Include exactly {calendar_days} content items in content_items array, one per day.
Mix channels: LinkedIn, blog, TikTok/Reels, YouTube, Instagram."""

            plan, result = await ai.complete_structured(
                AITask.CONTENT_PLANNING,
                user_prompt,
                ContentPlanSchema,
                max_tokens=8192,
            )

            return AgentResult(
                success=True,
                data=plan.model_dump(),
                tokens_used=result.total_tokens,
            )

        except Exception as e:
            return AgentResult(success=False, error=self._agent_error(e))
