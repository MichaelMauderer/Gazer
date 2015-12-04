"""
Defines unit tests for :mod:`gcviewer.modules.dof.scenes` module.
"""

from __future__ import division, unicode_literals, print_function

import numpy as np

import unittest

from gcviewer.modules.dof.dof_data import DOFData
from gcviewer.modules.dof.image_manager import ArrayStackImageManager
from gcviewer.modules.dof.interpolator import InstantInterpolator
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
        self.scene = ImageStackScene.from_dof_data(dof_data, InstantInterpolator())

    def test_frame_corners(self):
        self.scene.update_gaze((0.0, 0.0))
        np.testing.assert_almost_equal(self.frame_mapping[0], self.scene.get_image(), err_msg="Assert one has failed")
        self.scene.update_gaze((0.9, 0.0))
        np.testing.assert_almost_equal(self.frame_mapping[3], self.scene.get_image(), err_msg="Assert two has failed")
        self.scene.update_gaze((0.0, 0.9))
        np.testing.assert_almost_equal(self.frame_mapping[2], self.scene.get_image(), err_msg="Assert three has failed")
        self.scene.update_gaze((0.9, 0.9))
        np.testing.assert_almost_equal(self.frame_mapping[1], self.scene.get_image(), err_msg="Assert four has failed")


class TestImageStackManager(unittest.TestCase):
    def setUp(self):
        self.frames = [
            np.array([0]),
            np.array([1]),
            np.array([2]),
            np.array([3]),
        ]
        self.image_manager = ArrayStackImageManager(self.frames)

    def test_load_image(self):
        np.testing.assert_almost_equal(self.image_manager.load_image(2), self.frames[2])

    def test_load_image_fraction(self):
        np.testing.assert_almost_equal(self.image_manager.load_image(1.7), self.frames[1])


class TestLookupTable(unittest.TestCase):
    def setUp(self):
        self.depth_array = np.array([
            [0, 1, 2],
            [3, 4, 5],
            [6, 7, 8],
        ])
        self.lookup_table = ArrayLookupTable(self.depth_array)

    def test_sample_corners(self):
        np.testing.assert_equal(self.lookup_table.sample_position((0.0, 0.0)), 0)
        np.testing.assert_equal(self.lookup_table.sample_position((0.9, 0.0)), 2)
        np.testing.assert_equal(self.lookup_table.sample_position((0.0, 0.9)), 6)
        np.testing.assert_equal(self.lookup_table.sample_position((0.9, 0.9)), 8)

    def test_out_of_bounds(self):
        np.testing.assert_equal(self.lookup_table.sample_position((0.0, 1.0)), None)
        np.testing.assert_equal(self.lookup_table.sample_position((1.0, 0.0)), None)
        np.testing.assert_equal(self.lookup_table.sample_position((-1.8, 0.0)), None)
        np.testing.assert_equal(self.lookup_table.sample_position((0.1, 1.1)), None)
