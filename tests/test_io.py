from __future__ import division, unicode_literals, print_function

import unittest

from gazer.gcio import load_scene


class TestFileFormatIntegrity(unittest.TestCase):
    def test_load_correct(self):
        result_a = 'result_a'
        result_b = 'result_b'

        test_loaders = {
            'aaa': lambda x: result_a,
            'bbb': lambda x: result_b,
        }
        test_path_1 = '\\sample\\path\\test_file.aaa'
        test_path_2 = '\\sample\\path\\test_file.bbb'

        self.assertEqual(
            load_scene(test_path_1, test_loaders),
            result_a
        )
        self.assertEqual(
            load_scene(test_path_2, test_loaders),
            result_b
        )
