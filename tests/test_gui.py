"""
Defines unit tests for :mod:`gcviewer.gui` module.
"""

from __future__ import division, unicode_literals, print_function

import sys
import unittest

import PyQt4.QtCore as qt
import mock
import numpy as np
from PyQt4.QtGui import QApplication

from gcviewer.qt_gui.gcwidget import GCImageWidget

app = QApplication(sys.argv)


class TestCoordinateConversion(unittest.TestCase):
    def setUp(self):
        self.mock_scene = mock.MagicMock()
        self.mock_scene.get_image = mock.MagicMock(return_value=np.zeros([100,
                                                                          100]))
        self.mock_scene.update_gaze = mock.MagicMock()

        self.gc_image_widget = GCImageWidget(self.mock_scene)

    @unittest.skip
    def test_pixmap_resizing(self):
        self.gc_image_widget.setFixedSize(1000, 2000)
        pixmap = self.gc_image_widget.get_scaled_pixmap()
        self.assertEqual(pixmap.size(), qt.QSize(1000, 1000))

        self.gc_image_widget.setFixedSize(3000, 1000)
        pixmap = self.gc_image_widget.get_scaled_pixmap()
        self.assertEqual(pixmap.size(), qt.QSize(1000, 1000))

        self.gc_image_widget.setFixedSize(500, 1000)
        pixmap = self.gc_image_widget.get_scaled_pixmap()
        self.assertEqual(pixmap.size(), qt.QSize(500, 500))

        self.gc_image_widget.setFixedSize(500, 10)
        pixmap = self.gc_image_widget.get_scaled_pixmap()
        self.assertEqual(pixmap.size(), qt.QSize(10, 10))

    @unittest.skip
    def test_local_to_pixmap_conversion(self):
        self.gc_image_widget.setFixedSize(1000, 2000)
        self.gc_image_widget.active_pixmap_size = qt.QSize(1000, 1000)

        convert = self.gc_image_widget.local_to_image_norm_coordinates

        np.testing.assert_allclose(convert((0, 0)), (0, 0))
        np.testing.assert_allclose(convert((1000, 1000)), (1.0, 1.0))

        np.testing.assert_allclose(convert((500, 1000)), (0.5, 1.0))
        np.testing.assert_allclose(convert((250, 1500)), (0.25, 1.0))

        np.testing.assert_allclose(convert((1000, 500)), (1.0, 0.5))
        np.testing.assert_allclose(convert((1500, 250)), (1.0, 0.25))
