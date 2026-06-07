"""Usage limits and quota enforcement."""

from typing import Any

from app.exceptions import NotFoundError, QuotaExceededError
from database.models import UsageResponse
from database.supabase import get_supabase


class UsageService:
    """Enforces per-plan analysis and regeneration limits."""

    def __init__(self):
        self.client = get_supabase().client

    def get_usage(self, user_id: str) -> UsageResponse:
        result = self.client.rpc("get_usage_stats", {"user_uuid": user_id}).execute()
        rows = result.data or []
        if not rows:
            raise NotFoundError("Profile not found")
        row = rows[0] if isinstance(rows, list) else rows
        return UsageResponse(
            analyses_used=row["analyses_used"],
            analyses_limit=row["analyses_limit"],
            regenerations_used=row["regenerations_used"],
            regenerations_limit=row["regenerations_limit"],
            plan=row["plan"],
        )

    def consume_analysis(self, user_id: str) -> None:
        allowed = self._rpc_bool("try_consume_analysis", user_id)
        if not allowed:
            usage = self.get_usage(user_id)
            raise QuotaExceededError(
                f"Analysis limit reached ({usage.analyses_used}/{usage.analyses_limit} this month). "
                "Upgrade your plan to run more analyses."
            )

    def consume_regeneration(self, user_id: str) -> None:
        allowed = self._rpc_bool("try_consume_regeneration", user_id)
        if not allowed:
            usage = self.get_usage(user_id)
            raise QuotaExceededError(
                f"Regeneration limit reached ({usage.regenerations_used}/{usage.regenerations_limit} this month). "
                "Upgrade your plan for more regenerations."
            )

    def refund_analysis(self, user_id: str) -> None:
        try:
            self.client.rpc("refund_analysis", {"user_uuid": user_id}).execute()
        except Exception:
            row = (
                self.client.table("profiles")
                .select("analyses_used")
                .eq("id", user_id)
                .maybe_single()
                .execute()
            )
            used = (row.data or {}).get("analyses_used", 0) if row else 0
            self.client.table("profiles").update(
                {"analyses_used": max(used - 1, 0)}
            ).eq("id", user_id).execute()

    def refund_regeneration(self, user_id: str) -> None:
        try:
            self.client.rpc("refund_regeneration", {"user_uuid": user_id}).execute()
        except Exception:
            row = (
                self.client.table("profiles")
                .select("regenerations_used")
                .eq("id", user_id)
                .maybe_single()
                .execute()
            )
            used = (row.data or {}).get("regenerations_used", 0) if row else 0
            self.client.table("profiles").update(
                {"regenerations_used": max(used - 1, 0)}
            ).eq("id", user_id).execute()

    def _rpc_bool(self, fn: str, user_id: str) -> bool:
        result = self.client.rpc(fn, {"user_uuid": user_id}).execute()
        data: Any = result.data
        if data is None:
            return False
        if isinstance(data, bool):
            return data
        if isinstance(data, list) and data:
            return bool(data[0])
        return bool(data)


def get_usage_service() -> UsageService:
    return UsageService()
