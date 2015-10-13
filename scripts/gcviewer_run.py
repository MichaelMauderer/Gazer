import logging
import sys
import os

from PyQt4.QtGui import QApplication

from gcviewer.gui import GCImageViewer


def run_qt_gui():
    """
    Set up example configuration to run qt gui with eyex and save log files.
    """
    logging.basicConfig(filename='log.debug', level=logging.DEBUG)

    app = QApplication(sys.argv)
    imageViewer = GCImageViewer()

    try:
        import eyex
        lib_path = os.path.join(os.getenv('EYEX_LIB_PATH', ''),
                                'Tobii.EyeX.Client.dll')
        eye_x = eyex.api.EyeXInterface(lib_path)
        eye_x.on_event.append(
            lambda sample: imageViewer.render_area.gaze_change.emit(sample))
    except Exception:
        logging.exception('Could not load EyeX. ')

    imageViewer.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    try:
        run_qt_gui()
    except Exception:
        logging.exception('Program terminated with an exception. ')
