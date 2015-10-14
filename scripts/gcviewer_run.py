import logging
import sys

from PyQt4.QtGui import QApplication

import gcviewer.eyetracking.api

from gcviewer.gui import GCImageViewer


def run_qt_gui():
    """
    Set up example configuration to run qt gui with eyex and save log files.
    """
    logging.basicConfig(filename='log.debug', level=logging.DEBUG)

    app = QApplication(sys.argv)
    imageViewer = GCImageViewer()

    tracking_apis = gcviewer.eyetracking.api.get_available()

    try:
        tracking_apis['eyex'].on_event.append(
            lambda sample: imageViewer.render_area.gaze_change.emit(sample))
    except Exception:
        logging.exception('Could not load EyeX. ')

    imageViewer.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    try:
        run_qt_gui()
        logging.f
    except Exception:
        logging.exception('Program terminated with an exception. ')
