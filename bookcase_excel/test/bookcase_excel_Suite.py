import os
import unittest
from bookcase_excel.bookcase_excel import Excel
import bookcase_exceptions as exc


class BookcaseExcelSuite(unittest.TestCase):
    def setUp(self):
        self.bookcase_excel = Excel(path="")
        self.filename = "bookcase_test_lib.xlsx"
        self.input_data = ((1, 2, 3, 4), (5, 6, 7, 8))

    def tearDown(self):
        if os.path.exists(self.filename):
            os.remove(self.filename)

    def test_invalid_filename(self):
        try:
            self.bookcase_excel.validate_filename("invalid.xlsx")
            self.fail()
        except exc.InvalidInputException:
            pass

    def test_valid_filename(self):
        try:
            self.bookcase_excel.validate_filename(self.filename)
        except exc.InvalidInputException:
            self.fail()

    def test_write_file(self):
        self.bookcase_excel.write_excel("test_lib", self.input_data)
        self.assertTrue(os.path.exists(self.filename))

        read_data = self.bookcase_excel.read_excel(self.filename)
        self.assertEqual(read_data, self.input_data)
