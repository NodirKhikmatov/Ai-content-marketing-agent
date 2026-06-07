# Step 4 — Dashboard + Create Project

## Files created / updated

| File | Purpose |
|------|---------|
| `contexts/project-context.tsx` | Global project state + localStorage persistence |
| `components/dashboard/create-project-dialog.tsx` | Modal to create projects |
| `components/dashboard/project-card.tsx` | Project card with status badge |
| `components/dashboard/project-stats.tsx` | Stats grid (items, keywords, etc.) |
| `components/dashboard/project-switcher.tsx` | Sidebar project selector |
| `components/dashboard/empty-projects.tsx` | Empty state CTA |
| `components/dashboard/project-page-header.tsx` | Shared header for sub-pages |
| `components/ui/badge.tsx` | Status badges |
| `components/ui/dialog.tsx` | Modal dialog |
| `components/ui/textarea.tsx` | Description field |
| `app/(dashboard)/layout.tsx` | Wraps app in `ProjectProvider` |
| `app/(dashboard)/dashboard/page.tsx` | Overview with CRUD |
| Sub-pages (competitors, calendar, library, seo) | Use `useProject()` hook |

## Features

- **Create project** — name + optional description via dialog
- **List projects** — grid with status badges
- **Select project** — click card or use sidebar switcher
- **Persist selection** — `localStorage` key `active_project_id`
- **Delete project** — with confirmation
- **Empty state** — guides new users to create first project
- **Sub-pages** — all use active project from context

## Data flow

```
Dashboard → projectsService.create/list/get/delete
         → Authorization: Bearer <supabase_jwt>
         → FastAPI /api/v1/projects
         → Supabase PostgreSQL (service role)
```

## How to run

### 1. Ensure Steps 1–3 are complete

- Database migration applied
- Backend running with Supabase + JWT secret
- Frontend logged in

### 2. Start services

```bash
# Terminal 1
cd backend && source venv/bin/activate && python run.py

# Terminal 2
cd frontend && npm run dev
```

### 3. Test project CRUD

1. Go to http://localhost:3000/dashboard
2. Click **New Project** → enter name → **Create project**
3. Project appears in grid and sidebar switcher
4. Create a second project → switch between them in sidebar
5. Refresh page → same project stays selected
6. Delete a project → confirm → removed from list

### 4. Verify via API

```bash
export ACCESS_TOKEN="your-jwt"
curl -s http://localhost:8000/api/v1/projects \
  -H "Authorization: Bearer $ACCESS_TOKEN" | python3 -m json.tool
```

## What's next

**Step 5 — Website URL Submission**  
Dedicated URL input flow, validation, and website record creation.

Reply **"step 5"** or **"continue"** when ready.
