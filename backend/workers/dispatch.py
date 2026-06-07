"""Dispatch an analysis job to the durable queue, falling back to in-process tasks.

Behavior:
- USE_WORKER_QUEUE=true  -> enqueue onto Redis (arq). The separate worker process runs it.
- USE_WORKER_QUEUE=false -> run via FastAPI BackgroundTasks (default, no Redis required).
- If queueing is requested but Redis/arq is unavailable, log and fall back to
  BackgroundTasks so an analysis is never silently dropped.
"""

import logging
from typing import Any
from uuid import UUID

from fastapi import BackgroundTasks

from app.config import settings
from workers.tasks import run_analysis

logger = logging.getLogger(__name__)


async def dispatch_analysis(
    background_tasks: BackgroundTasks,
    job_id: UUID,
    project_id: UUID,
    website_id: UUID,
    url: str,
    options: dict[str, Any],
    user_id: str,
) -> str:
    """Schedule an analysis run. Returns "queue" or "background" (the path taken)."""
    args = (str(job_id), str(project_id), str(website_id), url, options, user_id)

    if settings.use_worker_queue:
        try:
            from arq import create_pool
            from arq.connections import RedisSettings

            pool = await create_pool(RedisSettings.from_dsn(settings.redis_url))
            await pool.enqueue_job("run_analysis_task", *args)
            logger.info("Enqueued analysis job %s on the worker queue", job_id)
            return "queue"
        except Exception:
            logger.exception(
                "Failed to enqueue job %s on Redis; falling back to BackgroundTasks", job_id
            )

    background_tasks.add_task(run_analysis, *args)
    return "background"
