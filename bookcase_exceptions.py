class BookcaseManagerException(Exception):
    pass


class InvalidInputException(BookcaseManagerException):
    pass


class NotBookcaseExcel(BookcaseManagerException):
    pass
