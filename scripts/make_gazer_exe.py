# Build file for windows executable.
# Requires pyinstaller script to be in PATH or PYINSTALLER_PATH env variable
# to be set to pyinstaller script location.
from __future__ import print_function, division, unicode_literals
import os
import platform

from subprocess import check_output

app_name = 'gazer'
project_root = '..'
pyinstaller_path = os.getenv('PYINSTALLER_PATH', 'pyinstaller')
lib_path = os.path.join('..', 'lib')
hook_path = os.path.join(project_root, 'hooks')
target = os.path.join(project_root, 'scripts', 'gazer_run.py')
out_path = os.path.join('..', 'dist')
build_path = os.path.join('..', 'build')
architecture = platform.architecture()[0]
icon = '../gazer/assets/logo/Gazer-Logo-Square-128px.ico'

app_file_name = '{}.{}'.format(app_name, architecture)

opts = '--clean ' \
       '--onefile ' \
       '--noconsole ' \
       '-p {project_root} ' \
       '--paths={lib_path} ' \
       '--additional-hooks-dir={hook_path} ' \
       '-y ' \
       '--distpath={out_path} ' \
       '--workpath={build_path} ' \
       '--name {app_file_name} ' \
       '--icon {icon}'

opts = opts.format(project_root=project_root,
                   lib_path=lib_path,
                   hook_path=hook_path,
                   out_path=out_path,
                   build_path=build_path,
                   app_file_name=app_file_name,
                   icon=icon,
                   )

command = pyinstaller_path + ' ' + opts + ' ' + target
print(command)
print(check_output(command, shell=True))

print('End of program.')
