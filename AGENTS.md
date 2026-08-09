# AGENTS.md

This repository contains a FastAPI backend and a Vue 3 + PrimeVue frontend for the Kaku CRM console.

## Project layout
- Backend: [backend/](backend/)
  - API routers live in [backend/api/](backend/api/)
  - SQLAlchemy models live in [backend/models/](backend/models/)
  - Pydantic schemas live in [backend/schemas/](backend/schemas/)
  - Business logic lives in [backend/services/](backend/services/)
  - Config and middleware live in [backend/core/](backend/core/) and [backend/middleware/](backend/middleware/)
- Frontend: [frontend/](frontend/)
  - App views live in [frontend/src/views/](frontend/src/views/)
  - API wrappers live in [frontend/src/api/](frontend/src/api/)
  - Auth state lives in [frontend/src/stores/auth.js](frontend/src/stores/auth.js)
  - Routing lives in [frontend/src/router/index.js](frontend/src/router/index.js)

## Working conventions
- Keep backend and frontend changes aligned. If an API route, payload shape, or permission changes, update the matching frontend client module, auth checks, and router metadata.
- Follow the existing architecture: keep FastAPI endpoints thin, place business logic in the service layer, and keep schema validation in the schema layer.
- Prefer the existing Pinia auth store and router guards over introducing a new auth pattern.
- Preserve the role/permission model. Permission keys are used directly in templates via `auth.can(...)` and in route metadata.
- When you need implementation details, read [backend/README.md](backend/README.md) and [frontend/README.md](frontend/README.md) before inventing a new pattern.

## Common commands
- Backend setup:
  - `cd backend && python3 -m venv venv && source venv/bin/activate && pip install -r requirements.txt`
  - `PYTHONPATH=. python3 scripts/seed.py`
  - `uvicorn main:app --reload`
- Frontend setup:
  - `cd frontend && npm install`
  - `npm run dev`

## Notes
- The backend defaults to local SQLite and serves the API at `http://localhost:8000` in development.
- The frontend Vite dev server defaults to `http://localhost:5173` unless the environment changes it.
- The seeded demo accounts are documented in [backend/README.md](backend/README.md).
