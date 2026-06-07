"""Database models and Pydantic schemas."""

from datetime import date, datetime
from enum import StrEnum
from typing import Any
from uuid import UUID

from pydantic import BaseModel, Field, HttpUrl


class ProjectStatus(StrEnum):
    DRAFT = "draft"
    ANALYZING = "analyzing"
    ACTIVE = "active"
    ARCHIVED = "archived"


class ContentChannel(StrEnum):
    BLOG = "blog"
    LINKEDIN = "linkedin"
    INSTAGRAM = "instagram"
    TIKTOK = "tiktok"
    YOUTUBE = "youtube"
    TWITTER = "twitter"
    FACEBOOK = "facebook"


class ContentFormat(StrEnum):
    POST = "post"
    ARTICLE = "article"
    VIDEO = "video"
    REEL = "reel"
    STORY = "story"
    CAROUSEL = "carousel"
    THREAD = "thread"


class ContentStatus(StrEnum):
    DRAFT = "draft"
    GENERATING = "generating"
    READY = "ready"
    APPROVED = "approved"
    REJECTED = "rejected"
    PUBLISHED = "published"
    SCHEDULED = "scheduled"


class JobStatus(StrEnum):
    QUEUED = "queued"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class AssetType(StrEnum):
    CAPTION = "caption"
    SCRIPT = "script"
    BLOG_OUTLINE = "blog_outline"
    IMAGE_PROMPT = "image_prompt"
    HASHTAGS = "hashtags"
    HOOK = "hook"
    CTA = "cta"


# --- Request/Response Schemas ---


class ProjectCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: str | None = None


class ProjectUpdate(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=255)
    description: str | None = None
    status: ProjectStatus | None = None


class ProjectResponse(BaseModel):
    id: UUID
    user_id: UUID
    name: str
    description: str | None
    status: ProjectStatus
    created_at: datetime
    updated_at: datetime


class ProjectStats(BaseModel):
    content_items: int = 0
    approved_items: int = 0
    keywords: int = 0
    competitors: int = 0


class ProjectDetailResponse(ProjectResponse):
    stats: ProjectStats = Field(default_factory=ProjectStats)


class WebsiteCreate(BaseModel):
    url: HttpUrl


class WebsiteResponse(BaseModel):
    id: UUID
    project_id: UUID
    url: str
    status: str
    business_type: str | None = None
    products_services: list[str] = []
    target_audience: str | None = None
    unique_value_proposition: str | None = None
    brand_tone: str | None = None
    analyzed_at: datetime | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None


class AnalyzeRequest(BaseModel):
    website_id: UUID
    options: dict[str, Any] = Field(
        default_factory=lambda: {
            "calendar_days": 7,
            "competitor_count": 4,
            "keyword_count": 10,
            "generate_assets": True,
            "sample_asset_count": 3,
        }
    )


class JobResponse(BaseModel):
    id: UUID
    project_id: UUID
    status: JobStatus
    progress: int
    current_step: str | None = None
    steps_completed: list[str] = []
    error_message: str | None = None
    started_at: datetime | None = None
    completed_at: datetime | None = None


class CompetitorResponse(BaseModel):
    id: UUID
    name: str
    url: str
    strengths: list[str] = []
    weaknesses: list[str] = []
    content_gaps: list[str] = []
    positioning_summary: str | None = None


class ContentPlanResponse(BaseModel):
    id: UUID
    name: str
    start_date: date
    end_date: date
    status: str
    pillars: list[str] = []
    channel_mix: dict[str, int] = Field(default_factory=dict)


class ContentItemResponse(BaseModel):
    id: UUID
    title: str
    description: str | None = None
    channel: ContentChannel
    format: ContentFormat
    scheduled_date: date | None = None
    status: ContentStatus
    body: str | None = None
    keyword_targets: list[str] = []


class ContentItemUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    body: str | None = None
    status: ContentStatus | None = None
    scheduled_date: date | None = None


class GeneratedAssetResponse(BaseModel):
    id: UUID
    content_item_id: UUID | None = None
    asset_type: AssetType
    platform: str | None = None
    content: str
    version: int = 1


class ContentItemDetailResponse(ContentItemResponse):
    assets: list[GeneratedAssetResponse] = Field(default_factory=list)


class RegenerateAssetsRequest(BaseModel):
    asset_types: list[AssetType] | None = None
    instructions: str | None = None


class SEOKeywordResponse(BaseModel):
    id: UUID
    keyword: str
    search_volume: int | None = None
    difficulty: int | None = None
    intent: str | None = None
    cluster: str | None = None
    priority: str = "medium"
    content_suggestions: list[str] = []


class PaginatedResponse(BaseModel):
    items: list[Any]
    total: int
    page: int = 1
    limit: int = 20


class UserProfileResponse(BaseModel):
    id: UUID
    email: str
    full_name: str | None = None
    avatar_url: str | None = None
    plan: str = "free"
    analyses_used: int = 0
    analyses_limit: int = 1
    created_at: datetime


class UserProfileUpdate(BaseModel):
    full_name: str | None = Field(None, max_length=255)


class UsageResponse(BaseModel):
    analyses_used: int
    analyses_limit: int
    regenerations_used: int = 0
    regenerations_limit: int = 10
    plan: str


class HealthDetailResponse(BaseModel):
    status: str
    version: str
    supabase: str
    auth: str
