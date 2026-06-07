from typing import Any
from uuid import UUID

from database.repositories.base import BaseRepository, maybe_single_data


class UserRepository(BaseRepository):
    async def get_profile(self, user_id: str) -> dict[str, Any] | None:
        result = (
            self.table("profiles")
            .select("*")
            .eq("id", user_id)
            .maybe_single()
            .execute()
        )
        return maybe_single_data(result)

    async def update_profile(self, user_id: str, data: dict[str, Any]) -> dict[str, Any] | None:
        result = self.table("profiles").update(data).eq("id", user_id).execute()
        return result.data[0] if result.data else None

    async def ensure_profile(
        self,
        user_id: str,
        email: str | None = None,
        full_name: str | None = None,
    ) -> dict[str, Any]:
        """Create profile if missing (e.g. user signed up before DB trigger existed)."""
        existing = await self.get_profile(user_id)
        if existing:
            return existing

        result = (
            self.table("profiles")
            .upsert(
                {
                    "id": user_id,
                    "email": email or f"{user_id}@users.local",
                    "full_name": full_name,
                },
                on_conflict="id",
            )
            .execute()
        )
        if not result.data:
            # Race: another request may have created the row
            existing = await self.get_profile(user_id)
            if existing:
                return existing
            raise RuntimeError("Failed to create user profile")
        return result.data[0]
