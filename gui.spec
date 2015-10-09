# -*- mode: python -*-
a = Analysis(['gcviewer\\gui.py'],
             pathex=['C:\\Users\\project\\PycharmProjects\\gcviewer-py2', '.\\\\lib', 'C:\\Users\\project\\PycharmProjects\\gcviewer-py2'],
             hiddenimports=['gcviewer'],
             hookspath=['C:\\Users\\project\\PycharmProjects\\gcviewer-py2\\hooks'],
             runtime_hooks=None)
pyz = PYZ(a.pure)
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
