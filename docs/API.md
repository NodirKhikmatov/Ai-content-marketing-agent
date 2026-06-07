# API Reference

**Base URL:** `https://api.yourdomain.com/api/v1`  
**Auth:** Bearer token (Supabase JWT)  
**Content-Type:** `application/json`

---

## Authentication

All endpoints except health check require:

```
Authorization: Bearer <supabase_access_token>
```

---

## Health

### GET /health

```json
{ "status": "ok", "version": "1.0.0" }
```

---

## Projects

### POST /projects

Create a new project workspace.

**Request:**
```json
{
  "name": "Acme Corp Marketing",
  "description": "Q2 content strategy"
}
```

**Response:** `201 Created`
```json
{
  "id": "uuid",
  "name": "Acme Corp Marketing",
  "description": "Q2 content strategy",
  "status": "draft",
  "created_at": "2026-06-07T00:00:00Z"
}
```

### GET /projects

List user's projects.

**Query:** `?page=1&limit=20&status=active`

**Response:** `200 OK`
```json
{
  "items": [...],
  "total": 5,
  "page": 1,
  "limit": 20
}
```

### GET /projects/{project_id}

Get project with summary stats.

**Response:** `200 OK`
```json
{
  "id": "uuid",
  "name": "Acme Corp Marketing",
  "status": "active",
  "website": { ... },
  "stats": {
    "content_items": 30,
    "approved_items": 12,
    "keywords": 52,
    "competitors": 8
  }
}
```

### PATCH /projects/{project_id}

Update project metadata.

### DELETE /projects/{project_id}

Soft-delete project.

---

## Websites

### POST /projects/{project_id}/websites

Add website URL to project.

**Request:**
```json
{
  "url": "https://acme.com"
}
```

**Response:** `201 Created`
```json
{
  "id": "uuid",
  "url": "https://acme.com",
  "status": "pending_analysis"
}
```

### GET /projects/{project_id}/websites/{website_id}

Get website analysis results.

**Response:** `200 OK`
```json
{
  "id": "uuid",
  "url": "https://acme.com",
  "status": "analyzed",
  "business_type": "B2B SaaS",
  "products_services": ["CRM", "Analytics"],
  "target_audience": "SMB sales teams",
  "unique_value_proposition": "...",
  "brand_tone": "professional, approachable",
  "analyzed_at": "2026-06-07T00:00:00Z"
}
```

---

## Analysis Jobs

### POST /projects/{project_id}/analyze

Trigger full AI analysis pipeline.

**Request:**
```json
{
  "website_id": "uuid",
  "options": {
    "calendar_days": 30,
    "competitor_count": 8,
    "generate_assets": true
  }
}
```

**Response:** `202 Accepted`
```json
{
  "job_id": "uuid",
  "status": "queued",
  "estimated_duration_seconds": 180
}
```

### GET /jobs/{job_id}

Poll job status.

**Response:** `200 OK`
```json
{
  "id": "uuid",
  "status": "processing",
  "progress": 45,
  "current_step": "seo_strategy",
  "steps_completed": ["website_analysis", "competitor_research", "audience_research"],
  "error": null,
  "started_at": "2026-06-07T00:00:00Z"
}
```

**Status values:** `queued` | `processing` | `completed` | `failed`

---

## Competitors

### GET /projects/{project_id}/competitors

**Response:** `200 OK`
```json
{
  "items": [
    {
      "id": "uuid",
      "name": "Competitor Inc",
      "url": "https://competitor.com",
      "strengths": ["Strong SEO", "Active blog"],
      "weaknesses": ["Weak social presence"],
      "content_gaps": ["No video content"],
      "positioning_summary": "..."
    }
  ]
}
```

### POST /projects/{project_id}/competitors/{competitor_id}/refresh

Re-run competitor analysis for single competitor.

---

## Content Plans

### GET /projects/{project_id}/content-plans

Get active content plan.

**Response:** `200 OK`
```json
{
  "id": "uuid",
  "name": "30-Day Launch Plan",
  "start_date": "2026-06-08",
  "end_date": "2026-07-07",
  "status": "active",
  "pillars": ["Product Education", "Thought Leadership", "Social Proof"]
}
```

### GET /projects/{project_id}/content-plans/{plan_id}/calendar

Get calendar view with all items.

**Query:** `?start_date=2026-06-01&end_date=2026-06-30`

**Response:** `200 OK`
```json
{
  "items": [
    {
      "id": "uuid",
      "scheduled_date": "2026-06-08",
      "channel": "linkedin",
      "format": "post",
      "title": "Why SMBs need better CRM",
      "status": "draft",
      "keyword_targets": ["crm for smb"]
    }
  ]
}
```

---

## Content Items

### GET /projects/{project_id}/content-items

List content items with filters.

**Query:** `?channel=linkedin&status=draft&page=1&limit=20`

### GET /projects/{project_id}/content-items/{item_id}

Get single item with all generated assets.

**Response:** `200 OK`
```json
{
  "id": "uuid",
  "title": "Why SMBs need better CRM",
  "channel": "linkedin",
  "format": "post",
  "scheduled_date": "2026-06-08",
  "status": "draft",
  "body": "...",
  "assets": [
    {
      "id": "uuid",
      "asset_type": "caption",
      "content": "...",
      "platform": "linkedin"
    },
    {
      "id": "uuid",
      "asset_type": "image_prompt",
      "content": "Professional illustration of..."
    }
  ]
}
```

### PATCH /projects/{project_id}/content-items/{item_id}

Update content item (user edits).

**Request:**
```json
{
  "title": "Updated title",
  "body": "Edited caption text",
  "status": "approved",
  "scheduled_date": "2026-06-10"
}
```

### POST /projects/{project_id}/content-items/{item_id}/regenerate

Regenerate assets for a content item.

**Request:**
```json
{
  "asset_types": ["caption", "script"],
  "instructions": "Make it more casual and add a CTA"
}
```

**Response:** `202 Accepted` (async job)

---

## SEO Keywords

### GET /projects/{project_id}/seo-keywords

**Query:** `?cluster=product&intent=commercial&sort=volume_desc`

**Response:** `200 OK`
```json
{
  "items": [
    {
      "id": "uuid",
      "keyword": "crm for small business",
      "search_volume": 2400,
      "difficulty": 45,
      "intent": "commercial",
      "cluster": "product",
      "priority": "high",
      "content_suggestions": ["Comparison post", "Feature highlight"]
    }
  ],
  "clusters": ["product", "education", "comparison"],
  "summary": {
    "total_keywords": 52,
    "high_priority": 12,
    "avg_difficulty": 38
  }
}
```

---

## Generated Assets

### GET /projects/{project_id}/assets

List all generated assets.

**Query:** `?asset_type=script&content_item_id=uuid`

### GET /projects/{project_id}/assets/{asset_id}

Get single asset.

---

## Settings

### GET /users/me

Get current user profile.

### PATCH /users/me

Update profile.

### GET /users/me/usage

Get usage stats for billing.

```json
{
  "analyses_used": 1,
  "analyses_limit": 1,
  "regenerations_used": 5,
  "regenerations_limit": 10,
  "plan": "free"
}
```

---

## Error Responses

```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid website URL",
    "details": [{ "field": "url", "message": "Must be a valid HTTPS URL" }]
  }
}
```

| Status | Code | Description |
|--------|------|-------------|
| 400 | VALIDATION_ERROR | Invalid input |
| 401 | UNAUTHORIZED | Missing/invalid token |
| 403 | FORBIDDEN | No access to resource |
| 404 | NOT_FOUND | Resource not found |
| 429 | RATE_LIMITED | Too many requests |
| 500 | INTERNAL_ERROR | Server error |

---

## Webhooks (Phase 2)

### POST /webhooks/analysis-complete

Notify external systems when analysis completes.
