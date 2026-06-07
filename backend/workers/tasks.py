"""Analysis task entrypoint shared by the in-process fallback and the arq worker.

Accepts plain strings (JSON-serializable) so the same callable works whether it is
invoked directly via FastAPI BackgroundTasks or enqueued onto Redis via arq.
"""

import logging
from typing import Any
from uuid import UUID

from workflows.analysis_pipeline import AnalysisPipeline

logger = logging.getLogger(__name__)


async def run_analysis(
    job_id: str,
    project_id: str,
    website_id: str,
    url: str,
    options: dict[str, Any],
    user_id: str | None = None,
) -> None:
    """Run the full analysis pipeline for a single job."""
    logger.info("Running analysis pipeline for job %s", job_id)
    pipeline = AnalysisPipeline()
    await pipeline.run(
        UUID(job_id),
        UUID(project_id),
        UUID(website_id),
        url,
        options or {},
        user_id=user_id,
    )


async def run_analysis_task(
    ctx: dict[str, Any],
    job_id: str,
    project_id: str,
    website_id: str,
    url: str,
    options: dict[str, Any],
    user_id: str | None = None,
) -> None:
    """arq task wrapper. ``ctx`` is supplied by the arq worker runtime."""
    await run_analysis(job_id, project_id, website_id, url, options, user_id)
