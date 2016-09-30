import re
import openpyxl as xl

import bookcase_exceptions as exc
import bookcase_lib as lib


class Excel(object):
    def __init__(self, path=lib.FileManager().path):
        self.path = path

    @staticmethod
    def validate_filename(filename):
        exp = re.compile(r'(?<=bookcase_).*(?=\.xlsx)')
        name = re.search(exp, filename)
        if not name:
            raise exc.NotBookcaseExcel
        return name

    def read_excel(self, filename):
        self.validate_filename(filename)
        workbook = xl.load_workbook(self.path + filename)
        result = []
        for row in workbook.active.iter_rows():
            result.append(tuple(cell.value for cell in row))
        return tuple(result)

    def write_excel(self, name, array):
        workbook = xl.Workbook()
        worksheet = workbook.active
        for row_num, row in enumerate(array):
            for col_num, value in enumerate(row):
                worksheet.cell(row=row_num + 1, column=col_num + 1, value=value)
        file = self.path + "bookcase_{name}.xlsx".format(name=name)
        workbook.save(file)
        return file
