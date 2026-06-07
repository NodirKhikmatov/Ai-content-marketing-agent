# Step 1 — PostgreSQL Schema & Supabase Integration

## Files created / updated

| File | Purpose |
|------|---------|
| `supabase/config.toml` | Local Supabase CLI config |
| `supabase/migrations/001_initial_schema.sql` | Full MVP schema + RLS + triggers |
| `frontend/lib/supabase/database.types.ts` | TypeScript types for all tables |
| `frontend/lib/supabase/client.ts` | Typed browser Supabase client |
| `frontend/lib/supabase/server.ts` | Typed server Supabase client |
| `backend/database/supabase.py` | Typed service-role client wrapper |
| `backend/services/storage/supabase_client.py` | Re-exports for existing imports |
| `scripts/verify-supabase.sh` | Post-migration verification script |

## Schema overview

```
auth.users ──► profiles ──► projects ──┬── websites
                                       ├── competitors
                                       ├── content_plans ──► content_items ──► generated_assets
                                       ├── seo_keywords
                                       └── analysis_jobs
```

## How to run

### 1. Create Supabase project

1. Go to [supabase.com/dashboard](https://supabase.com/dashboard) → **New project**
2. Save these values (Settings → API):
   - Project URL
   - `anon` public key
   - `service_role` secret key
   - JWT Secret (Settings → API → JWT Settings)

### 2. Apply migration

**Option A — Dashboard (recommended for first setup)**

1. Open **SQL Editor** in Supabase
2. Paste contents of `supabase/migrations/001_initial_schema.sql`
3. Click **Run**

**Option B — Supabase CLI**

```bash
npm install -g supabase
supabase login
supabase link --project-ref YOUR_PROJECT_REF
supabase db push
```

### 3. Configure environment

```bash
# Backend
cp backend/.env.example backend/.env
# Set: SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY, SUPABASE_JWT_SECRET

# Frontend
cp frontend/.env.example frontend/.env.local
# Set: NEXT_PUBLIC_SUPABASE_URL, NEXT_PUBLIC_SUPABASE_ANON_KEY
```

### 4. Verify schema

```bash
export SUPABASE_URL="https://xxxx.supabase.co"
export SUPABASE_SERVICE_ROLE_KEY="your-service-role-key"
chmod +x scripts/verify-supabase.sh
./scripts/verify-supabase.sh
```

Expected output: all 9 tables show ✓

### 5. Smoke test (optional)

In Supabase SQL Editor:

```sql
SELECT tablename FROM pg_tables WHERE schemaname = 'public' ORDER BY tablename;
```

You should see all 9 public tables.

## What's next

**Step 2 — Backend API foundation + JWT authentication middleware**

Reply **"continue"** or **"step 2"** when ready.
