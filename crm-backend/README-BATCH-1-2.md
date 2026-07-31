# Qihui CRM Backend — Batches 1–2

This archive contains the first two backend implementation batches.

## Included

- `requirements.txt`: Python runtime dependencies.
- `app/core/config.py`: environment-driven application configuration.
- `app/core/security.py`: password hashing, JWT helpers, four-role RBAC hierarchy, and granular permission catalog.
- `app/core/logging_config.py`: structured application and security-audit logging setup.
- `app/db/session.py`: SQLAlchemy 2.0 asynchronous database engine/session setup.
- `app/models/`: branch, staff/RBAC, student, academic, OA, and finance models.

## Role boundaries

| Role | Scope |
|---|---|
| `superuser` | Global; creates/manages branches and all staff/data |
| `school_admin` | Full access within their assigned branch; assigns granular staff permissions |
| `manager` | Medium branch-scoped operational access |
| `teacher` | Minimum teaching-related access |

## Important

This is a source-only checkpoint. Batches 3+ will add schemas, seed data, authorization dependencies, anti-bot/rate-limit middleware, routes, app startup, Docker deployment, and frontend API integration.

SQLite is configured for mock/development. Production should use `postgresql+asyncpg` plus Alembic migrations and a Redis service.
