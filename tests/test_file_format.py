from __future__ import division, unicode_literals, print_function

import os
import shutil
import sys
import tempfile
import unittest

import numpy as np

from gcviewer.gcio import read_gcfile, write_file
from gcviewer.modules.dof.directory_of_images_import import dir_to_scene
from gcviewer.modules.dof.scenes import SimpleArrayStackEncoder


class TestFileFormatIO(unittest.TestCase):
    def setUp(self):
        self.scene = dir_to_scene('./data/example_stack')

    def test_simple_save(self):
        data = SimpleArrayStackEncoder().data_from_scene(self.scene)
        self.assertIsNotNone(data)

    def test_simple_load(self):
        scene = read_gcfile('./data/example.gc')
        self.assertIsNotNone(scene)


class TestFileFormatIntegrity(unittest.TestCase):
    def setUp(self):
        self.reference_scene = dir_to_scene('./data/example_stack')
        self.tmp_dir = tempfile.mkdtemp()
        self.test_scene_path = os.path.join(self.tmp_dir, 'test_file.gc')
        with open(self.test_scene_path, 'wb') as tmp_file:
            write_file(tmp_file, self.reference_scene)
        self.test_scene = read_gcfile(self.test_scene_path)

    def tearDown(self):
        shutil.rmtree(self.tmp_dir)

    def test_depth_map_equality(self):
        np.testing.assert_allclose(self.reference_scene.lookup_table.array,
                                   self.test_scene.lookup_table.array)

    def test_index_equality(self):
        np.testing.assert_allclose(self.reference_scene.get_indices_image(),
                                   self.test_scene.get_indices_image()
                                   )

