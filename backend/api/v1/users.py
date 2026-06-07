from uuid import UUID

from fastapi import APIRouter, Depends, status

from app.auth.models import AuthenticatedUser
from app.dependencies import get_current_user
from app.exceptions import NotFoundError
from database.models import UsageResponse, UserProfileResponse, UserProfileUpdate
from database.repositories.user_repository import UserRepository
from services.usage.service import get_usage_service

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me", response_model=UserProfileResponse)
async def get_me(user: AuthenticatedUser = Depends(get_current_user)):
    repo = UserRepository()
    profile = await repo.ensure_profile(user.id, email=user.email)
    return profile


@router.patch("/me", response_model=UserProfileResponse)
async def update_me(
    body: UserProfileUpdate,
    user: AuthenticatedUser = Depends(get_current_user),
):
    repo = UserRepository()
    data = body.model_dump(exclude_none=True)
    if not data:
        profile = await repo.get_profile(user.id)
        if not profile:
            raise NotFoundError("Profile not found")
        return profile
    updated = await repo.update_profile(user.id, data)
    if not updated:
        raise NotFoundError("Profile not found")
    return updated


@router.get("/me/usage", response_model=UsageResponse)
async def get_usage(user: AuthenticatedUser = Depends(get_current_user)):
    usage_service = get_usage_service()
    return usage_service.get_usage(user.id)
