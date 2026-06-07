# Step 9 — Usage Limits & Polish

## Files created / updated

| File | Purpose |
|------|---------|
| `supabase/migrations/002_usage_limits.sql` | Regenerations columns + atomic quota RPCs |
| `backend/services/usage/service.py` | Usage checks and consumption |
| `backend/app/exceptions.py` | `QuotaExceededError` (403) |
| `backend/api/v1/analysis.py` | Enforce analysis limit before start |
| `backend/api/v1/projects.py` | Enforce regeneration limit |
| `backend/api/v1/users.py` | Usage stats via `get_usage_stats` RPC |
| `backend/tests/test_usage.py` | Usage service unit tests |
| `frontend/components/dashboard/usage-meter.tsx` | Progress bars for limits |
| `frontend/components/dashboard/website-analyzer.tsx` | Block start when at limit |
| `frontend/components/dashboard/content-item-detail.tsx` | Regeneration limit UX |
| `frontend/app/(dashboard)/dashboard/settings/page.tsx` | Full usage dashboard |

## Plan limits (MVP)

| Plan | Analyses / month | Regenerations / month |
|------|------------------|------------------------|
| Free | 1 | 10 |
| Pro | 10 | 100 |
| Team | 50 | 500 |
| Agency | 200 | 2000 |

Limits are stored on `profiles.analyses_limit` and `profiles.regenerations_limit`. Counters reset automatically on the 1st of each month via `usage_period_start`.

## Database RPCs

| Function | Purpose |
|----------|---------|
| `get_usage_stats(user_uuid)` | Return current usage (with monthly reset) |
| `try_consume_analysis(user_uuid)` | Atomically increment if under limit |
| `try_consume_regeneration(user_uuid)` | Atomically increment if under limit |

## API behavior

When a limit is exceeded, the API returns:

```json
{
  "error": {
    "code": "QUOTA_EXCEEDED",
    "message": "Analysis limit reached (1/1 this month)..."
  }
}
```

HTTP status: **403 Forbidden**

## How to run

### 1. Apply migration

Run in Supabase SQL Editor:

```
supabase/migrations/002_usage_limits.sql
```

Or if using Supabase CLI: `supabase db push`

### 2. Verify

```bash
# Check usage
curl "http://localhost:8000/api/v1/users/me/usage" \
  -H "Authorization: Bearer $ACCESS_TOKEN"

# Start analysis (consumes 1 credit)
curl -X POST "http://localhost:8000/api/v1/projects/$PROJECT_ID/analysis" \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"website_id": "'$WEBSITE_ID'"}'

# Second attempt on free plan → 403 QUOTA_EXCEEDED
```

### 3. Frontend

1. Open **Settings** — see usage meters
2. Run one analysis on free plan
3. Try second analysis — button disabled with limit message
4. Regenerate content until limit — button disabled

## Production deployment checklist

### Supabase
- [ ] Run `001_initial_schema.sql` and `002_usage_limits.sql`
- [ ] Enable Google OAuth provider (if using)
- [ ] Set Site URL + redirect URLs for production domain
- [ ] Copy `SUPABASE_URL`, anon key, service role key, JWT secret

### Backend (Railway / Fly.io)
- [ ] Set all env vars from `backend/.env.example`
- [ ] Set `CORS_ORIGINS=["https://your-domain.com"]`
- [ ] Deploy with `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
- [ ] Verify `/api/v1/health` returns `ok`

### Frontend (Vercel)
- [ ] Set `NEXT_PUBLIC_SUPABASE_URL`, `NEXT_PUBLIC_SUPABASE_ANON_KEY`
- [ ] Set `NEXT_PUBLIC_API_URL=https://your-api.railway.app/api/v1`
- [ ] Deploy; confirm auth callback works on production URL

### Smoke test
- [ ] Sign up → create project → submit URL → run analysis
- [ ] Calendar + library load content
- [ ] Settings shows usage meters
- [ ] Free-tier limit blocks second analysis

## What's next

**MVP complete.** Optional follow-ups:
- Stripe billing + plan upgrades
- E2E tests (Playwright)
- Redis job queue for long-running pipelines
- Email notifications on analysis complete

Reply with any feature area to expand, or **"deploy"** for a guided production setup.
