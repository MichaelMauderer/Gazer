from __future__ import unicode_literals, division, print_function

import logging
import io

from bson import BSON
import bson.json_util
import numpy as np

logger = logging.getLogger(__name__)


class DataDecoder(object):
    """
    Class responsible for deserializing gcviewer.scene.Scene objects.
    """

    def scene_from_data(self, data):
        pass


class DataEncoder(object):
    """
    Class responsible for serialising gcviewer.scene.Scene objects.
    """

    def data_from_scene(self, scene):
        pass


def array_to_bytes(array):
    """
    Convert numpy array to byte string.

    Parameters
    ----------
    array : ndarray
        Array to covnert.

    Returns
    -------
    str
        Array encodes as string.
    """
    stream = io.BytesIO()
    np.save(stream, array)
    return stream.getvalue()


def bytes_to_array(string):
    """
    Convert byte string to numpy array.

    Parameters
    ----------
    array : str
        Byte string covnert.

    Returns
    -------
    ndarray
        Decoded array.
    """
    stream = io.BytesIO(string)
    array = np.load(stream)
    array = np.require(array, requirements=['C'])
    array.flags.writeable = False
    return array


def read_file(file):
    """
    Read a gc file and decode the encoded scene object.
    Uses the decoder object specified in the gcviwer.settings.

    Parameters
    ----------
    file : file like stream
        File that contains an encoded scene.

    Returns
    -------
    gcviewer.scene.Scene
        Scene object encoded in the file or None if no valid Scene was encoded.
    """
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
    """
    Write a scene to a file.
    Uses the Encoder object specified in the gcviwer.settings.

    Parameters
    ----------
    file : file like stream
        File that contains an encoded scene.
    scene : gcviewer.scene.Scene
        Scene object to be saved.
    """

    from settings import ENCODERS
    encoder = ENCODERS.get(scene.scene_id)
    wrapper = {'encoder': 'gcviewer',
               'version': '0.1',
               'compression': 'none',
               'type': scene.scene_id,
               'data': encoder.data_from_scene(scene)
               }
    file.write(bson.json_util.dumps(BSON.encode(wrapper)))
