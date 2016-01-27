from __future__ import unicode_literals, division, print_function

import os
import logging
import io
import bz2
import skimage
import skimage.io

from bson import BSON
import numpy as np

logger = logging.getLogger(__name__)


class DataDecoder(object):
    """
    Class responsible for deserializing gazer.scene.Scene objects.
    """

    def scene_from_data(self, data):
        pass


class DataEncoder(object):
    """
    Class responsible for serialising gazer.scene.Scene objects.
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
    string : str
        Byte string convert.

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


def load_scene(path):
    """
    Loads the appropriate scene for the file indicated by the path.

    Parameters
    ----------
    path : str
        Path to file to load.

    Returns
    -------
    gcviwer.scene.Scene
        Appropriate scene object to display file.
        Is None if no suitable scene is found.
    """

    file_name, file_extension = os.path.splitext(path)
    logger.debug('Got file to load: {}'.format(path))
    logger.debug('File extension is {}'.format(file_extension))
    filetype_loaders = {
        '.gc': read_gcfile,
    }
    loader = filetype_loaders.get(file_extension)
    if loader is not None:
        return loader(path)
    return read_image(path)


def read_gcfile(path):
    """
    Read a gc in_file and decode the encoded scene object.
    Uses the decoder object specified in the gcviwer.settings.

    Parameters
    ----------
    path : in_file like stream
        File that contains an encoded scene.

    Returns
    -------
    gcviewer.scene.Scene
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
    gcviewer.scene.Scene
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
    gcviewer.scene.Scene
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
    encoder = ENCODERS.get(scene.scene_type)
    wrapper = {'encoder': 'gazer',
               'version': '0.1',
               'compression': 'none',
               'type': scene.scene_type,
               'data': encoder.data_from_scene(scene)
               }
    enoded_bson = BSON.encode(wrapper)
    out_file.write(enoded_bson)


def extract_file_to_stack(in_file, out_folder):
    scene = read_gcfile(in_file)
    extract_scene_to_stack(scene, out_folder)


def extract_scene_to_stack(scene, out_folder):
    for idx, image in enumerate(scene.iter_images):
        out_filename = os.path.join(str(out_folder), str(idx) + ".jpg")
        skimage.io.imsave(out_filename, image)
    depth_path = os.path.join(str(out_folder), 'depthmap.png')
    depht_array = scene.lookup_table.array
    depth_image = np.asarray(depht_array, np.uint8)
    skimage.io.imsave(depth_path, depth_image)
