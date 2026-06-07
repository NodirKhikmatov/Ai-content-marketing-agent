from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status

from app.dependencies import get_current_user_id
from database.models import JobResponse
from database.repositories.job_repository import JobRepository
from database.repositories.project_repository import ProjectRepository

router = APIRouter(prefix="/jobs", tags=["jobs"])


@router.get("/{job_id}", response_model=JobResponse)
async def get_job_status(job_id: UUID, user_id: str = Depends(get_current_user_id)):
    job_repo = JobRepository()
    job = await job_repo.get_by_id(job_id)
    if not job:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job not found")

    project_repo = ProjectRepository()
    project = await project_repo.get_by_id(UUID(job["project_id"]), user_id)
    if not project:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")

    return job
