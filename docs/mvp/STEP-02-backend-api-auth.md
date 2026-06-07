# Step 2 — Backend API Foundation + JWT Authentication

## Files created / updated

| File | Purpose |
|------|---------|
| `backend/app/auth/jwt.py` | Supabase JWT validator (iss, aud, role, exp) |
| `backend/app/auth/models.py` | `AuthenticatedUser` dataclass |
| `backend/app/dependencies.py` | `get_current_user`, `get_current_user_id` |
| `backend/app/exceptions.py` | Standardized error responses |
| `backend/app/middleware.py` | Request logging + `X-Request-ID` |
| `backend/app/main.py` | App factory, lifespan, CORS, handlers |
| `backend/app/config.py` | Env parsing + config helpers |
| `backend/api/v1/health.py` | `GET /api/v1/health`, `GET /api/v1/me` |
| `backend/api/v1/users.py` | `GET/PATCH /users/me`, `GET /users/me/usage` |
| `backend/database/repositories/base.py` | Base Supabase repository |
| `backend/database/repositories/user_repository.py` | Profile CRUD |
| `backend/tests/test_auth.py` | JWT unit tests |
| `backend/tests/test_api.py` | Integration tests |
| `scripts/test-api.sh` | Manual smoke test script |

## API endpoints (Step 2)

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| GET | `/health` | No | Root health check |
| GET | `/api/v1/health` | No | DB + auth config status |
| GET | `/api/v1/me` | Yes | JWT auth probe |
| GET | `/api/v1/users/me` | Yes | User profile |
| PATCH | `/api/v1/users/me` | Yes | Update profile |
| GET | `/api/v1/users/me/usage` | Yes | Plan usage limits |
| GET/POST | `/api/v1/projects` | Yes | List / create projects |
| GET/PATCH/DELETE | `/api/v1/projects/{id}` | Yes | Project CRUD |

## Auth flow

```
Frontend (Supabase login)
    → access_token (JWT)
    → Authorization: Bearer <token>
    → FastAPI get_current_user()
    → SupabaseJWTValidator.decode()
    → AuthenticatedUser(id, email, role)
```

## How to run

### 1. Install dependencies

```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2. Configure `.env`

```bash
cp .env.example .env
```

Required for Step 2:

```env
SUPABASE_URL=https://xxxx.supabase.co
SUPABASE_SERVICE_ROLE_KEY=eyJ...
SUPABASE_JWT_SECRET=your-jwt-secret-from-supabase-settings
DEBUG=true
CORS_ORIGINS=["http://localhost:3000"]
```

JWT secret: Supabase Dashboard → **Settings → API → JWT Secret**

### 3. Start the server

```bash
cd backend
source venv/bin/activate
python run.py
```

- API: http://localhost:8000
- Swagger: http://localhost:8000/docs

### 4. Run tests

```bash
cd backend
pytest tests/ -v
```

### 5. Test with a real token

1. Sign up a user in Supabase (or wait for Step 3 frontend)
2. Copy `access_token` from Supabase session
3. Run:

```bash
export ACCESS_TOKEN="eyJ..."
chmod +x scripts/test-api.sh
./scripts/test-api.sh
```

Or via Swagger: **Authorize** → paste `Bearer <token>` (without the word Bearer in some UIs — Swagger adds it).

### 6. Create a project (authenticated)

```bash
curl -X POST http://localhost:8000/api/v1/projects \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"name": "My Brand", "description": "Q2 campaign"}'
```

## Error format

All errors return:

```json
{
  "error": {
    "code": "UNAUTHORIZED",
    "message": "Missing authentication token"
  }
}
```

## What's next

**Step 3 — Authentication (Frontend)**  
Supabase login/signup, session handling, protected routes.

Reply **"step 3"** or **"continue"** when ready.
