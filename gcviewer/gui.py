from __future__ import unicode_literals, division, print_function

import logging
from functools import partial

import numpy as np
from PyQt4 import QtGui
from PyQt4.QtCore import QDir, Qt, pyqtSignal, QPoint, QEvent, QPointF
from PyQt4.QtGui import QImage, QPixmap, QActionGroup

from PyQt4.QtGui import (QAction, QFileDialog, QLabel,
                         QMainWindow, QMenu, QSizePolicy)

from gcviewer import gcio, eyetracking
from gcviewer.eyetracking.api import EyeData

logger = logging.getLogger(__name__)


def array_to_pixmap(array):
    array = np.require(array, dtype=np.int8, requirements=['C'])
    array.flags.writeable = False
    q_image = QImage(array.data,
                     array.shape[1],
                     array.shape[0],
                     3 * array.shape[1],
                     QImage.Format_RGB888)
    return QPixmap.fromImage(q_image)


class GCImageWidget(QLabel):
    """
    QtLabel that draws gaze contingent scenes based on current gaze position.

    Gaze updates are retrieved through the qt event system.
    """
    gaze_change = pyqtSignal(EyeData)

    def __init__(self, gc_scene, *args, **kwargs):
        super(GCImageWidget, self).__init__(*args, **kwargs)

        self._gc_scene = None
        self.gc_scene = gc_scene

        self._gaze = QPoint(0, 0)
        self.gaze_change.connect(self.update_gaze)

        self.mouse_mode = False
        self.show_cursor = False
        self._show_depthmap = False

        self._last_sample = None

        self.memo_pixmap = None

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

        pixmap = self.pixmap()
        if pixmap is None:
            return 0, 0
        pixmap_size = pixmap.size()

        norm_pos_x = np.clip(local_pos[0] / pixmap_size.width(), 0, 1)
        norm_pos_y = np.clip(local_pos[1] / pixmap_size.height(), 0, 1)

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

        self.repaint()

    def get_current_image(self):
        if self.gc_scene is None:
            return None

        if self._show_depthmap:
            image = self.gc_scene.get_depth_image()
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
        super(QLabel, self).paintEvent(QPaintEvent)
        painter = QtGui.QPainter(self)
        painter.setBrush(QtGui.QColor(0, 255, 0))
        pixmap = self.get_scaled_pixmap()
        if pixmap is not None:
            self.setPixmap(pixmap)
            painter.drawPixmap(QPointF(0.0, 0.0), pixmap)
        if self.show_cursor:
            size = 10
            painter.drawEllipse(self._gaze.x() - size / 2,
                                self._gaze.y() - size / 2,
                                size, size)
            painter.end()

    def heightForWidth(self, p_int):
        width = self.self.gc_scene.get_image().size().width()
        height = self.self.gc_scene.get_image().size().height()
        return (p_int / width) * height

    def update(self, *__args):
        super(GCImageWidget, self).update()
        self.update_gaze(self._last_sample)


class GCImageViewer(QMainWindow):
    """
    Main window of GCViewer qt gui.
    Provides overall layout and menus to access basic functionality.
    """

    def __init__(self, tracking_apis={}):
        super(GCImageViewer, self).__init__()

        self.tracking_apis = tracking_apis
        self.tracker = None

        self.render_area = GCImageWidget(None)
        self.render_area.setSizePolicy(QSizePolicy.Ignored,
                                       QSizePolicy.Ignored)
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
        self.import_ifp_action = QAction("&Import Lytro file",
                                         self,
                                         shortcut="Ctrl+I",
                                         triggered=self.import_ifp)
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

        self.cursor_toggle_action = QAction("Toggle debug cursor",
                                            self,
                                            triggered=self.toggle_cursor,
                                            checkable=True,
                                            checked=False,
                                            )
        self.toggle_depthmap_action = QAction("Toggle depthmap",
                                              self,
                                              triggered=self.toggle_depthmap,
                                              checkable=True,
                                              checked=False,
                                              )

        self._make_tracker_select_menu()

        # Create Menues
        self.file_menu = QMenu("&File", self)
        self.file_menu.addAction(self.open_action)
        self.file_menu.addAction(self.save_action)
        self.file_menu.addAction(self.import_ifp_action)
        self.file_menu.addSeparator()
        self.file_menu.addAction(self.exit_action)

        # Create Option Menu
        self.options_menu = QMenu("&Options", self)
        self.options_menu.addAction(self.mouse_toggle_action)
        self.options_menu.addAction(self.cursor_toggle_action)
        self.options_menu.addAction(self.toggle_depthmap_action)

        tracker_Menu = self.options_menu.addMenu('Select Tracker')
        tracker_Menu.addActions(self.select_tracker_action_group.actions())

        self.menuBar().addMenu(self.file_menu)
        self.menuBar().addMenu(self.options_menu)

        self.setWindowTitle("GC Image Viewer")
        self.resize(800, 600)

    def _make_tracker_select_menu(self):
        self.select_tracker_action_group = QActionGroup(self)
        self.select_tracker_action_group.setExclusive(True)

        for name, api in self.tracking_apis.items():
            action = QAction(name,
                             self,
                             triggered=partial(self.select_eye_tracker, name),
                             checkable=True,
                             )
            self.select_tracker_action_group.addAction(action)

    def select_eye_tracker(self, tracker_api_key):
        logger.debug('Selecting tracker {}'.format(tracker_api_key))
        if self.tracker:
            self.tracker.on_event = []
        self.tracker = self.tracking_apis.get(tracker_api_key)
        self.tracker.on_event.append(
            lambda sample: self.render_area.gaze_change.emit(sample))

    def toggle_mouse_mode(self):
        self.render_area.mouse_mode = not self.render_area.mouse_mode

    def toggle_cursor(self):
        self.render_area.show_cursor = not self.render_area.show_cursor

    def toggle_depthmap(self):
        self.render_area.toggle_depthmap()
        self.update()

    def load_scene(self):
        file_name = QFileDialog.getOpenFileName(self,
                                                "Open File",
                                                QDir.currentPath(),
                                                )
        if file_name:
            scene = gcio.load_scene(str(file_name))
            self.render_area.gc_scene = scene
            self.render_area.update()

    def save_scene(self):
        file_name, _ = QFileDialog.getSaveFileName(self,
                                                   "Save File",
                                                   QDir.currentPath(),
                                                   )
        if file_name:
            with open(file_name, 'w') as out_file:
                scene = self.render_area.gc_scene._scene
                gcio.write_file(out_file, scene)

    def import_ifp(self):
        try:
            from modules.dof.lytro_import import read_ifp
            file_name = QFileDialog.getOpenFileName(self,
                                                    "Import File",
                                                    QDir.currentPath(),
                                                    )
            if file_name:
                read_ifp(file_name)
        except ImportError:
            logger.exception('Could not import Lytro Power Tools.')
            return None

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

    def update(self, *__args):
        super(GCImageViewer, self).update()
        self.render_area.update()
