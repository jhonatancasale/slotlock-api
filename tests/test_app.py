from http import HTTPStatus
from unittest.mock import AsyncMock

import pytest
from asyncpg import PostgresError
from fastapi.testclient import TestClient
from httpx import ASGITransport, AsyncClient
from sqlalchemy.exc import SQLAlchemyError

from slotlock import database
from slotlock.app import app
from slotlock.database import get_session
from slotlock.settings import Settings


def test_health_returns_ok():
    client = TestClient(app)
    response = client.get('/health')

    assert response.status_code == HTTPStatus.OK
    assert response.headers['content-type'] == 'application/json'
    assert response.json() == {'status': 'ok'}


@pytest.mark.asyncio
async def test_ready_uses_real_database_dependency(
    migrated_database, monkeypatch
):

    monkeypatch.setattr(
        database,
        'get_settings',
        lambda: Settings(database_url=migrated_database),
    )
    async with app.router.lifespan_context(app):
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url='http://test'
        ) as client:
            response = await client.get('/ready')
    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'status': 'ready'}


@pytest.mark.asyncio
@pytest.mark.parametrize(
    'error', [OSError, TimeoutError, SQLAlchemyError, PostgresError]
)
async def test_database_failure_is_sanitized_and_health_survives(error):
    session = AsyncMock()
    session.execute.side_effect = error('sensitive connection details')

    async def failed_session():
        yield session

    app.dependency_overrides[get_session] = failed_session
    try:
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url='http://test'
        ) as client:
            health = await client.get('/health')
            session.execute.assert_not_called()
            ready = await client.get('/ready')
        assert health.status_code == HTTPStatus.OK
        assert health.json() == {'status': 'ok'}
        assert ready.status_code == HTTPStatus.SERVICE_UNAVAILABLE
        assert ready.json() == {'detail': 'Database unavailable'}
    finally:
        app.dependency_overrides.clear()
