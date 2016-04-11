from __future__ import unicode_literals, division, print_function

import sys
import os
import argparse

import nose

import logging

DEBUG_LOG_FILE = 'debug.log'
logging.basicConfig(filename=DEBUG_LOG_FILE, level=logging.DEBUG, filemode='w')

logger = logging.getLogger(__name__)


def log_heading():
    logging.info('*' * 70)
    logging.info('*' * 3 + ' In case of problems with this applications please'
                           ' provide the  ***')
    logging.info(
        '*** content of this file for diagnostics.' + ' ' * 26 + '*' * 3)
    logging.info('*' * 70)


def run_qt_gui():
    """
    Set up example configuration to run qt gui with eyex and save log files.
    """

    log_heading()

    from PyQt4 import QtGui, QtCore

    import gazer
    import gazer.eyetracking.api
    from gazer.qt_gui.mainwindow import GazerMainWindow

    app = QtGui.QApplication(sys.argv)
    tracking_apis = gazer.eyetracking.api.get_available()
    logger.info(
        'Available tracking apis: {}'.format(str(tracking_apis.keys())))

    import ctypes
    app_id = 'gazer'
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(app_id)

    try:
        # Pyinstaller workaround to find assets while deployed.
        if getattr(sys, 'frozen', False):
            # noinspection PyProtectedMember
            base_path = sys._MEIPASS
        else:
            base_path = './'

        # Create window
        imageviewer = GazerMainWindow(tracking_apis)
        imageviewer.show()

        # Set icons

        icon_path_pattern = 'gazer/assets/logo/Gazer-Logo-Square-{size}px.png'
        app_icon = QtGui.QIcon()

        def app_icon_add_size(size):
            icon_path = icon_path_pattern.format(size=size)
            icon_path = os.path.join(base_path, icon_path)
            assert os.path.exists(icon_path)
            app_icon.addFile(icon_path, QtCore.QSize(size, size))

        app_icon_add_size(16)
        app_icon_add_size(32)
        app_icon_add_size(128)

        imageviewer.setWindowIcon(app_icon)

        # Set default scene
        default_scene_path = 'gazer/assets/sachi_workbench.gc'
        sample_scene = gazer.gcio.load_scene(
            os.path.join(base_path, default_scene_path))
        imageviewer.update_scene(sample_scene)



    except RuntimeError:
        logger.exception('Could not load sample scene.')

    sys.exit(app.exec_())


def run_tests():
    return nose.run()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', action='store_true',
                        help='run test suite')
    args = parser.parse_args()

    if args.d:
        run_tests()
    try:
        run_qt_gui()
    except RuntimeError:
        logging.exception('Program terminated with an exception. ')
