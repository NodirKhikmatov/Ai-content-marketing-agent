import logging
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.dependencies import get_current_user_id
from database.models import (
    CompetitorResponse,
    ContentItemDetailResponse,
    ContentItemResponse,
    ContentItemUpdate,
    ContentPlanResponse,
    GeneratedAssetResponse,
    PaginatedResponse,
    ProjectCreate,
    ProjectDetailResponse,
    ProjectResponse,
    ProjectStats,
    ProjectUpdate,
    RegenerateAssetsRequest,
    SEOKeywordResponse,
)
from database.repositories.project_repository import ProjectRepository
from database.repositories.base import maybe_single_data
from database.supabase import get_supabase
from services.usage.service import get_usage_service
from workflows.asset_generation import AssetGenerationWorkflow

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/projects", tags=["projects"])


async def _verify_project_access(project_id: UUID, user_id: str) -> dict:
    repo = ProjectRepository()
    project = await repo.get_by_id(project_id, user_id)
    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
    return project


@router.post("", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
async def create_project(body: ProjectCreate, user_id: str = Depends(get_current_user_id)):
    repo = ProjectRepository()
    project = await repo.create(user_id, body.name, body.description)
    return project


@router.get("", response_model=PaginatedResponse)
async def list_projects(
    user_id: str = Depends(get_current_user_id),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    project_status: str | None = Query(None, alias="status"),
):
    repo = ProjectRepository()
    items, total = await repo.list_by_user(user_id, page, limit, project_status)
    return PaginatedResponse(items=items, total=total, page=page, limit=limit)


@router.get("/{project_id}", response_model=ProjectDetailResponse)
async def get_project(project_id: UUID, user_id: str = Depends(get_current_user_id)):
    repo = ProjectRepository()
    project = await repo.get_by_id(project_id, user_id)
    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
    stats_data = await repo.get_stats(project_id)
    return {**project, "stats": ProjectStats(**stats_data)}


@router.patch("/{project_id}", response_model=ProjectResponse)
async def update_project(
    project_id: UUID, body: ProjectUpdate, user_id: str = Depends(get_current_user_id)
):
    repo = ProjectRepository()
    data = body.model_dump(exclude_none=True)
    if "status" in data:
        data["status"] = data["status"].value
    project = await repo.update(project_id, user_id, data)
    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
    return project


@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_project(project_id: UUID, user_id: str = Depends(get_current_user_id)):
    repo = ProjectRepository()
    deleted = await repo.delete(project_id, user_id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")


@router.get("/{project_id}/competitors")
async def list_competitors(project_id: UUID, user_id: str = Depends(get_current_user_id)):
    await _verify_project_access(project_id, user_id)
    db = get_supabase()
    result = db.table("competitors").select("*").eq("project_id", str(project_id)).execute()
    return {"items": [CompetitorResponse(**c) for c in (result.data or [])]}


@router.get("/{project_id}/content-plans")
async def get_content_plans(project_id: UUID, user_id: str = Depends(get_current_user_id)):
    await _verify_project_access(project_id, user_id)
    db = get_supabase()
    result = (
        db.table("content_plans")
        .select("*")
        .eq("project_id", str(project_id))
        .order("created_at", desc=True)
        .limit(1)
        .execute()
    )
    if not result.data:
        return {"items": []}
    return {"items": [ContentPlanResponse(**p) for p in result.data]}


@router.get("/{project_id}/content-items")
async def list_content_items(
    project_id: UUID,
    user_id: str = Depends(get_current_user_id),
    channel: str | None = None,
    item_status: str | None = Query(None, alias="status"),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
):
    await _verify_project_access(project_id, user_id)
    db = get_supabase()
    query = db.table("content_items").select("*", count="exact").eq("project_id", str(project_id))
    if channel:
        query = query.eq("channel", channel)
    if item_status:
        query = query.eq("status", item_status)
    offset = (page - 1) * limit
    result = query.order("scheduled_date").range(offset, offset + limit - 1).execute()
    return PaginatedResponse(
        items=[ContentItemResponse(**i) for i in (result.data or [])],
        total=result.count or 0,
        page=page,
        limit=limit,
    )


@router.get("/{project_id}/content-items/{item_id}", response_model=ContentItemDetailResponse)
async def get_content_item(
    project_id: UUID,
    item_id: UUID,
    user_id: str = Depends(get_current_user_id),
):
    await _verify_project_access(project_id, user_id)
    db = get_supabase()
    item_result = (
        db.table("content_items")
        .select("*")
        .eq("id", str(item_id))
        .eq("project_id", str(project_id))
        .maybe_single()
        .execute()
    )
    item_data = maybe_single_data(item_result)
    if not item_data:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Content item not found")

    assets_result = (
        db.table("generated_assets")
        .select("*")
        .eq("content_item_id", str(item_id))
        .eq("is_active", True)
        .order("created_at")
        .execute()
    )
    assets = [GeneratedAssetResponse(**a) for a in (assets_result.data or [])]
    return ContentItemDetailResponse(**item_data, assets=assets)


@router.patch("/{project_id}/content-items/{item_id}", response_model=ContentItemResponse)
async def update_content_item(
    project_id: UUID,
    item_id: UUID,
    body: ContentItemUpdate,
    user_id: str = Depends(get_current_user_id),
):
    await _verify_project_access(project_id, user_id)
    db = get_supabase()
    data = body.model_dump(exclude_none=True)
    if "status" in data:
        data["status"] = data["status"].value
    if "scheduled_date" in data and data["scheduled_date"]:
        data["scheduled_date"] = data["scheduled_date"].isoformat()
    result = (
        db.table("content_items")
        .update(data)
        .eq("id", str(item_id))
        .eq("project_id", str(project_id))
        .execute()
    )
    if not result.data:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Content item not found")
    return ContentItemResponse(**result.data[0])


@router.post(
    "/{project_id}/content-items/{item_id}/regenerate",
    response_model=ContentItemDetailResponse,
)
async def regenerate_content_item(
    project_id: UUID,
    item_id: UUID,
    body: RegenerateAssetsRequest | None = None,
    user_id: str = Depends(get_current_user_id),
):
    await _verify_project_access(project_id, user_id)
    db = get_supabase()

    item_result = (
        db.table("content_items")
        .select("*")
        .eq("id", str(item_id))
        .eq("project_id", str(project_id))
        .maybe_single()
        .execute()
    )
    item_data = maybe_single_data(item_result)
    if not item_data:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Content item not found")

    website_result = (
        db.table("websites")
        .select("brand_tone")
        .eq("project_id", str(project_id))
        .eq("status", "analyzed")
        .order("created_at", desc=True)
        .limit(1)
        .execute()
    )
    brand_tone = ""
    if website_result.data:
        brand_tone = website_result.data[0].get("brand_tone") or ""

    usage_service = get_usage_service()
    usage_service.consume_regeneration(user_id)

    workflow = AssetGenerationWorkflow()
    req = body or RegenerateAssetsRequest()
    await workflow.regenerate_item(
        project_id,
        item_data,
        brand_tone,
        asset_types=[t.value for t in req.asset_types] if req.asset_types else None,
        instructions=req.instructions,
    )

    updated = (
        db.table("content_items")
        .select("*")
        .eq("id", str(item_id))
        .maybe_single()
        .execute()
    )
    updated_data = maybe_single_data(updated)
    assets_result = (
        db.table("generated_assets")
        .select("*")
        .eq("content_item_id", str(item_id))
        .eq("is_active", True)
        .order("created_at")
        .execute()
    )
    assets = [GeneratedAssetResponse(**a) for a in (assets_result.data or [])]
    return ContentItemDetailResponse(**updated_data, assets=assets)


@router.get("/{project_id}/seo-keywords")
async def list_seo_keywords(
    project_id: UUID,
    user_id: str = Depends(get_current_user_id),
    cluster: str | None = None,
):
    await _verify_project_access(project_id, user_id)
    db = get_supabase()
    query = db.table("seo_keywords").select("*").eq("project_id", str(project_id))
    if cluster:
        query = query.eq("cluster", cluster)
    result = query.order("priority").execute()
    keywords = result.data or []
    clusters = list({k["cluster"] for k in keywords if k.get("cluster")})
    return {
        "items": [SEOKeywordResponse(**k) for k in keywords],
        "clusters": clusters,
        "summary": {
            "total_keywords": len(keywords),
            "high_priority": sum(1 for k in keywords if k.get("priority") == "high"),
        },
    }
