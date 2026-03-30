from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from bot.db import RoleDB

async def create_role(
    role_id: int,
    user_id: int,
    guild_id: int,
    session: AsyncSession
) -> RoleDB:
    role = RoleDB(role_id = role_id, user_id = user_id, guild_id = guild_id)

    session.add(role)
    await session.commit()

    return role

async def get_role(
    user_id: int,
    guild_id: int,
    session: AsyncSession
) -> RoleDB | None:
    return await session.execute(
        select(RoleDB)
        .where(RoleDB.user_id == user_id, RoleDB.guild_id == guild_id)
    )
