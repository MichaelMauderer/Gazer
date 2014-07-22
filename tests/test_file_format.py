import bz2
import unittest
from gcviewer.io import array_to_string, read_file
import numpy
from bson import BSON
import bson
import io


class LoadSimpleArrayStackTestCase(unittest.TestCase):
    def setUp(self):
        wrapper = {'encoder': 'gcviewer',
                   'version': '0.1',
                   'compression': 'bz2',
                   'type': 'simple_array_stack'
        }

        self.lut = numpy.array([1, 1, 2, 2])
        self.frame1 = numpy.array([3, 3, 3, 3])
        self.frame2 = numpy.array([4, 4, 4, 4])
        data = {'lookup_table': array_to_string(self.lut),
                'frames': {'1': array_to_string(self.frame1),
                           '2': array_to_string(self.frame2)
                }
        }
        wrapper['data'] = bz2.compress(BSON.encode(data))
        serialized = bson.json_util.dumps(BSON.encode(wrapper))
        self.test_stream = io.StringIO()
        self.test_stream.write(serialized)
        self.test_stream.seek(0)

    def load_file_test(self):
        scene = read_file(self.test_stream)