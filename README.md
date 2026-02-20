# Daily Goal App

Set one goal per project per day. That's it.

## Stack

- **Backend** — Flask + PostgreSQL
- **Frontend** — React 19, TypeScript, Tailwind CSS v4, Vite
- **Auth** — access tokens (15 min TTL) + refresh tokens, both stored in the DB

## Setup

**Backend**

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

Create the database and run the schema:

```bash
psql -U daily_user -d daily_goals_db -f create_tables.sql
```

Set env vars (or let the defaults run in dev):

```
ACCESS_TOKEN_SECRET=your-secret
ACCESS_TOKEN_TTL_SECONDS=900
```

**Frontend**

```bash
cd frontend
npm install
```

## Running

```bash
# Backend (port 8000)
make run

# Frontend (port 5173, proxies API calls to backend)
cd frontend && npm run dev
```

## Testing & other commands

```bash
make test       # pytest -q
make testv      # pytest -vv
make lint       # ruff check
make format     # ruff format
make db-psql    # open a psql session
```

## API overview

| Method | Path | Description |
|--------|------|-------------|
| POST | `/auth/register` | Create account |
| POST | `/auth/login` | Get tokens |
| POST | `/auth/refresh` | Refresh access token |
| POST | `/auth/logout` | Revoke tokens |
| GET/POST | `/projects` | List or create projects |
| GET | `/projects/:id` | Get a project |
| DELETE | `/projects/:id` | Archive a project |
| POST | `/projects/:id/archive` | Archive a project |
| POST | `/projects/:id/restore` | Restore an archived project |
| GET | `/projects/archived` | List archived projects |
| GET/POST | `/projects/:id/goals` | List or create goals |
| GET/PUT | `/projects/:id/goals/today` | Get or upsert today's goal |

All routes except `/health` and `/auth/*` require a `Bearer` token.
