"""JWT authentication tests."""

from datetime import datetime, timedelta, timezone

import pytest
from jose import jwt

from app.auth.jwt import SupabaseJWTValidator
from app.config import settings
from app.exceptions import AuthenticationError


def _make_token(
    *,
    sub: str = "user-123",
    role: str = "authenticated",
    email: str = "test@example.com",
    expired: bool = False,
    wrong_role: bool = False,
) -> str:
    now = datetime.now(timezone.utc)
    payload = {
        "sub": sub,
        "email": email,
        "role": "anon" if wrong_role else role,
        "aud": "authenticated",
        "iss": settings.supabase_jwt_issuer or "https://example.supabase.co/auth/v1",
        "iat": now,
        "exp": now + (timedelta(seconds=-10) if expired else timedelta(hours=1)),
    }
    secret = settings.supabase_jwt_secret or "test-secret"
    return jwt.encode(payload, secret, algorithm="HS256")


@pytest.fixture(autouse=True)
def _configure_jwt_secret(monkeypatch):
    monkeypatch.setattr(settings, "supabase_jwt_secret", "test-secret")
    monkeypatch.setattr(settings, "supabase_url", "https://example.supabase.co")


def test_valid_token_decodes():
    validator = SupabaseJWTValidator()
    token = _make_token()
    user = validator.decode(token)
    assert user.id == "user-123"
    assert user.email == "test@example.com"
    assert user.role == "authenticated"


def test_expired_token_rejected():
    validator = SupabaseJWTValidator()
    with pytest.raises(AuthenticationError, match="Invalid or expired"):
        validator.decode(_make_token(expired=True))


def test_wrong_role_rejected():
    validator = SupabaseJWTValidator()
    with pytest.raises(AuthenticationError, match="role"):
        validator.decode(_make_token(wrong_role=True))


def test_missing_sub_rejected():
    validator = SupabaseJWTValidator()
    now = datetime.now(timezone.utc)
    token = jwt.encode(
        {
            "role": "authenticated",
            "aud": "authenticated",
            "iss": "https://example.supabase.co/auth/v1",
            "exp": now + timedelta(hours=1),
        },
        "test-secret",
        algorithm="HS256",
    )
    with pytest.raises(AuthenticationError, match="subject"):
        validator.decode(token)
