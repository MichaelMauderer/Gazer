from __future__ import unicode_literals, division, print_function

import sys
import os

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

    from PyQt4 import QtGui

    import gazer
    import gazer.eyetracking.api
    from gazer.qt_gui.mainwindow import GCImageViewerMainWindow

    app = QtGui.QApplication(sys.argv)
    tracking_apis = gazer.eyetracking.api.get_available()
    logger.info(
            'Available tracking apis: {}'.format(str(tracking_apis.keys())))
    imageviewer = GCImageViewerMainWindow(tracking_apis)
    imageviewer.show()

    try:
        # Pyinstaller workaround to find assets while deployed.
        if getattr(sys, 'frozen', False):
            base_path = sys._MEIPASS
        else:
            base_path = './'
        rel_path = 'gazer/assets/sachi_workbench.gc'
        sample_scene = gazer.gcio.load_scene(os.path.join(base_path, rel_path))
        imageviewer.update_scene(sample_scene)
    except RuntimeError:
        logger.exception('Could not load sample scene.')

    sys.exit(app.exec_())


if __name__ == '__main__':
    try:
        run_qt_gui()
    except RuntimeError:
        logging.exception('Program terminated with an exception. ')
