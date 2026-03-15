from collections.abc import AsyncGenerator
from logging import getLogger

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from .models.base import BaseModel

logger = getLogger('database')


async_engine, async_session = None, None

async def init_db() -> None:
    global async_engine, async_session

    async_engine = create_async_engine(
        'sqlite+aiosqlite:///data.sqlite',
        echo = False,
        future = True
    )
    async_session = async_sessionmaker(
        bind = async_engine,
        class_ = AsyncSession,
        expire_on_commit = False
    )

    # Create necessary tables.
    async with async_engine.begin() as connection:
        await connection.run_sync(BaseModel.metadata.create_all)

async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """ Returns session as AsyncGenerator for database operations. """
    if not async_session:
        raise Exception(
            'Please initialize database'\
            'with "init_db" function before accessing.'
        )

    async with async_session() as session:
        try:
            yield session
        except SQLAlchemyError as error:
            await session.rollback()

            logger.error('Database exception:', error)
        finally:
            await session.close()
