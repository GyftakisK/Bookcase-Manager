from distutils.core import setup
import py2exe
import os
images = [os.path.join(os.path.abspath('artifacts'), file) for file in os.listdir('artifacts')]
setup(name="Bookcase Manager",
      version="1.0",
      description="Application to manage your home library",
      windows=[{
          "script": "bookcase.py",
          "icon_resources": [(0, "books.ico")]
      }],
      data_files=[('artifacts', images)],
      options={
          'py2exe': {
              'packages': ['sqlalchemy', 'openpyxl'],
              'bundle_files': 2
          }
      },
      zipfile=None
)