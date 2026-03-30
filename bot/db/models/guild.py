from sqlalchemy import BigInteger
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import BaseModel

class Guild(BaseModel):
    __tablename__ = 'guild'

    guild_id: Mapped[int] = mapped_column(BigInteger, nullable = False)
    roles: Mapped[list['Role']] = relationship(
        back_populates = 'guild',
        cascade = 'all, delete-orphan'
    )
