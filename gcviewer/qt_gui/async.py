from __future__ import unicode_literals, division, print_function

import logging

from PyQt4.QtCore import QThread, pyqtSignal, QObject
from PyQt4.QtGui import QProgressBar, QProgressDialog

from gcviewer import scene

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


class SceneLoader(QObject):
    load_finished = pyqtSignal(scene.Scene)

    def __init__(self, scene_load_func, *args, **kwargs):
        super(SceneLoader, self).__init__(*args, **kwargs)
        self.scene_load_func = scene_load_func

        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 0)
        self.worker = None

    def start_import(self):
        self._async_load()

    def _on_load_finished(self):
        logger.debug('On load finished')
        self.scene = self.worker.result
        if self.scene is not None:
            self.load_finished.emit(self.scene)
        self.progress_dialog.hide()

    def _on_load_start(self):
        logger.debug('On load start')
        start_message = 'Loading scene'
        self.progress_dialog = QProgressDialog(start_message,
                                               "Abort",
                                               0,
                                               0,
                                               self.parent()
                                               )
        self.progress_dialog.canceled.connect(self._abort)
        self.progress_dialog.show()

    def _abort(self):
        self.worker.terminate()

    def _async_load(self):
        self._on_load_start()
        self.worker = TaskWorker(self.scene_load_func)
        self.worker.task_done.connect(self._on_load_finished)
        self.worker.start()
