from uuid import UUID

from fastapi import APIRouter, BackgroundTasks, Depends, status

from app.config import settings
from app.dependencies import get_current_user_id
from app.exceptions import NotFoundError, ValidationError
from database.models import AnalyzeRequest, JobResponse
from database.repositories.job_repository import JobRepository
from database.repositories.project_repository import ProjectRepository
from database.repositories.website_repository import WebsiteRepository
from services.usage.service import get_usage_service
from workers.dispatch import dispatch_analysis
from workflows.pipeline_steps import PIPELINE_STEPS, STEP_LABELS

router = APIRouter(prefix="/projects/{project_id}/analysis", tags=["analysis"])


async def _verify_project(project_id: UUID, user_id: str) -> None:
    repo = ProjectRepository()
    if not await repo.get_by_id(project_id, user_id):
        raise NotFoundError("Project not found")


@router.get("/steps")
async def get_pipeline_steps(_project_id: UUID, _user_id: str = Depends(get_current_user_id)):
    return {"steps": PIPELINE_STEPS, "labels": STEP_LABELS}


@router.get("/active", response_model=JobResponse)
async def get_active_job(project_id: UUID, user_id: str = Depends(get_current_user_id)):
    await _verify_project(project_id, user_id)
    job_repo = JobRepository()
    job = await job_repo.get_active_for_project(project_id)
    if not job:
        raise NotFoundError("No active analysis job")
    return job


@router.post("", response_model=JobResponse, status_code=status.HTTP_202_ACCEPTED)
async def start_analysis(
    project_id: UUID,
    body: AnalyzeRequest,
    background_tasks: BackgroundTasks,
    user_id: str = Depends(get_current_user_id),
):
    await _verify_project(project_id, user_id)

    if not settings.is_ai_configured:
        raise ValidationError(
            "AI services not configured. Set GEMINI_API_KEY, OPENAI_API_KEY, or ANTHROPIC_API_KEY."
        )

    job_repo = JobRepository()
    active = await job_repo.get_active_for_project(project_id)
    if active:
        raise ValidationError("An analysis is already running for this project")

    website_repo = WebsiteRepository()
    website = await website_repo.get_by_id(project_id, body.website_id)
    if not website:
        raise NotFoundError("Website not found")

    if website["status"] not in ("pending", "failed"):
        raise ValidationError("Website has already been analyzed")

    usage_service = get_usage_service()
    usage_service.consume_analysis(user_id)

    job = await job_repo.create(project_id, body.website_id, body.options)

    await dispatch_analysis(
        background_tasks,
        UUID(job["id"]),
        project_id,
        body.website_id,
        website["url"],
        body.options,
        user_id,
    )

    return job
