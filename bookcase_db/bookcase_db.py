import sqlalchemy as sql
from sqlalchemy.orm import create_session

from bookcase_db.data_schema import Base, Book, book_header
import bookcase_exceptions as exc
from bookcase_translations import Translations


class BookcaseDbManager(object):
    """
    Class that manages all DB operations
    """
    def __init__(self, path="", db_name="bookcase"):
        self._db_name = self.validate_db_name(db_name)
        self.engine = sql.create_engine('sqlite:///{path}{db_name}.db'
                                        .format(path=path, db_name=self.db_name))
        self.session = create_session(bind=self.engine)

    @property
    def db_name(self):
        return self._db_name

    @staticmethod
    def validate_db_name(name):
        """
        Validates input
        :param name: the name of DB as specified by the user
        :return: the filename without the extension
        :raises: InvalidInputException if the name contains spaces
        """
        if " " in name:
            raise exc.InvalidInputException(Translations().no_spaces_in_names_warn)
        return name if not ".db" in name else name.strip(".db")

    def create_db(self):
        Base.metadata.create_all(self.engine)

    def add_book(self, **kwargs):
        """
        Adds a new book to database
        :param kwargs: "title", "author", "translator", "publisher",
            "publication_year", "isbn", "copies", "genre", "shelf"
        """
        if not "author" in kwargs.keys() or not "title" in kwargs.keys():
            raise exc.InvalidInputException()
        new_book = Book(**kwargs)
        self.session.add(new_book)
        print(new_book)
        self.session.flush()

    def save_book(self):
        self.session.flush()

    def delete_book(self, row):
        self.session.delete(row)
        self.session.flush()

    def clear_table(self):
        for row in self.get_all_books():
            self.session.delete(row)
        self.session.flush()

    def get_all_books(self):
        return self.session.query(Book).all()

    def cleanup(self):
        self.session.close()

    def search_by_title(self, title):
        return self.session.query(Book).filter(Book.title.contains(title.upper())).all()

    def search_by_author(self, author):
        return self.session.query(Book).filter(Book.author.contains(author.upper())).all()

    def search_by_isbn(self, isbn):
        return self.session.query(Book).filter_by(isbn=isbn).all()

    def search_by_shelf(self, shelf):
        return self.session.query(Book).filter_by(shelf=shelf).all()

    def search_by_genre(self, genre):
        return self.session.query(Book).filter(Book.genre.contains(genre.upper())).all()

    def dump_table(self):
        """
        Dumps all entries to a 2-D array
        :return: a tuple containing row entries as tuples
        """
        books = self.get_all_books()
        table = list()
        table.append(book_header())
        table.extend([book.get_row() for book in books])
        return tuple(table)

    def import_table(self, table):
        """
        Creates book entries from a table and saves them to DB
        :param table: a tuple of tuples containing book attributes
        """
        attributes_to_index = self.get_indexes_for_book_attributes(table[0])
        books = self.create_books_from_table(attributes_to_index, table[1:])
        self.session.add_all(books)
        self.session.flush()

    @staticmethod
    def get_indexes_for_book_attributes(header):
        """
        Maps provided table header with the header defined in schema
        :param header: a tuple containing the header
        :return: a dict that maps indexes of header elements to the book elements
        """
        return dict([(attribute, header.index(attribute)) for attribute in book_header() if attribute in header])

    def create_books_from_table(self, attributes_to_index, table):
        """
        Converts all rows of the table to book objects
        :param attributes_to_index: a dict that maps indexes of header elements to the book elements
        :param table: a tuple of tuples containing multiple books
        :return: a list of book objects
        """
        books = []
        for row in table:
            try:
                new_book = Book(**self.get_book_attributes_from_row(attributes_to_index, row))
                books.append(new_book)
            except exc.InvalidInputException:
                continue
        return books

    @staticmethod
    def get_book_attributes_from_row(attributes_to_index, row):
        book_args = dict()
        for key, index in attributes_to_index.items():
            value = row[index]
            if value:
                book_args[key] = row[index]
        if not book_args["author"] or not book_args["title"]:
            raise exc.InvalidInputException
        return book_args
