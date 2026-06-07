from fastapi import APIRouter, Depends

from app.dependencies import get_current_user_id
from services.ai.service import get_ai_service

router = APIRouter(prefix="/ai", tags=["ai"])


@router.get("/health")
async def ai_health(_user_id: str = Depends(get_current_user_id)):
    """Check AI provider configuration and model routing."""
    service = get_ai_service()
    return service.health()


@router.get("/models")
async def list_models(_user_id: str = Depends(get_current_user_id)):
    """Return model routing table for all agent tasks."""
    service = get_ai_service()
    health = service.health()
    return {"ready": health.ready, "models": health.models}
