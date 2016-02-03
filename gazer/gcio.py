from __future__ import unicode_literals, division, print_function

import io
import logging
import os

import numpy as np
import skimage
import skimage.io
from bson import BSON

from gazer.file_loading import read_gcfile, read_image, read_fits

logger = logging.getLogger(__name__)


def create_default_file_format_loaders():
    file_format_loaders = {'gc': read_gcfile,
                           'fits': read_fits,
                           }
    for ext in ['jpg', 'bmp', 'png']:
        file_format_loaders[ext] = read_image
    return file_format_loaders


DEFAULT_FILE_FORMAT_LOADERS = create_default_file_format_loaders()


def get_supported_file_formats():
    """
    Return list of supported file extensions.
    """
    return list(DEFAULT_FILE_FORMAT_LOADERS.keys())


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


def load_scene(path, file_format_loaders=DEFAULT_FILE_FORMAT_LOADERS):
    """
    Loads the appropriate scene for the file indicated by the path.

    Parameters
    ----------
    path : str
        Path to file to load.
    file_format_loaders: dict
        Dictionary of filename extension to loading function.
        Loading functions need to take a file path and return a Scene object.
    Returns
    -------
    gazer.scene.Scene
        Appropriate scene object to display file.
        Is None if no suitable scene is found.
    """

    file_name, file_extension = os.path.splitext(path)
    logger.debug('Got file to load: {}'.format(path))
    logger.debug('File extension is {}'.format(file_extension))
    file_extension = file_extension[1:]  # Remove leading period.
    loader = file_format_loaders.get(file_extension)
    if loader is not None:
        return loader(path)
    logging.warning('Unknown file extension: {}'.format(file_extension))


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
    """
    Extract frames and depth map from the given gc file to the given folder.

    Parameters
    ----------
    in_file: str
        Path to the input gc file.
    out_folder: str
        Path to the output folder.
    """
    scene = read_gcfile(in_file)
    extract_scene_to_stack(scene, out_folder)


def extract_scene_to_stack(scene, out_folder):
    """
    Extract frames and depth map from the given scene to the given folder.

    Parameters
    ----------
    scene: Scene
        Scene object to be extracted.
    out_folder: str
        Path to the output folder.
    """
    logger.debug('Available skimage.io plugins: {}'.format(
        str(skimage.io.find_available_plugins())))

    for idx, image in enumerate(scene.iter_images):
        out_filename = os.path.join(str(out_folder), str(idx) + ".jpg")
        skimage.io.imsave(out_filename, image)
    depth_path = os.path.join(str(out_folder), 'depthmap.png')
    depht_array = scene.lookup_table.array
    depth_image = np.asarray(depht_array, np.uint8)
    skimage.io.imsave(depth_path, depth_image)
