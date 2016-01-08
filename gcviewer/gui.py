from __future__ import unicode_literals, division, print_function

import logging
import os
from functools import partial

import numpy as np
from PyQt4 import QtGui
from PyQt4.QtCore import QDir, Qt, pyqtSignal, QPoint, QEvent, QPointF, QSize, \
    QThread, QObject
from PyQt4.QtGui import (QAction, QFileDialog,
                         QMainWindow, QMenu, QSizePolicy)
from PyQt4.QtGui import QImage, QPixmap, QActionGroup
from PyQt4.QtOpenGL import QGLWidget

import gcviewer.modules.dof.directory_of_images_import as dir_import
import preferences
from gcviewer import gcio, eyetracking, scene
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


class GCImageWidget(QGLWidget):
    """
    Widget that draws gaze contingent scenes based on current gaze position.

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

        self.active_pixmap_size = QSize(0, 0)

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

        painter = QtGui.QPainter(self)
        painter.setRenderHint(painter.Antialiasing)

        pixmap = self.get_scaled_pixmap()
        if pixmap is not None:
            self.active_pixmap_size = pixmap.size()
            painter.drawPixmap(QPointF(0.0, 0.0), pixmap)
            print(self.active_pixmap_size)

        if self.show_cursor:
            size = 20
            painter.setBrush(QtGui.QColor(0, 255, 0))
            painter.drawEllipse(self._gaze.x() - size / 2,
                                self._gaze.y() - size / 2,
                                size, size)
            painter.drawText(self._gaze.x() - size / 2,
                             self._gaze.y() - size / 2,
                             str(self.gc_scene.current_index))
        painter.end()

    def heightForWidth(self, p_int):
        width = self.self.gc_scene.get_image().size().width()
        height = self.self.gc_scene.get_image().size().height()
        return (p_int / width) * height


class GCImageViewer(QMainWindow):
    """
    Main window of GCViewer qt gui.
    Provides overall layout and menus to access basic functionality.
    """

    scene_update = pyqtSignal(scene.Scene)

    def __init__(self, tracking_apis={}):
        super(GCImageViewer, self).__init__()

        # Ete tracking setup
        self.tracking_apis = tracking_apis
        self.tracker = None

        # Main layout
        self.render_area = GCImageWidget(None)
        self.render_area.setSizePolicy(QSizePolicy.Ignored,
                                       QSizePolicy.Ignored)
        self.setCentralWidget(self.render_area)

        # Create actions
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
        self.import_directory_of_images_action = QAction(
                "&Import directory of images",  # NOQA
                self,
                shortcut="Ctrl+D",
                triggered=self.import_directory_of_images)
        self.export_image_stack_action = QAction(
                "&Export as Image Stack",  # NOQA
                self,
                shortcut="Ctrl+E",
                triggered=self.export_image_stack)
        self.preferences_action = QAction("&Preferences",
                                          self,
                                          shortcut="Ctrl+P",
                                          triggered=self.open_preferences
                                          )
        self.exit_action = QAction("E&xit",
                                   self,
                                   shortcut="Ctrl+Q",
                                   triggered=self.close
                                   )

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
        self.file_menu.addAction(self.export_image_stack_action)
        self.file_menu.addAction(self.import_directory_of_images_action)
        self.file_menu.addSeparator()
        self.file_menu.addAction(self.preferences_action)
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

        self.scene_update.connect(self.update_scene)

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

        self.tracker.on_event.append(self.render_area.gaze_change.emit)

    def toggle_mouse_mode(self):
        self.render_area.mouse_mode = not self.render_area.mouse_mode

    def toggle_cursor(self):
        self.render_area.show_cursor = not self.render_area.show_cursor

    def toggle_depthmap(self):
        self.render_area.toggle_depthmap()
        self.update()

    def update_scene(self, scene):
        self.render_area.gc_scene = scene
        self.render_area.update()

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
        file_name = QFileDialog.getSaveFileName(self,
                                                "Save File",
                                                QDir.currentPath(),
                                                )
        if file_name:
            with open(file_name, 'wb') as out_file:
                scene = self.render_area.gc_scene
                gcio.write_file(out_file, scene)

    def import_ifp(self):
        importer = LFPImporter(self.statusBar(), parent=self)
        importer.load_finished.connect(self.scene_update.emit)
        importer.start_import()

    def import_directory_of_images(self):
        param = QFileDialog.ShowDirsOnly | QFileDialog.DontResolveSymlinks
        folder_name = QFileDialog.getExistingDirectory(self,
                                                       "Open Directory",
                                                       QDir.currentPath(),
                                                       param
                                                       )
        if folder_name:
            dir_import.dir_to_dof_data(str(folder_name))

    def export_image_stack(self):
        folder_name = str(QFileDialog.getExistingDirectory(self,
                                                           "Select Directory"))
        if folder_name:
            gcio.extract_scene_to_stack(self.render_area.gc_scene, folder_name)

    def open_preferences(self):
        # print("Open Preferences!")
        dialog = PreferencesDialog()
        dialog.exec_()

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


class PreferencesDialog(QtGui.QDialog):
    def __init__(self, parent=None):
        super(PreferencesDialog, self).__init__(parent)
        # add the line edit
        label = QtGui.QLabel()
        label.setText('Path to camera calibration directory:')

        self.line_edit = QtGui.QLineEdit()
        self.calibration_path = preferences.get_calibration_path()
        self.line_edit.setText(self.calibration_path)

        edit_layout = QtGui.QHBoxLayout()
        edit_layout.addWidget(self.line_edit)
        select_button = QtGui.QPushButton("Select")
        select_button.clicked.connect(self.open_file_picker)
        edit_layout.addWidget(select_button)

        # buttons
        ok_button = QtGui.QPushButton("OK")
        cancel_button = QtGui.QPushButton("Cancel")

        ok_button.clicked.connect(self.ok_clicked)
        cancel_button.clicked.connect(self.cancel_clicked)

        # layout
        hbox = QtGui.QHBoxLayout()
        hbox.addStretch(1)
        hbox.addWidget(ok_button)
        hbox.addWidget(cancel_button)

        vbox = QtGui.QVBoxLayout()
        vbox.addStretch(1)
        vbox.addWidget(label)
        vbox.addLayout(edit_layout)
        vbox.addLayout(hbox)
        self.setLayout(vbox)

        # show the window
        # self.setGeometry(300, 300, 300, 150)
        self.setFixedWidth(400)
        self.setWindowTitle("Preferences")
        self.show()

    def ok_clicked(self):
        preferences.set_calibration_path(self.calibration_path)
        self.close()

    def cancel_clicked(self):
        self.close()

    def open_file_picker(self):
        msg = 'Select calibration directory'
        dir_name = QFileDialog.getExistingDirectory(self, msg)

        if dir_name:
            self.calibration_path = dir_name
            self.line_edit.setText(dir_name)


class TaskWorker(QThread):
    task_done = pyqtSignal()

    def __init__(self, task, *args, **kwargs):
        super(TaskWorker, self).__init__(*args, **kwargs)
        self.task = task
        self.result = None

    def run(self):
        self.result = self.task()
        self.task_done.emit()


class LFPImporter(QObject):
    load_finished = pyqtSignal(scene.Scene)

    def __init__(self, status_bar, *args, **kwargs):
        super(LFPImporter, self).__init__(*args, **kwargs)
        self.status_bar = status_bar
        self.file_path = None

        self.progress_bar = QtGui.QProgressBar()
        self.progress_bar.setRange(0, 0)
        self.worker = None

    def start_import(self):
        self._choose_file()
        self._async_load()

    def _on_load_finished(self):
        logger.debug('On load finished')
        self.scene = self.worker.result
        self.status_bar.showMessage('Finished importing', 3000)
        self.status_bar.removeWidget(self.progress_bar)
        self.load_finished.emit(self.scene)

    def _on_load_start(self):
        logger.debug('On load start')
        file_base_name = os.path.basename(str(self.file_path))
        start_message = 'Importing {}'.format(file_base_name)
        self.status_bar.showMessage(start_message)
        self.status_bar.insertPermanentWidget(0, self.progress_bar)

    def _choose_file(self):
        file_name = QFileDialog.getOpenFileName(self.parent(),
                                                "Import File",
                                                QDir.currentPath(),
                                                filter="LFP Raw File (*.lfr)",
                                                )
        self.file_path = file_name

    def _load(self):
        try:
            from modules.dof.lytro_import import read_ifp
        except ImportError:
            logger.exception('Could not import Lytro Power Tools.')
            return

        current_preferences = preferences.load_preferences()
        result_scene = read_ifp(self.file_path,
                                current_preferences,
                                )
        return result_scene

    def _async_load(self):
        self._on_load_start()
        self.worker = TaskWorker(self._load)
        self.worker.task_done.connect(self._on_load_finished)
        self.worker.start()

    def _status_update(self, status_message):
        file_base_name = os.path.basename(str(self.file_path))
        message = 'Importing {}'.format(file_base_name)
        message += ' (Frame ' + status_message + ')'
        self.status_bar.showMessage(message)
