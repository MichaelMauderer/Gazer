import functools
import pygame
from abc import ABCMeta, abstractmethod


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


class PyGameImageManager(ImageManager):
    def __init__(self, screen, depth_to_image_path=lambda x: x):
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
            print('Image ', path, 'not found')
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

