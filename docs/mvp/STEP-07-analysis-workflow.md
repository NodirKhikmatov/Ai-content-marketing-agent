# Step 7 — Website Analysis Workflow

## Files created / updated

| File | Purpose |
|------|---------|
| `workflows/pipeline_steps.py` | Step order, progress %, labels |
| `workflows/analysis_pipeline.py` | Improved progress tracking, website status updates |
| `api/v1/analysis.py` | Start analysis, get active job, pipeline steps |
| `database/repositories/job_repository.py` | Active job lookup, fixed timestamps |
| `frontend/services/analysis.ts` | Analysis API client |
| `frontend/components/dashboard/analysis-progress.tsx` | Step checklist + polling |
| `frontend/components/dashboard/website-analyzer.tsx` | Start analysis button |
| `frontend/components/dashboard/website-section.tsx` | Full URL → analyze → progress flow |

## Pipeline steps

```
1. website_analysis    (5%)   — Crawl + extract business intel
2. competitor_research (20%)  — Identify competitors
3. audience_research   (40%)  — Build personas
4. seo_strategy        (55%)  — Keyword clusters
5. content_planning    (70%)  — 30-day calendar
6. asset_generation    (85%)  — Captions, scripts, prompts
→ completed            (100%)
```

## API endpoints

| Method | Path | Description |
|--------|------|-------------|
| POST | `/projects/{id}/analysis` | Start pipeline (202) |
| GET | `/projects/{id}/analysis/active` | Poll running job |
| GET | `/projects/{id}/analysis/steps` | Step metadata |
| GET | `/jobs/{id}` | Job status by ID |

## User flow

```
Submit URL → "Start AI Analysis" → Progress UI (poll every 2.5s)
    → Step checklist updates live → Complete → Stats + quick links
```

Resuming: if user refreshes during analysis, active job is restored automatically.

## How to run

### 1. Prerequisites

- Steps 1–6 complete (DB, auth, OpenAI/Anthropic keys)
- Backend + frontend running

### 2. End-to-end test

1. Create project → submit `stripe.com`
2. Click **Start AI Analysis**
3. Watch 6-step progress checklist
4. On complete: project status → `active`, stats populate
5. Visit Calendar, SEO, Library pages

### 3. API test

```bash
# Start analysis
curl -X POST "http://localhost:8000/api/v1/projects/$PROJECT_ID/analysis" \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"website_id": "'$WEBSITE_ID'", "options": {"calendar_days": 30}}'

# Poll active job
curl "http://localhost:8000/api/v1/projects/$PROJECT_ID/analysis/active" \
  -H "Authorization: Bearer $ACCESS_TOKEN"
```

## What's next

**Step 8 — Content Plan Generation**  
Polish content plan output, calendar views, and content library UX.

Reply **"step 8"** or **"continue"** when ready.
