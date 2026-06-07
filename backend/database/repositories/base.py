from typing import Any

from database.supabase import get_supabase


def maybe_single_data(result: Any) -> dict[str, Any] | None:
    """Supabase maybe_single() returns None when no row exists."""
    if result is None:
        return None
    return result.data


class BaseRepository:
    """Base class for Supabase-backed repositories."""

    def __init__(self) -> None:
        self._db = get_supabase()

    @property
    def client(self) -> Any:
        return self._db.client

    def table(self, name: str) -> Any:
        return self._db.table(name)
