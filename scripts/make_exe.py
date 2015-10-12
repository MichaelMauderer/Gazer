# Build file for windows executable.
# Requires pyinstaller script to be in PATH or PYINSTALLER_PATH env variable
# to be set to pyinstaller script location.

from __future__ import print_function, division, unicode_literals
import os

from subprocess import check_output

project_root = '.\\'
pyinstaller_path = os.getenv('PYINSTALLER_PATH', 'pyinstaller')
lib_path = '.\\lib'
hook_path = os.path.join(project_root, 'hooks')
target = os.path.join(project_root, 'gcviewer', 'gui.py')

opts = '--clean ' \
       '--onefile ' \
       'gcviewer\gui.py ' \
       '-p {project_root} ' \
       '--paths={lib_path} ' \
       '--additional-hooks-dir={hook_path} ' \
       '-y '

opts = opts.format(project_root=project_root,
                   lib_path=lib_path,
                   hook_path=hook_path,
                   )

command = pyinstaller_path + ' ' + opts + ' ' + target
print(command)
print(check_output(command, shell=True))

print('End of program.')
