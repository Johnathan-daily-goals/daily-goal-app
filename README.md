# Daily Goals App

## Quick start

### Backend (FastAPI)

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
uvicorn app:app --reload --port 8000
```

### Frontend (React + Vite)

```bash
cd frontend
npm install
npm run dev
```

Open the app at `http://localhost:5173`.

## API overview

- `GET /api/dashboard`
- `GET /api/projects`
- `POST /api/projects`
- `GET /api/projects/{id}`
- `PATCH /api/projects/{id}`
- `GET /api/projects/{id}/goals`
- `POST /api/projects/{id}/goals`
- `GET /api/projects/{id}/retros`
- `POST /api/projects/{id}/retros`
