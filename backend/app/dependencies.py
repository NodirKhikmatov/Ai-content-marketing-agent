"""FastAPI dependency injection for authentication."""

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.auth.jwt import jwt_validator
from app.auth.models import AuthenticatedUser
from app.exceptions import AuthenticationError
from database.repositories.user_repository import UserRepository

security = HTTPBearer(auto_error=False)


async def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(security),
) -> AuthenticatedUser:
    if not credentials:
        raise AuthenticationError("Missing authentication token")
    return jwt_validator.decode(credentials.credentials)


async def get_current_user_id(user: AuthenticatedUser = Depends(get_current_user)) -> str:
    repo = UserRepository()
    await repo.ensure_profile(user.id, email=user.email)
    return user.id
