from datetime import datetime, timedelta
from typing import Optional

from simple_term_menu import TerminalMenu
from sqlalchemy import and_, or_

from database import Database
from models import UserType, UserEntity, BookEntity

database_url = 'sqlite:///database.sqlite'
booking_period = timedelta(days=30)
admin_username = 'admin'
default_limit = 20


class System:
    _user: Optional[UserEntity] = None

    def __init__(self):
        self._database = Database(database_url)
        self._ensure_admin_user()

    def run(self):
        while True:
            if not self._user:
                self._login()
            else:
                if self._user.type == UserType.READER:
                    options = {
                        'Borrow book': self._borrow_book,
                        'Extend borrowing period': self._extend_borrowing_period,
                        'Reserve book': self._reserve_book,
                        'Browse catalog': self._browse_catalog,
                        'Logout': self._logout,
                    }
                else:
                    options = {
                        'Add book': self._add_book,
                        'Remove book': self._remove_book,
                        'Add user': self._add_user,
                        'Accept return': self._accept_return,
                        'Browse catalog': self._browse_catalog,
                        'Logout': self._logout,
                    }
                keys = list(options.keys())
                result = TerminalMenu(keys, title='Select action (q to exit):').show()
                if result is None:
                    return
                options[keys[result]]()
            print()

    def _login(self):
        print("Logging in")
        username = input('Username: ')
        self._user = self._database.get_user(username)
        if self._user:
            print(f'Logged in as {self._user}')
        else:
            print('User not found')

    def _logout(self):
        print("Logging out")
        self._user = None

    def _borrow_book(self):
        print("Borrowing book")
        book = self._select_book(
            filter=and_(
                BookEntity.borrowed_by_id.is_(None),
                or_(BookEntity.reserved_by_id.is_(None), BookEntity.reserved_by_id == self._user.id),
            )
        )
        if book:
            book.reserved_by = None
            self._database.save_book(book)
            book.borrowed_by = self._user
            book.borrowed_until = datetime.now() + booking_period
            self._database.save_book(book)
            print(f"Borrowed {book}")

    def _extend_borrowing_period(self):
        print("Extending borrowing period")
        book = self._select_book(
            filter=and_(BookEntity.borrowed_by_id == self._user.id)
        )
        if book:
            book.borrowed_until = datetime.now() + booking_period
            self._database.save_book(book)
        print(f"Extended borrowing period for {book}")

    def _reserve_book(self):
        print("Reserving book")
        book = self._select_book(
            filter=and_(
                BookEntity.borrowed_by_id.is_not(None),
                BookEntity.borrowed_by_id != self._user.id,
                BookEntity.reserved_by_id.is_(None)
            )
        )
        if book:
            book.reserved_by = self._user
            self._database.save_book(book)
        print(f"Reserved {book}")

    def _remove_book(self):
        print("Removing book")
        book = self._select_book()
        if book:
            self._database.delete_book(book)
            print(f"Removed {book}")

    def _add_book(self):
        print("Adding book")
        title = None
        while not title:
            title = input('Title (required): ')
        author = None
        while not author:
            author = input('Author (required): ')
        keywords = input('Keywords (comma separated) [empty]: ')
        book = BookEntity(title=title, author=author, keywords=keywords)
        self._database.save_book(book)
        print(f'Added {book}')

    def _add_user(self):
        print("Adding user")
        username = input('Username: ')
        type = UserType.LIBRARIAN if input('Type (LIBRARIAN/READER) [READER]: ') == 'LIBRARIAN' else UserType.READER
        user = self._database.add_user(username, type)
        print(f'Added {user}')

    def _accept_return(self):
        print("Accepting return")
        book = self._select_book(
            filter=and_(BookEntity.borrowed_by_id.is_not(None))
        )
        if book:
            book.borrowed_by = None
            book.borrowed_until = None
            self._database.save_book(book)
            print(f"Accepted return for {book}")

    def _browse_catalog(self):
        print("Browsing catalog")
        self._select_book(confirm_none_selected=False)

    def _select_book(self, filter: Optional = None, confirm_none_selected: bool = True) -> Optional[BookEntity]:
        while True:
            id = input('Enter id [skip]: ')
            title, author, keywords = '', '', ''
            if not id:
                title = input('Search title [any]: ')
                author = input('Search author [any]: ')
                keywords = input('Search keyword [any]: ')
            books = self._database.get_books(id and int(id), title, author, keywords, filter, limit=default_limit)
            if not books:
                if TerminalMenu(['Search again', 'Exit'], title='No books found').show() == 1:
                    return
                else:
                    print()
                    continue
            result = TerminalMenu(map(str, books), title='Select book (q to exit):').show()
            if result is None:
                if not confirm_none_selected or \
                        TerminalMenu(['Search again', 'Exit'], title='No book selected').show() == 1:
                    return
                else:
                    print()
            else:
                return books[result]

    def _ensure_admin_user(self):
        if not self._database.get_user(admin_username):
            self._database.add_user(admin_username, UserType.LIBRARIAN)


System().run()
