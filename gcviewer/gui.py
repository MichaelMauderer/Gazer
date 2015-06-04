import numpy as np

from PyQt5 import QtGui
from PyQt5.QtCore import QDir, Qt, pyqtSignal, QPoint, QEvent
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtWidgets import (QAction, QApplication, QFileDialog, QLabel,
                             QMainWindow, QMenu, QSizePolicy)

from eyexinterface import EyeXInterface, Sample

import gcviewer.io
import gcviewer.scene


class QtSceneWrapper(gcviewer.scene.Scene):
    def __init__(self, scene):
        super(QtSceneWrapper, self).__init__()
        self._scene = scene

    @staticmethod
    def array_to_pixmap(array):
        q_image = QImage(array.data,
                         array.shape[1],
                         array.shape[0],
                         3 * array.shape[1],
                         QImage.Format_RGB888)
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
        super(GCImageWidget, self).__init__(*args, **kwargs)

        self._gc_scene = None
        self.gc_scene = gc_scene

        self._gaze = QPoint(0, 0)
        self.gaze_change.connect(self.update_gaze)

        self.mouse_mode = False

    def update_gaze(self, sample):
        if self.gc_scene is None:
            return

        local_pos = self.mapFromGlobal(QPoint(sample.x, sample.y))
        self._gaze = local_pos
        norm_pos = local_pos.x() / self.size().width(), (
            local_pos.y() / self.size().height())
        self.gc_scene.update_gaze(tuple(np.clip(norm_pos, 0, 1)))
        image = self.gc_scene.get_image()
        if image is not None:
            image = image.scaled(self.size(), Qt.KeepAspectRatio)
            self.setPixmap(image)
            self.update()

    @staticmethod
    def mouse_event_to_gaze_sample(QMouseEvent):
        return Sample(-1,
                      float(QMouseEvent.timestamp()),
                      float(QMouseEvent.globalX()),
                      float(QMouseEvent.globalY()))

    def mouseMoveEvent(self, QMouseEvent):
        if self.mouse_mode:
            sample = self.mouse_event_to_gaze_sample(QMouseEvent)
            self.gaze_change.emit(sample)

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
        self.open_action = QAction("&Open...",
                                   self,
                                   shortcut="Ctrl+O",
                                   triggered=self.load_scene)
        self.save_action = QAction("&Save...",
                                   self,
                                   shortcut="Ctrl+S",
                                   triggered=self.save_scene)
        self.exit_action = QAction("E&xit",
                                   self,
                                   shortcut="Ctrl+Q",
                                   triggered=self.close)

        self.mouse_toggle_action = QAction("Toggle mouse mode",
                                           self,
                                           triggered=self.toggle_mouse_mode,
                                           checkable=True,
                                           checked=False,
                                           )

        # Create Menues
        self.file_menu = QMenu("&File", self)
        self.file_menu.addAction(self.open_action)
        self.file_menu.addAction(self.save_action)
        self.file_menu.addSeparator()
        self.file_menu.addAction(self.exit_action)

        # Create Option Menu
        self.options_menu = QMenu("&Options", self)
        self.options_menu.addAction(self.mouse_toggle_action)

        self.menuBar().addMenu(self.file_menu)
        self.menuBar().addMenu(self.options_menu)

        self.setWindowTitle("GC Image Viewer")
        self.resize(800, 600)

    def toggle_mouse_mode(self):
        self.render_area.mouse_mode = not self.render_area.mouse_mode

    def load_scene(self):
        file_name, _ = QFileDialog.getOpenFileName(self,
                                                   "Open File",
                                                   QDir.currentPath(),
                                                   )
        if file_name:
            with open(file_name) as in_file:
                scene = gcviewer.io.read_file(in_file)
                self.render_area.gc_scene = scene

                # if image.isNull():
                # QMessageBox.information(self, "Image Viewer",
                # "Cannot load %s." % file_name)
                # return

    def save_scene(self):
        file_name, _ = QFileDialog.getSaveFileName(self,
                                                   "Save File",
                                                   QDir.currentPath(),
                                                   )
        if file_name:
            with open(file_name, 'w') as out_file:
                scene = self.render_area.gc_scene._scene
                gcviewer.io.write_file(out_file, scene)

    def event(self, event):
        if event.type() == QEvent.KeyPress:
            if event.key() == Qt.Key_F12:
                self.toggle_fullscreen()
                return True
        return super(GCImageViewer, self).event(event)

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
    eye_x.on_event.append(
        lambda sample: imageViewer.render_area.gaze_change.emit(sample))

    imageViewer.show()
    sys.exit(app.exec_())
