from sqlalchemy import BigInteger, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import BaseModel

class Role(BaseModel):
    __tablename__ = 'role'

    role_id: Mapped[int] = mapped_column(
        BigInteger,
        nullable = False,
        unique = True
    )
    user_id: Mapped[int] = mapped_column(nullable = False)
    guild_id: Mapped[int] = mapped_column(ForeignKey('guild.id'))

    guild: Mapped['Guild'] = relationship(back_populates = 'roles')

    __table_args__ = (
        UniqueConstraint('user_id', 'guild_id', name = 'user_guild_uc'),
    )
