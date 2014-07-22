import bson
import scipy.misc
import os
import numpy
import io
import bz2

import bson.json_util
from bson import BSON

from gcviewer.io import array_to_string


def convert_to_file(out_path, depth_array, arrays):
    wrapper = {'encoder': 'gcviewer',
               'version': '0.1',
               'compression': 'bz2',
               'type': 'simple_array_stack'
    }
    data = {'lookup_table': array_to_string(depth_array),
            'frames': {str(key): array_to_string(array) for key, array in enumerate(arrays)}
    }

    with open(out_path, 'w') as out_file:
        wrapper['data'] = bz2.compress(BSON.encode(data))
        out_file.write(bson.json_util.dumps(BSON.encode(wrapper)))


if __name__ == '__main__':
    depth_array = scipy.misc.imread(
        os.path.abspath('./resources/{0}_scene/depth_maps/dilate{1}/finalMap{2}.png').format('kitchen', 30, 15))
    depth_array = numpy.floor(30 - (abs(depth_array) / (255 / 29))).astype(numpy.int8)
    path_pattern = os.path.abspath('./resources/kitchen_scene/kitchen{0:0>3}.bmp')
    frames = []
    for index in [i + 1 for i in range(30)]:
        array = scipy.misc.imread(path_pattern.format(index))
        frames.append(array)

    convert_to_file('out.gc', depth_array, frames)