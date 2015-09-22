# -*- mode: python -*-

block_cipher = None


a = Analysis(['gcviewer\\gui.py'],
             pathex=['C:\\Users\\Administrator\\PycharmProjects\\PyeX', '.\\\\lib', 'C:\\Users\\Administrator\\git\\GCViewer'],
             hiddenimports=['scipy.linalg', 'scipy.linalg.cython_blas', 'scipy.linalg.cython_lapack', 'scipy.integrate', 'gcviewer'],
             hookspath=['C:\\Users\\Administrator\\git\\GCViewer\\hooks'],
             runtime_hooks=None,
             excludes=None,
             cipher=block_cipher)
pyz = PYZ(a.pure,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          name='gui.exe',
          debug=False,
          strip=None,
          upx=True,
          console=True )
