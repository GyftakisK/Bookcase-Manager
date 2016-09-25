import os
import configparser


class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class Configuration(object, metaclass=Singleton):
    def __init__(self):
        self.config = configparser.ConfigParser()
        self.config_file = FileManager().path + "config.ini"

    def config_file_exists(self):
        return os.path.exists(self.config_file)

    def set_config(self, key, value, label='LOCAL'):
        self.config[label] = {key: value}
        self.write_config()

    def get_config(self, key, label='LOCAL'):
        return self.config[label][key]

    def write_config(self):
        with open(self.config_file, 'w') as configuration:
            self.config.write(configuration)

    def read_config(self):
        if not self.config_file_exists():
            self.setup_default_configuration()
        self.config.read(self.config_file)

    def setup_default_configuration(self):
        self.set_config("gui_language", "en")


class InstanceLock(object):
    def __init__(self, path):
        self.file = path + ".lock"
        self.fd = -1

    def acquire_instance_lock(self):
        if os.path.isfile(self.file):
            raise FileExistsError
        else:
            self.fd = os.open(self.file, os.O_CREAT | os.O_EXCL)

    def release_instance_lock(self):
        if self.fd != -1:
            os.close(self.fd)
            os.remove(self.file)


class FileManager(object):
    def __init__(self):
        self._path = os.path.expanduser("~") + "/BookcaseDb/"

    @property
    def path(self):
        return self._path

    def data_directory_exist(self):
        return os.path.exists(self._path)

    def setup_data_directory(self):
        if not self.data_directory_exist():
            os.mkdir(self._path)

    def find_all_db_files(self):
        return self.find_files_with_extension(".db")

    def find_all_xlsx_files(self):
        return self.find_files_with_extension(".xlsx")

    def find_files_with_extension(self, extension):
        return [filename for filename in os.listdir(self._path) if extension in filename]


    @staticmethod
    def load_photos():
        return [file for file in os.listdir("artifacts") if ".png" in file]

