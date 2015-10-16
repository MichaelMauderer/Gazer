from PyInstaller.utils.hooks import collect_submodules

datas = [
    ('.\\lib\\Tobii.EyeX.Client.dll', '.\\'),
]

hiddenimports = ['gcviewer',
                 'scipy',
                 'skimage.io',
                 ]

hiddenimports += collect_submodules('scipy')
