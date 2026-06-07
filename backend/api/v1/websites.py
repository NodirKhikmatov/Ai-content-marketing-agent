from uuid import UUID

from fastapi import APIRouter, Depends, status

from app.dependencies import get_current_user_id
from app.exceptions import NotFoundError
from database.models import WebsiteCreate, WebsiteResponse
from database.repositories.project_repository import ProjectRepository
from database.repositories.website_repository import WebsiteRepository

router = APIRouter(prefix="/projects/{project_id}/websites", tags=["websites"])


async def _verify_project(project_id: UUID, user_id: str) -> None:
    repo = ProjectRepository()
    project = await repo.get_by_id(project_id, user_id)
    if not project:
        raise NotFoundError("Project not found")


@router.get("")
async def list_websites(project_id: UUID, user_id: str = Depends(get_current_user_id)):
    await _verify_project(project_id, user_id)
    repo = WebsiteRepository()
    items = await repo.list_by_project(project_id)
    return {"items": [WebsiteResponse(**w) for w in items]}


@router.get("/primary", response_model=WebsiteResponse)
async def get_primary_website(project_id: UUID, user_id: str = Depends(get_current_user_id)):
    await _verify_project(project_id, user_id)
    repo = WebsiteRepository()
    website = await repo.get_primary(project_id)
    if not website:
        raise NotFoundError("No website submitted for this project")
    return website


@router.get("/{website_id}", response_model=WebsiteResponse)
async def get_website(
    project_id: UUID, website_id: UUID, user_id: str = Depends(get_current_user_id)
):
    await _verify_project(project_id, user_id)
    repo = WebsiteRepository()
    website = await repo.get_by_id(project_id, website_id)
    if not website:
        raise NotFoundError("Website not found")
    return website


@router.post("", response_model=WebsiteResponse, status_code=status.HTTP_201_CREATED)
async def submit_website(
    project_id: UUID,
    body: WebsiteCreate,
    user_id: str = Depends(get_current_user_id),
):
    await _verify_project(project_id, user_id)
    repo = WebsiteRepository()
    website = await repo.create(project_id, str(body.url))
    return website
