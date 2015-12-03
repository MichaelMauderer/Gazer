"""
Defines unit tests for :mod:`gcviewer.modules.dof.scenes` module.
"""

from __future__ import division, unicode_literals, print_function

import numpy as np

import unittest

from gcviewer.modules.dof.dof_data import DOFData
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


class TestImageStackScene(unittest.TestCase):
    def setUp(self):
        self.depth_array = np.array([
            [0, 3],
            [2, 1]
        ])
        self.frame_mapping = {
            0: np.array([0]),
            1: np.array([1]),
            2: np.array([2]),
            3: np.array([3]),
        }
        dof_data = DOFData(self.depth_array, self.frame_mapping)
        self.scene = ImageStackScene.from_dof_data(dof_data)

    def test_frame_corners(self):
        self.scene.update_gaze((0.0, 0.0))
        np.testing.assert_almost_equal(self.frame_mapping[0], self.scene.get_image())
        self.scene.update_gaze((1.0, 0.0))
        np.testing.assert_almost_equal(self.frame_mapping[3], self.scene.get_image())
        self.scene.update_gaze((0.0, 1.0))
        np.testing.assert_almost_equal(self.frame_mapping[2], self.scene.get_image())
        self.scene.update_gaze((1.0, 1.0))
        np.testing.assert_almost_equal(self.frame_mapping[1], self.scene.get_image())
