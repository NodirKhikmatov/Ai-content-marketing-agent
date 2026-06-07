from contextlib import asynccontextmanager
import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.router import api_router
from app.config import settings
from app.exceptions import register_exception_handlers
from app.middleware import RequestLoggingMiddleware

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting %s v%s", settings.app_name, settings.app_version)

    if not settings.is_supabase_configured:
        logger.warning("Supabase credentials missing — database calls will fail")
    elif settings.supabase_api_key.startswith("sb_publishable_"):
        logger.warning(
            "SUPABASE key looks like a publishable key (sb_publishable_). "
            "Backend requires SUPABASE_SECRET_KEY (sb_secret_...) or legacy service_role."
        )
    if not settings.is_auth_configured:
        logger.warning("SUPABASE_JWT_SECRET missing — auth will fail")

    if settings.is_supabase_configured:
        try:
            from database.supabase import get_supabase
            if get_supabase().health_check():
                logger.info("Supabase connection OK")
            else:
                logger.warning("Supabase health check failed")
        except Exception as exc:
            logger.warning("Supabase startup check failed: %s", exc)

    yield
    logger.info("Shutting down API")


def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        lifespan=lifespan,
        docs_url="/docs",
        redoc_url="/redoc",
    )

    register_exception_handlers(app)

    app.add_middleware(RequestLoggingMiddleware)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(api_router, prefix=settings.api_prefix)

    @app.get("/health")
    async def root_health():
        return {"status": "ok", "version": settings.app_version}

    return app


app = create_app()
