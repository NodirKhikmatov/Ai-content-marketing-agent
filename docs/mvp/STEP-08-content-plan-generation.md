# Step 8 — Content Plan Generation

## Files created / updated

| File | Purpose |
|------|---------|
| `backend/database/models.py` | `ContentItemDetailResponse`, `RegenerateAssetsRequest`, `channel_mix` on plans |
| `backend/api/v1/projects.py` | GET item detail, POST regenerate |
| `backend/workflows/asset_generation.py` | Sync caption/script to `body`, regeneration flow |
| `frontend/services/projects.ts` | Content plan + item CRUD client methods |
| `frontend/lib/content-utils.ts` | Week grouping, channel/status helpers |
| `frontend/components/dashboard/content-plan-summary.tsx` | Plan overview (pillars, channel mix) |
| `frontend/components/dashboard/content-calendar-view.tsx` | Week-grouped calendar |
| `frontend/components/dashboard/content-item-detail.tsx` | Edit, approve, regenerate panel |
| `frontend/app/(dashboard)/dashboard/calendar/page.tsx` | Full calendar UX |
| `frontend/app/(dashboard)/dashboard/library/page.tsx` | Library with filters + detail panel |

## Features

### Content plan summary
After analysis, the calendar page shows:
- Plan name and date range
- Content pillars (thematic buckets)
- Channel mix breakdown (LinkedIn ×12, Blog ×8, etc.)

### Calendar view
- Items grouped by week (collapsible)
- Channel icon, format, status badge per item
- Click item → detail panel on the right

### Content library
- Filter by channel and status
- Preview body text in list
- Full detail panel: edit body, approve/reject, regenerate with instructions
- View all generated assets (caption, script, image prompt, etc.)

## API endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/projects/{id}/content-plans` | Latest content plan |
| GET | `/projects/{id}/content-items?limit=50` | List items (paginated) |
| GET | `/projects/{id}/content-items/{item_id}` | Item + active assets |
| PATCH | `/projects/{id}/content-items/{item_id}` | Edit title/body/status |
| POST | `/projects/{id}/content-items/{item_id}/regenerate` | Regenerate AI assets |

## User flow

```
Analysis complete → Calendar shows 30-day plan
    → Click any day → Edit caption → Approve
    → Library → Filter by channel → Regenerate with instructions
```

## How to run

### 1. Prerequisites

- Steps 1–7 complete (analysis pipeline generates plan + assets)
- Backend + frontend running with AI keys configured

### 2. End-to-end test

1. Complete analysis on a project (see Step 7)
2. Open **Calendar** — verify plan summary and week groups
3. Click a content item — edit body, click **Save edits**
4. Click **Approve** — status changes to approved
5. Open **Library** — filter by LinkedIn, select item
6. Add regenerate instructions → **Regenerate** — new assets appear

### 3. API test

```bash
# Get content plan
curl "http://localhost:8000/api/v1/projects/$PROJECT_ID/content-plans" \
  -H "Authorization: Bearer $ACCESS_TOKEN"

# Get item with assets
curl "http://localhost:8000/api/v1/projects/$PROJECT_ID/content-items/$ITEM_ID" \
  -H "Authorization: Bearer $ACCESS_TOKEN"

# Approve item
curl -X PATCH "http://localhost:8000/api/v1/projects/$PROJECT_ID/content-items/$ITEM_ID" \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"status": "approved"}'

# Regenerate
curl -X POST "http://localhost:8000/api/v1/projects/$PROJECT_ID/content-items/$ITEM_ID/regenerate" \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"instructions": "Make it punchier with a question hook"}'
```

## What's next

**Step 9 — Usage limits & polish** ✅ See `STEP-09-usage-limits-polish.md`
