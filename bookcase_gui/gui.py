import tkinter as tk

from bookcase_gui.gui_frames import MainToolbar, StatusBar
import bookcase_lib as lib


class BookcaseGui(object):
    def __init__(self):
        path = lib.FileManager().path
        self.lock = lib.InstanceLock(path)
        self.root = tk.Tk()
        self.toolbar = MainToolbar(self.root)

    def cleanup(self):
        self.toolbar.cleanup()
        self.lock.release_instance_lock()

    def setup_env(self):
        self.lock.acquire_instance_lock()
        lib.Configuration().read_config()

    def run(self):
        self.setup_env()
        self.toolbar.setup_toolbar()
        StatusBar().pack(side=tk.BOTTOM, fill=tk.X)
        self.root.title("Bookcase Manager")
        self.root.geometry("1280x720+150+100")
        self.root.mainloop()


