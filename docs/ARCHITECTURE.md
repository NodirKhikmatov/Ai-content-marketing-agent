# System Architecture

## High-Level Architecture

```mermaid
flowchart TB
    subgraph Client["Client Layer"]
        WEB[Next.js 15 App<br/>Vercel]
    end

    subgraph Auth["Authentication"]
        SA[Supabase Auth]
    end

    subgraph API["API Layer"]
        FA[FastAPI Backend<br/>Railway/Fly.io]
    end

    subgraph AI["AI Layer"]
        ORCH[Workflow Orchestrator]
        WA[Website Analyzer]
        CR[Competitor Research]
        AR[Audience Research]
        SEO[SEO Strategy]
        CP[Content Planner]
        CW[Caption Writer]
        SW[Script Writer]
    end

    subgraph Data["Data Layer"]
        PG[(PostgreSQL<br/>Supabase)]
        REDIS[(Redis<br/>Job Queue)]
        S3[(Supabase Storage<br/>Assets)]
    end

    subgraph External["External Services"]
        OPENAI[OpenAI API]
        CLAUDE[Anthropic API]
        CRAWL[Web Crawler]
    end

    WEB --> SA
    WEB --> FA
    FA --> SA
    FA --> PG
    FA --> REDIS
    FA --> S3
    FA --> ORCH
    ORCH --> WA & CR & AR & SEO & CP & CW & SW
    WA & CR & AR & SEO & CP & CW & SW --> OPENAI & CLAUDE
    WA --> CRAWL
```

---

## Component Architecture

```mermaid
flowchart LR
    subgraph Frontend["frontend/"]
        APP[app/]
        COMP[components/]
        LIB[lib/]
        SVC_FE[services/]
    end

    subgraph Backend["backend/"]
        APP_BE[app/]
        API_BE[api/]
        AGENTS[agents/]
        WORKFLOWS[workflows/]
        SVC_BE[services/]
        DB[database/]
    end

    APP --> COMP
    APP --> LIB
    APP --> SVC_FE
    SVC_FE -->|REST| API_BE
    API_BE --> WORKFLOWS
    WORKFLOWS --> AGENTS
    AGENTS --> SVC_BE
    SVC_BE --> DB
```

---

## Analysis Pipeline Workflow

```mermaid
sequenceDiagram
    participant U as User
    participant FE as Next.js Frontend
    participant API as FastAPI
    participant Q as Job Queue
    participant W as Workflow Orchestrator
    participant DB as PostgreSQL

    U->>FE: Enter website URL
    FE->>API: POST /projects/{id}/analyze
    API->>DB: Create analysis job (pending)
    API->>Q: Enqueue pipeline job
    API-->>FE: 202 Accepted + job_id

    loop Poll status
        FE->>API: GET /jobs/{job_id}
        API-->>FE: progress + status
    end

    Q->>W: Process pipeline
    W->>W: 1. Website Analyzer
    W->>DB: Save website profile
    W->>W: 2. Competitor Research
    W->>DB: Save competitors
    W->>W: 3. Audience Research
    W->>DB: Update project metadata
    W->>W: 4. SEO Strategy
    W->>DB: Save keywords
    W->>W: 5. Content Planner
    W->>DB: Save content_plan + items
    W->>W: 6. Generate Assets (parallel)
    W->>DB: Save generated_assets
    W->>DB: Mark job complete

    FE->>API: GET /projects/{id}/dashboard
    API-->>FE: Full strategy + content
```

---

## Scalability Design (100K Users)

### Horizontal Scaling
- **Frontend:** Vercel edge + ISR for marketing pages
- **Backend:** Stateless FastAPI replicas behind load balancer
- **Workers:** Separate worker processes for AI pipeline (Celery/ARQ)
- **Database:** Supabase connection pooling (PgBouncer), read replicas at scale

### Caching Strategy
| Layer | Cache | TTL |
|-------|-------|-----|
| Website crawl | Redis | 24h per URL |
| AI responses | Redis | 7d per input hash |
| Dashboard data | React Query | 5min stale |
| Static assets | CDN | 1y |

### Rate Limiting
- Free: 1 analysis/month, 10 regenerations/day
- Pro: 10 analyses/month, 100 regenerations/day
- Implemented via Redis sliding window + Supabase usage table

### Multi-Tenancy
- Row-Level Security (RLS) on all Supabase tables
- `user_id` / `project_id` on every row
- API validates JWT + project ownership on every request

---

## Security Architecture

```mermaid
flowchart TB
    REQ[Incoming Request]
    JWT[JWT Validation<br/>Supabase]
    RLS[Row-Level Security<br/>PostgreSQL]
    ENC[Encrypted Secrets<br/>API Keys at rest]

    REQ --> JWT
    JWT -->|Valid| RLS
    JWT -->|Invalid| REJECT[401 Unauthorized]
    RLS --> ENC
    ENC --> HANDLER[Route Handler]
```

- All API routes require Bearer token from Supabase
- Service role key only on backend (never exposed to client)
- AI API keys stored in backend env only
- CORS restricted to frontend domain
- Input sanitization on URLs (SSRF prevention)

---

## Deployment Architecture

| Service | Platform | Environment |
|---------|----------|-------------|
| Frontend | Vercel | Production + Preview |
| Backend API | Railway / Fly.io | Production + Staging |
| Workers | Railway / Fly.io | Separate service |
| Database | Supabase | Managed PostgreSQL |
| Redis | Upstash | Serverless Redis |
| Storage | Supabase Storage | Generated assets |

---

## Folder Structure

```
AI Content Marketing Agent/
├── docs/                          # Documentation
│   ├── PRD.md
│   ├── ARCHITECTURE.md
│   ├── API.md
│   ├── USER_FLOWS.md
│   ├── MVP_ROADMAP.md
│   ├── PHASE2_ROADMAP.md
│   └── DEVELOPMENT_TASKS.md
├── frontend/                      # Next.js 15
│   ├── app/
│   │   ├── (auth)/               # Login, signup
│   │   ├── (dashboard)/          # Protected routes
│   │   │   ├── projects/
│   │   │   ├── calendar/
│   │   │   ├── library/
│   │   │   ├── seo/
│   │   │   └── settings/
│   │   ├── api/                  # Next.js API routes (BFF)
│   │   └── layout.tsx
│   ├── components/
│   │   ├── ui/                   # Shadcn components
│   │   ├── dashboard/
│   │   ├── content/
│   │   └── shared/
│   ├── lib/
│   │   ├── supabase/
│   │   ├── utils.ts
│   │   └── constants.ts
│   └── services/
│       ├── api-client.ts
│       ├── projects.ts
│       └── content.ts
├── backend/                       # FastAPI
│   ├── app/
│   │   ├── main.py
│   │   ├── config.py
│   │   └── dependencies.py
│   ├── api/
│   │   ├── v1/
│   │   │   ├── projects.py
│   │   │   ├── websites.py
│   │   │   ├── competitors.py
│   │   │   ├── content.py
│   │   │   ├── seo.py
│   │   │   └── jobs.py
│   │   └── router.py
│   ├── agents/
│   │   ├── base.py
│   │   ├── website_analyzer.py
│   │   ├── competitor_research.py
│   │   ├── audience_research.py
│   │   ├── seo_strategy.py
│   │   ├── content_planner.py
│   │   ├── caption_writer.py
│   │   └── script_writer.py
│   ├── workflows/
│   │   ├── analysis_pipeline.py
│   │   └── asset_generation.py
│   ├── services/
│   │   ├── ai/
│   │   │   ├── openai_client.py
│   │   │   └── anthropic_client.py
│   │   ├── crawler/
│   │   │   └── website_crawler.py
│   │   └── storage/
│   │       └── supabase_client.py
│   └── database/
│       ├── models.py
│       └── repositories/
├── supabase/
│   └── migrations/
│       └── 001_initial_schema.sql
├── docker-compose.yml
└── README.md
```
