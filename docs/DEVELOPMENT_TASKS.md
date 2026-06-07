# Development Tasks — Execution Order

Tasks are ordered by dependency. Complete each group before moving to the next.

---

## Group 1: Project Foundation (Days 1–3)

| # | Task | Owner | Depends On |
|---|------|-------|------------|
| 1.1 | Initialize monorepo structure | Dev | — |
| 1.2 | Create Supabase project (auth + DB) | Dev | — |
| 1.3 | Run `001_initial_schema.sql` migration | Dev | 1.2 |
| 1.4 | Configure RLS policies | Dev | 1.3 |
| 1.5 | Set up Docker Compose (Postgres, Redis) | Dev | 1.1 |
| 1.6 | Create `.env.example` files | Dev | 1.1 |
| 1.7 | Configure ESLint, Prettier, Ruff | Dev | 1.1 |
| 1.8 | Set up GitHub Actions CI | Dev | 1.7 |

---

## Group 2: Backend Core (Days 4–7)

| # | Task | Depends On |
|---|------|------------|
| 2.1 | FastAPI app scaffold (`main.py`, config) | 1.1 |
| 2.2 | Supabase JWT auth middleware | 2.1, 1.2 |
| 2.3 | Database models + repositories | 2.1, 1.3 |
| 2.4 | Health + projects CRUD endpoints | 2.2, 2.3 |
| 2.5 | OpenAI + Anthropic client wrappers | 2.1 |
| 2.6 | Website crawler service | 2.1 |
| 2.7 | Redis + ARQ job queue setup | 1.5, 2.1 |

---

## Group 3: Frontend Core (Days 4–10, parallel with Group 2)

| # | Task | Depends On |
|---|------|------------|
| 3.1 | Next.js 15 scaffold + Tailwind + Shadcn | 1.1 |
| 3.2 | Supabase client (browser + server) | 3.1, 1.2 |
| 3.3 | Auth pages (login, signup, callback) | 3.2 |
| 3.4 | Protected route middleware | 3.3 |
| 3.5 | Dashboard layout + sidebar | 3.4 |
| 3.6 | API client service layer | 3.1, 2.4 |
| 3.7 | Projects list + create page | 3.5, 3.6 |

---

## Group 4: AI Agents (Days 8–18)

| # | Task | Depends On |
|---|------|------------|
| 4.1 | Base agent class + prompt templates | 2.5 |
| 4.2 | Website Analyzer agent | 4.1, 2.6 |
| 4.3 | Competitor Research agent | 4.1 |
| 4.4 | Audience Research agent | 4.1 |
| 4.5 | SEO Strategy agent | 4.1 |
| 4.6 | Content Planner agent | 4.1 |
| 4.7 | Caption Writer agent | 4.1 |
| 4.8 | Script Writer agent | 4.1 |
| 4.9 | Unit tests for agent output schemas | 4.2–4.8 |

---

## Group 5: Workflow Orchestration (Days 12–20)

| # | Task | Depends On |
|---|------|------------|
| 5.1 | Analysis pipeline workflow | 4.2–4.6, 2.7 |
| 5.2 | Asset generation workflow | 4.7, 4.8, 5.1 |
| 5.3 | Job status tracking + progress updates | 5.1, 2.3 |
| 5.4 | POST /analyze + GET /jobs endpoints | 5.3 |
| 5.5 | Error handling + retry logic | 5.1 |
| 5.6 | Integration test: full pipeline | 5.4 |

---

## Group 6: Frontend Features (Days 14–28)

| # | Task | Depends On |
|---|------|------------|
| 6.1 | Project detail / overview page | 3.7, 5.4 |
| 6.2 | Website URL input + analyze trigger | 6.1 |
| 6.3 | Analysis progress screen (polling) | 6.2, 5.4 |
| 6.4 | Competitors page | 6.1 |
| 6.5 | SEO dashboard page | 6.1 |
| 6.6 | Content calendar (month/week) | 6.1 |
| 6.7 | Content library with filters | 6.1 |
| 6.8 | Content item detail drawer/modal | 6.7 |
| 6.9 | Inline editor + approve/regenerate | 6.8, 5.2 |
| 6.10 | Settings page | 3.5 |

---

## Group 7: Polish & Launch (Days 25–35)

| # | Task | Depends On |
|---|------|------------|
| 7.1 | Landing page | 3.1 |
| 7.2 | Empty states + loading skeletons | 6.1–6.10 |
| 7.3 | Toast notifications + error boundaries | 6.1 |
| 7.4 | Usage limits enforcement (free tier) | 5.4 |
| 7.5 | E2E tests (Playwright) | 6.9 |
| 7.6 | Production env setup (Vercel, Railway) | All |
| 7.7 | Monitoring (Sentry) | 7.6 |
| 7.8 | Beta user onboarding | 7.6 |

---

## Critical Path

```
1.2 Supabase → 1.3 Schema → 2.2 Auth → 2.4 Projects API
    → 3.3 Auth UI → 3.7 Projects UI
    → 4.2 Website Analyzer → 5.1 Pipeline → 5.4 Analyze API
    → 6.2 URL Input → 6.3 Progress → 6.6 Calendar → 7.8 Launch
```

**Estimated MVP duration:** 35 working days (~7 weeks) with 2 developers

---

## Definition of Done (per task)

- [ ] Code merged to main via PR
- [ ] Types/lint pass in CI
- [ ] Unit tests for business logic
- [ ] API documented in OpenAPI/Swagger
- [ ] No secrets in codebase
