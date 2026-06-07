# Step 6 — OpenAI & AI Integration

## Files created / updated

| File | Purpose |
|------|---------|
| `services/ai/models.py` | AITask enum, model routing, response types |
| `services/ai/schemas.py` | Pydantic schemas for all agent outputs |
| `services/ai/prompts.py` | Centralized system prompts |
| `services/ai/openai_client.py` | OpenAI client with retry + token tracking |
| `services/ai/anthropic_client.py` | Anthropic client (separated) |
| `services/ai/service.py` | Unified AIService with model routing |
| `api/v1/ai.py` | AI health + model routing endpoints |
| All 7 agents | Refactored to use AIService + schemas |
| `tests/test_ai_service.py` | Unit tests |

## Model routing

| Task | Provider | Model |
|------|----------|-------|
| Website Analysis | Anthropic | claude-sonnet-4 |
| Competitor Research | OpenAI | gpt-4o |
| Audience Research | Anthropic | claude-sonnet-4 |
| SEO Strategy | OpenAI | gpt-4o |
| Content Planning | Anthropic | claude-sonnet-4 |
| Caption Writing | OpenAI | gpt-4o-mini |
| Script Writing | Anthropic | claude-sonnet-4 |

## Features

- **Structured outputs** — Pydantic validation on all AI responses
- **Retry logic** — 3 attempts with exponential backoff (tenacity)
- **Token tracking** — `tokens_used` on every AgentResult
- **Centralized prompts** — single source in `prompts.py`
- **Health check** — verify API keys are configured

## How to run

### 1. Configure API keys

```bash
# backend/.env
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
```

### 2. Start backend

```bash
cd backend && source venv/bin/activate && python run.py
```

### 3. Check AI health (authenticated)

```bash
export ACCESS_TOKEN="your-jwt"

curl -s http://localhost:8000/api/v1/ai/health \
  -H "Authorization: Bearer $ACCESS_TOKEN" | python3 -m json.tool

curl -s http://localhost:8000/api/v1/ai/models \
  -H "Authorization: Bearer $ACCESS_TOKEN" | python3 -m json.tool
```

Expected:

```json
{
  "openai_configured": true,
  "anthropic_configured": true,
  "ready": true,
  "models": { "website_analysis": "anthropic/claude-sonnet-4-20250514", ... }
}
```

### 4. Run tests

```bash
pytest tests/test_ai_service.py -v
```

## Usage in agents

```python
from services.ai.models import AITask
from services.ai.schemas import WebsiteAnalysisSchema
from services.ai.service import get_ai_service

ai = get_ai_service()
analysis, result = await ai.complete_structured(
    AITask.WEBSITE_ANALYSIS,
    user_prompt,
    WebsiteAnalysisSchema,
)
# result.total_tokens → token count
```

## What's next

**Step 7 — Website Analysis Workflow**  
Wire URL submission → analysis pipeline → progress UI.

Reply **"step 7"** or **"continue"** when ready.
