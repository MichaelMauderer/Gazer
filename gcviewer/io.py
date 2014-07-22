import logging
import operator
from bson import BSON
import bson.json_util
import bz2
import numpy
import io
from gcviewer.image_manager import ArrayStackImageManager, PyGameArrayStackManager
from gcviewer.lookup_table import ArrayLookupTable
from gcviewer.scene import ImageStackScene

logger = logging.getLogger(__name__)


class SimpleArrayStack():
    def scene_from_data(self, data, screen):
        data_dict = BSON.decode(data)
        lut = ArrayLookupTable(string_to_array(data_dict['lookup_table']))
        print(set(string_to_array(data_dict['lookup_table']).flatten()))
        print(sorted(map(float, data_dict['frames'].keys())))
        frames = [numpy.flipud(numpy.rot90(string_to_array(value))) for key, value in
                  sorted(data_dict['frames'].items(), key=lambda x: int(x[0]))]
        # print(frames)
        image_manager = PyGameArrayStackManager(frames, screen)
        scene = ImageStackScene(image_manager, lut)
        return scene


decoders = {'simple_array_stack': SimpleArrayStack}


def array_to_string(array):
    stream = io.BytesIO()
    numpy.save(stream, array)
    return stream.getvalue()


def string_to_array(string):
    stream = io.BytesIO(string)
    array = numpy.load(stream)
    return array


def read_file(file, screen):
    wrapper = BSON.decode(bson.json_util.loads(file.read()))

    logger.debug('Loading gc file with content type,', wrapper['type'])
    decoder = decoders[wrapper['type']]
    logger.debug('Found decoder:', decoder)
    body = wrapper['data']
    if wrapper['compression'] == 'bz2':
        body = bz2.decompress(body)
    scene = decoder().scene_from_data(body, screen)
    print(scene)
    return scene


def write_file(scene):
    wrapper = {'encoder': 'gcviewer',
               'version': '0.1',
               'compression': None,
               'type': 'simple_stack'
    }
    data = {'lookup_table': scene,
            'frames': {'key', 'value'

            }
    }

    wrapper['data'] = data
