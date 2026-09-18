from contextlib import asynccontextmanager
from pathlib import Path

import pytest
import pytest_asyncio
from alembic import command
from alembic.config import Config
from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy.engine import make_url
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine


class TestSettings(BaseSettings):
    model_config = SettingsConfigDict(env_file='.env', extra='ignore')
    test_database_url: str


def safe_test_url(value):
    url = make_url(value)
    if (
        url.drivername != 'postgresql+asyncpg'
        or url.database != 'slotlock_test'
    ):
        raise ValueError(
            'TEST_DATABASE_URL must use asyncpg and database slotlock_test'
        )
    return value


@pytest.fixture(scope='session')
def test_database_url():
    try:
        return safe_test_url(TestSettings().test_database_url)
    except ValueError:
        pytest.fail(
            'Set TEST_DATABASE_URL to a PostgreSQL asyncpg slotlock_test '
            'database; no fallback to DATABASE_URL is allowed.',
            pytrace=False,
        )


@pytest.fixture(scope='session')
def migrated_database(test_database_url):
    root = Path(__file__).resolve().parents[1]
    config = Config(str(root / 'alembic.ini'))
    config.set_main_option('script_location', str(root / 'migrations'))
    config.attributes['database_url'] = test_database_url
    command.upgrade(config, 'head')
    return test_database_url


@pytest_asyncio.fixture
async def test_engine(migrated_database):
    engine = create_async_engine(migrated_database)
    try:
        yield engine
    finally:
        await engine.dispose()


@asynccontextmanager
async def isolated_session(engine):
    async with engine.connect() as connection:
        transaction = await connection.begin()
        factory = async_sessionmaker(
            connection,
            expire_on_commit=False,
            join_transaction_mode='create_savepoint',
        )
        try:
            async with factory() as session:
                yield session
        finally:
            await transaction.rollback()


@pytest_asyncio.fixture
async def session(test_engine):
    async with isolated_session(test_engine) as db_session:
        yield db_session
