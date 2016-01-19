from __future__ import unicode_literals, division, print_function

import logging

from PyQt4.QtCore import QThread, pyqtSignal, QObject, Qt
from PyQt4.QtGui import QProgressBar, QProgressDialog

from gazer import scene

logger = logging.getLogger(__name__)


class TaskWorker(QThread):
    task_done = pyqtSignal()

    def __init__(self, task, *args, **kwargs):
        super(TaskWorker, self).__init__(*args, **kwargs)
        self.task = task
        self.result = None

    def run(self):
        try:
            self.result = self.task()
        except RuntimeError:
            logger.exception('Task raised an exception.')
        finally:
            self.task_done.emit()


class BlockingTask(QObject):
    load_finished = pyqtSignal(scene.Scene)

    def __init__(self, scene_load_func, message, *args, **kwargs):
        super(BlockingTask, self).__init__(*args, **kwargs)
        self.scene_load_func = scene_load_func
        self.message = message

        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 0)
        self.worker = None

    def start_task(self):
        self._async_execute()

    def _on_load_finished(self):
        logger.debug('On task finished')
        self.scene = self.worker.result
        if self.scene is not None:
            self.load_finished.emit(self.scene)
        self.progress_dialog.hide()

    def _on_load_start(self):
        logger.debug('On task start')
        self.progress_dialog = QProgressDialog(self.message,
                                               "Abort",
                                               0,
                                               0,
                                               self.parent(),
                                               flags=Qt.CustomizeWindowHint,
                                               )
        self.progress_dialog.setWindowModality(Qt.WindowModal)
        self.progress_dialog.canceled.connect(self._abort)
        self.progress_dialog.show()

    def _abort(self):
        self.worker.terminate()

    def _async_execute(self):
        self._on_load_start()
        self.worker = TaskWorker(self.scene_load_func)
        self.worker.task_done.connect(self._on_load_finished)
        self.worker.start()
