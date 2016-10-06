from tkinter import StringVar

import bookcase_exceptions as exc
from bookcase_translations import Translations


class GuiBook(object):
    """
    Class that defines the book entity as viewed by User
    """
    def __init__(self):
        self._title = StringVar()
        self._author_last = StringVar()
        self._author_first = StringVar()
        self._trans_last = StringVar()
        self._trans_first = StringVar()
        self._publisher = StringVar()
        self._pub_year = StringVar()
        self._isbn = StringVar()
        self._num_of_copies = StringVar()
        self._shelf_row = StringVar()
        self._shelf_col = StringVar()
        self.num_of_copies = 1

    def get_object(self, name):
        return getattr(self, "_" + name)

    @property
    def title(self):
        return self._title.get()

    @title.setter
    def title(self, val):
        self._title.set(val)

    @property
    def author_last(self):
        return self._author_last.get()

    @author_last.setter
    def author_last(self, val):
        self._author_last.set(val)

    @property
    def author_first(self):
        return self._author_first.get()

    @author_first.setter
    def author_first(self, val):
        self._author_first.set(val)

    @property
    def trans_last(self):
        return self._trans_last.get()

    @trans_last.setter
    def trans_last(self, val):
        self._trans_last.set(val)

    @property
    def trans_first(self):
        return self._trans_first.get()

    @trans_first.setter
    def trans_first(self, val):
        self._trans_first.set(val)

    @property
    def publisher(self):
        return self._publisher.get()

    @publisher.setter
    def publisher(self, val):
        self._publisher.set(val)

    @property
    def pub_year(self):
        return self._pub_year.get()

    @pub_year.setter
    def pub_year(self, val):
        self._pub_year.set(val)

    @property
    def isbn(self):
        return self._isbn.get()

    @isbn.setter
    def isbn(self, val):
        self._isbn.set(val)

    @property
    def num_of_copies(self):
        return self._num_of_copies.get()

    @num_of_copies.setter
    def num_of_copies(self, val):
        self._num_of_copies.set(val)

    @property
    def shelf_row(self):
        return self._shelf_row.get()

    @shelf_row.setter
    def shelf_row(self, val):
        self._shelf_row.set(val)

    @property
    def shelf_col(self):
        return self._shelf_col.get()

    @shelf_col.setter
    def shelf_col(self, val):
        self._shelf_col.set(val)

    def get_author_in_schema_form(self):
        """
        Wrapper method to convert author attribute from User to DB format
        :return: author name in DB format
        """
        return self.get_name_in_schema_form(self.author_last, self.author_first)

    def get_translator_in_schema_form(self):
        """
        Wrapper method to convert translator attribute from User to DB format
        :return: translator name in DB format
        """
        return self.get_name_in_schema_form(self.trans_last, self.trans_first)

    @staticmethod
    def get_name_in_schema_form(last, first):
        """
        Method to convert name attributes from User to DB format
        :return: name in DB format
        """
        return "{last} {first}".format(last=last, first=first)

    def get_shelf_in_schema_form(self):
        """
        Method to convert shelf attributes from User to DB format
        :return: shelf in DB format
        """
        return "{row}-{column}".format(row=self.shelf_row,
                                       column=self.shelf_col)

    @staticmethod
    def get_name_from_schema(name):
        """
        Method to convert name attribute from DB to User format
        :return: tuple containing last and first name
        """
        return name.split(" ")

    @staticmethod
    def get_shelf_from_schema(shelf):
        """
        Method to convert shelf attribute from DB to User format
        :return: tuple containing shelf's row and column
        """
        return shelf.split('-')

    def init_entries_from_book(self, book):
        self.title = book.title
        self.author_last, self.author_first = self.get_name_from_schema(book.author)
        self.trans_last, self.trans_first = self.get_name_from_schema(book.translator)
        self.publisher = book.publisher
        self.pub_year = book.publication_year if book.publication_year > 0 else ""
        self.isbn = book.isbn
        self.num_of_copies = book.copies
        self.shelf_row, self.shelf_col = self.get_shelf_from_schema(book.shelf)

    def get_book_attributes_in_schema_form(self):
        """
        Method to convert attribute from User to DB format
        :return: tuple containing book attributes
        """
        title = self.title
        author = self.get_author_in_schema_form()
        translator = self.get_translator_in_schema_form()
        publisher = self.publisher
        publication_year = int(self.pub_year) if self.pub_year else -1
        isbn = self.isbn
        shelf = self.get_shelf_in_schema_form()
        copies = int(self.num_of_copies)
        return title, author, translator, publisher, publication_year, isbn, copies, shelf

    def clear_entries(self):
        """
        Resets book entries
        """
        self.title = ""
        self.author_last = ""
        self.author_first = ""
        self.trans_last = ""
        self.trans_first = ""
        self.publisher = ""
        self.pub_year = ""
        self.isbn = ""
        self.num_of_copies = 1
        self.shelf_row = ""
        self.shelf_col = ""

    def validate_book_inputs(self):
        """
        Runs input validations
        """
        self.mandatory_fields_set()
        self.names_have_no_spaces()
        self.translator_is_valid()
        self.year_is_valid()
        self.isbn_is_valid()
        self.shelf_is_valid()
        self.copies_is_valid()

    def mandatory_fields_set(self):
        """
        Validates that Title and Author fields are not empty
        :raises: InvalidInputException
        """
        if not self.title or not self.author_last or not self.author_first:
            raise exc.InvalidInputException(Translations().mandatory_fields_warn)

    def names_have_no_spaces(self):
        """
        Validates that names include no spaces
        :raises: InvalidInputException
        """
        if " " in "".join([self.author_first, self.author_last, self.trans_last, self.trans_first, self.publisher]):
            raise exc.InvalidInputException(Translations().no_spaces_in_names_warn)

    def translator_is_valid(self):
        """
        Validates that both first and last translator's name are set
        :raises: InvalidInputException
        """
        if bool(self.trans_first) != bool(self.trans_last):
            raise exc.InvalidInputException(Translations().translator_validation_warn)

    def year_is_valid(self):
        """
        Validates that year has the format XXXX where X is a number
        :raises: InvalidInputException
        """
        if not self.pub_year:
            return
        if len(self.pub_year) > 4 or not self.pub_year.isdigit():
            raise exc.InvalidInputException(Translations().year_validation_warning)

    def isbn_is_valid(self):
        """
        Validates that ISBN has the valid number of digits (10 for old format, 13 for new)
        :raises: InvalidInputException
        """
        if not self.isbn:
            return
        if len(self.isbn) not in (10, 13) or not self.isbn.isdigit():
            raise exc.InvalidInputException(Translations().isbn_validation_warn)

    def shelf_is_valid(self):
        """
        Validates that both shelf's row and column are set and are numbers
        :raises: InvalidInputException
        """
        if self.shelf_row and self.shelf_col:
            if not self.shelf_row.isdigit() or not self.shelf_col.isdigit():
                raise exc.InvalidInputException(Translations().shelf_no_numbers_warn)
        else:
            if bool(self.shelf_col) != bool(self.shelf_row):
                raise exc.InvalidInputException(Translations().shelf_row_col_not_set_warn)

    def copies_is_valid(self):
        """
        Validates that number of copies is a number greater or equal to 1
        :raises: InvalidInputException
        """
        if not self.num_of_copies.isdigit() or int(self.num_of_copies) < 1:
            raise exc.InvalidInputException(Translations().num_of_copies_warn)

    def changed(self, book):
        """
        Detects any changes made in book fields compared to the book from DB
        :param book: book loaded from DB
        :return: True if any field is changed else False
        """
        (title, author, translator, publisher,
         publication_year, isbn, copies, shelf) = self.get_book_attributes_in_schema_form()
        checks = [book.title != title.upper(),
                  book.author != author.upper(),
                  book.translator != translator.upper(),
                  book.publisher != publisher.upper(),
                  book.publication_year != publication_year,
                  book.isbn != isbn.upper(),
                  book.copies != copies,
                  book.shelf != shelf.upper()]
        return any(checks)

    def update_book(self, book):
        """
        Migrate changes in fields to DB entry
        :param book: book loaded from DB
        """
        (title, author, translator, publisher,
         publication_year, isbn, copies, shelf) = self.get_book_attributes_in_schema_form()
        book.title = title
        book.author = author
        book.translator = translator
        book.publisher = publisher
        book.publication_year = publication_year
        book.isbn = isbn
        book.copies = copies
        book.shelf = shelf
