from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from bot.db import GuildDB

async def create_guild(guild_id: int, session: AsyncSession) -> GuildDB:
    guild = GuildDB(guild_id = guild_id)

    session.add(guild)
    await session.commit()

    return guild

async def get_guild(guild_id: int, session: AsyncSession) -> GuildDB | None:
    return await session.execute(
        select(GuildDB)
        .where(GuildDB.guild_id == guild_id)
    )
