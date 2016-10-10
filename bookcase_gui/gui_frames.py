from collections import OrderedDict
import tkinter as tk
import tkinter.ttk as ttk

from bookcase_db.bookcase_db import BookcaseDbManager
from bookcase_excel.bookcase_excel import Excel
from bookcase_exceptions import InvalidInputException
import bookcase_lib as lib
from bookcase_gui.gui_data_schema import GuiBook
from bookcase_translations import Translations
import bookcase_exceptions as exc


FONT_11_NORMAL = ('Verdana', 11, 'normal')
FONT_12_NORMAL = ('Verdana', 12, 'normal')
FONT_14_NORMAL = ('Verdana', 14, 'normal')


class ButtonToolbar(tk.Frame):
    """
    Base Frame class to create toolbars with buttons
    """
    def __init__(self, root):
        super(ButtonToolbar, self).__init__(root, bg="Light Grey")
        self.root = root
        self.photos = self.load_artifacts()

    def create_toolbar_button(self, photo, command=lambda: None, on_hover_text="", side=tk.LEFT):
        button = tk.Button(self, command=command)
        button.config(image=photo, width=30, height=30)
        button.pack(side=side, padx=2, pady=2)
        button.bind("<Enter>", lambda x: StatusBar().set_status_from_event(x, on_hover_text))
        button.bind("<Leave>", StatusBar().clear_status_from_event)
        return button

    @staticmethod
    def load_artifacts():
        photos = dict()
        for file in lib.FileManager().load_photos():
            photos[file] = tk.PhotoImage(file="artifacts/" + file)
        return photos


class MainToolbar(ButtonToolbar):
    """
    The main toolbar of the GUI
    """
    def __init__(self, root):
        super(MainToolbar, self).__init__(root)
        self.root = root
        self.db_view = None
        self.buttons = []

    def setup_toolbar(self):
        self.buttons.append(self.create_toolbar_button(self.photos["create.png"],
                                                       command=self.create_new_db,
                                                       on_hover_text=Translations().create_button_desc))
        self.buttons.append(self.create_toolbar_button(self.photos["open.png"],
                                                       command=self.click_open,
                                                       on_hover_text=Translations().open_button_desc))
        self.buttons.append(self.create_lang_button())

        self.pack(fill=tk.X, ipady=5)

    def clear_toolbar(self):
        for button in self.buttons:
            button.destroy()

    def create_lang_button(self):
        lang = lib.Configuration().get_config("gui_language")
        lang_changes = dict(gr="en", en="gr")
        return self.create_toolbar_button(self.photos[lang_changes[lang] + "_icon.png"],
                                          command=lambda: self.change_lang(lang_changes[lang]),
                                          side=tk.RIGHT)

    def change_lang(self, lang):
        """
        Method called when language button is pushed.
        Changes the GUI language
        :param lang: Language to be ser
        """
        lib.Configuration().set_config("gui_language", lang)
        self.clear_toolbar()
        self.setup_toolbar()

    def click_open(self):
        """
        Method called when open button is pushed.
        Creates an open pop-up window
        """
        top_level = tk.Toplevel()
        top_level.title(Translations().open_window_title)
        OpenFrame(top_level, self.open_selected_db, lib.FileManager().find_all_db_files()).create_layout()

    def open_selected_db(self, selection):
        """
        Callback method called from open or create pop-up window
        Creates a DB view Frame
        :param selection: the Db file to be loaded
        """
        db_name = selection.strip(".db")
        if self.db_view and self.db_view.db_name == db_name:
            return
        if self.db_view:
            self.db_view.close()
        self.db_view = DbView(self.root, db_name, self.on_db_view_close)
        self.db_view.create_db_view()

    def create_new_db(self):
        """
        Method called when create button is pushed.
        Creates a create pop-up window
        """
        top_level = tk.Toplevel()
        top_level.title(Translations().create_window_title)
        CreateDb(top_level, self.open_selected_db).create_layout()

    def cleanup(self):
        """
        Cleanup method called when window is closing
        """
        if self.db_view:
            self.db_view.cleanup()
            self.db_view = None

    def on_db_view_close(self):
        """
        Cleanup method called when DB view frame is destroyed
        """
        self.db_view = None


class DbView(ButtonToolbar):
    """
    Toolbar frame that manages the loaded DB
    """
    def __init__(self, root, name, on_close_cb_func):
        super(DbView, self).__init__(root)
        self.db_manager = BookcaseDbManager(lib.FileManager().path, db_name=name)
        self._db_name = name
        self.book_view = None
        self.search_view = None
        self.on_close_cb_func = on_close_cb_func

    @property
    def db_name(self):
        return self._db_name

    def create_db_view(self):
        self.db_manager.create_db()
        print(self.db_manager.db_name)
        label = tk.Label(self, bg="SteelBlue1", text=self.db_manager.db_name, font=FONT_12_NORMAL,
                         relief=tk.GROOVE)
        label.pack(fill=tk.X)

        self.create_toolbar_button(self.photos["edit.png"],
                                   command=self.open_book_view,
                                   on_hover_text=Translations().create_book_button_desc)
        self.create_toolbar_button(self.photos["file_search.png"],
                                   command=self.open_search_view,
                                   on_hover_text=Translations().search_button_desc)
        self.create_menu_button()
        self.create_toolbar_button(self.photos["exit_button.png"],
                                   command=self.close,
                                   on_hover_text=Translations().exit_button_desc)
        self.pack(fill=tk.X, ipady=5)

    def create_menu_button(self):
        button = tk.Menubutton(self)
        button.config(image=self.photos["import_export.png"], width=34, height=34, relief=tk.RAISED)
        button.menu = tk.Menu(button, tearoff=0)
        button["menu"] = button.menu
        button.bind("<Enter>", lambda x: StatusBar().set_status_from_event(x, Translations().import_export_desc))
        button.bind("<Leave>", StatusBar().clear_status_from_event)

        button.menu.add_command(label=Translations().import_excel, command=self.import_from_excel, font=FONT_12_NORMAL)
        button.menu.add_command(label=Translations().export_excel, command=self.export_to_excel, font=FONT_12_NORMAL)

        button.pack(side=tk.LEFT, padx=2, pady=2)

    def import_from_excel(self):
        """
        Method called when import Excel menu option is selected.
        Creates an open pop-up window
        """
        top_level = tk.Toplevel(self.root)
        OpenFrame(top_level, self.dump_excel_to_db, lib.FileManager().find_all_xlsx_files()).create_layout()

    def dump_excel_to_db(self, filename):
        """
        Callback method called from open window.
        Reads a table from excel and imports it to the database
        """
        table = Excel().read_excel(filename)
        self.db_manager.import_table(table)
        StatusBar().set_status(Translations().imported_from + filename)

    def export_to_excel(self):
        """
        Method called when export Excel menu option is selected.
        Gets a table dumped from DB and writes it to an excel workbook
        """
        table = self.db_manager.dump_table()
        file = Excel().write_excel(self.db_manager.db_name, table)
        StatusBar().set_status(Translations().exported_to + file)

    def open_book_view(self):
        """
        Method called when create book button is pushed.
        Creates a book view frame
        """
        if not self.book_view:
            if self.search_view:
                self.search_view.close()
            self.book_view = BookViewNew(self.root, self.db_manager, self.on_book_view_close)
            self.book_view.open_book_view()

    def open_search_view(self):
        """
        Method called when search book button is pushed.
        Creates a search view frame
        """
        if not self.search_view:
            if self.book_view:
                self.book_view.close()
            self.search_view = SearchView(self.root, self.db_manager, self.on_search_view_close)
            self.search_view.open_search_view()

    def cleanup(self):
        """
        Cleanup method called when window is closing
        """
        self.db_manager.cleanup()

    def close(self):
        """
        Method called when exit button is pushed.
        Runs cleanup operations
        """
        self.cleanup()
        if self.book_view:
            self.book_view.close()
        if self.search_view:
            self.search_view.close()
        self.on_close_cb_func()
        self.destroy()

    def on_book_view_close(self):
        """
        Cleanup method called when book view frame is destroyed
        """
        self.book_view = None

    def on_search_view_close(self):
        """
        Cleanup method called when search view frame is destroyed
        """
        self.search_view = None


class BookView(tk.Frame):
    """
    Base Frame Class for book view
    """
    def __init__(self, root, db_manager, on_close_cb_func):
        super(BookView, self).__init__(root)
        self.gui_book = GuiBook()

        self.entries_desc_grid_pref_var = OrderedDict(
            [(Translations().title_msg, (0, 0, 100, self.gui_book.get_object("title"))),
             (Translations().author_last_name_desc,
              (1, 0, 40, self.gui_book.get_object("author_last"))),
             (Translations().author_first_name_desc,
              (1, 2, 40, self.gui_book.get_object("author_first"))),
             (Translations().translator_last_name_desc,
              (2, 0, 40, self.gui_book.get_object("trans_last"))),
             (Translations().translator_first_name_desc,
              (2, 2, 40, self.gui_book.get_object("trans_first"))),
             (Translations().publisher_desc,
              (3, 0, 40, self.gui_book.get_object("publisher"))),
             (Translations().publication_year_desc,
              (3, 2, 40, self.gui_book.get_object("pub_year"))),
             ("ISBN", (4, 0, 40, self.gui_book.get_object("isbn"))),
             (Translations().num_of_copies_desc,
              (4, 2, 20, self.gui_book.get_object("num_of_copies"))),
             (Translations().genre_text, (5, 0, 40, self.gui_book.get_object("genre"))),
             (Translations().shelf_row_desc, (6, 0, 25, self.gui_book.get_object("shelf_row"))),
             (Translations().shelf_col_desc,
              (6, 2, 25, self.gui_book.get_object("shelf_col")))])
        self.db_manager = db_manager
        self.on_close_cb_func = on_close_cb_func
        self.buttons = None

    def open_book_view(self):
        """
        Creates book view layout as specified in self.entries_desc_grid_pref_var
        """
        StatusBar().clear_status()
        for key in self.entries_desc_grid_pref_var.keys():
            row, column, width, var = self.entries_desc_grid_pref_var[key]
            msg = tk.Message(self, text=key, width=100, justify=tk.RIGHT, font=FONT_11_NORMAL)
            msg.grid(row=row, column=column, padx=5, pady=5, sticky=tk.E)
            entry_grid_opts = dict(row=row, column=column + 1, pady=5, sticky=tk.W)
            if row == 0:
                entry_grid_opts['columnspan'] = 3
            tk.Entry(self, width=width, textvariable=var, font=FONT_11_NORMAL).grid(**entry_grid_opts)

        buttons_frame = ButtonFrame(self)
        buttons_frame.create_buttons(self.buttons)
        buttons_frame.grid(row=row + 1, columnspan=4)

        self.pack(ipadx=40, ipady=10)

    def close(self):
        """
        Method called when cancel button is pushed
        """
        self.on_close_cb_func()
        self.destroy()


class BookViewNew(BookView):
    """
    BookView frame used when a new book is created
    """
    def __init__(self, *args):
        super(BookViewNew, self).__init__(*args)
        self.buttons = OrderedDict(
            [(Translations().save_text, self.save_new_book_to_db), (Translations().cancel_text, self.close)])

    def save_new_book_to_db(self):
        """
        Method called when save button is pushed
        Validates the input and inserts a new book to DB
        """
        try:
            self.gui_book.validate_book_inputs()
        except InvalidInputException as e:
            StatusBar().set_status(e)
            return
        (title, author, translator, publisher,
         publication_year, isbn, copies, shelf) = self.gui_book.get_book_attributes_in_schema_form()
        self.db_manager.add_book(title, author, translator=translator, publication_year=publication_year,
                                 isbn=isbn, publisher=publisher, shelf=shelf, copies=copies)
        self.gui_book.clear_entries()
        StatusBar().set_status(Translations().book_saved_msg)


class BookViewOpen(BookView):
    """
    BookView frame used when a book from DB is displayed
    """
    def __init__(self, root, db_manager, on_close_cb_func, book):
        super(BookViewOpen, self).__init__(root, db_manager, on_close_cb_func)
        self.root = root
        self.buttons = OrderedDict([(Translations().save_text, self.save_changes_to_db),
                                    (Translations().delete_text, self.delete),
                                    (Translations().cancel_text, self.close)])
        self.book = book
        self.gui_book.init_entries_from_book(book)

    def save_changes_to_db(self):
        """
        Method called when save button is pushed
        Validates the input and saves the changes to DB
        """
        try:
            self.gui_book.validate_book_inputs()
        except InvalidInputException as e:
            StatusBar().set_status(e)
            return
        if self.gui_book.changed(self.book):
            self.gui_book.update_book(self.book)
            self.db_manager.save_book()
        StatusBar().set_status(Translations().book_saved_msg)

    def delete(self):
        """
        Method called when save button is pushed
        Creates a delete book prompt
        """
        top_level = tk.Toplevel(self)
        DeleteBookPrompt(top_level, self.delete_book, self.book.title).create_layout()

    def delete_book(self):
        """
        Callback method for delete book prompt
        Deletes selected book from DB
        """
        self.db_manager.delete_book(self.book)
        StatusBar().set_status(Translations().book_deleted_msg)
        self.close()

    def close(self):
        """
        Method called when cancel button is called
        """
        self.on_close_cb_func()
        self.root.destroy()


class SearchView(tk.Frame):
    """
    Frame class used to facilitate queries to the DB and change book entries
    """
    def __init__(self, root, db_manager, on_close_cb_func):
        super(SearchView, self).__init__(root)
        self.choices = (Translations().title_text, Translations().author_text, "ISBN",
                        Translations().shelf_text, Translations().genre_text)
        self.option = ttk.Combobox(self, values=self.choices, state="readonly", font=FONT_11_NORMAL)
        self.option.set(self.choices[0])
        self.search_str = tk.Entry(self, width=60, font=FONT_11_NORMAL)
        self.listbox_with_scroll = ListboxWithScroll(self, 100, FONT_11_NORMAL, self.open_book)
        self.db_manager = db_manager
        self.on_close_cb_func = on_close_cb_func
        self.root = root
        self.books = None

    def open_search_view(self):
        self.option.grid(row=0, column=0, pady=10, sticky=tk.E)
        self.search_str.grid(row=0, column=1, pady=10)

        buttons_frame = ButtonFrame(self)
        buttons = OrderedDict(
            [(Translations().search_text, self.perform_db_search), (Translations().cancel_text, self.close)])
        buttons_frame.create_buttons(buttons)
        buttons_frame.grid(row=1, columnspan=2)

        self.listbox_with_scroll.create_layout()
        self.listbox_with_scroll.grid(row=2, columnspan=2)

        self.pack(ipadx=40, ipady=10)

    def get_db_search_results(self):
        """
        :returns: list of entries if no search string is given else specific search results
        """
        if not self.search_str.get():
            return self.db_manager.get_all_books()
        else:
            return self.search_by(self.option.get(), self.search_str.get())

    def perform_db_search(self):
        """
        Method that performs DB search when search button is pushed
        """
        self.listbox_with_scroll.clear()
        self.books = self.get_db_search_results()
        if not self.books:
            StatusBar().set_status(Translations().no_books_found_msg)
        else:
            StatusBar().set_status("{found} {num} {msg}".format(found=Translations().found,
                                                                num=len(self.books),
                                                                msg=Translations().search_complete_msg))
            self.listbox_with_scroll.insert_results(self.books)

    def search_by(self, option, string):
        """
        Performs the search based on the selected search type
        :parameter option: Option to select attribute for DB search
        :parameter string: The search string
        :returns list of book entries
        """
        if option == Translations().title_text:
            return self.db_manager.search_by_title(string)
        if option == Translations().author_text:
            return self.db_manager.search_by_author(string)
        if option == "ISBN":
            return self.db_manager.search_by_isbn(string)
        if option == Translations().shelf_text:
            return self.db_manager.search_by_shelf(string)
        if option == Translations().genre_text:
            return self.db_manager.search_by_genre(string)


    def open_book(self, event):
        """
        Method called when a book entry is double clicked
        Creates a pop-up book view window
        """
        top_level = tk.Toplevel(self.root)
        book_view = BookViewOpen(top_level, self.db_manager, self.perform_db_search,
                                 self.books[self.listbox_with_scroll.get_selection()])
        book_view.open_book_view()
        book_view.pack(fill=tk.BOTH)

    def close(self):
        """
        Method called when cancel button is pushed
        """
        self.on_close_cb_func()
        self.destroy()


class ButtonFrame(tk.Frame):
    """
    Frame class that creates a specified number of buttons
    """
    def __init__(self, root):
        super(ButtonFrame, self).__init__(root)

    def create_buttons(self, buttons):
        """
        :parameter buttons: Ordered Dict containing the button text and action
        """
        for text, command in buttons.items():
            button = tk.Button(self, command=command)
            button.config(text=text, width=10, height=2, font=FONT_11_NORMAL)
            button.pack(side=tk.LEFT, padx=8, pady=10)


class StatusBar(tk.Frame, metaclass=lib.Singleton):
    """
    Singleton Frame class that creates a status bar frame
    """
    def __init__(self, root=None):
        super(StatusBar, self).__init__(root)
        self._text = tk.StringVar()
        self.label = tk.Label(self, bd=1, relief=tk.SUNKEN, anchor=tk.W,
                              textvariable=self._text, font=FONT_14_NORMAL)
        self._text.set(Translations().welcome_msg)
        self.label.pack(fill=tk.X)

    def set_status(self, text):
        self._text.set(text)

    def clear_status(self):
        self.set_status("")

    def set_status_from_event(self, event, text):
        self.set_status(text)

    def clear_status_from_event(self, event):
        self.clear_status()


class PopUpFrame(tk.Frame):
    """
    Base Frame Class for pop-up windows
    """
    def __init__(self, root, caller_cb_func):
        super(PopUpFrame, self).__init__(root)
        self.root = root
        self.caller_cb_func = caller_cb_func

    def create_layout(self):
        raise NotImplementedError


class OpenFrame(PopUpFrame):
    """
    Pop-up Window to load files
    """
    def __init__(self, root, caller_cd_func, choices):
        super(OpenFrame, self).__init__(root, caller_cd_func)
        self.choices = choices

    def create_layout(self):
        listbox = tk.Listbox(self, width=60, font=FONT_11_NORMAL)
        listbox.grid(row=0, column=0, padx=10, pady=15)

        if not self.choices:
            listbox.insert(tk.END, Translations().no_file_found_msg + lib.FileManager().path)
            ok_button_command = self.root.destroy
        else:
            for choice in self.choices:
                listbox.insert(tk.END, choice)
            ok_button_command = lambda: self.open_selection(listbox.get(listbox.curselection()))

        button_frame = ButtonFrame(self)
        buttons = OrderedDict(
            [(Translations().ok_text, ok_button_command), (Translations().cancel_text, self.root.destroy)])
        button_frame.create_buttons(buttons)
        button_frame.grid(row=1, column=0)

        self.pack()

    def open_selection(self, selection):
        """
        Method called when ok button is pushed
        Calls the cb function registered during initialization
        """
        if not selection:
            return
        try:
            self.caller_cb_func(selection)
        except exc.BookcaseManagerException as e:
            StatusBar().set_status(e)
            return
        self.root.destroy()


class CreateDb(PopUpFrame):
    """
    Pop-up Window to create a new DB
    """
    def create_layout(self):
        message = tk.Message(self, text=Translations().enter_db_name_msg, width=200,
                             font=FONT_12_NORMAL, justify=tk.CENTER)
        message.grid(row=0, column=0, padx=20, pady=5)

        database_name = tk.Entry(self, width=30, font=FONT_12_NORMAL, justify=tk.CENTER)
        database_name.grid(row=1, column=0, padx=20, pady=5)

        ok_button_command = lambda: self.create_db(database_name.get())

        button_frame = ButtonFrame(self)
        buttons = OrderedDict(
            [(Translations().ok_text, ok_button_command), (Translations().cancel_text, self.root.destroy)])
        button_frame.create_buttons(buttons)
        button_frame.grid(row=2, column=0)

        self.pack()

    def create_db(self, selection):
        """
        Method called when ok button is pushed
        Calls the cb function registered during initialization
        """
        if not selection:
            return
        try:
            self.caller_cb_func(selection)
        except exc.InvalidInputException as e:
            StatusBar().set_status(e)
            return
        self.root.destroy()


class DeleteBookPrompt(PopUpFrame):
    """
    Pop-up Window to delete a book form DB
    """
    def __init__(self, root, caller_cb_func, book_title):
        super(DeleteBookPrompt, self).__init__(root, caller_cb_func)
        self.book_title = book_title

    def create_layout(self):
        delete_message = tk.Message(self.root,
                                    text="{msg} {title}?".format(msg=Translations().delete_confirm_msg,
                                                                 title=self.book_title),
                                    width=200, justify=tk.CENTER, font=FONT_12_NORMAL)
        delete_message.pack(fill=tk.X, padx=10, pady=5)
        buttons = ButtonFrame(self.root)
        buttons.create_buttons(OrderedDict(
            [(Translations().ok_text, self.confirm), (Translations().cancel_text, self.root.destroy)]))
        buttons.pack(fill=tk.X, padx=10, pady=5)

        self.pack()

    def confirm(self):
        """
        Method called when ok button is pushed
        Calls the cb function registered during initialization
        """
        self.caller_cb_func()
        self.root.destroy()


class ListboxWithScroll(tk.Frame):
    """
    Frame composed of a listbox and a scrollbar
    """
    def __init__(self, root, width, font, double_click_cb):
        super(ListboxWithScroll, self).__init__(root)
        self.scroll = tk.Scrollbar(self, orient=tk.VERTICAL)
        self.listbox = tk.Listbox(self, width=width, font=font, yscrollcommand=self.scroll.set)
        self.scroll.config(command=self.listbox.yview)
        self.listbox.bind('<Double-1>', double_click_cb)

    def create_layout(self):
        self.scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=1)

    def clear(self):
        """
        Clears previous entries in the listbox frame
        """
        if self.listbox.size():
            self.listbox.delete(0, tk.END)

    def insert_results(self, results):
        for i, book in enumerate(results):
            self.listbox.insert(i, book)

    def get_selection(self):
        return self.listbox.curselection()[-1]
