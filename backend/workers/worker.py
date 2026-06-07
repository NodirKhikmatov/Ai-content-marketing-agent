"""arq worker process.

Run with:  arq workers.worker.WorkerSettings   (from the backend/ directory, venv active)

This consumes analysis jobs from Redis so they survive API restarts and can scale
across multiple processes. Requires REDIS_URL to point at a running Redis instance.
"""

import logging

from arq.connections import RedisSettings

from app.config import settings
from workers.tasks import run_analysis_task

logging.basicConfig(level=logging.INFO)


async def startup(ctx: dict) -> None:
    logging.getLogger(__name__).info("Analysis worker started")


async def shutdown(ctx: dict) -> None:
    logging.getLogger(__name__).info("Analysis worker stopped")


class WorkerSettings:
    functions = [run_analysis_task]
    redis_settings = RedisSettings.from_dsn(settings.redis_url)
    on_startup = startup
    on_shutdown = shutdown
    max_jobs = 5
    job_timeout = 900  # 15 minutes — the full pipeline can be long-running
    keep_result = 3600
