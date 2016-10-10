import bookcase_lib as lib


class Translations(object, metaclass=lib.Singleton):
    def __init__(self):
        self.author_first_name_desc = {"en": '* Author First Name',
                                       "gr": '* Όνομα Συγγραφέα'}
        self.author_last_name_desc = {"en": '* Author Last Name',
                                      "gr": '* Επίθετο Συγγραφέα'}
        self.author_text = {"en": 'Author',
                            "gr": 'Συγγραφέας'}
        self.book_deleted_msg = {"en": 'Book Deleted',
                                 "gr": 'Το βιβλίο διαφράφηκε'}
        self.book_saved_msg = {"en": 'Book Saved',
                               "gr": 'Το βιβλίο αποθηκεύτηκε'}
        self.cancel_text = {"en": 'Cancel',
                            "gr": 'Άκυρο'}
        self.create_book_button_desc = {"en": 'Create a new book entry',
                                        "gr": 'Δημιουργία Νέου Βιβλίου'}
        self.create_button_desc = {"en": 'Create a new Bookcase Database',
                                   "gr": 'Δημιουργία Καινούργιας Βιβλιοθήκης'}
        self.create_window_title = {"en": 'Create',
                                    "gr": 'Δημιουργία'}
        self.delete_confirm_msg = {"en": 'Are you sure you want to delete: ',
                                   "gr": 'Είστε σίγουροι ότι θέλετε να διαγράψετε το βιβλίο: '}
        self.delete_text = {"en": 'Delete',
                            "gr": 'Διαγραφή'}
        self.enter_db_name_msg = {"en": 'Enter DB Name:',
                                  "gr": 'Επιλέξτε όνομα νέας βιβλιοθήκης:'}
        self.exit_button_desc = {"en": 'Close Loaded Database',
                                 "gr": 'Κλείσιμο ανοιχτής βιβλιοθήκης'}
        self.exported_to = {"en": 'Successfully Exported to ',
                            "gr": 'Επιτυχής εξαγωγή στο '}
        self.export_excel = {"en": 'Export to Excel',
                             "gr": 'Εξαγωγή σε Excel'}
        self.found = {"en": 'Found',
                      "gr": 'Βρέθηκαν'}
        self.genre_text = {"en": "Genre",
                           "gr": "Είδος"}
        self.imported_from = {"en": 'Successfully Imported from ',
                              "gr": 'Επιτυχής Εισαγωγή από '}
        self.import_excel = {"en": 'Import from Excel',
                             "gr": 'Εισαγωγή από Excel'}
        self.import_export_desc = {"en": 'Import/Export Bookcase',
                                   "gr": 'Εισαγωγή/Εξαγωγή βιβλιοθήκης'}
        self.invalid_xl_msg = {"en": "Excel file not created by Bookcase Manager",
                               "gr": "Το αρχείο δεν έχει δημιουργηθεί από το πρόγραμμα"}
        self.isbn_validation_warn = {"en": 'Invalid ISBN format - Must be 10 or 13 digit long',
                                     "gr": 'Το ISBN πρέπει να αποτελείται από 10 ή 13 ψηφία'}
        self.mandatory_fields_warn = {"en": 'Fields with asterisk (*) are mandatory',
                                      "gr": 'Τα πεδία με αστερίσκο (*) είναι υποχρεωτικά'}
        self.no_books_found_msg = {"en": 'No books found matching the search criteria',
                                   "gr": 'Δε βρέθηκαν βιβλία που να ταιριάζουν στα κριτήρια αναζήτησης'}
        self.no_file_found_msg = {"en": 'No matching files found under ',
                                  "gr": 'Δε βρέθηκαν αρχεία στο '}
        self.no_spaces_in_names_warn = {"en": 'Use - instead of spaces in names',
                                        "gr": 'Χρησιμοποιήστε παύλα αντί για κενό στα ονόματα'}
        self.num_of_copies_desc = {"en": 'Num of Copies',
                                   "gr": 'Αντίτυπα'}
        self.num_of_copies_warn = {"en": 'Number of copies must be a number greater than 1',
                                   "gr": 'Ο αριθμός αντιτύπων πρέπει να είναι μεγαλύτερος ίσος του 1'}
        self.ok_text = {"en": 'Ok',
                        "gr": 'Εντάξει'}
        self.open_button_desc = {"en": 'Load an existing Bookcase Database',
                                 "gr": 'Φόρτωση Βιβλιοθήκης'}
        self.open_window_title = {"en": 'Open',
                                  "gr": 'Άνοιγμα'}
        self.publication_year_desc = {"en": 'Publication Year',
                                      "gr": 'Έτος έκδοσης'}
        self.publisher_desc = {"en": 'Publisher',
                               "gr": 'Εκδοτικός Οίκος'}
        self.save_text = {"en": 'Save',
                          "gr": 'Αποθήκευση'}
        self.search_button_desc = {"en": 'Search for book(s)',
                                   "gr": 'Αναζήτηση Βιβλίων'}
        self.search_complete_msg = {"en": 'books - Double click on book to open',
                                    "gr": 'βιβλία - '
                                          'Πατήστε διπλό κλικ πάνω στο βιβλίο που θέλετε να επεξεργαστείτε'}
        self.search_text = {"en": 'Search',
                            "gr": 'Αναζήτηση'}
        self.shelf_col_desc = {"en": 'Shelf Column',
                               "gr": 'Ράφι Στήλη'}
        self.shelf_no_numbers_warn = {"en": 'Both Shelf column and row must be numbers',
                                      "gr": 'Και η γραμμή και η στήλη πρέπει να είναι αριθμοί'}
        self.shelf_row_col_not_set_warn = {"en": 'Both Shelf column and row must be set',
                                           "gr": 'Το ράφι πρέπει να αποτελείται απο γραμμή ΚΑΙ στήλη'}
        self.shelf_row_desc = {"en": 'Shelf Row',
                               "gr": 'Ράφι Γραμμή'}
        self.shelf_text = {"en": 'Shelf (Row-Column)',
                           "gr": 'Ράφι (Γραμμή-Στήλη)'}
        self.title_msg = {"en": '* Title',
                          "gr": '* Τίτλος'}
        self.title_text = {"en": 'Title',
                           "gr": 'Τίτλος'}
        self.translator_first_name_desc = {"en": 'Translator First Name',
                                           "gr": 'Όνομα Μεταφραστη'}
        self.translator_last_name_desc = {"en": 'Translator Last Name',
                                          "gr": 'Επίθετο Μεταφραστή'}
        self.translator_validation_warn = {"en": 'Both First and Last translator names should be set',
                                           "gr": 'Ο Μεταφραστλης πρέπεί να έχει όνομα και επώνυμο'}
        self.welcome_msg = {"en": 'Welcome',
                            "gr": 'Καλώς ήρθατε!'}
        self.year_validation_warning = {"en": 'Invalid year format',
                                        "gr": 'Λάθος Έτος Έκδοσης'}

    def __getattribute__(self, item):
        text = super(Translations, self).__getattribute__(item)
        return text[get_language()]


def get_language():
    try:
        return lib.Configuration().get_config("gui_language")
    except KeyError:
        return "en"

