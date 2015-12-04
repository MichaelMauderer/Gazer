from __future__ import unicode_literals, division, print_function

import logging
import numpy as np

from abc import ABCMeta, abstractmethod, abstractproperty

logger = logging.getLogger(__name__)


class ImageManager():
    """
    Object that manages a collection of images.
    Specifies common functionality for different implementations.
    """
    __metaclass__ = ABCMeta

    def preload(self, keys):
        pass

    @abstractmethod
    def load_image(self, key):
        pass

    def draw_image(self, key):
        pass

    @abstractmethod
    def load_array(self, key):
        pass

    @abstractproperty
    def keys(self):
        pass

    @abstractproperty
    def iter_images(self):
        pass


class ArrayStackImageManager(ImageManager):
    def __init__(self, arrays):
        super(ArrayStackImageManager, self).__init__()
        self._arrays = arrays[:]

    def _get_array(self, key):
        try:
            return self._arrays[int(key)]
        except IndexError:
            logger.warn('Image {} not found'.format(key))
            return None
        except TypeError:
            logger.warn('{} not a valid key'.format(key))
            return None

    def load_image(self, key):
        return self.load_array(key)

    def load_array(self, key):
        array = self._get_array(key)
        return array

    @property
    def keys(self):
        return range(len(self._arrays))

    @property
    def iter_images(self):
        return iter(self._arrays)
