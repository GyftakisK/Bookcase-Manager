from sys import platform, version_info
from cx_Freeze import setup, Executable


if version_info < (3,):
    print('Python version 2.x is not supported')

    
bdist_msi_options = {'add_to_path': False,
                     'initial_target_dir': r'[ProgramFilesFolder]\Bookcase_Manager'}
buildOptions = dict(include_files=['artifacts/'], bin_path_includes=[r'[ProgramFilesFolder]\Bookcase_Manager\artifacts'])
setup(
    name="Bookcase Manager",
    version="1.1",
    description="Application to manage your home library",
    executables=[Executable("bookcase.py",
                            shortcutName="Bookcase Manager",
                            shortcutDir="DesktopFolder",
                            icon="books.ico", base="Win32GUI")],
                            install_requires=['cx_Freeze'],
                            options={'bdist_msi': bdist_msi_options, 'build_exe': buildOptions},
                            copyDependentFiles = True)