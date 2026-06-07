from datetime import datetime, timezone
from typing import Any
from uuid import UUID

from database.repositories.base import BaseRepository, maybe_single_data

ACTIVE_STATUSES = ("queued", "processing")


class JobRepository(BaseRepository):
    async def create(
        self, project_id: UUID, website_id: UUID | None, options: dict[str, Any]
    ) -> dict[str, Any]:
        result = (
            self.table("analysis_jobs")
            .insert(
                {
                    "project_id": str(project_id),
                    "website_id": str(website_id) if website_id else None,
                    "options": options,
                    "status": "queued",
                }
            )
            .execute()
        )
        return result.data[0]

    async def get_by_id(self, job_id: UUID) -> dict[str, Any] | None:
        result = (
            self.table("analysis_jobs")
            .select("*")
            .eq("id", str(job_id))
            .maybe_single()
            .execute()
        )
        return maybe_single_data(result)

    async def get_active_for_project(self, project_id: UUID) -> dict[str, Any] | None:
        result = (
            self.table("analysis_jobs")
            .select("*")
            .eq("project_id", str(project_id))
            .in_("status", list(ACTIVE_STATUSES))
            .order("created_at", desc=True)
            .limit(1)
            .execute()
        )
        return result.data[0] if result.data else None

    async def update_progress(
        self,
        job_id: UUID,
        progress: int,
        current_step: str | None = None,
        steps_completed: list[str] | None = None,
        status: str | None = None,
    ) -> None:
        data: dict[str, Any] = {"progress": progress}
        if current_step is not None:
            data["current_step"] = current_step
        if steps_completed is not None:
            data["steps_completed"] = steps_completed
        if status is not None:
            data["status"] = status
            if status == "processing":
                data["started_at"] = datetime.now(timezone.utc).isoformat()
        self.table("analysis_jobs").update(data).eq("id", str(job_id)).execute()

    async def mark_failed(self, job_id: UUID, error_message: str) -> None:
        self.table("analysis_jobs").update(
            {
                "status": "failed",
                "error_message": error_message,
                "completed_at": datetime.now(timezone.utc).isoformat(),
            }
        ).eq("id", str(job_id)).execute()

    async def mark_completed(self, job_id: UUID) -> None:
        self.table("analysis_jobs").update(
            {
                "status": "completed",
                "progress": 100,
                "current_step": None,
                "completed_at": datetime.now(timezone.utc).isoformat(),
            }
        ).eq("id", str(job_id)).execute()
