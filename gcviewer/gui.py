import functools
from functools import lru_cache
from PyQt5 import QtGui
from PyQt5.QtCore import QDir, Qt, pyqtSlot, pyqtSignal, QPoint, QEvent
from PyQt5.QtGui import QImage, QPainter, QPalette, QPixmap
from PyQt5.QtWidgets import (QAction, QApplication, QFileDialog, QLabel,
                             QMainWindow, QMenu, QMessageBox, QScrollArea, QSizePolicy)
from eyexinterface import EyeXInterface, Sample
import gcviewer.io
import numpy as np


class QtSceneWrapper(gcviewer.scene.Scene):
    def __init__(self, scene):
        self._scene = scene

    def array_to_pixmap(self, array):
        array = np.require(array, np.uint8, 'C')
        q_image = QImage(array.data, array.shape[1], array.shape[0], QImage.Format_RGB888)
        return QPixmap.fromImage(q_image)

    def _get_pixmap(self):
        image = self._scene.get_image()
        if image is None:
            return None
        return self.array_to_pixmap(image)

    def update_gaze(self, pos):
        super(QtSceneWrapper, self).update_gaze(pos)
        self._scene.update_gaze(pos)

    def get_image(self):
        return self._get_pixmap()


class GCImageWidget(QLabel):
    gaze_change = pyqtSignal(Sample)

    @property
    def gc_scene(self):
        return self._gc_scene

    @gc_scene.setter
    def gc_scene(self, value):
        if value is not None:
            self._gc_scene = QtSceneWrapper(value)
        else:
            self._gc_scene = None

    def __init__(self, gc_scene, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.gc_scene = gc_scene
        self._gaze = QPoint(0, 0)
        self.gaze_change.connect(self.update_gaze)


    def update_gaze(self, sample):
        if self.gc_scene is None:
            return

        local_pos = self.mapFromGlobal(QPoint(sample.x, sample.y))
        self._gaze = local_pos
        norm_pos = local_pos.x() / self.size().width(), 1 - (local_pos.y() / self.size().height())
        self.gc_scene.update_gaze(tuple(np.clip(norm_pos, 0, 1)))
        image = self.gc_scene.get_image()
        if image is not None:
            image = image.scaled(self.size(), Qt.KeepAspectRatio)
            self.setPixmap(image)
            self.update()

    def paintEvent(self, QPaintEvent):
        super().paintEvent(QPaintEvent)
        painter = QtGui.QPainter(self)
        painter.setBrush(QtGui.QColor(0, 255, 0))
        painter.drawEllipse(self._gaze.x(), self._gaze.y(), 50, 50)
        painter.end()

    def heightForWidth(self, p_int):
        width = self.self.gc_scene.get_image().size().width()
        height = self.self.gc_scene.get_image().size().height()
        return (p_int / width) * height

    def hasHeightForWidth(self):
        return True


class GCImageViewer(QMainWindow):
    def __init__(self):
        super(GCImageViewer, self).__init__()

        self.render_area = GCImageWidget(None)
        self.render_area.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Ignored)
        self.render_area.setAlignment(Qt.AlignCenter)
        self.setCentralWidget(self.render_area)

        # Create Actions
        self.open_action = QAction("&Open...", self, shortcut="Ctrl+O", triggered=self.load_scene)

        self.exit_action = QAction("E&xit", self, shortcut="Ctrl+Q", triggered=self.close)

        # Create Menues
        self.file_menu = QMenu("&File", self)
        self.file_menu.addAction(self.open_action)
        self.file_menu.addSeparator()
        self.file_menu.addAction(self.exit_action)

        self.menuBar().addMenu(self.file_menu)

        self.setWindowTitle("GC Image Viewer")
        self.resize(800, 600)

    def load_scene(self):
        file_name, _ = QFileDialog.getOpenFileName(self, "Open File",
                                                   QDir.currentPath())
        if file_name:
            with open(file_name) as in_file:
                scene = gcviewer.io.read_file(in_file)
                self.render_area.gc_scene = scene

                # if image.isNull():
                # QMessageBox.information(self, "Image Viewer",
                # "Cannot load %s." % file_name)
                # return

    def event(self, event):
        if event.type() == QEvent.KeyPress:
            if event.key() == Qt.Key_F12:
                self.toggle_fullscreen()
                return True
        return False

    def toggle_fullscreen(self):
        if self.isFullScreen():
            self.showNormal()
        else:
            self.showFullScreen()

if __name__ == '__main__':
    import sys

    app = QApplication(sys.argv)
    imageViewer = GCImageViewer()

    eye_x = EyeXInterface('../lib/Tobii.EyeX.Client.dll')
    eye_x.on_event.append(lambda sample: imageViewer.render_area.gaze_change.emit(sample))

    imageViewer.show()
    sys.exit(app.exec_())