from sqlalchemy.orm import DeclarativeBase

from .mixins import IdMixin

class Base(DeclarativeBase):
    pass

class BaseModel(Base, IdMixin):
    # Remove __abstract__ when you're done copying the template.
    __abstract__ = True
