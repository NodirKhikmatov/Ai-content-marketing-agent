from typing import Any
from uuid import UUID

from database.repositories.base import BaseRepository, maybe_single_data


class ProjectRepository(BaseRepository):
    async def create(self, user_id: str, name: str, description: str | None = None) -> dict[str, Any]:
        result = (
            self.table("projects")
            .insert({"user_id": user_id, "name": name, "description": description})
            .execute()
        )
        return result.data[0]

    async def list_by_user(
        self, user_id: str, page: int = 1, limit: int = 20, status: str | None = None
    ) -> tuple[list[dict[str, Any]], int]:
        query = self.table("projects").select("*", count="exact").eq("user_id", user_id)
        if status:
            query = query.eq("status", status)
        offset = (page - 1) * limit
        result = query.order("created_at", desc=True).range(offset, offset + limit - 1).execute()
        return result.data or [], result.count or 0

    async def get_by_id(self, project_id: UUID, user_id: str) -> dict[str, Any] | None:
        result = (
            self.table("projects")
            .select("*")
            .eq("id", str(project_id))
            .eq("user_id", user_id)
            .maybe_single()
            .execute()
        )
        return maybe_single_data(result)

    async def update(
        self, project_id: UUID, user_id: str, data: dict[str, Any]
    ) -> dict[str, Any] | None:
        result = (
            self.table("projects")
            .update(data)
            .eq("id", str(project_id))
            .eq("user_id", user_id)
            .execute()
        )
        return result.data[0] if result.data else None

    async def delete(self, project_id: UUID, user_id: str) -> bool:
        result = (
            self.table("projects")
            .delete()
            .eq("id", str(project_id))
            .eq("user_id", user_id)
            .execute()
        )
        return len(result.data or []) > 0

    async def get_stats(self, project_id: UUID) -> dict[str, int]:
        pid = str(project_id)
        content = (
            self.table("content_items")
            .select("id, status", count="exact")
            .eq("project_id", pid)
            .execute()
        )
        keywords = (
            self.table("seo_keywords").select("id", count="exact").eq("project_id", pid).execute()
        )
        competitors = (
            self.table("competitors").select("id", count="exact").eq("project_id", pid).execute()
        )
        approved = sum(1 for item in (content.data or []) if item.get("status") == "approved")
        return {
            "content_items": content.count or 0,
            "approved_items": approved,
            "keywords": keywords.count or 0,
            "competitors": competitors.count or 0,
        }
