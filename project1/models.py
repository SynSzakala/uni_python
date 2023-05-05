from datetime import datetime
from enum import Enum
from typing import Optional

import sqlalchemy
from sqlalchemy import ForeignKey
from sqlalchemy.orm import MappedAsDataclass, DeclarativeBase, Mapped, mapped_column, relationship


class BaseEntity(MappedAsDataclass, DeclarativeBase):
    pass


class UserType(Enum):
    READER = 1
    LIBRARIAN = 2


class UserEntity(BaseEntity):
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(init=False, primary_key=True)
    username: Mapped[str]
    type: Mapped[UserType] = mapped_column(sqlalchemy.Enum(UserType))

    def __str__(self):
        return f'{self.id}: {self.username} ({self.type.name})'


class BookEntity(BaseEntity):
    __tablename__ = 'books'

    id: Mapped[int] = mapped_column(init=False, primary_key=True)
    title: Mapped[str]
    author: Mapped[str]
    keywords: Mapped[str]  # separated by ','
    borrowed_by_id: Mapped[Optional[int]] = mapped_column(ForeignKey(UserEntity.id), init=False)
    borrowed_by: Mapped[Optional[UserEntity]] = \
        relationship(UserEntity, foreign_keys=[borrowed_by_id], init=False, lazy='joined')
    borrowed_until: Mapped[Optional[datetime]] = mapped_column(init=False)
    reserved_by_id: Mapped[Optional[int]] = mapped_column(ForeignKey(UserEntity.id), init=False)
    reserved_by: Mapped[Optional[UserEntity]] = \
        relationship(UserEntity, foreign_keys=[reserved_by_id], init=False, lazy='joined')

    def __str__(self):
        return f'{self.id}: "{self.title}" by "{self.author}", keywords: {self.keywords or "<none>"}' + \
            (f" (borrowed by {self.borrowed_by} until {self.borrowed_until.date()})" if self.borrowed_by_id else '') + \
            (f" (reserved by {self.reserved_by})" if self.reserved_by_id else '')
