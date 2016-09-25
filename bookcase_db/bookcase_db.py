import sqlalchemy as sql
from sqlalchemy.orm import create_session
from bookcase_db.data_schema import Base, Book, book_header


class BookcaseDbManager(object):
    def __init__(self, path="", db_name="bookcase"):
        self._db_name = db_name if not ".db" in db_name else db_name.strip(".db")
        self.engine = sql.create_engine('sqlite:///{path}{db_name}.db'
                                        .format(path=path, db_name=self.db_name))
        self.session = create_session(bind=self.engine)

    @property
    def db_name(self):
        return self._db_name

    def create_db(self):
        Base.metadata.create_all(self.engine)

    def add_book(self, title, author, translator="", publication_year="",
                 isbn="", publisher="", shelf="", copies=1):
        new_book = Book(author=author.upper(),
                        title=title.upper(),
                        isbn=isbn,
                        publication_year=publication_year,
                        publisher=publisher.upper(),
                        translator=translator.upper(),
                        shelf=shelf,
                        copies=copies)
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

    def dump_table(self):
        books = self.get_all_books()
        table = list()
        table.append(book_header())
        table.extend([book.get_row() for book in books])
        return tuple(table)

    def import_table(self, table):
        attributes_to_index = self.get_indexes_for_book_attributes(table[0])
        books = self.create_books_from_table(attributes_to_index, table[1:])
        self.session.add_all(books)
        self.session.flush()

    @staticmethod
    def get_indexes_for_book_attributes(header):
        return dict([(attribute, header.index(attribute)) for attribute in book_header() if attribute in header])

    @staticmethod
    def create_books_from_table(attributes_to_index, table):
        books = []
        for row in table:
            author = row[attributes_to_index["author"]]
            title = row[attributes_to_index["title"]]
            isbn = row[attributes_to_index["isbn"]]
            publication_year = row[attributes_to_index["publication_year"]]
            publisher = row[attributes_to_index["publisher"]]
            translator = row[attributes_to_index["translator"]]
            shelf = row[attributes_to_index["shelf"]]
            copies = row[attributes_to_index["copies"]]
            if not author or not title:
                continue
            books.append(Book(author=author.upper(),
                              title=title.upper(),
                              isbn=isbn if isbn else "",
                              publication_year=publication_year if publication_year else -1,
                              publisher=publisher.upper() if publisher else "",
                              translator=translator.upper() if translator else "",
                              shelf=shelf if shelf else "-",
                              copies=copies))
        return books
