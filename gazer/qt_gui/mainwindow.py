from __future__ import unicode_literals, division, print_function

import logging
import webbrowser

from PyQt4 import QtGui
from functools import partial

from PyQt4.QtCore import QDir, Qt, QEvent
from PyQt4.QtGui import QAction, QFileDialog, QMainWindow, QMenu, \
    QErrorMessage
from PyQt4.QtGui import QActionGroup

import gazer
import gazer.modules.dof.directory_of_images_import as dir_import
from gazer import gcio
from gazer.qt_gui.async import BlockingTask
from gazer.qt_gui.dialogs import PreferencesDialog
from gazer.qt_gui.gcwidget import GCImageWidget

logger = logging.getLogger(__name__)

try:
    from gazer.modules.dof.lytro_import import read_ifp
except ImportError:
    logger.exception('Could not import Lytro Power Tools.')
    read_ifp = None


class GCImageViewerMainWindow(QMainWindow):
    """
    Main window of GCViewer qt gui.
    Provides overall layout and menus to access basic functionality.
    """

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
                                   triggered=self.load_scene_procedure)
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
        self.options_menu.addAction(self.cursor_toggle_action)
        self.options_menu.addAction(self.toggle_depthmap_action)

        tracker_menu = self.options_menu.addMenu('Select Tracker')
        tracker_menu.addActions(self.select_tracker_action_group.actions())

        # Set default gaze input or mouse simulation
        if self.select_tracker_action_group.actions():
            self.select_tracker_action_group.actions()[0].trigger()
        else:
            self.mouse_toggle_action.trigger()

        # Add menus to menu bar
        self.menuBar().addMenu(self.file_menu)
        self.menuBar().addMenu(self.options_menu)

        # Add help menu
        help_menu = QMenu("&Help", self)
        project_url = 'http://deepview.cs.st-andrews.ac.uk'
        help_menu.addAction(QAction("Project Website",
                                    self,
                                    triggered=lambda: webbrowser.open(
                                            project_url),
                                    )
                            )

        help_menu.addAction(QAction("About",
                                    self,
                                    triggered=self.show_about,
                                    )
                            )
        self.menuBar().addMenu(help_menu)

        self.setWindowTitle("GC Image Viewer")
        self.resize(800, 600)

    def _make_tracker_select_menu(self):
        self.select_tracker_action_group = QActionGroup(self)
        self.select_tracker_action_group.setExclusive(True)

        # Add detected eye trackers
        for name, api in self.tracking_apis.items():
            action = QAction(name,
                             self,
                             triggered=partial(self.select_eye_tracker, name),
                             checkable=True,
                             )
            self.select_tracker_action_group.addAction(action)

        # Add mouse input as fallback
        mouse_mode = QAction("Mouse",
                             self,
                             triggered=self.toggle_mouse_mode,
                             checkable=True,
                             )
        self.select_tracker_action_group.addAction(mouse_mode)

    def select_eye_tracker(self, tracker_api_key):
        self.disable_mouse_mode()
        logger.debug('Selecting tracker {}'.format(tracker_api_key))
        if self.tracker:
            self.tracker.on_event = []
        self.tracker = self.tracking_apis.get(tracker_api_key)

        self.tracker.on_event.append(self.render_area.update_gaze)

    def toggle_mouse_mode(self):
        self.render_area.mouse_mode = not self.render_area.mouse_mode

    def disable_mouse_mode(self):
        self.render_area.mouse_mode = False

    def toggle_cursor(self):
        self.render_area.show_cursor = not self.render_area.show_cursor

    def toggle_depthmap(self):
        self.render_area.toggle_depthmap()
        self.update()

    def update_scene(self, scene):
        self.render_area.gc_scene = scene
        self.render_area.update()

    def load_scene_procedure(self):
        """
        Starts UI procedure to load scene form .gc file.
        """
        file_name = QFileDialog.getOpenFileName(self,
                                                "Open File",
                                                QDir.currentPath(),
                                                filter="GC File (*.gc)"
                                                )
        if file_name:
            self.load_scene_file(str(file_name))

    def load_scene_file(self, path):
        """
        Starts asynchronous loading of scene object from a .gc file.

        Parameters
        ----------
        path: str
            Path to file that will be loaded.
        """

        scene_load_func = partial(gcio.load_scene, str(path))
        loader = BlockingTask(scene_load_func,
                              'Loading file.',
                              parent=self)
        loader.load_finished.connect(self.update_scene)
        loader.start_task()

    def save_scene(self):
        file_name = QFileDialog.getSaveFileName(self,
                                                "Save File",
                                                QDir.currentPath(),
                                                filter="GC File (*.gc)",
                                                )
        if file_name:
            def task():
                with open(file_name, 'wb') as out_file:
                    scene = self.render_area.gc_scene
                    gcio.write_file(out_file, scene)

            loader = BlockingTask(task,
                                  'Saving file.',
                                  parent=self)
            loader.start_task()

    def import_ifp(self):
        """
        Starts UI procedure to import a scene from a Lytro raw file.
        """
        if read_ifp is None:
            QErrorMessage(self).showMessage('Lytro import unavailable.')
            return
        file_name = QFileDialog.getOpenFileName(self.parent(),
                                                "Import File",
                                                QDir.currentPath(),
                                                filter="LFP Raw File (*.lfr)",
                                                )
        if file_name:
            self.import_ifp_file(str(file_name))

    def import_ifp_file(self, path):
        """
        Starts asynchronous importing of a scene from a Lytro raw file.

        Parameters
        ----------
        path: str
            Path to file that will be loaded.

        """
        if read_ifp is None:
            QErrorMessage(self).showMessage('Lytro import unavailable.')
            return

        current_preferences = gazer.preferences.load_preferences()
        scene_load_func = partial(read_ifp,
                                  path,
                                  current_preferences)
        loader = BlockingTask(scene_load_func,
                              'Importing file.',
                              parent=self)
        loader.load_finished.connect(self.update_scene)
        loader.start_task()

    def import_directory_of_images(self):
        """
        Starts UI procedure to load scene from image stack.
        """
        param = QFileDialog.ShowDirsOnly | QFileDialog.DontResolveSymlinks
        folder_name = QFileDialog.getExistingDirectory(self,
                                                       "Open Directory",
                                                       QDir.currentPath(),
                                                       param
                                                       )
        if folder_name:
            self.load_image_stack_folder(str(folder_name))

    def load_image_stack_folder(self, path):
        """
        Starts asynchronous loading of scene object from an image stack.

        Parameters
        ----------
        path: str
            Path to folder that will be loaded.

        """
        scene_load_func = partial(dir_import.dir_to_scene,
                                  path,
                                  )
        loader = BlockingTask(scene_load_func,
                              'Importing files.',
                              parent=self)
        loader.load_finished.connect(self.update_scene)
        loader.start_task()

    def export_image_stack(self):
        folder_name = str(QFileDialog.getExistingDirectory(self,
                                                           "Select Directory"))
        if folder_name:
            export_function = partial(gcio.extract_scene_to_stack,
                                      self.render_area.gc_scene,
                                      folder_name
                                      )
            task = BlockingTask(export_function,
                                'Extracting files.',
                                parent=self,
                                )
            task.start_task()

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

    def show_about(self):
        info_dict = {'version': '0.1',
                     'copyright_year': '2016'}

        about_text = """
        <p><b>Gazer</b>&nbsp;&nbsp;&nbsp;v{version}</p>
        <br>
        <p>&copy; {copyright_year}
        Michael Mauderer and Miguel Nacenta</p>
        """.format(**info_dict)
        QtGui.QMessageBox.about(self, 'About', about_text)
