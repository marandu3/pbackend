# Portfolio API

FastAPI backend for a personal portfolio site: profile, education, skills, projects and timeline
content, served over a JWT-authenticated REST API backed by MongoDB.

## Features

- Public read access to all portfolio content (profile, education, skills, projects, timeline)
- JWT-authenticated admin CRUD for every resource, addressed by stable MongoDB ids
- Bootstrap-only registration — the first `/register` call creates the one admin account,
  every call after that returns `403`. There is no open sign-up.
- Project slugs, generated from the title and stable across later edits, for clean public URLs
  (`/projects/{slug}`)
- Per-IP rate limiting on `/login` and `/register`
- Centralized, validated configuration (`core/config.py`); the app refuses to start with a
  missing `DATABASE_URL` or `SECRET_KEY` instead of failing confusingly later
- `GET /health/db` for deployment diagnostics

## Architecture

```text
main.py            FastAPI app: CORS, rate limiting, global error handling, startup
                    (Mongo connectivity check, index creation, one-time data migrations),
                    router registration, health endpoints
core/
  config.py         Typed settings (pydantic-settings), loaded once from the environment
  limiter.py        Shared slowapi Limiter instance
  object_id.py      Path-param -> Mongo ObjectId helper (400 on malformed id, not 500)
  slugify.py        Title -> URL slug, with collision-safe suffixing
database/
  config.py         Mongo client + collection handles
model/              Pydantic request/response schemas, one file per resource
routes/             FastAPI routers, one file per resource - talk to MongoDB directly,
                    no repository/service layer (not justified at this size)
tests/              pytest suite against mongomock (no real database needed to run it)
```

Routes call PyMongo directly rather than going through a service/repository layer. That's a
deliberate choice, not an oversight — introducing those layers wouldn't pay for itself at this
size and would just be extra indirection to read through.

## Tech stack

Python 3.12 · FastAPI · Uvicorn · PyMongo (sync) · Pydantic v2 · pydantic-settings ·
python-jose (JWT) · pwdlib/Argon2 (password hashing) · slowapi (rate limiting) · pytest + mongomock

## Local development

```bash
python -m venv .venv
.venv\Scripts\activate            # Windows; use `source .venv/bin/activate` on macOS/Linux
pip install -r requirement.txt
cp .env.example .env              # then fill in DATABASE_URL at minimum
python main.py                    # serves on http://localhost:8080
```

Interactive API docs: `http://localhost:8080/docs`

### Bootstrapping the admin account

With the server running and no user yet in the database:

```bash
curl -X POST http://localhost:8080/register \
  -H "Content-Type: application/json" \
  -d '{"username": "your-username", "password": "at-least-8-characters"}'
```

Any further call to `/register` returns `403` — there is no way to create a second account
through the API by design. To reset access, delete the one document in the `user` collection
and register again.

## Environment variables

See `.env.example`. `.env` is git-ignored and must never be committed.

| Variable | Required | Notes |
|---|---|---|
| `DATABASE_URL` | Yes | MongoDB connection string. App raises a clear error at startup if unset. |
| `SECRET_KEY` | Yes | Signs JWTs. Use a long random string; rotating it invalidates existing tokens. |
| `ALGORITHM` | No (default `HS256`) | JWT signing algorithm. |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | No (default `60`) | Login session length. |
| `ENVIRONMENT` | No (default `development`) | `development` or `production`. |
| `ALLOWED_ORIGINS` | No (default `http://localhost:4200`) | Comma-separated frontend origins allowed by CORS. **Must** list your real deployed frontend URL in production — never `*`. |

## Database setup

Any MongoDB instance works — a local `mongod`, or a free MongoDB Atlas cluster. Point
`DATABASE_URL` at it. On startup the app:

1. Pings the database and logs whether it connected.
2. Creates a unique index on `user.username`.
3. Runs two one-time, idempotent migrations: carrying forward a profile document saved under the
   old scheme, and backfilling `slug` on any project saved before that field existed. Both are
   no-ops on a fresh database.

No manual migration step is required.

## Running tests

```bash
pip install -r requirement.txt -r requirement-dev.txt
pytest
```

The suite runs against `mongomock` — an in-memory MongoDB stand-in — so it needs no real
database and won't touch your actual data. 50 tests cover authentication (bootstrap
registration, login, token/role validation), the profile singleton upsert, full CRUD for every
resource (including the id-stability and slug-stability regressions this API specifically
guards against), and access control on every mutating endpoint.

## Deployment

Deployed on Render as a standard Python web service. Whatever platform you use:

- Set every variable from the table above as real environment variables (not `.env` — that
  file is for local development only).
- `ALLOWED_ORIGINS` must be your actual frontend domain(s), comma-separated if more than one.
- `ENVIRONMENT=production`.
- Health check: `GET /` (liveness) or `GET /health/db` (checks Mongo connectivity too).

## Security notes

- Passwords are hashed with Argon2 (`pwdlib`), never stored in plaintext.
- Registration is bootstrap-only (see above) — there is no open sign-up endpoint.
- Every mutating endpoint requires a valid bearer token *and* an admin role, checked
  server-side; the frontend's route guards are UX only, not the actual security boundary.
- CORS is an explicit allowlist, not `*`.
- `/login` and `/register` are rate-limited per IP.
- Unhandled exceptions return a generic `500` — no stack traces are ever sent to the client.
