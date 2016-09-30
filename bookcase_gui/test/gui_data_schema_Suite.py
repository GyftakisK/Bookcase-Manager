import unittest
import tkinter as tk
from bookcase_exceptions import InvalidInputException
from bookcase_gui.gui_data_schema import GuiBook
from bookcase_db.data_schema import Book


class GuiDataSchemaTestSuite(unittest.TestCase):
    def setUp(self):
        self.root = tk.Tk()
        self.gui_book = GuiBook()
        self.gui_book.title = "title"
        self.gui_book.author_last = "author_last"
        self.gui_book.author_first = "author_first"
        self.gui_book.trans_last = "trans_last"
        self.gui_book.trans_first = "trans_first"
        self.gui_book.publisher = "publisher"
        self.gui_book.pub_year = "1111"
        self.gui_book.isbn = "0123456789"
        self.gui_book.num_of_copies = "3"
        self.gui_book.shelf_row = "1"
        self.gui_book.shelf_col = "2"

    def tearDown(self):
        self.root.quit()

    def test_get_book_attributes_in_schema_form(self):
        (title, author, translator, publisher,
         publication_year, isbn, copies, shelf) = self.gui_book.get_book_attributes_in_schema_form()
        self.assertEqual(title, "title")
        self.assertEqual(author, "author_last author_first")
        self.assertEqual(translator, "trans_last trans_first")
        self.assertEqual(publisher, "publisher")
        self.assertEqual(publication_year, 1111)
        self.assertEqual(isbn, "0123456789")
        self.assertEqual(copies, 3)
        self.assertEqual(shelf, "1-2")

    def test_mandatory_fields_are_set_all_set(self):
        try:
            self.gui_book.mandatory_fields_set()
        except InvalidInputException as e:
            self.fail(e)

    def test_mandatory_fields_are_set_no_title(self):
        try:
            self.gui_book.title = ""
            self.gui_book.mandatory_fields_set()
            self.fail()
        except InvalidInputException as e:
            print(e)

    def test_mandatory_fields_are_set_no_author_first(self):
        try:
            self.gui_book.author_first = ""
            self.gui_book.mandatory_fields_set()
            self.fail()
        except InvalidInputException as e:
            print(e)

    def test_mandatory_fields_are_set_no_author_last(self):
        try:
            self.gui_book.author_last = ""
            self.gui_book.mandatory_fields_set()
            self.fail()
        except InvalidInputException as e:
            print(e)

    def test_translator_is_valid_both_set(self):
        try:
            self.gui_book.translator_is_valid()
        except InvalidInputException as e:
            self.fail(e)

    def test_translator_is_valid_last_not_set(self):
        try:
            self.gui_book.trans_last = ""
            self.gui_book.translator_is_valid()
            self.fail()
        except InvalidInputException as e:
            print(e)

    def test_year_is_valid_pass(self):
        try:
            self.gui_book.year_is_valid()
        except InvalidInputException as e:
            self.fail(e)

    def test_year_is_valid_invalid_length(self):
        self.gui_book.pub_year = "12345"
        try:
            self.gui_book.year_is_valid()
            self.fail()
        except InvalidInputException as e:
            print(e)

    def test_year_is_valid_illegal_char(self):
        self.gui_book.pub_year = "1a00"
        try:
            self.gui_book.year_is_valid()
            self.fail()
        except InvalidInputException as e:
            print(e)

    def test_isbn_is_valid_pass_old_len(self):
        try:
            self.gui_book.isbn_is_valid()
        except InvalidInputException as e:
            self.fail(e)

    def test_isbn_is_valid_pass_new_len(self):
        self.gui_book.isbn = "0123456789012"
        try:
            self.gui_book.isbn_is_valid()
        except InvalidInputException as e:
            self.fail(e)

    def test_isbn_is_valid_invalid_length(self):
        self.gui_book.isbn = "01234567890"
        try:
            self.gui_book.isbn_is_valid()
            self.fail()
        except InvalidInputException as e:
            print(e)

    def test_isbn_is_valid_illegal_char(self):
        self.gui_book.isbn = "01234a6789"
        try:
            self.gui_book.isbn_is_valid()
            self.fail()
        except InvalidInputException as e:
            print(e)

    def test_shelf_is_valid_pass(self):
        try:
            self.gui_book.shelf_is_valid()
        except InvalidInputException as e:
            self.fail(e)

    def test_shelf_is_valid_one_not_set(self):
        self.gui_book.shelf_col = ""
        try:
            self.gui_book.shelf_is_valid()
            self.fail()
        except InvalidInputException as e:
            print(e)

    def test_shelf_is_valid_pass_both_not_set(self):
        self.gui_book.shelf_col = ""
        self.gui_book.shelf_row = ""
        try:
            self.gui_book.shelf_is_valid()
        except InvalidInputException as e:
            self.fail(e)

    def test_shelf_is_valid_one_nan(self):
        self.gui_book.shelf_col = "a"
        try:
            self.gui_book.shelf_is_valid()
            self.fail()
        except InvalidInputException as e:
            print(e)

    def test_shelf_is_valid_both_nan(self):
        self.gui_book.shelf_col = "a"
        self.gui_book.shelf_row = "a"
        try:
            self.gui_book.shelf_is_valid()
            self.fail()
        except InvalidInputException as e:
            print(e)

    def test_copies_is_valid_pass(self):
        try:
            self.gui_book.copies_is_valid()
        except InvalidInputException as e:
            self.fail(e)

    def test_copies_is_valid_zero(self):
        self.gui_book.num_of_copies = "0"
        try:
            self.gui_book.copies_is_valid()
            self.fail()
        except InvalidInputException as e:
            print(e)

    def test_copies_is_valid_letter(self):
        self.gui_book.num_of_copies = "a"
        try:
            self.gui_book.copies_is_valid()
            self.fail()
        except InvalidInputException as e:
            print(e)

    def test_name_has_no_spaces(self):
        self.gui_book.author_first = "J. R."
        self.gui_book.author_last = " Tolkien "
        self.gui_book.trans_first = ""
        self.gui_book.trans_last = ""
        self.gui_book.publisher = "Guy Richie"
        try:
            self.gui_book.names_have_no_spaces()
            self.fail()
        except InvalidInputException as e:
            print(e)

    def test_changed(self):
        book = Book(author="AUTHOR_LAST AUTHOR_FIRST".upper(),
                    title="TITLE",
                    isbn="0123456789",
                    publication_year=1111,
                    publisher="PUBLISHER",
                    translator="TRANS_LAST TRANS_FIRST",
                    shelf="1-2",
                    copies=3)

        self.assertFalse(self.gui_book.changed(book))

        self.gui_book.title = "title2"

        self.assertTrue(self.gui_book.changed(book))

    def test_init_from_book(self):
        book = Book(author="AUTHOR_LAST AUTHOR_FIRST".upper(),
                    title="TITLE",
                    isbn="0123456789",
                    publication_year=1111,
                    publisher="PUBLISHER",
                    translator=" ",
                    shelf="-",
                    copies=3)

        self.gui_book.init_entries_from_book(book)
