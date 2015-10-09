from __future__ import unicode_literals, division

from abc import ABCMeta, abstractmethod
import collections

EyeData = collections.namedtuple('EyeData',
                                 ['timestamp',
                                  'pos',
                                  'norm_pos',
                                  ])


class EyetrackingAPIBase:
    __metaclass__ = ABCMeta

    @abstractmethod
    def pop_sample(self):
        """
        Returns oldest available EyeData sample.
        """
        return NotImplemented

    @abstractmethod
    def pop_all_samples(self):
        """
        Returns all available EyeData samples.
        """
        return NotImplemented

    @abstractmethod
    def get_newest_sample(self):
        pass


class PygameMouseDummy(EyetrackingAPIBase):
    def _get_sample(self):
        import pygame

        pos = pygame.mouse.get_pos()

        posX = pos[0] / pygame.display.Info().current_w
        posY = pos[1] / pygame.display.Info().current_h
        return EyeData(None,
                       (posX, posY),
                       None)

    def pop_sample(self):
        return self._get_sample()

    def pop_all_samples(self):
        return [self.pop_sample()]

    def get_newest_sample(self):
        return self._get_sample()
