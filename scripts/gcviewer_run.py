from __future__ import unicode_literals, division, print_function

import logging
import sys
import os

from PyQt4 import QtGui

import gcviewer.eyetracking.api
from gcviewer.qt_gui.mainwindow import GCImageViewerMainWindow

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

    app = QtGui.QApplication(sys.argv)
    tracking_apis = gcviewer.eyetracking.api.get_available()
    logger.info(
            'Available tracking apis: {}'.format(str(tracking_apis.keys())))
    imageviewer = GCImageViewerMainWindow(tracking_apis)
    imageviewer.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    try:
        run_qt_gui()
    except RuntimeError:
        logging.exception('Program terminated with an exception. ')
