from typing import Any
from uuid import UUID

from app.exceptions import ValidationError
from database.repositories.base import BaseRepository, maybe_single_data
from services.validation.url_validator import validate_website_url


class WebsiteRepository(BaseRepository):
    async def create(self, project_id: UUID, url: str) -> dict[str, Any]:
        normalized = validate_website_url(url)

        existing = (
            self.table("websites")
            .select("id")
            .eq("project_id", str(project_id))
            .eq("url", normalized)
            .maybe_single()
            .execute()
        )
        if maybe_single_data(existing):
            raise ValidationError("This URL is already added to the project")

        result = (
            self.table("websites")
            .insert(
                {
                    "project_id": str(project_id),
                    "url": normalized,
                    "status": "pending",
                }
            )
            .execute()
        )
        return result.data[0]

    async def list_by_project(self, project_id: UUID) -> list[dict[str, Any]]:
        result = (
            self.table("websites")
            .select("*")
            .eq("project_id", str(project_id))
            .order("created_at", desc=True)
            .execute()
        )
        return result.data or []

    async def get_by_id(self, project_id: UUID, website_id: UUID) -> dict[str, Any] | None:
        result = (
            self.table("websites")
            .select("*")
            .eq("id", str(website_id))
            .eq("project_id", str(project_id))
            .maybe_single()
            .execute()
        )
        return maybe_single_data(result)

    async def get_primary(self, project_id: UUID) -> dict[str, Any] | None:
        """Return the most recent website for a project."""
        result = (
            self.table("websites")
            .select("*")
            .eq("project_id", str(project_id))
            .order("created_at", desc=True)
            .limit(1)
            .execute()
        )
        if result.data:
            return result.data[0]
        return None
