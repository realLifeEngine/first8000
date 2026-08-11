# Willook CRM Frontend — Batch 7 Integration

This adds real backend integration on top of the existing Vue 3 +
PrimeVue frontend: Axios API client, Pinia auth store, and router guards
enforcing the same role/permission checks the FastAPI backend enforces
server-side.

## What Changed

- **`src/api/`** — one module per backend router (`auth.js`, `students.js`,
  `school.js`, `oa.js`, `datacenter.js`, `staff.js`, `branches.js`), all
  built on a shared `client.js` Axios instance that attaches the JWT
  access token and silently refreshes it on a 401.
- **`src/stores/auth.js`** — Pinia store holding the access/refresh token
  pair (persisted to `localStorage`) and the resolved user profile +
  effective permissions from `GET /auth/me`. Exposes `auth.can(key)` and
  `auth.hasRoleAtLeast(role)` helpers for template-level UI gating.
- **`src/router/index.js`** — every protected route now declares
  `meta.permission` or `meta.minRole` matching the backend's permission
  keys exactly; a global `beforeEach` guard blocks navigation and
  redirects unauthenticated users to `/login` or under-privileged users
  to `/403`.
- **`src/views/Login.vue`** — real login form calling `POST /auth/login`,
  handling account-lockout (423) and bad-credential (401) responses.
- **`src/views/DashboardLayout.vue`** — shell with logged-in user info and
  logout wired to the auth store.
- **`src/views/frontdesk/MemberList.vue`** — converted from static
  `mockData.js` imports to live `GET/POST/PUT/DELETE /students` calls,
  with create/edit/delete buttons gated behind `student:create/edit/delete`
  permissions as a template for converting the remaining views.
- **`main.js`** — now installs Pinia and calls `auth.bootstrap()` (which
  validates any stored token and loads the profile) before mounting the
  app, so the router guard has permission data on the very first navigation.

## Remaining Work

Five views are now fully converted to live API calls: `MemberList.vue`,
`CourseReview.vue`, `CourseProducts.vue`, `Overview.vue` (work plans +
notices widgets; revenue/attendance charts remain illustrative pending a
Batch 8 reporting endpoint), and `Training.vue`. Apply the same three
changes to each remaining view (~25 files):

1. Replace the `import { ... } from '../../data/mockData'` line with the
   matching function(s) from `src/api/`.
2. Replace `ref([...seedData])` with `ref([])` + an async fetch function
   called on component setup.
3. Wrap create/edit/delete calls in `try/catch`, awaiting the API call,
   and gate the corresponding buttons with `v-if="auth.can('...')"` using
   the permission key from the matching backend router
   (see `backend/README.md`'s route table for the full mapping).

Note: `PageHeader.vue`, `StatusTag.vue`, and `RecordDialog.vue` shared
components referenced by the views were not included in your upload —
carry those over unmodified from your existing `src/components/` folder.

## Setup

```bash
cd frontend
cp .env.example .env   # point VITE_API_BASE_URL at your running backend
npm install
npm run dev
```

Ensure the backend (`../backend`) is running on the URL in `.env` — seed
it first with `PYTHONPATH=. python3 scripts/seed.py` so login has valid
accounts (see backend README for seeded credentials).
