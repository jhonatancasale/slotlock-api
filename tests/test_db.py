from datetime import datetime, timezone
from uuid import UUID

import pytest
from sqlalchemy import select
from sqlalchemy.engine import make_url

from slotlock.models import Resource
from tests.conftest import isolated_session, safe_test_url

UUID_VERSION = 4


@pytest.mark.asyncio
async def test_resource_persists(session):
    resource = Resource(name='Meeting Room A', description='Whiteboard')
    session.add(resource)
    await session.commit()
    await session.refresh(resource)
    resource_id = resource.id
    session.expunge_all()
    persisted = await session.scalar(
        select(Resource).where(Resource.id == resource_id)
    )
    assert isinstance(persisted.id, UUID)
    assert persisted.id.version == UUID_VERSION
    assert persisted.name == 'Meeting Room A'
    assert persisted.description == 'Whiteboard'
    assert persisted.active is True
    assert persisted.created_at.utcoffset() is not None
    assert persisted.updated_at.utcoffset() is not None


@pytest.mark.asyncio
async def test_select_returns_multiple_resources(session):
    resources = [Resource(name='Room A'), Resource(name='Room B')]
    session.add_all(resources)
    await session.commit()
    ids = [resource.id for resource in resources]
    session.expunge_all()
    rows = (
        await session.scalars(
            select(Resource)
            .where(Resource.id.in_(ids))
            .order_by(Resource.name)
        )
    ).all()
    assert [row.name for row in rows] == ['Room A', 'Room B']
    assert all(row.description is None for row in rows)


@pytest.mark.asyncio
async def test_commits_do_not_escape_test_transaction(test_engine):
    async with isolated_session(test_engine) as first:
        resource = Resource(name='Isolated')
        first.add(resource)
        await first.commit()
        resource_id = resource.id
        assert await first.get(Resource, resource_id) is not None
    async with isolated_session(test_engine) as second:
        assert await second.get(Resource, resource_id) is None


@pytest.mark.asyncio
async def test_orm_update_changes_timestamp(session):
    resource = Resource(name='Before')
    session.add(resource)
    await session.commit()
    await session.refresh(resource)
    # A deliberately old timestamp avoids clock/timing-dependent assertions.

    resource.updated_at = datetime(2000, 1, 1, tzinfo=timezone.utc)
    await session.commit()
    old_timestamp = resource.updated_at
    resource.name = 'After'
    await session.commit()
    await session.refresh(resource)
    assert resource.updated_at > old_timestamp
    assert resource.name == 'After'


@pytest.mark.parametrize('database', ['slotlock', 'postgres', ''])
def test_unsafe_database_is_rejected(test_database_url, database):

    unsafe = make_url(test_database_url).set(database=database)
    with pytest.raises(ValueError, match='slotlock_test'):
        safe_test_url(unsafe.render_as_string(hide_password=False))
