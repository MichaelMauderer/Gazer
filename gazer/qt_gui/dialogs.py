from __future__ import unicode_literals, division, print_function

import logging

from PyQt4.QtGui import QFileDialog, QDialog, QLabel, QHBoxLayout, QLineEdit, \
    QPushButton, QVBoxLayout

import gazer.preferences

logger = logging.getLogger(__name__)


class PreferencesDialog(QDialog):
    def __init__(self, parent=None):
        super(PreferencesDialog, self).__init__(parent)
        # add the line edit
        label = QLabel()
        label.setText('Path to camera calibration directory:')

        self.line_edit = QLineEdit()
        self.calibration_path = gazer.preferences.get_calibration_path()
        self.line_edit.setText(self.calibration_path)

        edit_layout = QHBoxLayout()
        edit_layout.addWidget(self.line_edit)
        select_button = QPushButton("Select")
        select_button.clicked.connect(self.open_file_picker)
        edit_layout.addWidget(select_button)

        # buttons
        ok_button = QPushButton("OK")
        cancel_button = QPushButton("Cancel")

        ok_button.clicked.connect(self.ok_clicked)
        cancel_button.clicked.connect(self.cancel_clicked)

        # layout
        hbox = QHBoxLayout()
        hbox.addStretch(1)
        hbox.addWidget(ok_button)
        hbox.addWidget(cancel_button)

        vbox = QVBoxLayout()
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
        gazer.preferences.set_calibration_path(self.calibration_path)
        self.close()

    def cancel_clicked(self):
        self.close()

    def open_file_picker(self):
        msg = 'Select calibration directory'
        dir_name = QFileDialog.getExistingDirectory(self, msg)

        if dir_name:
            self.calibration_path = dir_name
            self.line_edit.setText(dir_name)
