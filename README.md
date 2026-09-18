# SlotLock API

SlotLock is a personal portfolio project by [Jhonatan Casale](https://github.com/jhonatancasale),
building a production-oriented FastAPI reservation backend. It explores reliable
persistence, concurrency, idempotency, testing, and backend architecture.

Current milestone: M1 — Persistence (complete).

## Current scope

SlotLock uses async SQLAlchemy and asyncpg with PostgreSQL, Alembic migrations,
and a persisted `Resource` model (UUID, name, optional description, active flag,
and timezone-aware timestamps). Resource HTTP endpoints belong to M2.
Authentication and reservation behavior are planned for later milestones.

- `GET /health` returns `200` and `{"status":"ok"}` without querying PostgreSQL.
- `GET /ready` executes `SELECT 1` through an async session. It returns `200`
  and `{"status":"ready"}`, or `503` and `{"detail":"Database unavailable"}`.
  Readiness checks connectivity; migrations are a separate deployment step.

## Requirements

- Git
- Python 3.13
- Poetry 2.4.3 (the version used in CI)
- Docker with Docker Compose

Install Poetry using its [official instructions](https://python-poetry.org/docs/#installation).
On Windows, use WSL with these tools installed in the same distribution, or
install the prerequisites for native Windows. Start Docker before Compose.

## Installation and configuration

```bash
git clone https://github.com/jhonatancasale/slotlock-api.git
cd slotlock-api
cp .env.example .env
poetry env use 3.13
poetry install
```

The committed `poetry.lock` records resolved versions. Settings load from `.env`
and environment variables; environment variables take precedence. `.env` is
ignored by Git. Both URLs must use `postgresql+asyncpg`.

- `DATABASE_URL`: development database `slotlock` on `127.0.0.1:5432`.
- `TEST_DATABASE_URL`: dedicated `slotlock_test` database on `127.0.0.1:5433`.

The example credentials are for local development only. Tests never fall back
to `DATABASE_URL`; missing test configuration fails clearly. The test safety
guard requires the database name `slotlock_test`. Keep the URLs separate locally.

## Start databases

```bash
docker compose up -d --wait postgres
docker compose --profile test up -d --wait postgres-test
docker compose --profile test ps
```

PostgreSQL 18 uses a persistent named volume for development. The test service
uses separate disposable storage; stopping it discards its database contents.
If ports 5432 or 5433 are occupied, change the corresponding Compose host port
and `.env` URL together.

## Migrations

Apply schema changes to `DATABASE_URL` before using persistence:

```bash
poetry run alembic upgrade head
poetry run alembic current
poetry run alembic check
```

`current` should report `b287932560d1 (head)`. `check` verifies that ORM metadata
matches the migrated schema. Alembic owns schema creation; the application does
not create tables on startup.

For future model changes, generate a migration and review it before applying:

```bash
poetry run alembic revision --autogenerate -m "describe schema change"
```

On an **empty or disposable database only**, test rollback with
`poetry run alembic downgrade base`, followed by `poetry run alembic upgrade head`
and `poetry run alembic check`. The initial downgrade drops `resources` and its data.

## Start the API

```bash
poetry run task run
```

The development server runs at <http://127.0.0.1:8000> with automatic reload.
Interactive API documentation is at <http://127.0.0.1:8000/docs>.

In another terminal:

```bash
curl -i http://127.0.0.1:8000/health
curl -i http://127.0.0.1:8000/ready
```

Use `curl.exe` in Windows PowerShell. With PostgreSQL available, both return
HTTP `200` and their documented JSON bodies. With PostgreSQL unavailable,
`/health` stays `200` while `/ready` returns `503`.

## Quality commands

Start the test database and configure `TEST_DATABASE_URL` before running tests.

```bash
poetry run task lint
poetry run ruff format --check .
poetry run task test
poetry run task format
```

Tests run lint first, migrate the guarded test database to head, and exercise
persistence and readiness against real PostgreSQL. Each persistence test uses
an outer transaction and session savepoints; even explicit session commits are
rolled back after the test. Tests do not use SQLite or `create_all()`.
Coverage HTML is written to `htmlcov/index.html`. The format task applies fixes.

CI provisions a disposable PostgreSQL database and runs installation, lint,
format checking, migrations, drift checking, and tests for pushes to `main` and
pull requests targeting `main`. Both database URLs may refer to that same
CI-only test database.

## Stop local services

Stop the API with `Ctrl+C`, then:

```bash
docker compose --profile test down
```

Development data is retained in its named volume. Test data is disposable.

## Roadmap

- M0 — Skeleton (complete)
- M1 — Persistence (complete)
- M2 — Real API
- M3 — Backend Depth
- M4 — Performance & Integration
- M5 — Production Polish

Acceptance criteria and verification records:
[M0 specification](docs/specs/m0%20-%20spec.md),
[M1 specification](docs/specs/m1%20-%20spec.md).
