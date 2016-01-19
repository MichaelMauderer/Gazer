from __future__ import unicode_literals, division, print_function

import numpy as np

from PyQt4.QtCore import pyqtSignal, QPoint, QSize, Qt, QPointF
from PyQt4.QtGui import QImage, QPixmap, QPainter, QColor
from PyQt4.QtOpenGL import QGLWidget

from gazer import eyetracking
from gazer.eyetracking.api import EyeData


class GCImageWidget(QGLWidget):
    """
    Widget that draws gaze contingent scenes based on current gaze position.

    Gaze updates are retrieved through the qt event system.
    """
    gaze_change = pyqtSignal(EyeData)

    def __init__(self, gc_scene, *args, **kwargs):
        super(GCImageWidget, self).__init__(*args, **kwargs)

        self.gaze_change.connect(self.update_gaze)

        self.mouse_mode = False
        self.show_cursor = False
        self._show_depthmap = False

        self._last_sample = None

        self.active_pixmap_size = QSize(0, 0)

        self._gc_scene = None
        self.gc_scene = gc_scene

        self.setMouseTracking(True)

    @property
    def gc_scene(self):
        return self._gc_scene

    @gc_scene.setter
    def gc_scene(self, scene):
        self._gc_scene = scene
        self.update_gaze(self._last_sample)

    def toggle_depthmap(self):
        self._show_depthmap = not self._show_depthmap

    def local_to_image_norm_coordinates(self, local_pos):
        """
        Converts local coordinates to normalised coordinates relative to the
        current image array.

        Parameters
        ----------
        local_pos : tuple
            Local position.

        Returns
        -------
        tuple of float
            Normalised coordinates in (0,1), relative to current image/pixmap.
            If no pixmap is set returns (0,0).
        """

        size = self.active_pixmap_size

        try:

            norm_pos_x = np.clip(local_pos[0] / size.width(), 0, 1)
            norm_pos_y = np.clip(local_pos[1] / size.height(), 0, 1)
        except ZeroDivisionError:
            return 0, 0

        return norm_pos_x, norm_pos_y

    def update_gaze(self, sample):
        self._last_sample = sample

        if self.gc_scene is None:
            return

        if sample is None:
            x, y = 0, 0
        else:
            x, y = sample.pos

        local_pos = self.mapFromGlobal(QPoint(x, y))
        image_norm_pos = self.local_to_image_norm_coordinates((local_pos.x(),
                                                               local_pos.y()))
        self._gaze = local_pos
        self.gc_scene.update_gaze(tuple(np.clip(image_norm_pos, 0, 1)))
        self.update()

    def get_current_image(self):
        if self.gc_scene is None:
            return None

        if self._show_depthmap:
            image = self.gc_scene.get_indices_image()
        else:
            image = self.gc_scene.get_image()
        return image

    def get_scaled_pixmap(self):
        image = self.get_current_image()

        if image is None:
            return None

        pixmap = array_to_pixmap(image)
        return pixmap.scaled(self.size(), Qt.KeepAspectRatio)

    @staticmethod
    def mouse_event_to_gaze_sample(QMouseEvent):
        return eyetracking.api.EyeData(-1,
                                       (float(QMouseEvent.globalX()),
                                        float(QMouseEvent.globalY())))

    def mouseMoveEvent(self, QMouseEvent):
        if self.mouse_mode:
            sample = self.mouse_event_to_gaze_sample(QMouseEvent)
            self.gaze_change.emit(sample)

    def paintEvent(self, QPaintEvent):

        painter = QPainter(self)
        painter.setRenderHint(painter.Antialiasing)

        pixmap = self.get_scaled_pixmap()
        if pixmap is not None:
            self.active_pixmap_size = pixmap.size()
            painter.drawPixmap(QPointF(0.0, 0.0), pixmap)

        if self.show_cursor:
            size = 20
            painter.setPen(QColor(0, 0, 0))
            x_origin = self._gaze.x() - size / 2
            y_origin = self._gaze.y() - size / 2
            painter.drawEllipse(x_origin,
                                y_origin,
                                size, size)
            painter.drawText(x_origin,
                             y_origin,
                             size, size,
                             Qt.AlignCenter,
                             str(self.gc_scene.current_index))
        painter.end()

    def heightForWidth(self, p_int):
        width = self.self.gc_scene.get_image().size().width()
        height = self.self.gc_scene.get_image().size().height()
        return (p_int / width) * height


def array_to_pixmap(array):
    array = np.require(array, dtype=np.int8, requirements=['C'])
    array.flags.writeable = False
    q_image = QImage(array.data,
                     array.shape[1],
                     array.shape[0],
                     3 * array.shape[1],
                     QImage.Format_RGB888)
    return QPixmap.fromImage(q_image)
