# SlotLock API — M1 Specification

> **Milestone:** M1 — Persistence
> **Status:** Implemented — CI and fresh verification pending
> **Depends on:** M0 — Skeleton
> **Goal:** Connect SlotLock to PostgreSQL through an asynchronous SQLAlchemy persistence layer, manage schema evolution with Alembic, persist the first real domain entity, and prove the stack with integration tests against PostgreSQL.

## References

- FastAPI do Zero — Database and Alembic: https://fastapidozero.dunossauro.com/4.0/04/
- FastAPI do Zero — Database integration: https://fastapidozero.dunossauro.com/4.0/05/
- FastAPI do Zero — Async project: https://fastapidozero.dunossauro.com/4.0/08/
- SQLAlchemy 2.0 asyncio: https://docs.sqlalchemy.org/en/20/orm/extensions/asyncio.html
- SQLAlchemy PostgreSQL / asyncpg: https://docs.sqlalchemy.org/en/20/dialects/postgresql.html
- Alembic asyncio: https://alembic.sqlalchemy.org/en/latest/cookbook.html#using-asyncio-with-alembic
- Alembic autogenerate/check: https://alembic.sqlalchemy.org/en/latest/autogenerate.html
- pytest-asyncio configuration: https://pytest-asyncio.readthedocs.io/en/stable/reference/configuration.html

---

## 1. Purpose

M0 proved that SlotLock can be cloned, installed, started, linted, tested, and exercised through HTTP.

M1 must prove:

> SlotLock can connect asynchronously to a real PostgreSQL database, evolve its schema reproducibly through migrations, persist a real domain object, retrieve it again, expose database readiness through the application, and verify all of this automatically against PostgreSQL.

M1 is the first milestone where SlotLock becomes a **stateful backend**.

The milestone intentionally introduces only one domain entity so database fundamentals can be learned and verified without mixing them with authentication, reservations, authorization, caching, or business-heavy API behavior.

---

## 2. Milestone outcome

M1 is complete when:

- database configuration is externalized;
- SQLAlchemy 2.x async APIs are used;
- PostgreSQL is accessed through `asyncpg`;
- sessions come from `async_sessionmaker`;
- sessions are not globally shared;
- Alembic manages schema evolution;
- an empty PostgreSQL database can be brought to head using migrations only;
- a `Resource` ORM model exists;
- the `resources` table is created by migration;
- a Resource can be inserted, committed, refreshed, queried, and validated;
- integration tests execute against PostgreSQL, not SQLite;
- test and development databases are separate locally;
- tests are isolated;
- `/health` remains database-independent;
- `/ready` verifies PostgreSQL readiness;
- CI provisions PostgreSQL, runs migrations, checks migration drift, and runs tests;
- README documents the working M1 flow;
- fresh verification succeeds;
- the default branch is green.

---

## 3. Technical baseline

Keep from M0:

- Python 3.13
- FastAPI
- Poetry
- pytest / pytest-cov
- Ruff
- Taskipy
- Docker / Docker Compose
- PostgreSQL 18
- GitHub Actions

Add:

- SQLAlchemy 2.x
- asyncpg
- Alembic
- pydantic-settings
- pytest-asyncio

### Version policy

Target the stable SQLAlchemy 2.0 branch during M1.

Suggested install:

```bash
poetry add "sqlalchemy[asyncio]>=2.0,<2.1" asyncpg alembic pydantic-settings
poetry add --group dev pytest-asyncio
```

Let Poetry resolve concrete stable versions and commit `poetry.lock`.

Do not copy old package pins from tutorial material.

---

## 4. Non-goals

Do **not** implement during M1:

- users;
- registration/login;
- password hashing;
- JWT;
- authentication/authorization;
- Resource CRUD endpoints;
- reservations;
- overlap/double-booking rules;
- idempotency;
- Redis/caching;
- audit events;
- webhooks;
- external integrations;
- background workers;
- RabbitMQ/Celery/Kafka;
- Airflow;
- repository abstractions merely for abstraction;
- service-layer hierarchies merely for abstraction;
- domain/application/infrastructure package architecture;
- Kubernetes/Terraform/AWS deployment;
- AI/LLM functionality.

If it is not required to prove persistence, migration correctness, testability, or readiness, defer it.

---

## 5. Design decisions

### 5.1 PostgreSQL is the integration-test database

Do not use SQLite as a substitute for M1 integration tests.

The stack being proven is:

```text
FastAPI
  ↓
AsyncSession
  ↓
SQLAlchemy
  ↓
asyncpg
  ↓
PostgreSQL
```

### 5.2 Async from the beginning

Use:

```text
create_async_engine
async_sessionmaker
AsyncSession
```

Configure the session factory with:

```text
expire_on_commit=False
```

A single `AsyncSession` must not be shared across concurrent requests/tasks.

Each independent operation receives its own session.

### 5.3 Configuration outside source code

Use `pydantic-settings`.

Commit:

```text
.env.example
```

Ignore:

```text
.env
```

Database URLs must not be hard-coded in Python modules.

### 5.4 Separate local development and test databases

Development:

```text
slotlock
```

Integration tests:

```text
slotlock_test
```

Suggested URLs:

```dotenv
DATABASE_URL=postgresql+asyncpg://slotlock:slotlock@127.0.0.1:5432/slotlock
TEST_DATABASE_URL=postgresql+asyncpg://slotlock:slotlock@127.0.0.1:5433/slotlock_test
```

Tests must never silently fall back from `TEST_DATABASE_URL` to `DATABASE_URL`.

### 5.5 Alembic owns schema creation

Do not use `Base.metadata.create_all()` as the production/test schema-management mechanism.

The authoritative schema history is the Alembic migration chain.

### 5.6 Autogenerate is a draft

Using:

```bash
poetry run alembic revision --autogenerate -m "create resources table"
```

is encouraged.

The generated migration must be manually reviewed before commit.

### 5.7 Keep the package flat

M1 should remain close to:

```text
slotlock/
├── __init__.py
├── app.py
├── database.py
├── models.py
└── settings.py
```

Do not create architecture layers before the code needs them.

### 5.8 Health and readiness differ

`GET /health` means:

> the process is alive and can serve HTTP.

It must not query PostgreSQL.

`GET /ready` means:

> required database infrastructure is available.

M1 readiness checks PostgreSQL.

---

## 6. Expected structure

```text
slotlock-api/
├── .github/
│   └── workflows/
│       └── ci.yml
├── docs/
│   └── specs/
│       ├── m0 - spec.md
│       └── m1 - spec.md
├── migrations/
│   ├── versions/
│   │   └── <revision>_create_resources_table.py
│   ├── env.py
│   ├── README
│   └── script.py.mako
├── slotlock/
│   ├── __init__.py
│   ├── app.py
│   ├── database.py
│   ├── models.py
│   └── settings.py
├── tests/
│   ├── __init__.py
│   ├── conftest.py
│   ├── test_app.py
│   └── test_db.py
├── .env.example
├── .gitignore
├── alembic.ini
├── compose.yml
├── poetry.lock
├── pyproject.toml
└── README.md
```

---

## 7. First persisted entity: Resource

A Resource is something that may eventually be reserved.

Examples:

- meeting room;
- vehicle;
- piece of equipment;
- consultation room.

M1 does not implement reservation behavior.

### Required fields

#### `id`

- `uuid.UUID` in Python;
- PostgreSQL native UUID;
- primary key;
- automatically generated;
- UUID v4 is enough for M1.

Do not introduce UUID v7 dependencies.

#### `name`

- string;
- required;
- non-null;
- suggested max length: 120.

Do not make it unique without a business requirement.

#### `description`

- optional;
- nullable;
- text.

#### `active`

- boolean;
- non-null;
- defaults to true.

#### `created_at`

- timezone-aware datetime;
- non-null;
- database-generated current timestamp.

#### `updated_at`

- timezone-aware datetime;
- non-null;
- current timestamp initially;
- updated when ORM updates are persisted.

Do not create a database trigger solely for this field in M1.

### Required behavior

The model must support:

```text
construct
→ add
→ commit
→ refresh
→ query
→ equivalent persisted state
```

No Resource HTTP schema or Resource endpoint is required yet.

---

## 8. SQLAlchemy model baseline

Use modern SQLAlchemy 2.x typed declarative mappings:

```text
DeclarativeBase
Mapped
mapped_column
```

Create one application `Base`.

A naming convention for constraints is recommended so future migrations remain predictable.

Example convention:

```text
ix -> ix_<column>
uq -> uq_<table>_<column>
ck -> ck_<table>_<constraint>
fk -> fk_<table>_<column>_<referred_table>
pk -> pk_<table>
```

Alembic `target_metadata` must point to the application's metadata.

---

## 9. Settings

Create:

```text
slotlock/settings.py
```

Use `pydantic-settings`.

At minimum expose:

```text
database_url
```

from:

```text
DATABASE_URL
```

Tests separately consume:

```text
TEST_DATABASE_URL
```

If test configuration is missing, fail clearly.

Do not risk the development database.

### `.env.example`

Commit:

```dotenv
DATABASE_URL=postgresql+asyncpg://slotlock:slotlock@127.0.0.1:5432/slotlock
TEST_DATABASE_URL=postgresql+asyncpg://slotlock:slotlock@127.0.0.1:5433/slotlock_test
```

README setup must include:

```bash
cp .env.example .env
```

---

## 10. Database module

Create:

```text
slotlock/database.py
```

Responsibilities:

- create async SQLAlchemy engine;
- create `async_sessionmaker`;
- expose the FastAPI session dependency;
- contain no Resource-specific query logic.

Conceptually:

```text
Settings.database_url
        ↓
create_async_engine
        ↓
async_sessionmaker
        ↓
get_session
        ↓
one AsyncSession per request/use
```

The engine may be module-scoped.

The session may not be global/shared.

---

## 11. Readiness endpoint

Add:

```http
GET /ready
```

It must perform a trivial DB operation such as:

```sql
SELECT 1
```

through an injected async session.

### DB available

```http
200 OK
```

Suggested response:

```json
{"status": "ready"}
```

### DB unavailable

```http
503 Service Unavailable
```

Do not expose:

- connection strings;
- credentials;
- driver details;
- raw stack traces.

### Health behavior

`GET /health` remains:

```http
200 OK
{"status": "ok"}
```

and must remain independent of PostgreSQL readiness.

---

## 12. Docker Compose

Keep the existing development PostgreSQL service.

Add a dedicated test PostgreSQL service.

Suggested service name:

```text
postgres-test
```

Suggested configuration:

```text
database: slotlock_test
username: slotlock
password: slotlock
host port: 5433
container port: 5432
```

Give it a healthcheck.

Prefer a Compose profile:

```text
test
```

Expected flow:

```bash
docker compose up -d --wait postgres
docker compose --profile test up -d --wait postgres-test
```

The test service must not share the development volume.

A persistent volume for the test DB is unnecessary.

---

## 13. Alembic

Initialize using Alembic's async template:

```bash
poetry run alembic init -t async migrations
```

Configure it to use:

```text
SlotLock Settings
SlotLock Base.metadata
```

Do not duplicate credentials in `alembic.ini`.

Expected commands:

```bash
poetry run alembic current
poetry run alembic upgrade head
poetry run alembic downgrade base
poetry run alembic check
```

### Initial migration

Generate:

```bash
poetry run alembic revision --autogenerate -m "create resources table"
```

Review manually.

It must create only the intended M1 Resource schema.

It must contain a valid downgrade.

### Migration round-trip

From an empty/disposable DB:

```text
empty
 ↓
upgrade head
 ↓
resources exists
 ↓
downgrade base
 ↓
resources absent
 ↓
upgrade head
 ↓
resources restored
```

After `upgrade head`:

```bash
poetry run alembic check
```

must report no pending migration operations.

---

## 14. Async test support

Add:

```text
pytest-asyncio
```

Recommended pytest baseline:

```toml
[tool.pytest.ini_options]
pythonpath = ["."]
testpaths = ["tests"]
asyncio_default_fixture_loop_scope = "function"
```

Prefer explicit `@pytest.mark.asyncio` markers unless automatic mode is intentionally chosen.

---

## 15. Test-database safety

Integration tests must read:

```text
TEST_DATABASE_URL
```

They must not silently use the dev URL.

Before mutating data, add a defensive test-database assertion.

For example, require the configured database name to clearly identify itself as:

```text
slotlock_test
```

If the guard fails, abort the integration suite.

A bad test configuration must not destroy development data.

---

## 16. Test schema and isolation

Before DB integration tests run, the test database must be migrated to:

```text
head
```

Do not use `Base.metadata.create_all()` as a shortcut.

Tests must not depend on execution order.

Preferred isolation:

- test engine against `TEST_DATABASE_URL`;
- isolated transaction/session per test;
- rollback after test;
- application code may call `commit()` without leaking state to later tests.

A savepoint-based approach is acceptable.

A safe deterministic cleanup approach is also acceptable.

Do not rebuild the PostgreSQL container for every test.

---

## 17. Required integration tests

### 17.1 Resource persistence

Arrange:

```text
Resource(
    name="Meeting Room A",
    description="..."
)
```

Act:

```text
add
commit
refresh
query by id
```

Assert:

- row exists;
- UUID populated;
- name preserved;
- description preserved;
- `active` is true;
- `created_at` populated;
- `updated_at` populated.

### 17.2 Resource query round-trip

Persist at least two resources.

Query with SQLAlchemy 2.x `select()`.

Verify the expected rows.

Do not invent a repository interface just for this test.

### 17.3 Isolation

Data written in one test must not appear in a later independent test.

---

## 18. Required readiness tests

### Healthy DB

```http
GET /ready
→ 200
```

with expected JSON.

Exercise the real FastAPI DB dependency against the test database.

### Failed DB

Use dependency overrides or a deterministic failing session.

```http
GET /ready
→ 503
```

No internal DB details should leak.

### Health independence

Keep evidence that `/health` itself has no DB dependency.

---

## 19. CI changes

M0 CI proves:

```text
install
lint
format
tests
```

M1 CI additionally proves:

```text
PostgreSQL available
migrations apply
no migration drift
PostgreSQL integration tests pass
```

Required logical sequence:

```text
checkout
↓
Python 3.13
↓
Poetry
↓
install
↓
lint
↓
format check
↓
PostgreSQL ready
↓
alembic upgrade head
↓
alembic check
↓
tests
```

CI may use:

- GitHub Actions PostgreSQL service containers, or
- the test Docker Compose service.

Choose the clearest approach.

In CI, `DATABASE_URL` and `TEST_DATABASE_URL` may point to the same CI-only disposable database because no persistent developer data exists there.

Locally they must remain separate.

---

## 20. Taskipy

Keep M0 tasks.

Useful M1 additions may include:

```text
db_up
db_down
db_test_up
db_test_down
migrate
migration_check
```

Do not create elaborate command infrastructure.

Direct Docker/Poetry/Alembic commands are acceptable when clearer.

---

## 21. README changes

After commands are proven, update README.

Change current milestone to:

```text
M1 — Persistence
```

Document:

- `.env.example`;
- environment setup;
- dev PostgreSQL;
- test PostgreSQL;
- migrations;
- `alembic current`;
- `alembic check`;
- integration tests;
- `/health`;
- `/ready`;
- current Resource-only persistence scope;
- M2 owns Resource HTTP behavior.

Keep detailed reasoning in this spec, not the README.

---

## 22. Implementation sequence

### Step 1 — Dependencies

Add the M1 dependencies.

Verify M0 still passes:

```bash
poetry install
poetry run task lint
poetry run task test
```

**Done:** dependency resolution succeeds and existing behavior remains green.

### Step 2 — Settings

Create:

```text
slotlock/settings.py
.env.example
```

**Done:** DB configuration comes from environment and `.env` is ignored.

### Step 3 — Separate test PostgreSQL

Extend `compose.yml`.

**Done:** dev and test databases can be started independently and do not share storage.

### Step 4 — Resource model

Create `slotlock/models.py`.

**Done:** typed SQLAlchemy metadata contains `resources`.

### Step 5 — Async database layer

Create `slotlock/database.py`.

**Done:** an async session executes `SELECT 1` against dev PostgreSQL.

### Step 6 — `/ready`

Add DB-aware readiness.

**Done:**

```text
DB healthy:
  /health -> 200
  /ready  -> 200

DB unavailable:
  /health -> 200
  /ready  -> 503
```

### Step 7 — Alembic async setup

Run:

```bash
poetry run alembic init -t async migrations
```

Configure Settings and metadata.

**Done:** `alembic current` can connect.

### Step 8 — Initial Resource migration

Generate and review the migration.

**Done:** migration matches only M1 schema and has a valid downgrade.

### Step 9 — Migration round-trip

Run:

```bash
poetry run alembic upgrade head
poetry run alembic check
poetry run alembic downgrade base
poetry run alembic upgrade head
poetry run alembic check
```

**Done:** all succeed.

### Step 10 — PostgreSQL test fixtures

Create/update `tests/conftest.py`.

**Done:** tests use `TEST_DATABASE_URL`, safety guard, migrations, and isolation.

### Step 11 — Persistence tests

Create `tests/test_db.py`.

**Done:** Resource insert/commit/refresh/query is green.

### Step 12 — Readiness tests

Extend application tests.

**Done:** readiness success/failure contracts are green.

### Step 13 — CI

Add PostgreSQL and migration gates.

**Done:** CI proves migration correctness and integration tests.

### Step 14 — README

Document only verified commands.

### Step 15 — Fresh verification

Execute the M1 verification protocol.

If successful:

- mark this spec `Complete`;
- append verification record;
- commit;
- stop.

---

## 23. Acceptance criteria

### AC-01 — M0 survives

```http
GET /health
→ 200
→ {"status": "ok"}
```

### AC-02 — Config externalized

Database configuration comes from environment/settings, not hard-coded Python credentials.

### AC-03 — Async DB connection

`AsyncSession` successfully performs `SELECT 1` against PostgreSQL.

### AC-04 — Readiness success

```http
GET /ready
→ 200
```

with documented body when PostgreSQL is usable.

### AC-05 — Readiness failure

```http
GET /ready
→ 503
```

without sensitive internal details when DB access fails.

### AC-06 — Resource metadata

ORM metadata contains the required `resources` table and fields.

### AC-07 — Empty DB migration

`alembic upgrade head` creates the schema from an empty PostgreSQL database.

### AC-08 — Migration rollback

`downgrade base` removes M1 schema and a new `upgrade head` restores it.

### AC-09 — No drift

`alembic check` reports no pending operations at head.

### AC-10 — Resource persistence

A Resource persists and can be queried back through `AsyncSession`.

### AC-11 — PostgreSQL tests

Integration tests run against PostgreSQL, not SQLite.

### AC-12 — Isolation

Committed test data does not leak into later tests.

### AC-13 — Safety

Unsafe `TEST_DATABASE_URL` causes the integration suite to abort before mutation.

### AC-14 — CI

CI provisions PostgreSQL, migrates, checks drift, and passes the suite.

### AC-15 — Documentation

Fresh-clone instructions are sufficient to reproduce the milestone.

---

## 24. Expected command contract

### Configure

```bash
cp .env.example .env
poetry install
```

### Dev DB

```bash
docker compose up -d --wait postgres
```

### Test DB

```bash
docker compose --profile test up -d --wait postgres-test
```

### Migrate

```bash
poetry run alembic upgrade head
```

### Migration status

```bash
poetry run alembic current
```

### Drift check

```bash
poetry run alembic check
```

### Run API

```bash
poetry run task run
```

### Quality

```bash
poetry run task lint
poetry run ruff format --check .
poetry run task test
```

---

## 25. Fresh verification protocol

From a clean clone:

```bash
git clone https://github.com/jhonatancasale/slotlock-api.git slotlock-m1-verification
cd slotlock-m1-verification

cp .env.example .env
poetry env use 3.13
poetry install
```

Start databases:

```bash
docker compose up -d --wait postgres
docker compose --profile test up -d --wait postgres-test
docker compose ps
```

Verify migrations:

```bash
poetry run alembic upgrade head
poetry run alembic current
poetry run alembic check

poetry run alembic downgrade base
poetry run alembic upgrade head
poetry run alembic check
```

Run API:

```bash
poetry run task run
```

From another terminal:

```bash
curl http://127.0.0.1:8000/health
curl http://127.0.0.1:8000/ready
```

Expected:

```text
/health -> 200
/ready  -> 200
```

Run quality gates:

```bash
poetry run task lint
poetry run ruff format --check .
poetry run task test
```

Push and verify GitHub Actions is green.

Append the verified commit and workflow run to this document before closing M1.

---

## 26. Recommended commit story

```text
chore: add M1 persistence dependencies
feat: add environment-based database settings
chore: add isolated test PostgreSQL service
feat: add async database session infrastructure
feat: add Resource persistence model
feat: add database readiness endpoint
chore: configure async Alembic migrations
feat: add initial Resource migration
test: add PostgreSQL persistence fixtures and tests
ci: verify migrations and PostgreSQL integration tests
docs: document M1 persistence workflow
docs: mark M1 complete with verification results
```

Guidance, not ceremony.

---

## 27. Definition of Done

### Configuration

- [ ] `pydantic-settings` used.
- [ ] `.env.example` committed.
- [ ] `.env` ignored.
- [ ] `DATABASE_URL` externalized.
- [ ] `TEST_DATABASE_URL` explicit and safe.

### Persistence

- [ ] SQLAlchemy 2.x async stack configured.
- [ ] `asyncpg` used.
- [ ] `create_async_engine` used.
- [ ] `async_sessionmaker` used.
- [ ] `expire_on_commit=False` deliberate.
- [ ] sessions are not globally shared.
- [ ] async `SELECT 1` succeeds.

### Resource

- [ ] Resource model exists.
- [ ] UUID PK works.
- [ ] name persists.
- [ ] optional description persists.
- [ ] active defaults true.
- [ ] created_at populated.
- [ ] updated_at populated.

### Health/readiness

- [ ] `/health` remains DB-independent.
- [ ] `/ready` returns 200 with healthy PostgreSQL.
- [ ] `/ready` returns 503 for controlled DB failure.
- [ ] no sensitive DB error details leak.

### Alembic

- [ ] async migration environment configured.
- [ ] application metadata is target metadata.
- [ ] initial Resource migration exists.
- [ ] generated migration reviewed.
- [ ] empty DB → upgrade head works.
- [ ] downgrade base works.
- [ ] second upgrade head works.
- [ ] current reports head.
- [ ] `alembic check` reports no pending ops.
- [ ] schema setup does not depend on `create_all()`.

### Testing

- [ ] pytest-asyncio configured.
- [ ] DB tests use PostgreSQL.
- [ ] tests use dedicated local test DB.
- [ ] safety guard exists.
- [ ] test schema comes from migrations.
- [ ] tests are isolated.
- [ ] Resource persistence test passes.
- [ ] readiness success test passes.
- [ ] readiness failure test passes.
- [ ] M0 health test remains green.

### Docker / CI / docs

- [ ] dev PostgreSQL remains healthy.
- [ ] separate test PostgreSQL exists.
- [ ] test storage is separate/disposable.
- [ ] CI provisions PostgreSQL.
- [ ] CI applies migrations.
- [ ] CI runs `alembic check`.
- [ ] CI runs lint/format/tests.
- [ ] README reflects M1.
- [ ] `docs/specs/m1 - spec.md` committed.
- [ ] fresh verification succeeds.
- [ ] verification record appended.
- [ ] default branch green.
- [ ] spec marked `Complete`.

---

## 28. Hard stop

Once the Definition of Done is satisfied:

> **Stop. M1 is complete. Do not build the Resource API inside M1.**

Do not add:

```text
POST /resources
GET /resources
PATCH /resources
users
auth
reservations
Redis
```

Those belong to later milestones.

M1 exists to establish a trustworthy persistence layer and prove it against PostgreSQL.

---

## 29. What M1 unlocks

After M1, SlotLock has:

```text
FastAPI
+
CI
+
Dockerized PostgreSQL
+
externalized config
+
async SQLAlchemy
+
versioned Alembic migrations
+
real persisted domain state
+
PostgreSQL integration tests
+
health/readiness separation
```

The milestone progression becomes:

```text
M0: HTTP process exists
M1: persistent state exists
M2: useful domain API exists
```
