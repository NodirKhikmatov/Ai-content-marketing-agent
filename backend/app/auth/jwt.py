"""Supabase JWT validation (JWKS ES256 + legacy HS256)."""

import time

import httpx
from jose import jwk, jwt
from jose.exceptions import JWTError as JoseJWTError

from app.auth.models import AuthenticatedUser
from app.config import settings
from app.exceptions import AuthenticationError

_jwks_cache: dict[str, object] = {"keys": None, "fetched_at": 0.0}
JWKS_TTL_SECONDS = 3600


class SupabaseJWTValidator:
    """Validates access tokens issued by Supabase Auth."""

    LEGACY_ALGORITHM = "HS256"
    AUDIENCE = "authenticated"

    def decode(self, token: str) -> AuthenticatedUser:
        if not settings.can_validate_jwt:
            raise AuthenticationError("JWT validation not configured on server")

        try:
            payload = self._decode_payload(token)
        except AuthenticationError:
            raise
        except JoseJWTError as exc:
            raise AuthenticationError("Invalid or expired token") from exc

        return self._payload_to_user(payload)

    def _decode_payload(self, token: str) -> dict:
        header = jwt.get_unverified_header(token)
        algorithm = header.get("alg", "")

        if algorithm in ("ES256", "RS256") and settings.supabase_url:
            return self._decode_with_jwks(token, header)

        if settings.supabase_jwt_secret:
            return jwt.decode(
                token,
                settings.supabase_jwt_secret,
                algorithms=[self.LEGACY_ALGORITHM],
                audience=self.AUDIENCE,
                options={
                    "verify_aud": True,
                    "verify_exp": True,
                    "verify_iat": True,
                },
            )

        raise AuthenticationError("JWT validation not configured on server")

    def _decode_with_jwks(self, token: str, header: dict) -> dict:
        kid = header.get("kid")
        if not kid:
            raise AuthenticationError("Token missing key ID (kid)")

        keys = self._get_jwks()
        key_data = next((k for k in keys if k.get("kid") == kid), None)
        if not key_data:
            raise AuthenticationError("Unknown signing key")

        public_key = jwk.construct(key_data)
        return jwt.decode(
            token,
            public_key,
            algorithms=[header.get("alg", "ES256")],
            audience=self.AUDIENCE,
            options={
                "verify_aud": True,
                "verify_exp": True,
                "verify_iat": True,
            },
        )

    def _get_jwks(self) -> list[dict]:
        now = time.time()
        cached_keys = _jwks_cache.get("keys")
        fetched_at = float(_jwks_cache.get("fetched_at") or 0)
        if cached_keys and now - fetched_at < JWKS_TTL_SECONDS:
            return cached_keys  # type: ignore[return-value]

        url = f"{settings.supabase_url.rstrip('/')}/auth/v1/.well-known/jwks.json"
        try:
            response = httpx.get(url, timeout=10.0)
            response.raise_for_status()
            keys = response.json().get("keys", [])
        except Exception as exc:
            raise AuthenticationError("Unable to fetch JWT signing keys") from exc

        _jwks_cache["keys"] = keys
        _jwks_cache["fetched_at"] = now
        return keys

    def _payload_to_user(self, payload: dict) -> AuthenticatedUser:
        user_id = payload.get("sub")
        if not user_id:
            raise AuthenticationError("Token missing subject (sub)")

        role = payload.get("role", "")
        if role != "authenticated":
            raise AuthenticationError("Token role must be 'authenticated'")

        if settings.supabase_url:
            expected_iss = settings.supabase_jwt_issuer
            if payload.get("iss") != expected_iss:
                raise AuthenticationError("Token issuer mismatch")

        return AuthenticatedUser(
            id=str(user_id),
            email=payload.get("email"),
            role=str(role),
        )


jwt_validator = SupabaseJWTValidator()
