import unittest
from bookcase_db.bookcase_db import BookcaseDbManager
import bookcase_exceptions as exc
import os


class BookcaseDbManagerTestSuite(unittest.TestCase):
    def setUp(self):
        self.manager = BookcaseDbManager()
        self.manager.create_db()

    def tearDown(self):
        self.manager.clear_table()
        self.manager.cleanup()

    def add_three_books(self):
        self.manager.add_book(title="Lord of the Rings: The fellowship of the Ring", author="J.R.Tolkien",
                              isbn="978-960-04-0366-4")
        self.manager.add_book(title="Lord of the Rings: The return of the king", author="J.R.Tolkien",
                              isbn="978-960-04-0438-8")
        self.manager.add_book(title="Pride and Prejudice", author="Jane Austin",
                              isbn="978-618-02-0088-1", shelf="1-1")

    @classmethod
    def tearDownClass(cls):
        os.remove("bookcase.db")

    def test_create_db(self):
        self.assertTrue(os.path.exists("bookcase.db"))

    def test_add_book(self):
        self.manager.add_book(title="Lord of the Rings", author="J.R.Tolkien")
        rows = self.manager.get_all_books()
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[-1].title, "Lord of the Rings".upper())

    def test_add_book_no_author(self):
        try:
            self.manager.add_book(title="Lord of the Rings")
            self.fail()
        except exc.InvalidInputException:
            pass

    def test_add_two_books(self):
        self.add_three_books()
        rows = self.manager.get_all_books()
        self.assertEqual(len(rows), 3)

    def test_search_by_title(self):
        self.add_three_books()
        result = self.manager.search_by_title("Pride and Prejudice")
        self.assertEqual(len(result), 1)

    def test_search_by_title_keyword(self):
        self.add_three_books()
        result = self.manager.search_by_title("Lord of the rings")
        self.assertEqual(len(result), 2)

    def test_search_by_author(self):
        self.add_three_books()
        result = self.manager.search_by_author("Tolkien")
        self.assertEqual(len(result), 2)

    def test_search_by_isbn(self):
        self.add_three_books()
        result = self.manager.search_by_isbn("978-960-04-0366-4")
        self.assertEqual(len(result), 1)
        self.assertEqual(result[-1].title, "Lord of the Rings: The fellowship of the Ring".upper())

    def test_search_by_shelf(self):
        self.add_three_books()
        result = self.manager.search_by_shelf("1-1")
        self.assertEqual(len(result), 1)

    def test_delete_book(self):
        self.add_three_books()
        result = self.manager.search_by_isbn("978-960-04-0366-4")
        self.manager.delete_book(result[-1])
        rows = self.manager.get_all_books()
        self.assertEqual(len(rows), 2)

    def test_dump_table(self):
        self.add_three_books()
        table = self.manager.dump_table()
        print(table)
        self.assertEqual(len(table), 4)
        self.assertEqual(table[0], ("title", "author", "translator", "publisher",
                                    "publication_year", "isbn", "copies", "genre", "shelf"))

    def test_get_indexes_for_book_attribute_in_order(self):
        header = ("title", "author", "translator", "publisher", "publication_year", "isbn", "copies", "shelf")
        result = self.manager.get_indexes_for_book_attributes(header)
        self.assertEqual(result["title"], 0)
        self.assertEqual(result["author"], 1)
        self.assertEqual(result["translator"], 2)
        self.assertEqual(result["publisher"], 3)
        self.assertEqual(result["publication_year"], 4)
        self.assertEqual(result["isbn"], 5)
        self.assertEqual(result["copies"], 6)
        self.assertEqual(result["shelf"], 7)

    def test_get_indexes_for_book_attribute_out_of_order(self):
        header = ("author", "translator", "publication_year", "isbn", "publisher", "copies", "shelf", "title")
        result = self.manager.get_indexes_for_book_attributes(header)
        self.assertEqual(result["title"], 7)
        self.assertEqual(result["author"], 0)
        self.assertEqual(result["translator"], 1)
        self.assertEqual(result["publisher"], 4)
        self.assertEqual(result["publication_year"], 2)
        self.assertEqual(result["isbn"], 3)
        self.assertEqual(result["copies"], 5)
        self.assertEqual(result["shelf"], 6)

    def test_import_table(self):
        self.add_three_books()
        self.add_three_books()
        table = self.manager.dump_table()
        self.manager.import_table(table)
        self.assertEqual(len(self.manager.get_all_books()), 12)