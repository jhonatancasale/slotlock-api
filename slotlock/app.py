from typing import Annotated

from asyncpg import PostgresError
from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from slotlock.database import get_session, lifespan

app = FastAPI(title='SlotLock API', lifespan=lifespan)


@app.get('/health')
def health() -> dict[str, str]:
    return {'status': 'ok'}


@app.get('/ready')
async def ready(
    session: Annotated[AsyncSession, Depends(get_session)],
) -> dict[str, str]:
    try:
        await session.execute(text('SELECT 1'))
    except (SQLAlchemyError, PostgresError, OSError, TimeoutError):
        raise HTTPException(
            status_code=503, detail='Database unavailable'
        ) from None
    return {'status': 'ready'}
