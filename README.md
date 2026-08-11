# DIY CRM

DIY CRM is a full-stack customer relationship management console for Willook Education, built with a FastAPI backend and a Vue 3 + PrimeVue frontend.

## Project structure

- Backend: [backend/](backend/)
  - API routes and dependency wiring live under [backend/api](backend/api)
  - SQLAlchemy models and schemas live under [backend/models](backend/models) and [backend/schemas](backend/schemas)
  - Business logic and auth helpers live under [backend/services](backend/services) and [backend/core](backend/core)
- Frontend: [frontend/](frontend/)
  - UI views live under [frontend/src/views](frontend/src/views)
  - API wrappers live under [frontend/src/api](frontend/src/api)
  - Auth state and routing live under [frontend/src/stores](frontend/src/stores) and [frontend/src/router](frontend/src/router)

## Quick start

### Backend

```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
PYTHONPATH=. python3 scripts/seed.py
uvicorn main:app --reload
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

## Documentation

- Backend details: [backend/README.md](backend/README.md)
- Frontend details: [frontend/README.md](frontend/README.md)
- Repository conventions: [AGENTS.md](AGENTS.md)

## Notes

- The backend defaults to local SQLite and serves the API at http://localhost:8000 in development.
- The frontend Vite dev server defaults to http://localhost:5173 unless the environment changes it.
