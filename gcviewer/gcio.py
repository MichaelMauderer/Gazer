from __future__ import unicode_literals, division, print_function

import logging
import io

from bson import BSON
import bson.json_util
import numpy as np

logger = logging.getLogger(__name__)


class DataDecoder(object):
    """
    Class responsible for deserializing Scene.Scene objects.
    """

    def scene_from_data(self, data):
        pass


class DataEncoder(object):
    """
    Class responsible for serialising Scene.Scene objects.
    """

    def data_from_scene(cls, scene):
        pass


def array_to_bytes(array):
    stream = io.BytesIO()
    np.save(stream, array)
    return stream.getvalue()


def bytes_to_array(string):
    stream = io.BytesIO(string)
    array = np.load(stream)
    array = np.require(array, requirements=['C'])
    array.flags.writeable = False
    return array


def read_file(file):
    logger.debug('Reading file')
    try:
        contents = file.read()
        loaded = bson.json_util.loads(contents)
        bson_obj = BSON(loaded)
        wrapper = bson_obj.decode()
    except Exception as e:
        logger.exception('Failed to read file.' + e.message)
        return None

    from gcviewer.settings import DECODERS
    decoder = DECODERS.get(wrapper['type'])
    if decoder is None:
        raise ValueError('Decoder {} not found'.format(wrapper['type']))
    body = wrapper['data']
    if wrapper['compression'] == 'bz2':
        body = bz2.decompress(body)
    scene = decoder.scene_from_data(body)
    return scene


def write_file(file, scene):
    from settings import ENCODERS
    encoder = ENCODERS.get(scene.scene_id)
    wrapper = {'encoder': 'gcviewer',
               'version': '0.1',
               'compression': 'none',
               'type': scene.scene_id,
               'data': encoder.data_from_scene(scene)
               }
    file.write(bson.json_util.dumps(BSON.encode(wrapper)))
