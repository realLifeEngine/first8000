# Kaku CRM API

FastAPI backend for the "启慧教育" (Kaku Education) CRM console — powers the
Vue 3 + PrimeVue frontend, replacing its static mock data with a real,
authenticated, role-scoped API.

## Architecture

FastAPI (async) + SQLAlchemy 2.0 async ORM + SQLite for dev (swappable to
Postgres via `DATABASE_URL`) + JWT access/refresh tokens + 4-tier RBAC +
granular permission grants + Redis-backed sliding-window rate limiting +
slowapi + a defensive middleware stack (honeypot, security headers,
request ID tracing).

```
core/        settings, JWT + password hashing, RBAC/permission enums, logging
db/          async SQLAlchemy engine/session factory
models/      SQLAlchemy ORM models (21 tables across 4 domains)
schemas/     Pydantic request/response contracts
services/    business logic (auth, permission resolution, generic CRUD)
middleware/  rate limiting, honeypot, security headers, request ID
api/         FastAPI routers (auth, branches, staff, students, school, oa, data)
scripts/     seed.py — ports the frontend's mockData.js into real seeded rows
```

## Role Hierarchy

`teacher` → `manager` → `school_admin` → `superuser`, with 29 granular
permission keys that `school_admin`/`superuser` can grant or revoke per
staff member on top of role defaults (see `core/security.py`).

## Domains

| Module | Routes | Models |
|---|---|---|
| Front desk | `/api/v1/students` | `Student` |
| Academic affairs | `/api/v1/school/*` | `SchoolClass`, `CourseProduct`, `CourseRecord` |
| Office/OA | `/api/v1/oa/*` | 12 models (notices, plans, reports, contacts, leave, property, wages, KB, training, docs, messages, logs) |
| Data center | `/api/v1/data/*` | `CampusRevenue`, `BonusRecord` + computed ranking/summary endpoints |
| Auth/Staff | `/api/v1/auth/*`, `/api/v1/staff/*`, `/api/v1/branches/*` | `User`, `StaffPermission`, `Branch` |

## Getting Started (local dev)

```bash
cp .env.example .env
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt

# seed the database with mock data ported from the frontend
PYTHONPATH=. python3 scripts/seed.py

# run the dev server
uvicorn main:app --reload
```

API docs available at `http://localhost:8000/docs` (disabled automatically
in `APP_ENV=prod`).

### Seeded accounts

| Username | Password | Role |
|---|---|---|
| `admin` | `admin123` | superuser |
| `musajiang` | `teacher123` | manager |
| (7 more teacher accounts) | `teacher123` | teacher |

## Docker

```bash
docker compose up --build
```

Runs the API alongside a Redis container for rate limiting. Swap
`DATABASE_URL` to a Postgres DSN and uncomment the `postgres` service in
`docker-compose.yml` for staging/production.

## Security Notes

- Passwords are hashed with bcrypt (`passlib`); pin `bcrypt<4.1.0` — newer
  bcrypt builds break passlib's backend detection.
- Account lockout: 5 failed logins locks the account for 15 minutes.
- Rate limiting falls back to in-memory storage if Redis is unreachable —
  fine for dev, but **always run with Redis reachable in production** so
  limits are shared across worker processes.
- `APP_ENV=dev` auto-creates tables from ORM metadata on startup; use
  Alembic migrations for staging/prod instead.

## Frontend Integration (Batch 7 — pending)

The existing Vue frontend (`../frontend`) currently reads from a static
`src/data/mockData.js`. The next step replaces those imports with an Axios
client calling this API, a Pinia auth store holding the JWT pair, and
Vue Router navigation guards enforcing the same role/permission checks
this API enforces server-side.
