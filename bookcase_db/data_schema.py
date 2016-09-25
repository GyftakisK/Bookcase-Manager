import sqlalchemy as sql
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


def book_header():
    return ("title", "author", "translator", "publisher",
            "publication_year", "isbn", "copies", "shelf")


class Book(Base):
    __tablename__ = 'books'
    id = sql.Column(sql.Integer, primary_key=True)
    title = sql.Column(sql.String)
    author = sql.Column(sql.String)
    translator = sql.Column(sql.String)
    publication_year = sql.Column(sql.Integer)
    isbn = sql.Column(sql.String)
    publisher = sql.Column(sql.String)
    shelf = sql.Column(sql.String)
    copies = sql.Column(sql.Integer)

    def __repr__(self):
        return "{title}, {author}, {publisher}, {year} | {shelf}".format(title=self.title,
                                                                         author=self.author,
                                                                         publisher=self.publisher,
                                                                         year=self.publication_year,
                                                                         shelf=self.shelf)

    def get_row(self):
        return (self.title, self.author, self.translator, self.publisher,
                self.publication_year, self.isbn, self.copies, self.shelf)
