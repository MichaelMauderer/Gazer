from __future__ import unicode_literals, division, print_function

from abc import ABCMeta, abstractmethod


class Scene():
    __metaclass__ = ABCMeta

    def __init__(self):
        self.gaze_pos = None

    def update_gaze(self, pos):
        """
        :param pos: Gaze position normalized to image.
        """
        self.gaze_pos = pos

    @abstractmethod
    def get_image(self):
        pass
