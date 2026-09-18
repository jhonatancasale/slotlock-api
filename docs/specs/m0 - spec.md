# SlotLock API — M0 Specification

> **Milestone:** M0 — Skeleton  
> **Status:** Ready for implementation  
> **Goal:** Turn the repository into a small, reproducible, tested FastAPI project with PostgreSQL available locally and CI green.
>
> **Reference implementation:** [FastAPI do Zero — Aula 01: Configurando o ambiente de desenvolvimento](https://fastapidozero.dunossauro.com/4.0/01/)

---

## 1. Purpose

M0 exists to prove one thing:

> A developer can clone `slotlock-api`, install its dependencies, start the local infrastructure, run the API, call `GET /health`, run the quality gates, and obtain a green result without private knowledge of the project.

M0 is **not** a business-feature milestone.

At the end of M0, SlotLock does not need users, authentication, resources, reservations, persistence, caching, or domain logic.

It only needs a trustworthy engineering foundation.

---

## 2. Milestone outcome

M0 is complete when all of the following are true:

- The repository exists on GitHub and is public.
- The project is managed with Poetry.
- FastAPI starts locally.
- `GET /health` returns HTTP `200`.
- The health endpoint has an automated test.
- Ruff is configured and passes.
- pytest is configured and passes.
- Taskipy exposes the common development commands.
- PostgreSQL can be started with Docker Compose and reports healthy.
- GitHub Actions runs the quality gates on push and pull request.
- The README contains enough instructions for a clean local setup.
- A fresh-clone verification has been performed.
- CI is green on the default branch.

---

## 3. Technical baseline

### Runtime

Use:

- Python **3.13**
- FastAPI
- Poetry

Python 3.13 is intentionally conservative for this repository: modern enough for the project while staying close to the chosen FastAPI do Zero reference material.

### Development tools

Use:

- pytest
- pytest-cov
- Ruff
- Taskipy
- httpx

### Local infrastructure

Use:

- Docker
- Docker Compose
- PostgreSQL

PostgreSQL exists in M0 only as **available local infrastructure**.

The application does **not** need to connect to it yet.

Database integration belongs to M1.

### CI

Use:

- GitHub Actions

M0 CI must run at least:

1. dependency installation
2. lint
3. tests

A Docker image build is **not required in M0** unless it can be added without delaying the milestone.

---

## 4. Explicit non-goals

Do **not** implement any of the following during M0:

- SQLAlchemy
- Alembic migrations
- database repositories
- database models
- authentication
- JWT
- users
- resources
- reservations
- Redis
- caching
- idempotency
- audit events
- webhooks
- external integrations
- background jobs
- retry policies
- domain/application/infrastructure layering
- Kubernetes
- Terraform
- AWS deployment
- Kafka
- Airflow
- AI/LLM functionality

If an implementation decision is not necessary to satisfy an M0 acceptance criterion, defer it.

---

## 5. Repository name

```text
slotlock-api
```

Suggested GitHub description:

```text
Production-oriented FastAPI backend demonstrating reliable API design,
transaction-safe workflows, testing, observability, and pragmatic architecture.
```

Do not spend time optimizing the repository description during M0.

---

## 6. Initial repository structure

Keep the first structure deliberately small:

```text
slotlock-api/
├── slotlock/
│   ├── __init__.py
│   └── app.py
├── tests/
│   ├── __init__.py
│   └── test_app.py
├── .github/
│   └── workflows/
│       └── ci.yml
├── .gitignore
├── compose.yml
├── pyproject.toml
├── poetry.lock
├── README.md
└── spec.md
```

Do **not** create the future `domain/`, `application/`, or `infrastructure/` package hierarchy yet.

Create those boundaries when actual code gives us a reason to create them.

---

## 7. Implementation sequence

Follow this order.

The sequence is part of the specification because it minimizes wandering.

### Step 1 — Create the project

Create the project with Poetry.

Suggested starting point:

```bash
poetry new --flat slotlock
cd slotlock
```

If the Git repository directory is already named `slotlock-api`, initialize the Python package inside the existing repository instead of creating unnecessary nested directories.

The desired Python package name is:

```text
slotlock
```

The GitHub repository name is:

```text
slotlock-api
```

These do not need to be identical.

Set the project Python requirement to:

```toml
requires-python = ">=3.13,<3.14"
```

Verify:

```bash
poetry env use 3.13
poetry install
```

### Step 2 — Install FastAPI

Install FastAPI using the standard dependency bundle:

```bash
poetry add "fastapi[standard]"
```

Create:

```text
slotlock/app.py
```

The application must expose a FastAPI instance named:

```python
app
```

### Step 3 — Implement `/health`

Implement:

```http
GET /health
```

Required response:

```http
200 OK
Content-Type: application/json
```

Required JSON body:

```json
{
  "status": "ok"
}
```

No database check belongs here.

No Redis check belongs here.

This endpoint means:

> The application process is alive and able to serve HTTP.

A future `/ready` endpoint will represent dependency readiness.

### Step 4 — Install development tooling

Install:

```bash
poetry add --group dev pytest pytest-cov taskipy ruff httpx
```

Configure Ruff, pytest, and Taskipy inside `pyproject.toml`.

Use FastAPI do Zero as the baseline for these configurations.

Suggested Ruff baseline:

```toml
[tool.ruff]
line-length = 79

[tool.ruff.lint]
preview = true
select = ["I", "F", "E", "W", "PL", "PT"]

[tool.ruff.format]
preview = true
quote-style = "single"
```

Suggested pytest baseline:

```toml
[tool.pytest.ini_options]
pythonpath = "."
addopts = "-p no:warnings"
```

Suggested Taskipy baseline:

```toml
[tool.taskipy.tasks]
lint = "ruff check"
pre_format = "ruff check --fix"
format = "ruff format"
run = "fastapi dev slotlock/app.py"
pre_test = "task lint"
test = "pytest -s -x --cov=slotlock -vv"
post_test = "coverage html"
```

Exact package versions should be resolved by Poetry at implementation time.

Do not manually copy old pinned versions from tutorial material unless required for compatibility.

### Step 5 — Test `/health`

Use FastAPI's `TestClient`.

The test must verify both:

1. HTTP status code
2. response body

Minimum behavior:

```text
GET /health
→ 200
→ {"status": "ok"}
```

The test name should describe the behavior rather than the implementation.

Example:

```python
def test_health_returns_ok(): ...
```

The test must pass with:

```bash
poetry run task test
```

### Step 6 — Add PostgreSQL with Docker Compose

Create:

```text
compose.yml
```

It must define one PostgreSQL service.

Requirements:

- official PostgreSQL image
- explicit database name
- explicit development username
- explicit development password
- persistent named volume
- exposed local port
- health check

Development-only credentials are acceptable in M0.

Do not place production credentials in the repository.

Suggested environment names:

```text
POSTGRES_DB=slotlock
POSTGRES_USER=slotlock
POSTGRES_PASSWORD=slotlock
```

The service must become healthy after:

```bash
docker compose up -d
```

Verification:

```bash
docker compose ps
```

Expected outcome:

```text
postgres ... healthy
```

The FastAPI application does **not** need to use PostgreSQL yet.

### Step 7 — Add Git repository hygiene

The repository must ignore at least:

```text
__pycache__/
*.py[cod]
.pytest_cache/
.ruff_cache/
.coverage
htmlcov/
.env
.venv/
dist/
build/
*.egg-info/
.idea/
.vscode/
```

Editor-specific entries may be adjusted according to personal use.

Do not commit:

- `.env`
- local virtual environments
- coverage output
- IDE state
- secrets

### Step 8 — Add GitHub Actions CI

Create:

```text
.github/workflows/ci.yml
```

Trigger CI on:

- pushes to the default branch
- pull requests targeting the default branch

CI must:

1. check out the repository
2. install Python 3.13
3. install Poetry
4. install project dependencies
5. run lint
6. run tests

Equivalent implementations are acceptable.

Required logical gates:

```text
lint -> green
tests -> green
```

PostgreSQL is not required in CI during M0 because no application behavior depends on it yet.

Do not add a CI database service merely because one will be needed later.

### Step 9 — Write the M0 README

The README is not marketing copy yet.

It is an onboarding contract.

It must contain:

#### Project name

```text
SlotLock API
```

#### One-paragraph description

Explain that SlotLock will become a production-oriented FastAPI reservation backend designed to explore concurrency, idempotency, caching, integrations, testing, and reliable backend architecture.

State clearly that the project is currently in an early milestone.

#### Requirements

List:

- Python 3.13
- Poetry
- Docker / Docker Compose

#### Installation

Document the exact working commands.

For example:

```bash
git clone <repository-url>
cd slotlock-api
poetry install
```

#### Start infrastructure

```bash
docker compose up -d
```

#### Start API

```bash
poetry run task run
```

#### Health check

Document:

```http
GET /health
```

and expected response:

```json
{"status": "ok"}
```

#### Quality commands

```bash
poetry run task lint
poetry run task test
poetry run task format
```

#### Current scope

Say explicitly:

```text
Current milestone: M0 — project skeleton and engineering foundation.
```

#### Roadmap

Keep this extremely short:

```text
M0 — Skeleton
M1 — Persistence
M2 — Real API
M3 — Backend Depth
M4 — Performance & Integration
M5 — Production Polish
```

Do not document speculative implementation details for every future milestone in the README yet.

---

## 8. Command contract

By the end of M0, these commands must work.

### Install

```bash
poetry install
```

### Start PostgreSQL

```bash
docker compose up -d
```

### Inspect infrastructure

```bash
docker compose ps
```

### Start API

```bash
poetry run task run
```

### Lint

```bash
poetry run task lint
```

### Format

```bash
poetry run task format
```

### Test

```bash
poetry run task test
```

### Stop infrastructure

```bash
docker compose down
```

No contributor should need to memorize internal Python commands when a Taskipy task exists for that operation.

---

## 9. Acceptance criteria

### AC-01 — Installation

Given a clean checkout and Python 3.13,

when:

```bash
poetry install
```

is executed,

then dependency installation completes successfully.

### AC-02 — API starts

Given dependencies are installed,

when:

```bash
poetry run task run
```

is executed,

then FastAPI starts without an application error.

### AC-03 — Health endpoint

Given the API is running,

when:

```http
GET /health
```

is requested,

then the API returns:

```http
200 OK
```

with:

```json
{
  "status": "ok"
}
```

### AC-04 — Health test

Given the project dependencies are installed,

when:

```bash
poetry run task test
```

is executed,

then the automated health endpoint test passes.

### AC-05 — Lint

Given the repository code,

when:

```bash
poetry run task lint
```

is executed,

then Ruff exits successfully with no unresolved violations.

### AC-06 — PostgreSQL infrastructure

Given Docker is available,

when:

```bash
docker compose up -d
```

is executed,

then the PostgreSQL service starts and eventually reports healthy.

### AC-07 — CI

Given code is pushed to GitHub,

when the CI workflow runs,

then:

```text
dependency installation -> green
lint                    -> green
tests                   -> green
```

### AC-08 — Documentation

Given a developer with the documented prerequisites,

when they follow only the README,

then they can:

- install dependencies
- start PostgreSQL
- start FastAPI
- call `/health`
- run lint
- run tests

without additional instructions.

---

## 10. Fresh-clone verification

Do this **before declaring M0 complete**.

Do not trust the development directory that was used to build the project.

Use a temporary directory.

Example:

```bash
cd /tmp
git clone <repository-url> slotlock-m0-verification
cd slotlock-m0-verification

poetry install
docker compose up -d
poetry run task lint
poetry run task test
poetry run task run
```

From another terminal:

```bash
curl http://127.0.0.1:8000/health
```

Expected:

```json
{"status":"ok"}
```

Then:

```bash
docker compose down
```

Delete the temporary clone after verification.

---

## 11. Recommended commit sequence

Prefer small commits that tell the construction story.

Suggested sequence:

```text
chore: initialize Python project
feat: add health endpoint
test: cover health endpoint
chore: configure development tooling
chore: add PostgreSQL development service
ci: add lint and test workflow
docs: document local development setup
```

Do not contort the work merely to match these exact commits.

The goal is readable history, not ceremonial commit choreography.

---

## 12. M0 Definition of Done

M0 is **DONE** only when all checkboxes below are true:

- [ ] Public `slotlock-api` GitHub repository exists.
- [ ] Python 3.13 project is managed by Poetry.
- [ ] `poetry install` succeeds.
- [ ] FastAPI application starts.
- [ ] `GET /health` returns `200`.
- [ ] `/health` returns `{"status": "ok"}`.
- [ ] Automated test covers the health endpoint.
- [ ] `poetry run task lint` passes.
- [ ] `poetry run task test` passes.
- [ ] `poetry run task format` exists and works.
- [ ] PostgreSQL starts through Docker Compose.
- [ ] PostgreSQL reports healthy.
- [ ] `.gitignore` excludes local/generated/sensitive files.
- [ ] GitHub Actions runs on pushes and pull requests.
- [ ] GitHub Actions lint gate is green.
- [ ] GitHub Actions test gate is green.
- [ ] README contains reproducible setup instructions.
- [ ] Fresh-clone verification succeeds.
- [ ] Default branch is green.

---

## 13. Hard stop

Once the Definition of Done is satisfied:

> **Stop implementing features. Commit, push, mark M0 complete, and move to M1 deliberately.**

Do not use leftover energy to sneak authentication, SQLAlchemy, reservation models, Redis, or architecture abstractions into M0.

The purpose of this milestone is to create momentum and a trustworthy foundation.

Shipping M0 is more valuable than beginning M1 early.

---

## 14. References

Primary implementation/reference backbone:

- [FastAPI do Zero — Aula 01: Configurando o ambiente de desenvolvimento](https://fastapidozero.dunossauro.com/4.0/01/)

The FastAPI do Zero course introduces Docker/PostgreSQL and CI later in its sequence. M0 intentionally pulls only the minimal local PostgreSQL service and the minimal CI quality gates forward because both are required by this milestone.

The course is a **reference**, not a requirement to copy its domain or architecture. SlotLock decisions should remain driven by SlotLock's milestone requirements.
