"""Application-wide exceptions and FastAPI handlers."""

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse


class AppError(Exception):
    """Base application error."""

    def __init__(self, message: str, code: str = "APP_ERROR", status_code: int = 500):
        self.message = message
        self.code = code
        self.status_code = status_code
        super().__init__(message)


class AuthenticationError(AppError):
    def __init__(self, message: str = "Unauthorized"):
        super().__init__(message=message, code="UNAUTHORIZED", status_code=401)


class AuthorizationError(AppError):
    def __init__(self, message: str = "Forbidden"):
        super().__init__(message=message, code="FORBIDDEN", status_code=403)


class NotFoundError(AppError):
    def __init__(self, message: str = "Resource not found"):
        super().__init__(message=message, code="NOT_FOUND", status_code=404)


class ValidationError(AppError):
    def __init__(self, message: str = "Validation error"):
        super().__init__(message=message, code="VALIDATION_ERROR", status_code=400)


class QuotaExceededError(AppError):
    def __init__(self, message: str = "Usage limit exceeded"):
        super().__init__(message=message, code="QUOTA_EXCEEDED", status_code=403)


class ServiceUnavailableError(AppError):
    def __init__(self, message: str = "Service temporarily unavailable"):
        super().__init__(message=message, code="SERVICE_UNAVAILABLE", status_code=503)


def _error_body(code: str, message: str, details: list | None = None) -> dict:
    body: dict = {"error": {"code": code, "message": message}}
    if details:
        body["error"]["details"] = details
    return body


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(AppError)
    async def app_error_handler(_request: Request, exc: AppError) -> JSONResponse:
        return JSONResponse(
            status_code=exc.status_code,
            content=_error_body(exc.code, exc.message),
        )

    @app.exception_handler(RequestValidationError)
    async def validation_error_handler(
        _request: Request, exc: RequestValidationError
    ) -> JSONResponse:
        details = [
            {"field": ".".join(str(loc) for loc in err["loc"]), "message": err["msg"]}
            for err in exc.errors()
        ]
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content=_error_body("VALIDATION_ERROR", "Request validation failed", details),
        )

    try:
        from postgrest.exceptions import APIError as PostgrestAPIError

        @app.exception_handler(PostgrestAPIError)
        async def postgrest_error_handler(
            _request: Request, exc: PostgrestAPIError
        ) -> JSONResponse:
            import logging

            logging.getLogger(__name__).error("Supabase API error: %s", exc)
            raw = str(exc)
            if "Invalid API key" in raw:
                return JSONResponse(
                    status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                    content=_error_body(
                        "SUPABASE_CONFIG_ERROR",
                        "Invalid Supabase service key. Set SUPABASE_SECRET_KEY (sb_secret_...) "
                        "in backend/.env from Supabase Dashboard → Project Settings → API.",
                    ),
                )
            if "row-level security" in raw.lower() or "'code': '42501'" in raw:
                return JSONResponse(
                    status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                    content=_error_body(
                        "SUPABASE_CONFIG_ERROR",
                        "Database blocked the request (RLS). The backend must use "
                        "SUPABASE_SECRET_KEY (sb_secret_...), not the publishable key (sb_publishable_...). "
                        "Copy the Secret key from Supabase Dashboard → Project Settings → API.",
                    ),
                )
            if "profiles" in raw and ("23503" in raw or "foreign key" in raw.lower()):
                return JSONResponse(
                    status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                    content=_error_body(
                        "PROFILE_MISSING",
                        "User profile not found. Sign out and sign in again, or re-run the database migration "
                        "that creates profiles on signup (001_initial_schema.sql).",
                    ),
                )
            return JSONResponse(
                status_code=status.HTTP_502_BAD_GATEWAY,
                content=_error_body("DATABASE_ERROR", "Database request failed"),
            )
    except ImportError:
        pass

    @app.exception_handler(Exception)
    async def unhandled_error_handler(request: Request, exc: Exception) -> JSONResponse:
        from app.config import settings
        import logging

        logging.getLogger(__name__).exception("Unhandled error on %s", request.url.path)
        message = str(exc) if settings.debug else "Internal server error"
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=_error_body("INTERNAL_ERROR", message),
        )
