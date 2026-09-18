from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import Request
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from slotlock.settings import get_settings


@asynccontextmanager
async def lifespan(app):
    engine = create_async_engine(
        str(get_settings().database_url),
        pool_pre_ping=True,
        connect_args={'timeout': 5, 'command_timeout': 5},
    )
    app.state.session_factory = async_sessionmaker(
        engine, expire_on_commit=False
    )
    try:
        yield
    finally:
        await engine.dispose()


async def get_session(request: Request) -> AsyncIterator[AsyncSession]:
    async with request.app.state.session_factory() as session:
        yield session
