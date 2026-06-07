# AI Content Marketing Agent

A production-ready SaaS platform that transforms a website URL into a complete marketing strategy and content system powered by AI.

## What It Does

1. User signs up and creates a project
2. User enters their website URL
3. AI analyzes the website, researches competitors, and builds audience personas
4. AI generates SEO strategy, 30-day content calendar, and ready-to-publish assets
5. User reviews, edits, and approves content in the dashboard

## Tech Stack

| Layer | Technology |
|-------|------------|
| Frontend | Next.js 15, TypeScript, TailwindCSS, Shadcn UI |
| Backend | FastAPI, Python 3.11 |
| Database | PostgreSQL (Supabase) |
| Auth | Supabase Auth |
| AI | OpenAI GPT-4o + Anthropic Claude |
| Infrastructure | Vercel + Supabase + Railway |

## Project Structure

```
├── docs/                 # PRD, architecture, API docs, roadmaps
├── frontend/             # Next.js 15 application
├── backend/              # FastAPI + AI agents
├── supabase/migrations/  # Database schema
└── docker-compose.yml    # Local dev services
```

## Quick Start

### Prerequisites

- Node.js 20+
- Python 3.11+
- Supabase account
- OpenAI + Anthropic API keys

### 1. Supabase Setup

1. Create a new Supabase project
2. Run migrations in order:
   - `supabase/migrations/001_initial_schema.sql`
   - `supabase/migrations/002_usage_limits.sql`
3. Copy URL, anon key, service role key, and JWT secret

### 2. Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
# Edit .env with your credentials
python run.py
```

API docs: http://localhost:8000/docs

### 3. Frontend

```bash
cd frontend
npm install
cp .env.example .env.local
# Edit .env.local with your credentials
npm run dev
```

App: http://localhost:3000

### 4. Docker (optional)

```bash
docker-compose up -d redis
```

## AI Agents

| Agent | Purpose | Model |
|-------|---------|-------|
| Website Analyzer | Extract business intelligence from URL | Claude |
| Competitor Research | Identify and analyze competitors | GPT-4o |
| Audience Research | Build personas and preferences | Claude |
| SEO Strategy | Generate keyword clusters | GPT-4o |
| Content Planner | Create 30-day calendar | Claude |
| Caption Writer | Platform-specific captions | GPT-4o-mini |
| Script Writer | Video scripts, blog outlines | Claude |

> Claude tasks use `claude-sonnet-4-6` by default (configurable via `ANTHROPIC_MODEL`).
> The content calendar can be exported to CSV from the Calendar page (**Export CSV**).

## Documentation

- [Product Requirements (PRD)](docs/PRD.md)
- [System Architecture](docs/ARCHITECTURE.md)
- [API Reference](docs/API.md)
- [User Flows](docs/USER_FLOWS.md)
- [MVP Roadmap](docs/MVP_ROADMAP.md)
- [MVP Step Guides](docs/mvp/) — Step-by-step build instructions (Steps 1–9)
- [Phase 2 Roadmap](docs/PHASE2_ROADMAP.md)
- [Development Tasks](docs/DEVELOPMENT_TASKS.md)

## Environment Variables

### Backend (`backend/.env`)

```
SUPABASE_URL=
SUPABASE_SECRET_KEY=            # server key (sb_secret_…); preferred
SUPABASE_SERVICE_ROLE_KEY=     # legacy fallback; leave blank if using SECRET_KEY
SUPABASE_JWT_SECRET=           # blank for modern (JWKS) projects
OPENAI_API_KEY=
ANTHROPIC_API_KEY=
ANTHROPIC_MODEL=claude-sonnet-4-6
OPENAI_MODEL=gpt-4o
OPENAI_MODEL_MINI=gpt-4o-mini
REDIS_URL=redis://localhost:6379
USE_WORKER_QUEUE=false         # true = durable arq worker (needs Redis)
CORS_ORIGINS=["http://localhost:3000"]
```

> Model names are env-configurable so a provider model retirement is a one-line change,
> not a code edit.

### Frontend (`frontend/.env.local`)

```
NEXT_PUBLIC_SUPABASE_URL=
NEXT_PUBLIC_SUPABASE_PUBLISHABLE_KEY=    # sb_publishable_… (or legacy NEXT_PUBLIC_SUPABASE_ANON_KEY)
NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1
```

## Background Worker (optional, durable jobs)

Analyses run as in-process background tasks by default. To make them survive API
restarts and scale across processes, use the Redis-backed worker:

1. Start Redis: `docker-compose up -d redis`
2. Set `USE_WORKER_QUEUE=true` in `backend/.env`
3. Run the worker (from `backend/`, venv active): `arq workers.worker.WorkerSettings`

If Redis is unreachable while queueing is enabled, the API falls back to in-process
tasks automatically so a job is never dropped.

## Deployment

| Service | Platform |
|---------|----------|
| Frontend | Vercel |
| Backend | Railway or Fly.io |
| Database | Supabase |
| Redis | Upstash (optional) |

See [Step 9 deployment checklist](docs/mvp/STEP-09-usage-limits-polish.md#production-deployment-checklist) for production setup.

## License

Proprietary — All rights reserved.
# Ai-content-marketing-agent
