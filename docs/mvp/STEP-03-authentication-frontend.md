# Step 3 — Authentication (Frontend)

## Files created / updated

| File | Purpose |
|------|---------|
| `frontend/lib/auth/session.ts` | Server-side `requireUser()`, `getAccessToken()` |
| `frontend/components/auth/auth-provider.tsx` | Client session context + `onAuthStateChange` |
| `frontend/components/auth/auth-guard.tsx` | Loading state while session resolves |
| `frontend/app/auth/callback/route.ts` | OAuth + email confirmation callback |
| `frontend/app/(auth)/layout.tsx` | Shared auth page layout |
| `frontend/app/(auth)/login/page.tsx` | Email + Google sign in |
| `frontend/app/(auth)/signup/page.tsx` | Sign up + email confirmation flow |
| `frontend/app/(auth)/forgot-password/page.tsx` | Password reset |
| `frontend/services/auth.ts` | Auth service (login, signup, OAuth, reset) |
| `frontend/services/user.ts` | Profile API via backend |
| `frontend/services/api-client.ts` | Attaches JWT to all API calls |
| `frontend/lib/supabase/middleware.ts` | Route protection + redirects |
| `frontend/app/(dashboard)/layout.tsx` | Server auth check + AuthProvider |
| `frontend/components/dashboard/sidebar.tsx` | User info + sign out |

## Auth flow

```
/login or /signup
    → Supabase Auth (email or Google)
    → Session stored in HTTP-only cookies (SSR)
    → /auth/callback (OAuth / email links)
    → /dashboard (protected)

API calls
    → apiClient reads session.access_token
    → Authorization: Bearer <jwt>
    → FastAPI validates JWT (Step 2)
```

## Protected routes

Middleware blocks unauthenticated access to `/dashboard/*` and redirects to `/login?next=...`.

Server layout calls `requireUser()` as a second guard.

## How to run

### 1. Configure Supabase Auth

In Supabase Dashboard → **Authentication → URL Configuration**:

| Setting | Value |
|---------|-------|
| Site URL | `http://localhost:3000` |
| Redirect URLs | `http://localhost:3000/auth/callback` |

For Google OAuth (optional): **Authentication → Providers → Google** → enable and add credentials.

To skip email confirmation during dev: **Authentication → Providers → Email** → disable "Confirm email".

### 2. Configure frontend env

```bash
cd frontend
cp .env.example .env.local
```

```env
NEXT_PUBLIC_SUPABASE_URL=https://xxxx.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=eyJ...
NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1
```

### 3. Start backend + frontend

```bash
# Terminal 1 — backend (Step 2)
cd backend && source venv/bin/activate && python run.py

# Terminal 2 — frontend
cd frontend && npm run dev
```

### 4. Test the flow

1. Open http://localhost:3000
2. Click **Get Started** → create account
3. You should land on `/dashboard`
4. Sidebar shows your name and email
5. Visit **Settings** — profile loads from `GET /api/v1/users/me`
6. Sign out → redirected to `/login`
7. Try `/dashboard` while logged out → redirected to `/login`

### 5. Verify API auth end-to-end

After login, open browser DevTools → Application → Cookies, or run in console:

```js
const { createClient } = await import('/lib/supabase/client')
// Or check Network tab: API calls include Authorization header
```

Settings page calling the backend confirms JWT → FastAPI → Supabase profile works.

## Troubleshooting

| Issue | Fix |
|-------|-----|
| Redirect loop | Check Site URL and Redirect URLs in Supabase |
| 401 on Settings | Ensure backend is running and JWT secret matches |
| Email confirmation stuck | Disable confirm email in Supabase for dev |
| Google login fails | Add OAuth redirect URL + enable Google provider |

## What's next

**Step 4 — Dashboard + Create Project**  
Project list UI wired to backend CRUD, empty states, project selection.

Reply **"step 4"** or **"continue"** when ready.
