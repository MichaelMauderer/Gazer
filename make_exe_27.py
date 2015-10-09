# build file
# make Windows exe
import os
import sys

from subprocess import check_output

hidden_imports = [
    'gcviewer'
]

project_root = r'C:\Users\project\PycharmProjects\gcviewer-py2'

args = r'--clean --onefile gcviewer\gui.py -p ' + project_root
more_args = r"--paths=.\\lib --additional-hooks-dir=" + project_root + r"\hooks -y"

hidden_imports = r' '.join(['--hidden-import='+s for s in hidden_imports])

full_args = 'pyinstaller ' + r' '.join([args, hidden_imports, more_args])
print full_args
print check_output(full_args, shell=True)

print 'End of program.'
