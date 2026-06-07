from fastapi import APIRouter, Depends

from app.auth.models import AuthenticatedUser
from app.config import settings
from app.dependencies import get_current_user
from database.models import HealthDetailResponse
from database.supabase import get_supabase

router = APIRouter(tags=["health"])


@router.get("/health", response_model=HealthDetailResponse)
async def api_health():
    supabase_status = "not_configured"
    if settings.is_supabase_configured:
        try:
            supabase_status = "ok" if get_supabase().health_check() else "error"
        except Exception:
            supabase_status = "error"

    auth_status = "configured" if settings.can_validate_jwt else "not_configured"

    overall = "ok" if supabase_status == "ok" and auth_status == "configured" else "degraded"

    return HealthDetailResponse(
        status=overall,
        version=settings.app_version,
        supabase=supabase_status,
        auth=auth_status,
    )


@router.get("/me", response_model=dict)
async def auth_probe(user: AuthenticatedUser = Depends(get_current_user)):
    """Verify JWT auth — returns decoded user id and email."""
    return {"id": user.id, "email": user.email, "role": user.role}
