from PyInstaller.utils.hooks import collect_submodules
import os

datas = [
    (os.path.join(os.getenv('EYEX_LIB_PATH'), 'Tobii.EyeX.Client.dll'), '..\\'),
]

hiddenimports = ['gcviewer',
                 'scipy',
                 'skimage.io',
                 ]

hiddenimports += collect_submodules('scipy')
