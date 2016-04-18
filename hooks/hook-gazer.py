from PyInstaller.building.datastruct import Tree
from PyInstaller.utils.hooks import collect_submodules, collect_data_files
from distutils.sysconfig import get_python_lib
import os

datas = [
    (os.path.join(os.getenv('EYEX_LIB_PATH'), 'Tobii.EyeX.Client.dll'), '.\\'),
    ('../gazer/assets', './gazer/assets'),
    ('../tests', './tests')
]

datas += collect_data_files("skimage.io._plugins")

hiddenimports = ['gazer',
                 'scipy',
                 'skimage.io',
                 ]

hiddenimports += collect_submodules('scipy')
