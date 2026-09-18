# SlotLock API

SlotLock is a personal portfolio project by [Jhonatan Casale](https://github.com/jhonatancasale),
building toward a production-oriented FastAPI reservation backend. The project
will explore concurrency, idempotency, caching, integrations, testing, and
reliable backend architecture. It is currently in its first, early milestone.

Current milestone: M0 — project skeleton and engineering foundation.

## Current scope

The API exposes `GET /health`, which returns `200 OK` and
`{"status": "ok"}`. This is a liveness check: the application can serve HTTP.
It does not check PostgreSQL. Database integration starts in M1; authentication,
reservations, and the other backend capabilities are planned for later milestones.

## Requirements

- Git
- Python 3.13
- Poetry 2.4.3 (the version used in CI)
- Docker with Docker Compose

Install Poetry using its [official instructions](https://python-poetry.org/docs/#installation).
On Windows, run the commands in WSL with Python, Poetry, and Docker available
inside the same distribution, or install all prerequisites for native Windows.
Start your Docker engine before running the infrastructure commands.

## Installation

```bash
git clone https://github.com/jhonatancasale/slotlock-api.git
cd slotlock-api
poetry env use 3.13
poetry install
```

The committed `poetry.lock` records the resolved dependency versions.

## Start infrastructure

```bash
docker compose up -d
docker compose ps
```

Wait until `postgres` reports `healthy`. For a command that waits for readiness,
use `docker compose up -d --wait`.

PostgreSQL 18 is available at `127.0.0.1:5432`, with database, username, and
password all set to `slotlock`. These credentials are for local development only.
The `postgres_data` named volume persists database data between restarts.
The API does not connect to this database in M0.

If startup reports that port 5432 is occupied, stop the conflicting local
service or change the host port in `compose.yml`.

## Start the API

```bash
poetry run task run
```

The development server runs at <http://127.0.0.1:8000> with automatic reload.
Interactive API documentation is available at <http://127.0.0.1:8000/docs>.

In another terminal:

```bash
curl http://127.0.0.1:8000/health
```

Use `curl.exe` in Windows PowerShell. Expected response: HTTP `200`, content type
`application/json`, and:

```json
{"status": "ok"}
```

## Quality commands

```bash
poetry run task lint
poetry run task test
poetry run task format
```

Tests run lint first, verify the health response, and generate a coverage report
at `htmlcov/index.html`. The format task applies Ruff fixes and formatting.
CI installs dependencies, checks lint and formatting, and runs tests on pushes
to `main` and pull requests targeting `main`. CI does not need PostgreSQL in M0.

## Stop local services

Stop the API with `Ctrl+C`, then stop PostgreSQL:

```bash
docker compose down
```

The database volume is retained.

## Roadmap

- M0 — Skeleton
- M1 — Persistence
- M2 — Real API
- M3 — Backend Depth
- M4 — Performance & Integration
- M5 — Production Polish

The acceptance criteria are in the [M0 specification](docs/specs/m0%20-%20spec.md).
The tooling follows the [FastAPI do Zero reference](https://fastapidozero.dunossauro.com/4.0/01/).
