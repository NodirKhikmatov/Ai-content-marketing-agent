"""Authenticated user context extracted from Supabase JWT."""

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class AuthenticatedUser:
    id: str
    email: str | None
    role: str

    @property
    def is_authenticated(self) -> bool:
        return self.role == "authenticated"
