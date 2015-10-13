"""
Defines unit tests for :mod:`gcviewer.modules.dof.scenes` module.
"""

from __future__ import division, unicode_literals, print_function

import numpy as np

import unittest
from gcviewer.modules.dof.image_manager import ArrayStackImageManager
from gcviewer.modules.dof.lookup_table import ArrayLookupTable
from gcviewer.modules.dof.scenes import ImageStackScene


class TestBasicDOFScene(unittest.TestCase):
    def setUp(self):
        depth_array = np.zeros([100, 100])
        lut = ArrayLookupTable(depth_array)

        frames = [np.ones([100, 100]) + i for i in range(5)]
        manager = ArrayStackImageManager(frames)

        self.scene = ImageStackScene(manager, lut)

    def test_set_gaze(self):
        self.scene.update_gaze((0, 0))
        self.scene.update_gaze((0.2, 0.6))
        self.scene.update_gaze((1, 1))
