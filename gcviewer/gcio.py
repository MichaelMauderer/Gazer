from __future__ import unicode_literals, division

import logging
import bz2

from bson import BSON
import bson.json_util

import numpy as np
# import scipy.misc

from gcviewer.image_manager import ArrayStackImageManager
from gcviewer.lookup_table import ArrayLookupTable
from gcviewer.scene import ImageStackScene

import io

logger = logging.getLogger(__name__)


class SimpleArrayStack:
    @classmethod
    def scene_from_data(cls, data):
        bson_data = BSON(data)
        data_dict = bson_data.decode()
        decoded_array = cls._decode_array(data_dict[u'lookup_table'])
        lut = ArrayLookupTable(decoded_array)
        frames = [cls._decode_array(value) for key, value
                  in
                  sorted(data_dict['frames'].items(), key=lambda x: int(x[0]))]
        image_manager = ArrayStackImageManager(frames)
        scene = ImageStackScene(image_manager, lut)
        return scene

    @classmethod
    def data_from_scene(cls, scene):
        lut_array = scene.lookup_table.array

        def frame_iterator():
            for frame_index in sorted(scene.image_manager.keys):
                frame = scene.image_manager.load_array(frame_index)
                yield frame

        stream = io.BytesIO()

        data = {'lookup_table': cls._encode_array(lut_array),
                'frames': {str(key): cls._encode_array(array) for key, array in
                           enumerate(frame_iterator())}
                }

        stream.write(BSON.encode(data))
        stream.seek(0)
        return stream.getvalue()

    @classmethod
    def _encode_array(cls, array):
        return array_to_bytes(array)

    @classmethod
    def _decode_array(cls, data):
        array = bytes_to_array(data)
        array.flags.writeable = False
        return array


# class SimpleImageStack(SimpleArrayStack):
#     @classmethod
#     def _encode_array(cls, array):
#         stream = io.BytesIO()
#         scipy.misc.imsave(stream, array, format='png')
#
#     @classmethod
#     def _decode_array(cls, data):
#         scipy.misc.imread(data)


decoders = {'simple_array_stack': SimpleArrayStack}


def array_to_bytes(array):
    logger.debug('Converting array to bytes.')
    logger.debug('-- Input Array Info Start --')
    logger.debug('Shape:', array.shape)
    logger.debug('Dtype:', array.dtype)
    logger.debug('Flags:', array.flags)
    logger.debug('-- Input Array Info End --')
    stream = io.BytesIO()
    np.save(stream, array)
    return stream.getvalue()


def bytes_to_array(string):
    stream = io.BytesIO(string)
    array = np.load(stream)
    array = np.require(array, requirements=['C'])
    array.flags.writeable = False
    #logger.debug('Converting array to bytes.')
    #logger.debug('-- Output Array Info Start --')
    #logger.debug('Shape:', array.shape)
    #logger.debug('Dtype:', array.dtype)
    #logger.debug('Flags:', array.flags)
    #logger.debug('-- Output Array Info End --')
    return array


def read_file(file):
    logger.debug('Reading file')
    try:
        # contents = unicode(file.read(), 'utf-8')
        contents = file.read()
        loaded = bson.json_util.loads(contents)
        #wrapper = BSON.decode(loaded)
        bson_obj = BSON(loaded)
        wrapper = bson_obj.decode()
    except Exception, e:
        logger.exception('Failed to read file.' + e.message)
        return None

    #logger.debug('Processing file with content type,', wrapper['type'])
    decoder = decoders[wrapper['type']]

    # logger.debug('Found decoder:', decoder)
    body = wrapper['data']
    if wrapper['compression'] == 'bz2':
        body = bz2.decompress(body)
    scene = decoder.scene_from_data(body)
    return scene


def write_file(file, scene):
    wrapper = {'encoder': 'gcviewer',
               'version': '0.1',
               'compression': 'bz2',
               'type': 'simple_array_stack',
               'data': bz2.compress(SimpleArrayStack.data_from_scene(scene))
               }
    file.write(bson.json_util.dumps(BSON.encode(wrapper)))
