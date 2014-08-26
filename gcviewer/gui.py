from PyQt5 import QtGui
from PyQt5.QtCore import QDir, Qt, pyqtSlot, pyqtSignal, QPoint
from PyQt5.QtGui import QImage, QPainter, QPalette, QPixmap
from PyQt5.QtWidgets import (QAction, QApplication, QFileDialog, QLabel,
                             QMainWindow, QMenu, QMessageBox, QScrollArea, QSizePolicy)
from eyexinterface import EyeXInterface, Sample
import gcviewer.io
import numpy as np


class GCImageWidget(QLabel):
    gaze_change = pyqtSignal(Sample)

    def __init__(self, gc_scene, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.gc_scene = gc_scene

        self.gaze_change.connect(self.update_gaze)

    def update_gaze(self, sample):
        if self.gc_scene is None:
            return

        local_pos = self.mapFromGlobal(QPoint(sample.x, sample.y))
        self._gaze = local_pos
        self.gc_scene.update_gaze((local_pos.x() / self.size().width(), 1 - (local_pos.y() / self.size().height()) ))
        image = self.gc_scene.get_image()
        if image is not None:
            image = np.require(image, np.uint8, 'C')
            q_image = QImage(image.data, image.shape[1], image.shape[0], QImage.Format_RGB888)
            self.setPixmap(QPixmap.fromImage(q_image))
            self.update()

    def paintEvent(self, QPaintEvent):
        super().paintEvent(QPaintEvent)
        painter = QtGui.QPainter(self)
        painter.setBrush(QtGui.QColor(0, 255, 0))
        painter.drawEllipse(self._gaze.x(), self._gaze.y(), 50, 50)
        painter.end()


class GCImageViewer(QMainWindow):
    def __init__(self):
        super(GCImageViewer, self).__init__()

        self.render_area = GCImageWidget(None)
        self.render_area.setBackgroundRole(QPalette.Base)
        self.render_area.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Ignored)
        self.render_area.setScaledContents(True)
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


if __name__ == '__main__':
    import sys

    app = QApplication(sys.argv)
    imageViewer = GCImageViewer()

    eye_x = EyeXInterface('../lib/Tobii.EyeX.Client.dll')
    eye_x.on_event.append(lambda sample: imageViewer.render_area.gaze_change.emit(sample))

    imageViewer.show()
    sys.exit(app.exec_())