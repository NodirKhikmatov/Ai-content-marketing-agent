from typing import Any

from agents.base import AgentResult, BaseAgent
from services.ai.models import AITask
from services.ai.schemas import WebsiteAnalysisSchema
from services.ai.service import get_ai_service
from services.crawler.website_crawler import WebsiteCrawler


class WebsiteAnalyzerAgent(BaseAgent):
    name = "website_analyzer"
    description = "Analyzes a website to extract business intelligence"

    async def run(self, context: dict[str, Any]) -> AgentResult:
        url = context.get("url")
        if not url:
            return AgentResult(success=False, error="URL is required")

        try:
            crawler = WebsiteCrawler()
            crawl_data = await crawler.crawl(url)

            ai = get_ai_service()
            user_prompt = f"""Analyze this website and return JSON with these fields:
- business_type, products_services, target_audience, unique_value_proposition
- brand_tone, key_messages, industry

Website URL: {url}

Content:
{crawl_data['combined_text'][:30000]}"""

            analysis, result = await ai.complete_structured(
                AITask.WEBSITE_ANALYSIS, user_prompt, WebsiteAnalysisSchema
            )

            return AgentResult(
                success=True,
                data={
                    "website_analysis": analysis.model_dump(),
                    "crawl_data": crawl_data,
                },
                tokens_used=result.total_tokens,
            )

        except Exception as e:
            return AgentResult(success=False, error=self._agent_error(e))
