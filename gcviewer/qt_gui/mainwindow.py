from __future__ import unicode_literals, division, print_function

import logging
from functools import partial

from PyQt4.QtCore import QDir, Qt, pyqtSignal, QEvent
from PyQt4.QtGui import QAction, QFileDialog, QMainWindow, QMenu, QSizePolicy
from PyQt4.QtGui import QActionGroup

import gcviewer
import gcviewer.modules.dof.directory_of_images_import as dir_import
from gcviewer import gcio, scene
from gcviewer.qt_gui.async import SceneLoader
from gcviewer.qt_gui.dialogs import PreferencesDialog
from gcviewer.qt_gui.gcwidget import GCImageWidget

logger = logging.getLogger(__name__)


class GCImageViewerMainWindow(QMainWindow):
    """
    Main window of GCViewer qt gui.
    Provides overall layout and menus to access basic functionality.
    """

    scene_update = pyqtSignal(scene.Scene)

    def __init__(self, tracking_apis={}):
        super(GCImageViewerMainWindow, self).__init__()

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
            scene_load_func = partial(gcio.load_scene, str(file_name))
            loader = SceneLoader(scene_load_func, parent=self)
            loader.load_finished.connect(self.scene_update.emit)
            loader.start_import()

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
        try:
            from gcviewer.modules.dof.lytro_import import read_ifp
        except ImportError:
            logger.exception('Could not import Lytro Power Tools.')
            return

        file_name = QFileDialog.getOpenFileName(self.parent(),
                                                "Import File",
                                                QDir.currentPath(),
                                                filter="LFP Raw File (*.lfr)",
                                                )
        if file_name:
            current_preferences = gcviewer.preferences.load_preferences()
            scene_load_func = partial(read_ifp,
                                      str(file_name),
                                      current_preferences)
            loader = SceneLoader(scene_load_func, parent=self)
            loader.load_finished.connect(self.scene_update.emit)
            loader.start_import()

    def import_directory_of_images(self):
        param = QFileDialog.ShowDirsOnly | QFileDialog.DontResolveSymlinks
        folder_name = QFileDialog.getExistingDirectory(self,
                                                       "Open Directory",
                                                       QDir.currentPath(),
                                                       param
                                                       )
        if folder_name:
            scene_load_func = partial(dir_import.dir_to_scene,
                                      str(folder_name),
                                      )
            loader = SceneLoader(scene_load_func, parent=self)
            loader.load_finished.connect(self.scene_update.emit)
            loader.start_import()

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
        return super(GCImageViewerMainWindow, self).event(event)

    def toggle_fullscreen(self):
        if self.isFullScreen():
            self.showNormal()
        else:
            self.showFullScreen()

    def update(self, *__args):
        super(GCImageViewerMainWindow, self).update()
        self.render_area.update()
