import bz2
import logging

import numpy as np
import skimage
from bson import BSON

logger = logging.getLogger(__name__)


def read_gcfile(path):
    """
    Read a gc in_file and decode the encoded scene object.
    Uses the decoder object specified in the gazer.settings.

    Parameters
    ----------
    path : in_file like stream
        File that contains an encoded scene.

    Returns
    -------
    gazer.scene.Scene
        Scene object encoded in the in_file or None if no valid Scene
        was encoded.
    """
    logger.debug('Reading file as gcfile {}'.format(path))

    with open(path, 'rb') as in_file:
        try:
            contents = in_file.read()
            bson_obj = BSON(contents)
            wrapper = bson_obj.decode()
            from gazer.settings import DECODERS
            wrapper_type = wrapper['type']
            decoder = DECODERS.get(wrapper_type)
            if decoder is None:
                raise ValueError('Decoder {} not found'.format(wrapper_type))
            body = wrapper['data']
            if wrapper['compression'] == 'bz2':
                body = bz2.decompress(body)
            scene = decoder.scene_from_data(body)
            return scene
        except RuntimeError:
            logger.exception('Failed to read file.')


def read_image(path):
    """
    Read an image create a scene object.

    Parameters
    ----------
    path : in_file like stream
        File that contains an image scene.

    Returns
    -------
    gazer.scene.Scene
        Scene object
    """
    logger.debug('Reading file as image: {}'.format(path))
    try:
        from gazer.modules.color.scenes import SimpleArrayDecoder
        image = skimage.data.imread(path)
        scene = SimpleArrayDecoder().scene_from_array(image)
        return scene
    except RuntimeError:
        logger.exception('Failed to read file as image.')


def read_fits(path):
    """
    Read a fits file and create a scene object.

    Parameters
    ----------
    path : in_file like stream
        File that contains an encoded scene.

    Returns
    -------
    gazer.scene.Scene
        Scene object
    """
    logger.debug('Reading in_file as fits file')
    try:
        from gazer.modules.color.scenes import SimpleArrayDecoder
        from astropy.io import fits
        hdu_list = fits.open(path)
        image_data = hdu_list[0].data
        logger.debug('Retrieved {}'.format(type(image_data)))
        logger.debug('Has shape {}'.format(image_data.shape))
        image_data = np.dstack([image_data, image_data, image_data])
        scene = SimpleArrayDecoder().scene_from_array(image_data)
        return scene
    except RuntimeError:
        logger.exception('Failed to read file as image.')
