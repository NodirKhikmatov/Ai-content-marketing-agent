"""Typed Supabase client for backend (service role — bypasses RLS)."""

from functools import lru_cache
from typing import Any

from supabase import Client, create_client

from app.config import settings


class SupabaseService:
    """Singleton wrapper around the Supabase service-role client."""

    def __init__(self) -> None:
        if not settings.supabase_url or not settings.supabase_api_key:
            raise RuntimeError(
                "Supabase not configured. Set SUPABASE_URL and SUPABASE_SECRET_KEY "
                "(or SUPABASE_SERVICE_ROLE_KEY) in backend/.env"
            )
        self._client: Client = create_client(
            settings.supabase_url,
            settings.supabase_api_key,
        )

    @property
    def client(self) -> Client:
        return self._client

    def table(self, name: str) -> Any:
        return self._client.table(name)

    def increment_analyses_used(self, user_id: str) -> None:
        self._client.rpc("increment_analyses_used", {"user_uuid": user_id}).execute()

    def health_check(self) -> bool:
        try:
            self._client.table("profiles").select("id").limit(1).execute()
            return True
        except Exception:
            return False


@lru_cache
def get_supabase() -> SupabaseService:
    return SupabaseService()
