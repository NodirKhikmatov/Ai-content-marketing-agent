# Step 5 — Website URL Submission

## Files created / updated

| File | Purpose |
|------|---------|
| `backend/services/validation/url_validator.py` | Normalize + validate URLs, SSRF protection |
| `backend/database/repositories/website_repository.py` | Website CRUD |
| `backend/api/v1/websites.py` | Dedicated website endpoints |
| `backend/tests/test_url_validator.py` | URL validation unit tests |
| `frontend/lib/validation/url.ts` | Client-side URL validation |
| `frontend/services/websites.ts` | Website API service |
| `frontend/components/dashboard/website-url-form.tsx` | URL input form with live preview |
| `frontend/components/dashboard/website-card.tsx` | Submitted website display |
| `frontend/components/dashboard/website-section.tsx` | Loads/submits website for project |

## API endpoints

| Method | Path | Description |
|--------|------|-------------|
| POST | `/api/v1/projects/{id}/websites` | Submit + normalize URL |
| GET | `/api/v1/projects/{id}/websites` | List all websites |
| GET | `/api/v1/projects/{id}/websites/primary` | Get latest website |
| GET | `/api/v1/projects/{id}/websites/{website_id}` | Get single website |

## Validation rules

- Auto-adds `https://` if missing
- Normalizes to origin (e.g. `https://example.com`)
- Blocks localhost, private IPs, `.local` domains
- Prevents duplicate URLs per project
- Max length 2048 characters

## User flow

```
Create project → Submit URL → URL saved (status: pending)
                            → Website card shown
                            → Ready for AI analysis (Step 7)
```

## How to run

### 1. Start backend + frontend

```bash
cd backend && source venv/bin/activate && python run.py
cd frontend && npm run dev
```

### 2. Test URL submission

1. Log in → create a project
2. Enter `yourcompany.com` in the URL field
3. See live preview: `Will submit as: https://yourcompany.com`
4. Click **Submit Website URL**
5. Website card appears with status "Ready for analysis"

### 3. Test via API

```bash
export ACCESS_TOKEN="your-jwt"
export PROJECT_ID="your-project-uuid"

curl -X POST "http://localhost:8000/api/v1/projects/$PROJECT_ID/websites" \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"url": "stripe.com"}'
```

### 4. Run validation tests

```bash
cd backend && pytest tests/test_url_validator.py -v
```

## What's next

**Step 6 — OpenAI Integration**  
Structured AI client, prompt templates, model routing.

Reply **"step 6"** or **"continue"** when ready.
