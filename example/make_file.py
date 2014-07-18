import bson
import scipy.misc
import os
import numpy
import io
from bson import BSON
import bson.json_util

depth_array = scipy.misc.imread(
    os.path.abspath('./resources/{0}_scene/depth_maps/dilate{1}/finalMap{2}.png').format('kitchen', 30, 15))
depth_array = numpy.floor(abs(depth_array - 255) / (255 / 29)) + 1


def array_to_string(array):
    stream = io.BytesIO()
    numpy.save(stream, array)
    return stream.getvalue()


def string_to_array(string):
    stream = io.BytesIO(string)
    array = numpy.load(stream)
    return array


wrapper = {'encoder': 'gcviewer',
           'version': '0.1',
           'compression': None,
           'type': 'simple_array_stack'
}
data = {'lookup_table': array_to_string(depth_array),
        'frames': {}
}

path_pattern = os.path.abspath('./resources/kitchen_scene/kitchen{0:0>3}.bmp')
for index in [i + 1 for i in range(30)]:
    array = scipy.misc.imread(path_pattern.format(index))
    data['frames'][str(index)] = array_to_string(array)

with open('out.gc', 'w') as out_file:
    out_file.write(bson.json_util.dumps(BSON.encode(data)))

#print(string_to_array(undump['lookup_table']))
