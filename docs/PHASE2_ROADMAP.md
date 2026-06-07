# Phase 2 Roadmap

**Timeline:** 12–16 weeks post-MVP  
**Goal:** Monetization, automation, team features, scale to 100K users

---

## Phase 2 Themes

1. **Monetize** — Stripe billing, usage metering, plan enforcement
2. **Automate** — Social auto-posting, scheduled publishing
3. **Collaborate** — Teams, roles, approval workflows
4. **Intelligence** — Analytics, brand voice, performance feedback
5. **Scale** — Multi-region, advanced caching, agency features

---

## Quarter 1 Post-MVP (Weeks 1–8)

### Billing & Plans
- Stripe Checkout + Customer Portal
- Plans: Free, Pro ($49), Team ($149), Agency ($399)
- Usage metering: analyses/month, regenerations/day
- Upgrade prompts at limit boundaries
- Invoice history + tax support

### Auto-Posting
- OAuth connections: LinkedIn, Instagram, TikTok, YouTube
- Publish queue with scheduled times
- Platform-specific formatting (character limits, hashtags)
- Post status tracking (published, failed, retry)
- Webhook callbacks for publish events

### Enhanced Crawler
- Playwright for JavaScript-rendered sites
- Sitemap parsing + deep crawl (up to 50 pages)
- Screenshot capture for brand analysis
- PDF/brand asset extraction

---

## Quarter 2 Post-MVP (Weeks 9–16)

### Team Collaboration
- Invite team members by email
- Roles: Owner, Admin, Editor, Viewer
- Comment threads on content items
- Approval chains (Editor → Admin → Publish)
- Activity log / audit trail

### Brand Voice
- Upload 5–10 sample posts/articles
- AI learns tone, vocabulary, style
- Voice profile applied to all generation
- A/B tone variants on regenerate

### Analytics Dashboard
- Connect Google Analytics / Search Console
- Track content performance by item
- SEO rank tracking for target keywords
- ROI metrics: content → traffic → conversions
- Weekly AI-generated performance reports

---

## Future (Phase 3+)

| Feature | Description | Priority |
|---------|-------------|----------|
| White-label | Agency branding, custom domain | High |
| Public API | REST API for integrations | High |
| Zapier/Make | No-code integrations | Medium |
| Multi-language | Generate in 10+ languages | Medium |
| Image generation | DALL-E/Midjourney integration | Medium |
| Video generation | AI avatar / b-roll suggestions | Low |
| Mobile app | iOS/Android content approval | Low |
| Marketplace | Template packs, industry presets | Low |

---

## Scalability Milestones (Phase 2)

| Users | Infrastructure Changes |
|-------|------------------------|
| 1K | Redis job queue, connection pooling |
| 10K | Dedicated worker fleet, read replica |
| 50K | Multi-region backend, CDN for assets |
| 100K | Database sharding prep, AI cost optimization layer |

---

## AI Cost Optimization (Phase 2)

- **Model routing:** GPT-4o-mini for captions, Claude for strategy
- **Response caching:** Hash inputs, cache 7 days
- **Batch generation:** Group asset generation requests
- **Prompt compression:** Summarize context for downstream agents
- **Target:** < $0.80 per full analysis at 100K users/month

---

## Phase 2 Success Metrics

| Metric | Target |
|--------|--------|
| Paid conversion | > 5% of free users |
| MRR | $50K within 6 months post-MVP |
| Auto-post adoption | > 30% of Pro users |
| Team plan adoption | > 15% of paid users |
| Churn (monthly) | < 5% |

---

## Phase 2 Technical Priorities

1. Stripe webhooks + subscription state machine
2. OAuth token refresh for social platforms
3. Webhook delivery system (retry, dead letter)
4. Feature flags (LaunchDarkly or custom)
5. Observability: Datadog/Sentry + structured logging
6. Load testing: 1K concurrent analyses
