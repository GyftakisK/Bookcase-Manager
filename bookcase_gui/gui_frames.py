from collections import OrderedDict
from tkinter import (Frame, Button, LEFT, PhotoImage, X, Toplevel, Listbox, END, Message, Entry, Label, GROOVE,
                     RIGHT, E, W, BOTH, StringVar, SUNKEN, CENTER, Menubutton, Menu, RAISED)
from tkinter.ttk import Combobox

from bookcase_db.bookcase_db import BookcaseDbManager
from bookcase_excel.bookcase_excel import Excel
from bookcase_exceptions import InvalidInputException
import bookcase_lib as lib
from bookcase_gui.gui_data_schema import GuiBook
from bookcase_translations import Translations


FONT_11_NORMAL = ('Verdana', 11, 'normal')
FONT_12_NORMAL = ('Verdana', 12, 'normal')
FONT_14_NORMAL = ('Verdana', 14, 'normal')


class ButtonToolbar(Frame):
    def __init__(self, root):
        super(ButtonToolbar, self).__init__(root, bg="Light Grey")
        self.root = root
        self.photos = self.load_artifacts()

    def create_toolbar_button(self, photo, command=lambda: None, on_hover_text="", side=LEFT):
        button = Button(self, command=command)
        button.config(image=photo, width=30, height=30)
        button.pack(side=side, padx=2, pady=2)
        button.bind("<Enter>", lambda x: StatusBar().set_status_from_event(x, on_hover_text))
        button.bind("<Leave>", StatusBar().clear_status_from_event)
        return button

    @staticmethod
    def load_artifacts():
        photos = dict()
        for file in lib.FileManager().load_photos():
            photos[file] = PhotoImage(file="artifacts/" + file)
        return photos


class MainToolbar(ButtonToolbar):
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

        self.pack(fill=X, ipady=5)

    def clear_toolbar(self):
        for button in self.buttons:
            button.destroy()

    def create_lang_button(self):
        lang = lib.Configuration().get_config("gui_language")
        lang_changes = dict(gr="en", en="gr")
        return self.create_toolbar_button(self.photos[lang_changes[lang] + "_icon.png"],
                                          command=lambda: self.change_lang(lang_changes[lang]),
                                          side=RIGHT)

    def change_lang(self, lang):
        lib.Configuration().set_config("gui_language", lang)
        self.clear_toolbar()
        self.setup_toolbar()

    def click_open(self):
        top_level = Toplevel()
        top_level.title(Translations().open_window_title)
        OpenFrame(top_level, self.open_selected_db, lib.FileManager().find_all_db_files()).create_layout()

    def open_selected_db(self, selection):
        if self.db_view and self.db_view.db_name == selection:
            return
        if self.db_view:
            self.db_view.close()
        self.db_view = DbView(self.root, selection.strip(".db"), self.on_db_view_close)
        self.db_view.create_db_view()

    def create_new_db(self):
        top_level = Toplevel()
        top_level.title(Translations().create_window_title)
        CreateDb(top_level, self.open_selected_db).create_layout()

    def cleanup(self):
        if self.db_view:
            self.db_view.cleanup()
            self.db_view = None

    def on_db_view_close(self):
        self.db_view = None


class DbView(ButtonToolbar):
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
        label = Label(self, bg="SteelBlue1", text=self.db_manager.db_name, font=FONT_12_NORMAL,
                      relief=GROOVE)
        label.pack(fill=X)

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
        self.pack(fill=X, ipady=5)

    def create_menu_button(self):
        button = Menubutton(self)
        button.config(image=self.photos["import_export.png"], width=34, height=34, relief=RAISED)
        button.menu = Menu(button, tearoff=0)
        button["menu"] = button.menu
        button.bind("<Enter>", lambda x: StatusBar().set_status_from_event(x, Translations().import_export_desc))
        button.bind("<Leave>", StatusBar().clear_status_from_event)

        button.menu.add_command(label=Translations().import_excel, command=self.import_from_excel, font=FONT_12_NORMAL)
        button.menu.add_command(label=Translations().export_excel, command=self.export_to_excel, font=FONT_12_NORMAL)

        button.pack(side=LEFT, padx=2, pady=2)

    def import_from_excel(self):
        top_level = Toplevel(self.root)
        OpenFrame(top_level, self.dump_excel_to_db, lib.FileManager().find_all_xlsx_files()).create_layout()

    def dump_excel_to_db(self, filename):
        table = Excel().read_excel(filename)
        self.db_manager.import_table(table)
        StatusBar().set_status(Translations().imported_from + filename)

    def export_to_excel(self):
        table = self.db_manager.dump_table()
        file = Excel().write_excel(self.db_manager.db_name, table)
        StatusBar().set_status(Translations().exported_to + file)

    def open_book_view(self):
        if not self.book_view:
            if self.search_view:
                self.search_view.close()
            self.book_view = BookViewNew(self.root, self.db_manager, self.on_book_view_close)
            self.book_view.open_book_view()

    def open_search_view(self):
        if not self.search_view:
            if self.book_view:
                self.book_view.close()
            self.search_view = SearchView(self.root, self.db_manager, self.on_search_view_close)
            self.search_view.open_search_view()

    def cleanup(self):
        self.db_manager.cleanup()

    def close(self):
        self.cleanup()
        if self.book_view:
            self.book_view.close()
        if self.search_view:
            self.search_view.close()
        self.on_close_cb_func()
        self.destroy()

    def on_book_view_close(self):
        self.book_view = None

    def on_search_view_close(self):
        self.search_view = None


class BookView(Frame):
    def __init__(self, root, db_manager, on_close_cb_func):
        super(BookView, self).__init__(root)
        self.gui_book = GuiBook()

        self.entries_desc_grid_pref_var = OrderedDict(
            [(Translations().title_msg, (0, -1, 100, self.gui_book.get_object("title"))),
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
             (Translations().shelf_row_desc, (5, 0, 25, self.gui_book.get_object("shelf_row"))),
             (Translations().shelf_col_desc,
              (5, 2, 25, self.gui_book.get_object("shelf_col")))])
        self.db_manager = db_manager
        self.on_close_cb_func = on_close_cb_func
        self.buttons = None

    def open_book_view(self):
        StatusBar().clear_status()
        for key in self.entries_desc_grid_pref_var.keys():
            row, column, width, var = self.entries_desc_grid_pref_var[key]
            msg = Message(self, text=key, width=100, justify=RIGHT, font=FONT_11_NORMAL)
            if column == -1:
                msg.grid(row=row, column=0, padx=5, pady=5, sticky=E)
                Entry(self, width=width, textvariable=var, font=FONT_11_NORMAL).grid(row=row,
                                                                                     column=1,
                                                                                     columnspan=3,
                                                                                     pady=5, sticky=W)
            else:
                msg.grid(row=row, column=column, padx=5, pady=5, sticky=E)
                Entry(self, width=width, textvariable=var, font=FONT_11_NORMAL).grid(row=row,
                                                                                     column=column + 1,
                                                                                     pady=5, sticky=W)

        buttons_frame = ButtonFrame(self)
        buttons_frame.create_buttons(self.buttons)
        buttons_frame.grid(row=row + 1, columnspan=4)

        self.pack(ipadx=40, ipady=10)

    def close(self):
        self.on_close_cb_func()
        self.destroy()


class BookViewNew(BookView):
    def __init__(self, *args):
        super(BookViewNew, self).__init__(*args)
        self.buttons = OrderedDict(
            [(Translations().save_text, self.save_new_book_to_db), (Translations().cancel_text, self.close)])

    def save_new_book_to_db(self):
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
    def __init__(self, root, db_manager, on_close_cb_func, book):
        super(BookViewOpen, self).__init__(root, db_manager, on_close_cb_func)
        self.root = root
        self.buttons = OrderedDict([(Translations().save_text, self.save_changes_to_db),
                                    (Translations().delete_text, self.delete),
                                    (Translations().cancel_text, self.close)])
        self.book = book
        self.gui_book.init_entries_from_book(book)

    def save_changes_to_db(self):
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
        top_level = Toplevel(self)
        DeleteBookPrompt(top_level, self.delete_book, self.book.title).create_layout()

    def delete_book(self):
        self.db_manager.delete_book(self.book)
        StatusBar().set_status(Translations().book_deleted_msg)
        self.close()

    def close(self):
        self.on_close_cb_func()
        self.root.destroy()


class SearchView(Frame):
    def __init__(self, root, db_manager, on_close_cb_func):
        super(SearchView, self).__init__(root)
        self.choices = (Translations().title_text, Translations().author_text, "ISBN", Translations().shelf_text)
        self.option = Combobox(self, values=self.choices, state="readonly", font=FONT_11_NORMAL)
        self.option.set(self.choices[0])
        self.search_str = Entry(self, width=60, font=FONT_11_NORMAL)
        self.listbox = Listbox(self, width=100, font=FONT_11_NORMAL)
        self.listbox.bind('<Double-1>', self.open_book)
        self.db_manager = db_manager
        self.on_close_cb_func = on_close_cb_func
        self.root = root
        self.books = None

    def open_search_view(self):
        self.option.grid(row=0, column=0, pady=10, sticky=E)
        self.search_str.grid(row=0, column=1, pady=10)

        buttons_frame = ButtonFrame(self)
        buttons = OrderedDict(
            [(Translations().search_text, self.perform_db_search), (Translations().cancel_text, self.close)])
        buttons_frame.create_buttons(buttons)
        buttons_frame.grid(row=1, columnspan=2)

        self.listbox.grid(row=2, columnspan=2, pady=20)

        self.pack(ipadx=40, ipady=10)

    def clear_listbox(self):
        if self.listbox.size():
            self.listbox.delete(0, END)

    def get_db_search_results(self):
        if not self.search_str.get():
            return self.db_manager.get_all_books()
        else:
            return self.search_by(self.option.get(), self.search_str.get())

    def populate_listbox_with_search_results(self, results):
        for i, book in enumerate(results):
            self.listbox.insert(i, "{title}, {author}, {year} | {shelf}".format(title=book.title,
                                                                                author=book.author,
                                                                                year=book.publication_year,
                                                                                shelf=book.shelf))

    def perform_db_search(self):
        self.clear_listbox()
        self.books = self.get_db_search_results()
        if not self.books:
            StatusBar().set_status(Translations().no_books_found_msg)
        else:
            StatusBar().set_status(Translations().search_complete_msg)
            self.populate_listbox_with_search_results(self.books)

    def search_by(self, option, string):
        if option == Translations().title_text:
            return self.db_manager.search_by_title(string)
        if option == Translations().author_text:
            return self.db_manager.search_by_author(string)
        if option == "ISBN":
            return self.db_manager.search_by_isbn(string)
        if option == Translations().shelf_text:
            return self.db_manager.search_by_shelf(string)

    def open_book(self, event):
        top_level = Toplevel(self.root)
        book_view = BookViewOpen(top_level, self.db_manager, self.perform_db_search,
                                 self.books[self.listbox.curselection()[-1]])
        book_view.open_book_view()
        book_view.pack(fill=BOTH)

    def close(self):
        self.on_close_cb_func()
        self.destroy()


class ButtonFrame(Frame):
    def __init__(self, root):
        super(ButtonFrame, self).__init__(root)

    def create_buttons(self, buttons):
        for text, command in buttons.items():
            button = Button(self, command=command)
            button.config(text=text, width=10, height=2, font=FONT_11_NORMAL)
            button.pack(side=LEFT, padx=8, pady=10)


class StatusBar(Frame, metaclass=lib.Singleton):
    def __init__(self, root=None):
        super(StatusBar, self).__init__(root)
        self._text = StringVar()
        self.label = Label(self, bd=1, relief=SUNKEN, anchor=W,
                           textvariable=self._text, font=FONT_14_NORMAL)
        self._text.set(Translations().welcome_msg)
        self.label.pack(fill=X)

    def set_status(self, text):
        self._text.set(text)

    def clear_status(self):
        self._text.set("")

    def set_status_from_event(self, event, text):
        self._text.set(text)

    def clear_status_from_event(self, event):
        self._text.set("")


class PopUpFrame(Frame):
    def __init__(self, root, caller_cb_func):
        super(PopUpFrame, self).__init__(root)
        self.root = root
        self.caller_cb_func = caller_cb_func

    def create_layout(self):
        raise NotImplementedError


class OpenFrame(PopUpFrame):
    def __init__(self, root, caller_cd_func, choices):
        super(OpenFrame, self).__init__(root, caller_cd_func)
        self.choices = choices

    def create_layout(self):
        listbox = Listbox(self, width=60, font=FONT_11_NORMAL)
        listbox.grid(row=0, column=0, padx=10, pady=15)

        if not self.choices:
            listbox.insert(END, Translations().no_file_found_msg + lib.FileManager().path)
            ok_button_command = self.root.destroy
        else:
            for choice in self.choices:
                listbox.insert(END, choice)
            ok_button_command = lambda: self.open_db(listbox.get(listbox.curselection()))

        button_frame = ButtonFrame(self)
        buttons = OrderedDict(
            [(Translations().ok_text, ok_button_command), (Translations().cancel_text, self.root.destroy)])
        button_frame.create_buttons(buttons)
        button_frame.grid(row=1, column=0)

        self.pack()

    def open_db(self, selection):
        if not selection:
            return
        self.caller_cb_func(selection)
        self.root.destroy()


class CreateDb(PopUpFrame):
    def create_layout(self):
        message = Message(self, text=Translations().enter_db_name_msg, width=200, font=FONT_12_NORMAL, justify=CENTER)
        message.grid(row=0, column=0, padx=20, pady=5)

        database_name = Entry(self, width=30, font=FONT_12_NORMAL, justify=CENTER)
        database_name.grid(row=1, column=0, padx=20, pady=5)

        ok_button_command = lambda: self.create_db(database_name.get())

        button_frame = ButtonFrame(self)
        buttons = OrderedDict(
            [(Translations().ok_text, ok_button_command), (Translations().cancel_text, self.root.destroy)])
        button_frame.create_buttons(buttons)
        button_frame.grid(row=2, column=0)

        self.pack()

    def create_db(self, selection):
        if not selection:
            return
        self.caller_cb_func(selection)
        self.root.destroy()


class DeleteBookPrompt(PopUpFrame):
    def __init__(self, root, caller_cb_func, book_title):
        super(DeleteBookPrompt, self).__init__(root, caller_cb_func)
        self.book_title = book_title

    def create_layout(self):
        delete_message = Message(self.root,
                                 text="{msg} {title}?".format(msg=Translations().delete_confirm_msg,
                                                              title=self.book_title),
                                 width=200, justify=CENTER, font=FONT_12_NORMAL)
        delete_message.pack(fill=X, padx=10, pady=5)
        buttons = ButtonFrame(self.root)
        buttons.create_buttons(OrderedDict(
            [(Translations().ok_text, self.confirm), (Translations().cancel_text, self.root.destroy)]))
        buttons.pack(fill=X, padx=10, pady=5)

        self.pack()

    def confirm(self):
        self.caller_cb_func()
        self.root.destroy()
