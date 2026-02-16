# Daily Goal App – Backend Architecture

## Goals
- Simple, readable Flask API with Postgres.
- Clear separation of concerns: HTTP layer vs DB layer vs domain errors.
- Stable contract for the frontend: consistent JSON responses + status codes.
- Auth + multi-tenant data isolation (every project/goal belongs to a user).

---

## High-level components
- **Flask app (`backend/app/main.py`)**
  - Defines routes + HTTP semantics (status codes, request parsing, response shaping).
  - Sets request-scoped resources on `flask.g` (db connection, user id).
  - Contains global error handlers to convert domain errors into JSON responses.

- **Database connection (`backend/app/database.py`)**
  - Owns connection creation using env vars.
  - Provides a Postgres connection with dict-like rows via `RealDictCursor`.

- **CRUD / persistence (`backend/app/crud.py`)**
  - All SQL lives here.
  - Returns plain dicts / primitives (no Flask response objects).
  - Accepts `user_id` explicitly for authorization scoping.
  - Raises domain errors for expected business/constraint failures.

- **Domain errors (`backend/app/errors.py`)**
  - Defines `AppError` (base) with `status_code` and `detail`.
  - Specific errors (e.g., `Unauthorized`, `ProjectNotFound`, `DailyGoalAlreadyExists`)
    represent expected failure cases and map to HTTP statuses.

- **Migrations (`backend/migrations/*.sql`)**
  - Forward-only SQL scripts applied in numeric order.
  - Each migration is idempotent where practical (or safe to re-run).
  - Schema changes are never done by editing old migrations once applied to shared DBs.

---

## Request lifecycle
1. `before_request: open_db_connection`
   - Creates `g.db_conn`.
2. `before_request: authenticate_request`
   - Requires `Authorization: Bearer <token>` (except `/health`).
   - Looks up user by token; sets `g.user_id`.
3. Route handler runs
   - Uses `crud.*(g.db_conn, g.user_id, ...)` for all user-scoped reads/writes.
4. `teardown_request: close_db_connection`
   - Commits if no exception; rolls back on exception; always closes connection.

---

## API design conventions
- **JSON only**: request/response bodies are JSON.
- **Error shape**: `{"error": "<human readable message>"}`
- **Status codes**:
  - `200` OK (read / update success)
  - `201` Created (new resource created)
  - `401` Unauthorized (missing/invalid auth)
  - `404` Not Found (resource does not exist or does not belong to user)
  - `409` Conflict (unique constraint / business rule conflict)
  - `500` Internal Server Error (unexpected)

---

## Data ownership rules (multi-tenant isolation)
- Every **project** has `user_id NOT NULL`.
- Every **daily_goal** has `user_id NOT NULL` and references `projects(id)`.
- All queries must scope by `user_id`:
  - Projects: `WHERE user_id = %s`
  - Goals: `WHERE user_id = %s AND project_id = %s`
- For any `project_id` provided by the client:
  - Treat “doesn’t exist” and “belongs to another user” the same: return `404`.

---

## Business rules
- One daily goal per project per day:
  - Enforced by unique index on `(user_id, project_id, date(created_at))`.
  - Implemented via:
    - `POST /projects/<id>/goals` → returns `409` if already exists for today.
    - `PUT /projects/<id>/goals/today` → upsert (create or update).

- Soft-delete projects:
  - `archived_at` indicates archived.
  - “Delete” endpoint archives (does not remove rows).

---

## Authentication model (current)
- Token-based auth with bearer tokens stored in `users.token`.
- Requests require `Authorization: Bearer <token>`.
- `g.user_id` is the source of truth for the current request.

### Planned improvements
- Add `users.password_hash` (bcrypt/argon2).
- Implement `/auth/register` and `/auth/login`.
- Token rotation:
  - On login: issue new token and invalidate old one.
  - On logout: invalidate current token.

---

## SQL conventions
- Always parameterized queries (`%s`, tuple params).
- Prefer returning `RealDictCursor` rows for JSON serialization.
- CRUD closes cursors in all cases.

---

## Refactor threshold (when we do it)
When auth endpoints are implemented (register/login + rotation), we refactor into:
- `backend/app/routes/*.py` (Blueprints)
- `backend/app/auth.py` (auth middleware / helpers)
- `backend/app/services/*.py` (non-trivial business logic)
- Keep `crud.py` strictly SQL/persistence.

---

## Testing strategy (next)
- Add `pytest` with a test DB.
- Smoke tests for:
  - Auth required on protected routes.
  - User isolation (cannot read another user’s projects/goals).
  - Unique-per-day constraint (409 on POST, upsert works on PUT).
  - Archive/restore behavior.