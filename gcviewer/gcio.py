from __future__ import unicode_literals, division, print_function

import logging
import io

from bson import BSON
import bson.json_util
import numpy as np

import bz2

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


def read_file(in_file):
    """
    Read a gc in_file and decode the encoded scene object.
    Uses the decoder object specified in the gcviwer.settings.

    Parameters
    ----------
    in_file : in_file like stream
        File that contains an encoded scene.

    Returns
    -------
    gcviewer.scene.Scene
        Scene object encoded in the in_file or None if no valid Scene
        was encoded.
    """
    logger.debug('Reading in_file')

    scene = None
    try:
        contents = in_file.read()
        loaded = bson.json_util.loads(contents)
        bson_obj = BSON(loaded)
        wrapper = bson_obj.decode()
        from gcviewer.settings import DECODERS
        decoder = DECODERS.get(wrapper['type'])
        if decoder is None:
            raise ValueError('Decoder {} not found'.format(wrapper['type']))
        body = wrapper['data']
        if wrapper['compression'] == 'bz2':
            body = bz2.decompress(body)
        scene = decoder.scene_from_data(body)

    except Exception as e:
        logger.exception('Failed to read file.' + e.message)

    return scene


def read_image(in_file):
    """
    Read a gc in_file and decode the encoded scene object.
    Uses the decoder object specified in the gcviwer.settings.

    Parameters
    ----------
    in_file : in_file like stream
        File that contains an encoded scene.

    Returns
    -------
    gcviewer.scene.Scene
        Scene object encoded in the in_file or None if no valid Scene
        was encoded.
    """
    logger.debug('Reading in_file as image')
    scene = None
    try:
        from gcviewer.modules.color.scenes import SimpleArrayDecoder
        scene = SimpleArrayDecoder().scene_from_data(in_file)
    except Exception as e:
        logger.exception('Failed to read file as image.' + e.message)
    return scene


def read_fits(in_file):
    """
    Read a gc in_file and decode the encoded scene object.
    Uses the decoder object specified in the gcviwer.settings.

    Parameters
    ----------
    in_file : in_file like stream
        File that contains an encoded scene.

    Returns
    -------
    gcviewer.scene.Scene
        Scene object encoded in the in_file or None if no valid Scene
        was encoded.
    """
    logger.debug('Reading in_file as fits file')
    scene = None
    try:
        from gcviewer.modules.color.scenes import SimpleArrayDecoder
        from astropy.io import fits
        hdu_list = fits.open(in_file)
        image_data = hdu_list[0].data
        logger.debug('Retrieved {}'.format(type(image_data)))
        logger.debug('Has shape {}'.format(image_data.shape))
        image_data = np.dstack([image_data, image_data, image_data])
        scene = SimpleArrayDecoder().scene_from_array(image_data)
    except Exception as e:
        logger.exception('Failed to read file as image.' + e.message)
    return scene


def write_file(out_file, scene):
    """
    Write a scene to a out_file.
    Uses the Encoder object specified in the gcviwer.settings.

    Parameters
    ----------
    out_file : out_file like stream
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
    out_file.write(bson.json_util.dumps(BSON.encode(wrapper)))
