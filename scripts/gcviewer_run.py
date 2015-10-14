import logging
import sys

from PyQt4.QtGui import QApplication

import gcviewer.eyetracking.api

from gcviewer.gui import GCImageViewer

logger = logging.getLogger(__name__)


def run_qt_gui():
    """
    Set up example configuration to run qt gui with eyex and save log files.
    """
    logging.basicConfig(filename='log.debug')

    app = QApplication(sys.argv)
    imageViewer = GCImageViewer()

    tracking_apis = gcviewer.eyetracking.api.get_available()
    logger.debug('Available tracking apis: {}'.format(str(tracking_apis.keys())))
    try:
        tracker = tracking_apis['eyetribe']
        print(tracker.sample())
        tracker.on_event.append(
            lambda sample: imageViewer.render_area.gaze_change.emit(sample))
    except Exception:
        logger.exception('Could not load tracker. ')

    imageViewer.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    try:
        run_qt_gui()
        logging.f
    except Exception:
        logging.exception('Program terminated with an exception. ')
