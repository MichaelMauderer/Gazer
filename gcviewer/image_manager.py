import functools
import logging

import numpy
import pygame

from abc import ABCMeta, abstractmethod

logger = logging.getLogger(__name__)


class ImageManager():
    __metaclass__ = ABCMeta

    def preload(self, keys):
        pass

    @abstractmethod
    def load_image(self, key):
        pass

    @abstractmethod
    def draw_image(self, key):
        pass


class ArrayStackImageManager(ImageManager):
    def __init__(self, arrays):
        super(ArrayStackImageManager, self).__init__()
        self._arrays = arrays[:]

    def _get_array(self, key):
        try:
            print(key)
            return self._arrays[int(key)]
        except IndexError:
            logger.warn('Image {} not found'.format(key))
            return None


    def load_image(self, key):
        array = self._get_array(key)
        return array


class PyGameArrayStackManager(ArrayStackImageManager):
    def __init__(self, arrays, screen):
        super(PyGameArrayStackManager, self).__init__(arrays)
        self._screen = screen
        size = int(arrays[0].shape[0]), int(arrays[0].shape[1])
        self._surface = pygame.Surface(size)

    def draw_image(self, key):
        array = self.load_image(key)
        if array is None:
            return
        pygame.surfarray.blit_array(self._surface, array)
        self._screen.blit(self._surface, self._surface.get_rect())
        pygame.display.flip()


class PyGameImageManager(ImageManager):
    def __init__(self, screen, depth_to_image_path=lambda x: x):
        super(PyGameImageManager, self).__init__()
        self.depth_to_image_path = depth_to_image_path
        self.screen = screen

    def preload(self, keys):
        for key in keys:
            self.load_image(key)

    @functools.lru_cache(maxsize=128)
    def _load_image(self, path):
        try:
            return pygame.image.load(path)
        except pygame.error:
            logger.warn('Image {} not found'.format(path))
            return None

    def load_image(self, key):
        path = self.depth_to_image_path(key)
        image = self._load_image(path)
        return image

    def draw_image(self, key):
        image = self.load_image(key)
        if image is not None:
            self.screen.blit(image, image.get_rect())
            pygame.display.flip()

