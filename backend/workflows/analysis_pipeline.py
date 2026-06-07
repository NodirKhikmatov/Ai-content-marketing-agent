import asyncio
import logging
from datetime import date, datetime, timedelta, timezone
from typing import Any
from uuid import UUID

from agents.audience_research import AudienceResearchAgent
from agents.competitor_research import CompetitorResearchAgent
from agents.content_planner import ContentPlannerAgent
from agents.seo_strategy import SEOStrategyAgent
from agents.website_analyzer import WebsiteAnalyzerAgent
from database.repositories.job_repository import JobRepository
from database.supabase import get_supabase
from services.ai.errors import format_ai_error
from services.ai.schemas import (
    _coerce_to_int,
    _normalize_channel,
    _normalize_format,
    _normalize_keyword_intent,
    _normalize_keyword_priority,
)
from services.usage.service import get_usage_service
from workflows.analysis_defaults import merge_analysis_options
from workflows.asset_generation import AssetGenerationWorkflow
from workflows.pipeline_steps import NEXT_STEP, STEP_PROGRESS

logger = logging.getLogger(__name__)


class AnalysisPipeline:
    """Orchestrates the full website analysis → strategy → content pipeline."""

    def __init__(self):
        self.job_repo = JobRepository()
        self.client = get_supabase().client
        self.website_analyzer = WebsiteAnalyzerAgent()
        self.competitor_agent = CompetitorResearchAgent()
        self.audience_agent = AudienceResearchAgent()
        self.seo_agent = SEOStrategyAgent()
        self.content_planner = ContentPlannerAgent()
        self.asset_workflow = AssetGenerationWorkflow()

    async def run(
        self,
        job_id: UUID,
        project_id: UUID,
        website_id: UUID,
        url: str,
        options: dict[str, Any],
        user_id: str | None = None,
    ) -> None:
        options = merge_analysis_options(options)
        context: dict[str, Any] = {
            "url": url,
            "competitor_count": options.get("competitor_count", 4),
            "calendar_days": options.get("calendar_days", 7),
            "keyword_count": options.get("keyword_count", 10),
        }
        steps_completed: list[str] = []

        try:
            await self._set_website_status(website_id, "crawling")
            await self.job_repo.update_progress(
                job_id, STEP_PROGRESS["website_analysis"], "website_analysis", status="processing"
            )
            await self._update_project_status(project_id, "analyzing")

            # Step 1: Website Analysis
            result = await self.website_analyzer.run(context)
            if not result.success:
                raise RuntimeError(f"Website analysis failed: {result.error}")
            context["website_analysis"] = result.data["website_analysis"]
            await self._save_website_analysis(website_id, result.data)
            steps_completed.append("website_analysis")
            await self._advance(job_id, "website_analysis", steps_completed)

            # Step 2: Competitor Research
            result = await self.competitor_agent.run(context)
            if not result.success:
                raise RuntimeError(f"Competitor research failed: {result.error}")
            context.update(result.data)
            await self._save_competitors(project_id, result.data.get("competitors", []))
            steps_completed.append("competitor_research")
            await self._advance(job_id, "competitor_research", steps_completed)

            # Step 3: Audience Research
            result = await self.audience_agent.run(context)
            if not result.success:
                raise RuntimeError(f"Audience research failed: {result.error}")
            context.update(result.data)
            steps_completed.append("audience_research")
            await self._advance(job_id, "audience_research", steps_completed)

            # Step 4: SEO Strategy
            result = await self.seo_agent.run(context)
            if not result.success:
                raise RuntimeError(f"SEO strategy failed: {result.error}")
            context.update(result.data)
            await self._save_keywords(project_id, result.data.get("keywords", []))
            steps_completed.append("seo_strategy")
            await self._advance(job_id, "seo_strategy", steps_completed)

            # Step 5: Content Planning
            result = await self.content_planner.run(context)
            if not result.success:
                raise RuntimeError(f"Content planning failed: {result.error}")
            plan_id, content_items = await self._save_content_plan(project_id, result.data, options)
            context["content_items"] = content_items
            steps_completed.append("content_planning")
            await self._advance(job_id, "content_planning", steps_completed)

            # Step 6: Asset Generation (optional)
            if options.get("generate_assets", True):
                brand_tone = context.get("website_analysis", {}).get("brand_tone", "")
                sample_limit = int(options.get("sample_asset_count") or 0)
                await self.asset_workflow.generate_for_items(
                    project_id,
                    content_items,
                    brand_tone,
                    sample_limit=sample_limit,
                )
            steps_completed.append("asset_generation")

            await self.job_repo.mark_completed(job_id)
            await self._update_project_status(project_id, "active")

        except Exception as e:
            logger.exception("Pipeline failed for job %s", job_id)
            await self.job_repo.mark_failed(job_id, format_ai_error(e))
            if user_id:
                try:
                    get_usage_service().refund_analysis(user_id)
                except Exception:
                    logger.exception("Failed to refund analysis credit for user %s", user_id)
            await self._set_website_status(website_id, "failed")
            await self._update_project_status(project_id, "draft")

    async def _advance(self, job_id: UUID, completed_step: str, steps_completed: list[str]) -> None:
        next_step = NEXT_STEP.get(completed_step)
        progress = STEP_PROGRESS.get(completed_step, 0)
        await self.job_repo.update_progress(job_id, progress, next_step, steps_completed)
        # Brief pause between steps lets Gemini's per-minute bucket partially recover
        await asyncio.sleep(5)

    async def _set_website_status(self, website_id: UUID, status: str) -> None:
        self.client.table("websites").update({"status": status}).eq("id", str(website_id)).execute()

    async def _update_project_status(self, project_id: UUID, status: str) -> None:
        self.client.table("projects").update({"status": status}).eq("id", str(project_id)).execute()

    async def _save_website_analysis(self, website_id: UUID, data: dict[str, Any]) -> None:
        analysis = data["website_analysis"]
        self.client.table("websites").update(
            {
                "status": "analyzed",
                "business_type": analysis.get("business_type"),
                "products_services": analysis.get("products_services", []),
                "target_audience": analysis.get("target_audience"),
                "unique_value_proposition": analysis.get("unique_value_proposition"),
                "brand_tone": analysis.get("brand_tone"),
                "raw_crawl_data": data.get("crawl_data"),
                "analysis_result": analysis,
                "analyzed_at": datetime.now(timezone.utc).isoformat(),
            }
        ).eq("id", str(website_id)).execute()

    async def _save_competitors(self, project_id: UUID, competitors: list[dict[str, Any]]) -> None:
        rows = [
            {
                "project_id": str(project_id),
                "name": c["name"],
                "url": c["url"],
                "strengths": c.get("strengths", []),
                "weaknesses": c.get("weaknesses", []),
                "content_gaps": c.get("content_gaps", []),
                "positioning_summary": c.get("positioning_summary"),
                "social_presence": c.get("social_presence", {}),
            }
            for c in competitors
        ]
        if rows:
            self.client.table("competitors").insert(rows).execute()

    async def _save_keywords(self, project_id: UUID, keywords: list[dict[str, Any]]) -> None:
        seen: set[str] = set()
        rows: list[dict[str, Any]] = []
        for k in keywords:
            keyword = str(k.get("keyword", "")).strip()
            if not keyword:
                continue
            key = keyword.casefold()
            if key in seen:
                continue
            seen.add(key)
            rows.append(
                {
                    "project_id": str(project_id),
                    "keyword": keyword,
                    "search_volume": k.get("search_volume"),
                    "difficulty": max(0, min(100, _coerce_to_int(k.get("difficulty")))),
                    "intent": _normalize_keyword_intent(k.get("intent")),
                    "cluster": k.get("cluster"),
                    "priority": _normalize_keyword_priority(k.get("priority", "medium")),
                    "content_suggestions": k.get("content_suggestions", []),
                }
            )
        if rows:
            self.client.table("seo_keywords").upsert(
                rows, on_conflict="project_id,keyword"
            ).execute()

    async def _save_content_plan(
        self, project_id: UUID, plan_data: dict[str, Any], options: dict[str, Any]
    ) -> tuple[str, list[dict[str, Any]]]:
        days = options.get("calendar_days", 30)
        start = date.today() + timedelta(days=1)

        plan_result = (
            self.client.table("content_plans")
            .insert(
                {
                    "project_id": str(project_id),
                    "name": plan_data.get("plan_name", "30-Day Content Plan"),
                    "start_date": start.isoformat(),
                    "end_date": (start + timedelta(days=days - 1)).isoformat(),
                    "status": "active",
                    "pillars": plan_data.get("pillars", []),
                    "channel_mix": plan_data.get("channel_mix", {}),
                }
            )
            .execute()
        )
        plan_id = plan_result.data[0]["id"]

        items = []
        for item in plan_data.get("content_items", []):
            day_offset = item.get("day", 1) - 1
            items.append(
                {
                    "project_id": str(project_id),
                    "content_plan_id": plan_id,
                    "title": item["title"],
                    "description": item.get("description"),
                    "channel": _normalize_channel(item["channel"]),
                    "format": _normalize_format(item["format"]),
                    "scheduled_date": (start + timedelta(days=day_offset)).isoformat(),
                    "status": "draft",
                    "keyword_targets": item.get("keyword_targets", []),
                    "sort_order": item.get("day", 0),
                }
            )

        if items:
            result = self.client.table("content_items").insert(items).execute()
            return plan_id, result.data

        return plan_id, []
