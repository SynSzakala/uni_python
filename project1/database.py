from typing import Optional, List

from sqlalchemy import create_engine, select, and_, or_
from sqlalchemy.orm import Session

from models import BaseEntity, UserType, UserEntity, BookEntity


class Database:
    def __init__(self, url: str):
        self.engine = create_engine(url)
        BaseEntity.metadata.create_all(self.engine)

    def get_user(self, username: str) -> Optional[UserEntity]:
        with Session(self.engine) as session:
            return session.scalar(select(UserEntity).where(UserEntity.username == username))

    def add_user(self, username: str, type: UserType) -> UserEntity:
        with Session(self.engine) as session:
            user = UserEntity(username=username, type=type)
            session.add(user)
            _close_session(session)
        return user

    def get_books(
            self,
            id: Optional[int] = None, title: Optional[str] = None, author: Optional[str] = None,
            keyword: Optional[str] = None, filter: Optional = None, limit: Optional[int] = None,
    ) -> List[BookEntity]:
        with Session(self.engine) as session:
            clause = and_(
                or_(id == '', BookEntity.id == id),
                or_(title == '', BookEntity.title.icontains(title)),
                or_(author == '', BookEntity.author.icontains(author)),
                or_(keyword == '', BookEntity.keywords.icontains(keyword)),
                or_(filter is None, filter),
            )
            return session.scalars(select(BookEntity).where(clause).limit(limit)).all()

    def save_book(self, book: BookEntity):
        with Session(self.engine) as session:
            session.add(book)
            session.flush()
            session.refresh(book)
            _close_session(session)

    def delete_book(self, book: BookEntity):
        with Session(self.engine) as session:
            session.delete(book)
            _close_session(session)


def _close_session(session: Session):
    session.flush()
    session.expunge_all()
    session.commit()
