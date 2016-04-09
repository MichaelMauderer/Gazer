# Build file for windows executable.
# Requires pyinstaller script to be in PATH or PYINSTALLER_PATH env variable
# to be set to pyinstaller script location.
from __future__ import print_function, division, unicode_literals
import os
import platform

from subprocess import check_output

app_name = 'gazer'
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
print("Project root:", project_root)
pyinstaller_path = os.getenv('PYINSTALLER_PATH', 'pyinstaller')
lib_path = os.path.join(project_root, 'lib')
hook_path = os.path.join(project_root, 'hooks')
target = os.path.join(project_root, 'scripts', 'gazer_run.py')
out_path = os.path.join(project_root, 'dist')
build_path = os.path.join(project_root, 'build')
architecture = platform.architecture()[0]
icon = '../gazer/assets/logo/Gazer-Logo-Square-256px.ico'


def get_ops(debug=False):
    default_opts = ['--clean ',
                    '-y ',
                    '-p "{}" '.format(project_root),
                    '--paths="{}" '.format(lib_path),
                    '--additional-hooks-dir="{}" '.format(hook_path),
                    '--distpath="{}" '.format(out_path),
                    '--workpath="{}" '.format(build_path),
                    '--icon "{}"'.format(icon),
                    '--noconsole '
                    ]

    if not debug:
        app_file_name = '{}.{}'.format(app_name, architecture)
        opts = default_opts + ['--name {} '.format(app_file_name),
                               '--onefile ',]
    else:
        app_file_name = '{}-debug'.format(app_name)
        opts = default_opts[:-1] + [
            '--name {} '.format(app_file_name),
            '--onedir',
        ]

    return ' '.join(opts)


command = '{pyinstaller} {opts} "{target}"'.format(pyinstaller=pyinstaller_path,
                                                   opts=get_ops(),
                                                   target=target)
print(command)
print(check_output(command, shell=True))

command = '{pyinstaller} {opts} "{target}"'.format(pyinstaller=pyinstaller_path,
                                                   opts=get_ops(debug=True),
                                                   target=target)
print(command)
print(check_output(command, shell=True))

print('End of program.')
